"""
מודול לתרגול מילים - תרגול אוצר מילים באנגלית
"""

from typing import Dict, List, Tuple, Union, Optional
import random
import logging  # הוספת ייבוא
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from enum import Enum

# הגדרת logger
logger = logging.getLogger(__name__)

class States(Enum):
    """מצבי שיחה"""
    MAIN_MENU = 1
    PRACTICING = 2

class PracticeModule:
    """מחלקה לתרגול מילים"""
    
    def __init__(self, words_repo, user_repo, get_user_profile, save_user_profile, ensure_session_data):
        """אתחול המודול"""
        self.active_sessions = {}  # מילון לשמירת מצב התרגול לכל משתמש
        self.words_repo = words_repo
        self.user_repo = user_repo
        self.get_user_profile = get_user_profile
        self.save_user_profile = save_user_profile
        self.ensure_session_data = ensure_session_data
    
    async def start_practice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
        """פקודה להתחלת תרגול מילים"""
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        user_profile = self.ensure_session_data(user_profile)
        level = user_profile["level"]
        
        # בחירת 5 מילים אקראיות לתרגול
        words = self.words_repo.get_random_words(5, difficulty=level)
        word_ids = [word.word_id for word in words]
        
        # שמירת המילים הנוכחיות למשתמש
        user_profile["session_data"]["current_word_set"] = word_ids
        user_profile["session_data"]["current_word_index"] = 0
        self.save_user_profile(user_profile)
        
        # הצגת הודעת פתיחה לתרגול
        practice_intro_text = (
            "🔤 *התחלת סבב תרגול מילים*\n\n"
            f"בחרתי {len(word_ids)} מילים עבורך לתרגול.\n"
            "אציג כל מילה עם הפירוש והדוגמאות שלה, ואתה תסמן אם ידעת אותה או לא.\n\n"
            "בוא נתחיל!"
        )
        
        keyboard = [
            [InlineKeyboardButton("👉 הצג את המילה הראשונה", callback_data="practice_show_word")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(practice_intro_text, reply_markup=reply_markup, parse_mode='Markdown')
        
        return States.PRACTICING
    
    async def show_random_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
        """פקודה להצגת מילה אקראית ללימוד"""
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        user_profile = self.ensure_session_data(user_profile)
        level = user_profile["level"]
        
        # בחירת מילה אקראית
        words = self.words_repo.get_random_words(1, difficulty=level)
        if not words:
            await update.message.reply_text("לא נמצאו מילים מתאימות. אנא נסה שוב מאוחר יותר.")
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
                InlineKeyboardButton("✅ זכרתי", callback_data=f"practice_remembered_{word.word_id}"),
                InlineKeyboardButton("❌ לא זכרתי", callback_data=f"practice_forgot_{word.word_id}")
            ],
            [
                InlineKeyboardButton("🔄 מילה אקראית נוספת", callback_data="practice_random"),
                InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(word_text, reply_markup=reply_markup, parse_mode='Markdown')
        
        return States.PRACTICING
    
    async def handle_practice_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> Union[States, None]:
        """טיפול בלחיצות על כפתורים הקשורים לתרגול מילים"""
        query = update.callback_query
        
        if callback_data == "practice":
            # התחלת תרגול מילים
            user = query.from_user
            user_profile = await self.get_user_profile(user.id)
            user_profile = self.ensure_session_data(user_profile)
            
            # בחירת 5 מילים אקראיות לתרגול - בלי קשר לרמה
            words = self.words_repo.get_random_words(5)
            word_ids = [word.word_id for word in words]
            
            # שמירת המילים הנוכחיות למשתמש
            user_profile["session_data"]["current_word_set"] = word_ids
            user_profile["session_data"]["current_word_index"] = 0
            await self.save_user_profile(user_profile)
            
            # הצגת הודעת פתיחה לתרגול
            practice_intro_text = (
                "🔤 *התחלת סבב תרגול מילים*\n\n"
                f"בחרתי {len(word_ids)} מילים עבורך לתרגול.\n"
                "אציג כל מילה עם הפירוש והדוגמאות שלה, ואתה תסמן אם ידעת אותה או לא.\n\n"
                "בוא נתחיל!"
            )
            
            keyboard = [
                [InlineKeyboardButton("👉 הצג את המילה הראשונה", callback_data="practice_show_word")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(practice_intro_text, reply_markup=reply_markup, parse_mode='Markdown')
            
            return States.PRACTICING
        
        elif callback_data == "practice_show_word":
            # הצגת מילה לתרגול
            return await self.show_practice_word(update, context)
        
        elif callback_data == "practice_next":
            # מעבר למילה הבאה בתרגול
            user_profile = await self.get_user_profile(query.from_user.id)
            user_profile = self.ensure_session_data(user_profile)
            user_profile["session_data"]["current_word_index"] += 1
            self.save_user_profile(user_profile)
            return await self.show_practice_word(update, context)
        
        elif callback_data.startswith("practice_remembered_") or callback_data.startswith("practice_forgot_"):
            # עדכון סטטוס מילה (זכר/שכח)
            word_id = callback_data.split("_")[-1]
            remembered = callback_data.startswith("practice_remembered_")
            
            # עדכון התקדמות המילה
            user_id = query.from_user.id
            word_progress = await self.user_repo.get_user_word_progress(user_id, word_id)
            
            # עדכון הנתונים בהתאם למה שהמשתמש בחר
            word_progress.repetitions += 1
            
            if remembered:
                if word_progress.status == self.user_repo.WordStatus.NEW:
                    word_progress.status = self.user_repo.WordStatus.LEARNING
                elif word_progress.repetitions >= 3 and word_progress.success_rate >= 0.7:
                    word_progress.status = self.user_repo.WordStatus.MASTERED
                    
                word_progress.success_rate = (word_progress.repetitions - 1) / word_progress.repetitions + (1 / word_progress.repetitions)
            else:
                word_progress.success_rate = (word_progress.repetitions - 1) / word_progress.repetitions
                if word_progress.status == self.user_repo.WordStatus.MASTERED:
                    word_progress.status = self.user_repo.WordStatus.LEARNING
            
            # שמירת ההתקדמות
            self.user_repo.update_user_word_progress(user_id, word_progress)
            
            # מעבר למילה הבאה
            user_profile = await self.get_user_profile(user_id)
            user_profile = self.ensure_session_data(user_profile)
            user_profile["session_data"]["current_word_index"] += 1
            await self.save_user_profile(user_profile)
            
            # מציג הודעה על הצלחה/כישלון
            feedback_text = "✅ מצוין! המשך כך!" if remembered else "👨‍🎓 לא נורא, זה חלק מתהליך הלמידה!"
            await query.edit_message_text(
                f"{feedback_text}\n\nטוען את המילה הבאה...",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏭️ למילה הבאה", callback_data="practice_show_word")]
                ])
            )
            
            return States.PRACTICING
        
        elif callback_data == "practice_random":
            # הצגת מילה אקראית חדשה
            user = query.from_user
            user_profile = await self.get_user_profile(user.id)
            user_profile = self.ensure_session_data(user_profile)
            level = user_profile["level"]
            
            # בחירת מילה אקראית
            words = self.words_repo.get_random_words(1, difficulty=level)
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
                    InlineKeyboardButton("✅ זכרתי", callback_data=f"practice_remembered_{word.word_id}"),
                    InlineKeyboardButton("❌ לא זכרתי", callback_data=f"practice_forgot_{word.word_id}")
                ],
                [
                    InlineKeyboardButton("🔄 מילה אקראית נוספת", callback_data="practice_random"),
                    InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(word_text, reply_markup=reply_markup, parse_mode='Markdown')
            
            return States.PRACTICING
        
        # אם הגענו לכאן, הכפתור לא טופל
        return None
    
    async def show_practice_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
        """הצגת מילה לתרגול"""
        query = update.callback_query
        user_id = query.from_user.id
        user_profile = await self.get_user_profile(user_id)
        user_profile = self.ensure_session_data(user_profile)
        
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
        word = self.words_repo.get_word(current_word_id)
        
        if not word:
            logger.error(f"לא נמצאה מילה עם מזהה {current_word_id}")
            user_profile["session_data"]["current_word_index"] += 1
            self.save_user_profile(user_profile)
            return await self.show_practice_word(update, context)
        
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
                InlineKeyboardButton("✅ זכרתי", callback_data=f"practice_remembered_{current_word_id}"),
                InlineKeyboardButton("❌ לא זכרתי", callback_data=f"practice_forgot_{current_word_id}")
            ],
            [
                InlineKeyboardButton("⏭️ המילה הבאה", callback_data="practice_next")
            ],
            [
                InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(word_text, reply_markup=reply_markup, parse_mode='Markdown')
        
        return States.PRACTICING 