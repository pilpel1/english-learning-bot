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

from models import Word, WordsRepository, WordStatus, UserWordProgress, UserRepository

# טעינת משתני סביבה
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WORDS_FILE = os.getenv("WORDS_FILE", "data/words/words.json")
MONGO_URI = os.getenv("MONGO_URI")
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

# טעינת מאגר המילים
words_repo = WordsRepository(WORDS_FILE)
logger.info(f"Loaded {len(words_repo.words)} words from the dictionary")

# אתחול מאגר המשתמשים
user_repo = UserRepository(MONGO_URI)
if MONGO_URI:
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

# פונקציות עזר
def get_user_profile(user_id: int) -> Dict:
    """
    קבלת פרופיל משתמש באמצעות UserRepository
    """
    return user_repo.get_user(user_id)

def save_user_profile(user_profile: Dict) -> bool:
    """
    שמירת פרופיל משתמש באמצעות UserRepository
    """
    return user_repo.save_user(user_profile)

def ensure_session_data(user_profile: Dict) -> Dict:
    """
    וידוא שהמשתמש מכיל את כל הנתונים הדרושים למפגש הנוכחי
    """
    if "session_data" not in user_profile:
        user_profile["session_data"] = {}
    
    if "current_word_set" not in user_profile["session_data"]:
        user_profile["session_data"]["current_word_set"] = []
    
    if "current_word_index" not in user_profile["session_data"]:
        user_profile["session_data"]["current_word_index"] = 0
    
    if "conversation_context" not in user_profile["session_data"]:
        user_profile["session_data"]["conversation_context"] = {}
    
    return user_profile

# פקודות בוט
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    """טיפול בפקודת ההתחלה /start"""
    user = update.effective_user
    user_profile = get_user_profile(user.id)
    user_profile = ensure_session_data(user_profile)
    
    # בדיקה אם זה משתמש חדש
    is_new_user = "has_started" not in user_profile
    
    if is_new_user:
        user_profile["has_started"] = True
        save_user_profile(user_profile)
        
        welcome_text = (
            f"ברוך הבא {user.first_name}! 👋\n\n"
            "אני בוט ללימוד אנגלית שיעזור לך לשפר את אוצר המילים והכישורים שלך באנגלית.\n\n"
            "אני אלמד אותך כ-4,300 מילים באנגלית באמצעות תרגולים, משחקים ופעילויות מהנות."
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 בואו נתחיל!", callback_data="register")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        return States.REGISTRATION
    else:
        # משתמש קיים - הצגת התפריט הראשי
        return await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    """הצגת התפריט הראשי"""
    user = update.effective_user if update.effective_user else update.callback_query.from_user
    user_profile = get_user_profile(user.id)
    user_profile = ensure_session_data(user_profile)
    save_user_profile(user_profile)
    
    # חישוב סטריק יומי
    streak_text = f"🔥 סטריק יומי: {user_profile['progress']['daily_streaks']} ימים"
    
    # חישוב מספר המילים שנלמדו
    words_mastered = user_profile['progress']['words_mastered']
    words_progress = f"📚 מילים שנלמדו: {words_mastered}/4300 ({(words_mastered/4300)*100:.1f}%)"
    
    menu_text = (
        f"שלום {user.first_name}!\n\n"
        f"{streak_text}\n"
        f"{words_progress}\n\n"
        "מה תרצה לעשות היום?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🔤 תרגול מילים", callback_data="practice"),
            InlineKeyboardButton("🎮 משחקים", callback_data="games")
        ],
        [
            InlineKeyboardButton("📚 סיפורים", callback_data="stories"),
            InlineKeyboardButton("✍️ אתגרי כתיבה", callback_data="writing")
        ],
        [
            InlineKeyboardButton("💬 צ'אט", callback_data="chat"),
            InlineKeyboardButton("📊 התקדמות", callback_data="progress")
        ],
        [
            InlineKeyboardButton("⚙️ הגדרות", callback_data="settings")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # בדיקה אם זו הודעה חדשה או עדכון לקיימת
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
    
    return States.MAIN_MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """טיפול בפקודת העזרה /help"""
    help_text = """
🤖 *בוט ללימוד אנגלית - פקודות עיקריות*

/start - התחלת שיחה עם הבוט או חזרה לתפריט הראשי
/help - הצגת הודעת עזרה זו
/profile - צפייה בפרופיל שלך והתקדמות
/practice - התחלת תרגול מילים
/word - קבלת מילה אקראית ללימוד
/stats - הצגת סטטיסטיקות למידה

לכל שאלה או בעיה, אל תהסס לפנות אלינו!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """טיפול בפקודת הפרופיל /profile"""
    user = update.effective_user
    user_profile = get_user_profile(user.id)
    user_profile = ensure_session_data(user_profile)
    save_user_profile(user_profile)
    
    # חישוב אחוז התקדמות
    words_mastered = user_profile['progress']['words_mastered']
    progress_percent = (words_mastered / 4300) * 100
    
    profile_text = f"""
📊 *הפרופיל שלך*:

👤 שם: {user.first_name}
📅 הצטרפת בתאריך: {user_profile["join_date"]}
🔥 סטריק יומי: {user_profile["progress"]["daily_streaks"]} ימים

📚 *התקדמות*:
- מילים שנלמדו: {words_mastered} / 4300 ({progress_percent:.1f}%)
- זמן לימוד כולל: {user_profile["progress"]["total_practice_time"]} דקות

🏆 *הישגים*:
{', '.join(user_profile["progress"]["achievement_badges"]) if user_profile["progress"]["achievement_badges"] else "אין עדיין הישגים"}
"""
    
    # הוספת כפתורים לפרופיל
    keyboard = [
        [
            InlineKeyboardButton("📊 סטטיסטיקות מפורטות", callback_data="detailed_stats"),
            InlineKeyboardButton("🗓️ היסטוריית למידה", callback_data="learning_history")
        ],
        [
            InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(profile_text, reply_markup=reply_markup, parse_mode='Markdown')

async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    """פקודה להתחלת תרגול מילים"""
    user = update.effective_user
    user_profile = get_user_profile(user.id)
    user_profile = ensure_session_data(user_profile)
    level = user_profile["current_level"]
    
    # בחירת 5 מילים אקראיות לתרגול
    words = words_repo.get_random_words(5, difficulty=level)
    word_ids = [word.word_id for word in words]
    
    # שמירת המילים הנוכחיות למשתמש
    user_profile["session_data"]["current_word_set"] = word_ids
    user_profile["session_data"]["current_word_index"] = 0
    save_user_profile(user_profile)
    
    # הצגת הודעת פתיחה לתרגול
    practice_intro_text = (
        "🔤 *התחלת סבב תרגול מילים*\n\n"
        f"בחרתי {len(word_ids)} מילים עבורך לתרגול.\n"
        "אציג כל מילה עם הפירוש והדוגמאות שלה, ואתה תסמן אם ידעת אותה או לא.\n\n"
        "בוא נתחיל!"
    )
    
    keyboard = [
        [InlineKeyboardButton("👉 הצג את המילה הראשונה", callback_data="show_practice_word")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(practice_intro_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    return States.PRACTICING

async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """פקודה להצגת מילה אקראית ללימוד"""
    user = update.effective_user
    user_profile = get_user_profile(user.id)
    user_profile = ensure_session_data(user_profile)
    level = user_profile["current_level"]
    
    # בחירת מילה אקראית
    words = words_repo.get_random_words(1, difficulty=level)
    if not words:
        await update.message.reply_text("לא נמצאו מילים מתאימות. אנא נסה שוב מאוחר יותר.")
        return
    
    word = words[0]
    
    # הכנת הטקסט למילה
    word_text = (
        f"📝 *מילה אקראית*: *{word.english}*\n"
    )
    
    # אם יש תרגום באנגלית, מציגים אותו
    if word.translation:
        word_text += f"🔤 תרגום באנגלית: *{word.translation}*\n"
    
    # אם יש תרגום לעברית, מציגים אותו
    if word.hebrew:
        word_text += f"🔤 תרגום לעברית: *{word.hebrew}*\n"
    
    # אם יש חלק דיבור, מציגים אותו
    if word.part_of_speech:
        word_text += f"📋 חלק דיבור: *{word.part_of_speech}*\n"
    
    # אם יש דוגמאות, מציגים אותן
    if word.examples:
        word_text += "\n📚 דוגמאות:\n"
        for i, example in enumerate(word.examples[:2], 1):
            word_text += f"{i}. {example}\n"
    
    # אם יש מילים נרדפות, מציגים אותן
    if word.synonyms:
        word_text += f"\n🔄 מילים נרדפות: {', '.join(word.synonyms)}"
    
    # כפתורים למשתמש
    keyboard = [
        [
            InlineKeyboardButton("✅ זכרתי", callback_data=f"word_remembered_{word.word_id}"),
            InlineKeyboardButton("❌ לא זכרתי", callback_data=f"word_forgot_{word.word_id}")
        ],
        [
            InlineKeyboardButton("🔄 מילה אקראית נוספת", callback_data="random_word"),
            InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(word_text, reply_markup=reply_markup, parse_mode='Markdown')

# טיפול בלחיצות על כפתורים
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[States, None]:
    """טיפול בלחיצות על כפתורים"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "back_to_menu":
        return await show_main_menu(update, context)
    
    elif callback_data == "register":
        # התחלת תהליך הרשמה
        await query.edit_message_text(
            "בוא נתחיל בהגדרת הפרופיל שלך.\n\n"
            "מהי רמת האנגלית שלך?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("מתחיל 🔰", callback_data="level_1")],
                [InlineKeyboardButton("בינוני 🔷", callback_data="level_2")],
                [InlineKeyboardButton("מתקדם 🔹", callback_data="level_3")]
            ])
        )
        return States.REGISTRATION
    
    elif callback_data.startswith("level_"):
        # שמירת רמת האנגלית של המשתמש
        level = int(callback_data.split("_")[1])
        user_profile = get_user_profile(query.from_user.id)
        user_profile = ensure_session_data(user_profile)
        user_profile["current_level"] = level
        save_user_profile(user_profile)
        
        level_names = {1: "מתחיל", 2: "בינוני", 3: "מתקדם"}
        
        await query.edit_message_text(
            f"מצוין! בחרת ברמה: {level_names[level]}.\n\n"
            "הרשמתך הושלמה בהצלחה! 🎉\n"
            "אתה מוכן להתחיל ללמוד אנגלית.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 למסך הראשי", callback_data="back_to_menu")]
            ])
        )
        return States.MAIN_MENU
    
    elif callback_data == "practice":
        # התחלת תרגול מילים
        user_profile = get_user_profile(query.from_user.id)
        user_profile = ensure_session_data(user_profile)
        level = user_profile["current_level"]
        
        # בחירת 5 מילים אקראיות לתרגול
        words = words_repo.get_random_words(5, difficulty=level)
        word_ids = [word.word_id for word in words]
        
        # שמירת המילים הנוכחיות למשתמש
        user_profile["session_data"]["current_word_set"] = word_ids
        user_profile["session_data"]["current_word_index"] = 0
        save_user_profile(user_profile)
        
        # הצגת הודעת פתיחה לתרגול
        practice_intro_text = (
            "🔤 *התחלת סבב תרגול מילים*\n\n"
            f"בחרתי {len(word_ids)} מילים עבורך לתרגול.\n"
            "אציג כל מילה עם הפירוש והדוגמאות שלה, ואתה תסמן אם ידעת אותה או לא.\n\n"
            "בוא נתחיל!"
        )
        
        keyboard = [
            [InlineKeyboardButton("👉 הצג את המילה הראשונה", callback_data="show_practice_word")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(practice_intro_text, reply_markup=reply_markup, parse_mode='Markdown')
        
        return States.PRACTICING
    
    elif callback_data == "show_practice_word":
        # הצגת המילה לתרגול
        return await show_practice_word(update, context)
    
    elif callback_data == "next_word":
        # מעבר למילה הבאה בתרגול
        user_profile = get_user_profile(query.from_user.id)
        user_profile = ensure_session_data(user_profile)
        user_profile["session_data"]["current_word_index"] += 1
        save_user_profile(user_profile)
        return await show_practice_word(update, context)
    
    elif callback_data.startswith("word_remembered_") or callback_data.startswith("word_forgot_"):
        # עדכון סטטוס מילה (זכר/שכח)
        word_id = callback_data.split("_")[-1]
        remembered = callback_data.startswith("word_remembered_")
        
        # עדכון התקדמות המילה
        user_id = query.from_user.id
        word_progress = user_repo.get_user_word_progress(user_id, word_id)
        
        # עדכון הנתונים בהתאם למה שהמשתמש בחר
        word_progress.repetitions += 1
        
        if remembered:
            if word_progress.status == WordStatus.NEW:
                word_progress.status = WordStatus.LEARNING
            elif word_progress.repetitions >= 3 and word_progress.success_rate >= 0.7:
                word_progress.status = WordStatus.MASTERED
                
            word_progress.success_rate = (word_progress.repetitions - 1) / word_progress.repetitions + (1 / word_progress.repetitions)
        else:
            word_progress.success_rate = (word_progress.repetitions - 1) / word_progress.repetitions
            if word_progress.status == WordStatus.MASTERED:
                word_progress.status = WordStatus.LEARNING
        
        # שמירת ההתקדמות
        user_repo.update_user_word_progress(user_id, word_progress)
        
        # מעבר למילה הבאה
        user_profile = get_user_profile(user_id)
        user_profile = ensure_session_data(user_profile)
        user_profile["session_data"]["current_word_index"] += 1
        save_user_profile(user_profile)
        
        # מציג הודעה על הצלחה/כישלון
        feedback_text = "✅ מצוין! המשך כך!" if remembered else "👨‍🎓 לא נורא, זה חלק מתהליך הלמידה!"
        await query.edit_message_text(
            f"{feedback_text}\n\nטוען את המילה הבאה...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏭️ למילה הבאה", callback_data="show_practice_word")]
            ])
        )
        
        return States.PRACTICING
    
    elif callback_data == "random_word":
        # הצגת מילה אקראית חדשה
        user = query.from_user
        user_profile = get_user_profile(user.id)
        user_profile = ensure_session_data(user_profile)
        level = user_profile["current_level"]
        
        # בחירת מילה אקראית
        words = words_repo.get_random_words(1, difficulty=level)
        if not words:
            await query.edit_message_text(
                "לא נמצאו מילים מתאימות. אנא נסה שוב מאוחר יותר.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
                ])
            )
            return States.MAIN_MENU
        
        word = words[0]
        
        # הכנת הטקסט למילה
        word_text = (
            f"📝 *מילה אקראית*: *{word.english}*\n"
        )
        
        # אם יש תרגום באנגלית, מציגים אותו
        if word.translation:
            word_text += f"🔤 תרגום באנגלית: *{word.translation}*\n"
        
        # אם יש תרגום לעברית, מציגים אותו
        if word.hebrew:
            word_text += f"🔤 תרגום לעברית: *{word.hebrew}*\n"
        
        # אם יש חלק דיבור, מציגים אותו
        if word.part_of_speech:
            word_text += f"📋 חלק דיבור: *{word.part_of_speech}*\n"
        
        # אם יש דוגמאות, מציגים אותן
        if word.examples:
            word_text += "\n📚 דוגמאות:\n"
            for i, example in enumerate(word.examples[:2], 1):
                word_text += f"{i}. {example}\n"
        
        # אם יש מילים נרדפות, מציגים אותן
        if word.synonyms:
            word_text += f"\n🔄 מילים נרדפות: {', '.join(word.synonyms)}"
        
        # כפתורים למשתמש
        keyboard = [
            [
                InlineKeyboardButton("✅ זכרתי", callback_data=f"word_remembered_{word.word_id}"),
                InlineKeyboardButton("❌ לא זכרתי", callback_data=f"word_forgot_{word.word_id}")
            ],
            [
                InlineKeyboardButton("🔄 מילה אקראית נוספת", callback_data="random_word"),
                InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(word_text, reply_markup=reply_markup, parse_mode='Markdown')
        
        return States.MAIN_MENU
    
    # עבור פעולות אחרות שטרם מומשו
    else:
        await query.edit_message_text(
            "פיצ'ר זה עדיין בפיתוח. 🚧\nאנא נסה פעולה אחרת.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
            ])
        )
        return States.MAIN_MENU

async def show_practice_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    """הצגת מילה לתרגול"""
    query = update.callback_query
    user_id = query.from_user.id
    user_profile = get_user_profile(user_id)
    user_profile = ensure_session_data(user_profile)
    
    # קבלת מידע על המילה הנוכחית
    word_ids = user_profile["session_data"]["current_word_set"]
    current_index = user_profile["session_data"]["current_word_index"]
    
    # בדיקה אם סיימנו את הסט
    if current_index >= len(word_ids):
        await query.edit_message_text(
            "כל הכבוד! סיימת את מפגש התרגול. 🎉\n\n"
            "רוצה לתרגל עוד מילים?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ כן, תן לי עוד", callback_data="practice")],
                [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
            ])
        )
        return States.MAIN_MENU
    
    # קבלת המילה הנוכחית
    current_word_id = word_ids[current_index]
    word = words_repo.get_word(current_word_id)
    
    if not word:
        logger.error(f"לא נמצאה מילה עם מזהה {current_word_id}")
        user_profile["session_data"]["current_word_index"] += 1
        save_user_profile(user_profile)
        return await show_practice_word(update, context)
    
    # הכנת הטקסט למילה
    word_text = (
        f"📝 מילה #{current_index + 1}/{len(word_ids)}: *{word.english}*\n"
    )
    
    # אם יש תרגום באנגלית, מציגים אותו
    if word.translation:
        word_text += f"🔤 תרגום באנגלית: *{word.translation}*\n"
    
    # אם יש תרגום לעברית, מציגים אותו
    if word.hebrew:
        word_text += f"🔤 תרגום לעברית: *{word.hebrew}*\n"
    
    # אם יש חלק דיבור, מציגים אותו
    if word.part_of_speech:
        word_text += f"📋 חלק דיבור: *{word.part_of_speech}*\n"
    
    # אם יש דוגמאות, מציגים אותן
    if word.examples:
        word_text += "\n📚 דוגמאות:\n"
        for i, example in enumerate(word.examples[:2], 1):
            word_text += f"{i}. {example}\n"
    
    # אם יש מילים נרדפות, מציגים אותן
    if word.synonyms:
        word_text += f"\n🔄 מילים נרדפות: {', '.join(word.synonyms)}"
    
    # כפתורים למשתמש
    keyboard = [
        [
            InlineKeyboardButton("✅ זכרתי", callback_data=f"word_remembered_{current_word_id}"),
            InlineKeyboardButton("❌ לא זכרתי", callback_data=f"word_forgot_{current_word_id}")
        ],
        [
            InlineKeyboardButton("⏭️ המילה הבאה", callback_data="next_word")
        ],
        [
            InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(word_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    return States.PRACTICING

# פונקציית כניסה לתוכנית
def main() -> None:
    """פונקציית הרצה עיקרית של הבוט"""
    if not API_TOKEN:
        logger.error("Telegram API token not defined. Please set it in TELEGRAM_API_TOKEN.")
        return
    
    # יצירת האפליקציה
    application = Application.builder().token(API_TOKEN).build()
    
    # הגדרת פקודות
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("practice", practice_command))
    application.add_handler(CommandHandler("word", word_command))
    
    # הגדרת ConversationHandler עיקרי
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            States.MAIN_MENU: [
                CallbackQueryHandler(button_callback),
            ],
            States.REGISTRATION: [
                CallbackQueryHandler(button_callback),
            ],
            States.PRACTICING: [
                CallbackQueryHandler(button_callback),
            ],
            # מצבים נוספים יתווספו בהמשך
        },
        fallbacks=[CommandHandler("start", start_command)]
    )
    
    application.add_handler(conv_handler)
    
    # טיפול בשגיאות
    application.add_error_handler(lambda update, context: logger.error(f"Error: {context.error}"))
    
    # התחלת ההאזנה להודעות
    logger.info("Bot is starting...")
    application.run_polling()
    logger.info("Bot has stopped")


if __name__ == "__main__":
    main() 