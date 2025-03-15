"""
בוט טלגרם ללימוד אנגלית
"""

import logging
import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum, auto

# ביטול כל האזהרות
import warnings
warnings.filterwarnings("ignore")

# Setup logging to both file and console
if not os.path.exists('logs'):
    os.makedirs('logs')
log_file = os.path.join('logs', f'bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Configure file handler for detailed logs
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Configure console handler for minimal English logs
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Setup root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Create a custom logger for our bot
logger = logging.getLogger("EnglishBot")

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)

from dotenv import load_dotenv
import google.generativeai as genai

from models import WordsRepository, UserRepository
from modules.practice.practice_module import PracticeModule, States as PracticeStates
from modules.user.user_module import UserModule, UserStates
from modules.commands.commands_module import CommandsModule

# טעינת משתני סביבה
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WORDS_FILE = os.getenv("WORDS_FILE", "data/words/words.json")
DATA_DIR = os.getenv("DATA_DIR", "data")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DISABLE_HTTPX_LOGS = os.getenv("DISABLE_HTTPX_LOGS", "False").lower() in ("true", "1", "t")

# הגדרת לוגר
log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=log_level
)
logger = logging.getLogger(__name__)

# ביטול לוגים של HTTPX
if DISABLE_HTTPX_LOGS:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext.Application").setLevel(logging.WARNING)

# אתחול Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
else:
    logger.warning("מפתח ה-API של Gemini לא מוגדר. פונקציונליות ה-AI תהיה מוגבלת.")
    model = None

# אתחול מאגרי נתונים
words_repo = WordsRepository(WORDS_FILE)
logger.info(f"Loaded {len(words_repo.words)} words from the dictionary")
user_repo = UserRepository(os.path.join(DATA_DIR, "users"))
if DATA_DIR:
    logger.info("Connected to MongoDB database")
else:
    logger.warning("No MongoDB connection defined. User data will be stored in memory temporarily.")

# מצבי שיחה להגדרת ConversationHandler
class States(Enum):
    MAIN_MENU = auto()
    REGISTRATION = auto()
    PRACTICING = auto()
    PLAYING_GAME = auto()
    READING_STORY = auto()
    WRITING = auto()
    SETTINGS = auto()

# אתחול מודולים
user_module = UserModule(user_repo)
practice_module = PracticeModule(words_repo, user_repo, user_module.get_user_profile, user_module.save_user_profile, user_module.ensure_session_data)
commands_module = CommandsModule(user_module, practice_module, States)

# פונקציית כניסה לתוכנית
def main() -> None:
    """הפעלת הבוט"""
    if not TELEGRAM_TOKEN:
        logger.error("Telegram API token not defined. Please set it in TELEGRAM_API_TOKEN.")
        return
    
    # יצירת אפליקציית הבוט
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # הוספת handlers
    application.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("start", commands_module.start_command),
            CommandHandler("home", commands_module.home_command),
        ],
        states={
            States.MAIN_MENU: [
                CommandHandler("practice", commands_module.practice_command),
                CommandHandler("word", commands_module.word_command),
                CommandHandler("profile", commands_module.profile_command),
                CallbackQueryHandler(commands_module.button_callback),
            ],
            States.REGISTRATION: [
                CallbackQueryHandler(commands_module.button_callback),
            ],
            States.PRACTICING: [
                CallbackQueryHandler(commands_module.button_callback),
            ],
            States.PLAYING_GAME: [
                CallbackQueryHandler(commands_module.button_callback),
            ],
            States.READING_STORY: [
                CallbackQueryHandler(commands_module.button_callback),
            ],
            States.WRITING: [
                CallbackQueryHandler(commands_module.button_callback),
            ],
            States.SETTINGS: [
                CallbackQueryHandler(commands_module.button_callback),
            ],
        },
        fallbacks=[CommandHandler("start", commands_module.start_command)]
    ))
    
    # הוספת handlers נוספים שלא חלק מה-ConversationHandler
    application.add_handler(CommandHandler("help", commands_module.help_command))
    
    # הפעלת הבוט
    logger.info("Bot is starting...")
    application.run_polling()
    logger.info("Bot has stopped")

if __name__ == "__main__":
    main() 