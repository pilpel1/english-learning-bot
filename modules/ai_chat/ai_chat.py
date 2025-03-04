"""
מודול לצ'אט עם AI - תרגול שיחה באנגלית
"""

from typing import Dict, List
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# בדיקה אם יש מפתח API של Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class AIChat:
    """מחלקה לניהול שיחות עם AI"""
    
    def __init__(self):
        """אתחול המודול"""
        self.active_chats = {}  # מילון לשמירת היסטוריית שיחה לכל משתמש
        self.has_api_key = GEMINI_API_KEY is not None
    
    async def start_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_level: str) -> None:
        """התחלת שיחה חדשה"""
        user_id = update.effective_user.id
        
        if not self.has_api_key:
            await update.effective_message.reply_text(
                "מצטערים, אין אפשרות לשוחח עם AI כרגע. המפתח לא מוגדר."
            )
            return
        
        # איפוס היסטוריית השיחה
        self.active_chats[user_id] = []
        
        # הודעת פתיחה
        await update.effective_message.reply_text(
            f"בואו נתרגל אנגלית! אני בוט AI שישוחח איתך באנגלית ברמה {user_level}.\n"
            "אתה יכול לכתוב לי הודעות באנגלית ואני אענה לך.\n"
            "כשתרצה לסיים את השיחה, פשוט כתוב 'exit' או 'quit'.",
            reply_markup=self._create_chat_keyboard()
        )
    
    async def process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_level: str) -> None:
        """עיבוד הודעה מהמשתמש ושליחת תשובה"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # בדיקה אם המשתמש רוצה לצאת
        if user_message.lower() in ["exit", "quit"]:
            await update.effective_message.reply_text(
                "סיימנו את השיחה. מקווה שנהנית לתרגל אנגלית!",
                reply_markup=self._create_exit_keyboard()
            )
            return
        
        # TODO: שליחת ההודעה ל-Gemini API וקבלת תשובה
        ai_response = f"This is a placeholder response. In the future, I'll use Gemini API to respond to: '{user_message}'"
        
        # שמירת ההיסטוריה
        if user_id in self.active_chats:
            self.active_chats[user_id].append({"user": user_message, "ai": ai_response})
        
        await update.effective_message.reply_text(ai_response)
    
    def _create_chat_keyboard(self) -> InlineKeyboardMarkup:
        """יצירת מקלדת לשיחה"""
        keyboard = [
            [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def _create_exit_keyboard(self) -> InlineKeyboardMarkup:
        """יצירת מקלדת ליציאה מהשיחה"""
        keyboard = [
            [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(keyboard) 