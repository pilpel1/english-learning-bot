"""
מודול לניהול פקודות הבוט
"""
from typing import Dict, Optional
from enum import Enum
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ייבוא ישיר של UserStates
from modules.user.user_module import UserStates

class CommandsModule:
    """מחלקה לניהול פקודות הבוט"""
    
    def __init__(self, user_module, practice_module, states_enum):
        """
        אתחול מודול הפקודות
        
        Args:
            user_module: מודול ניהול המשתמשים
            practice_module: מודול התרגול
            states_enum: מחלקת ה-Enum של מצבי השיחה הראשיים
        """
        self.user_module = user_module
        self.practice_module = practice_module
        self.States = states_enum
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בפקודת ההתחלה /start"""
        user_state = await self.user_module.start_command(update, context)
        
        # השוואה ישירה עם UserStates
        if user_state == UserStates.MAIN_MENU:
            return self.States.MAIN_MENU
        elif user_state == UserStates.REGISTRATION:
            return self.States.REGISTRATION
        elif user_state == UserStates.SETTINGS:
            return self.States.SETTINGS
        return self.States.MAIN_MENU
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת התפריט הראשי"""
        user_state = await self.user_module.show_main_menu(update, context)
        # המרת מצב UserStates למצב States
        if user_state == self.user_module.UserStates.MAIN_MENU:
            return self.States.MAIN_MENU
        return self.States.MAIN_MENU
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """טיפול בפקודת העזרה /help"""
        help_text = """
🤖 *עזרה - בוט לימוד אנגלית* 🤖

הבוט מציע מגוון דרכים ללמוד אנגלית:

📚 *פקודות עיקריות*:
/start - התחלת השימוש בבוט
/help - הצגת הודעה זו
/profile - הצגת הפרופיל שלך
/practice - התחלת תרגול מילים
/word - קבלת מילה אקראית לתרגול
/home - חזרה לתפריט הראשי

🎯 *תרגול מילים*:
לימוד מילים חדשות באמצעות כרטיסיות ותרגולים

🎮 *משחקים*:
משחקים מהנים לשיפור אוצר המילים

📖 *סיפורים*:
קריאת סיפורים קצרים באנגלית

✍️ *כתיבה*:
תרגילי כתיבה לשיפור הכתיבה באנגלית

⚙️ *הגדרות*:
התאמת הבוט להעדפותיך
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """טיפול בפקודת הפרופיל /profile"""
        await self.user_module.profile_command(update, context)
    
    async def practice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בפקודת התרגול /practice"""
        practice_state = await self.practice_module.start_practice(update, context)
        # המרת מצב PracticeStates למצב States
        if practice_state == self.practice_module.States.PRACTICING:
            return self.States.PRACTICING
        return self.States.MAIN_MENU
    
    async def word_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בפקודת המילה /word"""
        practice_state = await self.practice_module.show_random_word(update, context)
        # המרת מצב PracticeStates למצב States
        if practice_state == self.practice_module.States.PRACTICING:
            return self.States.PRACTICING
        return self.States.MAIN_MENU
    
    async def home_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בפקודת הבית /home"""
        user_state = await self.user_module.home_command(update, context)
        
        # השוואה ישירה עם UserStates במקום דרך user_module
        if user_state == UserStates.MAIN_MENU:
            return self.States.MAIN_MENU
        return self.States.MAIN_MENU
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בלחיצות על כפתורים"""
        query = update.callback_query
        callback_data = query.data
        
        # בדיקה אם הכפתור קשור למודול המשתמש
        user_state = await self.user_module.handle_callback(update, context, callback_data)
        if user_state is not None:
            # המרת מצב UserStates למצב States
            if callback_data == "back_to_menu":
                return self.States.MAIN_MENU
            elif callback_data.startswith("register_"):
                return self.States.REGISTRATION
            elif callback_data == "settings":
                return self.States.SETTINGS
            elif callback_data == "practice":
                return self.States.PRACTICING
            return self.States.MAIN_MENU
        
        # בדיקה אם הכפתור קשור למודול התרגול
        if callback_data.startswith("practice_") or callback_data == "practice":
            practice_state = await self.practice_module.handle_practice_callback(update, context, callback_data)
            return self.States.PRACTICING if practice_state else self.States.MAIN_MENU
        
        # טיפול בכפתורים אחרים
        if callback_data == "games":
            await query.answer("משחקים יהיו זמינים בקרוב! 🎮")
            return self.States.MAIN_MENU
        elif callback_data == "stories":
            await query.answer("סיפורים יהיו זמינים בקרוב! 📖")
            return self.States.MAIN_MENU
        elif callback_data == "writing":
            await query.answer("תרגילי כתיבה יהיו זמינים בקרוב! ✍️")
            return self.States.MAIN_MENU
        elif callback_data == "settings":
            await query.answer("הגדרות יהיו זמינות בקרוב! ⚙️")
            return self.States.MAIN_MENU
        
        # אם הגענו לכאן, הכפתור לא טופל
        await query.answer("פעולה לא מוכרת")
        return self.States.MAIN_MENU
    
    async def show_practice_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת מילה לתרגול"""
        practice_state = await self.practice_module.show_practice_word(update, context)
        # המרת מצב PracticeStates למצב States
        if practice_state == self.practice_module.States.PRACTICING:
            return self.States.PRACTICING
        return self.States.MAIN_MENU 