"""
מודול לתרגול מילים - תרגול אוצר מילים באנגלית
"""

from typing import Dict, List, Tuple
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

class PracticeModule:
    """מחלקה לתרגול מילים"""
    
    def __init__(self):
        """אתחול המודול"""
        self.active_sessions = {}  # מילון לשמירת מצב התרגול לכל משתמש
    
    async def start_practice(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                            words: List[Dict], num_words: int = 5) -> None:
        """התחלת סשן תרגול חדש"""
        user_id = update.effective_user.id
        
        # בחירת מילים אקראיות לתרגול
        if len(words) < num_words:
            selected_words = words
        else:
            selected_words = random.sample(words, num_words)
        
        # שמירת המילים לתרגול עבור המשתמש
        self.active_sessions[user_id] = {
            "words": selected_words,
            "current_index": 0,
            "correct": 0,
            "total": len(selected_words)
        }
        
        # הצגת המילה הראשונה
        await self._show_next_word(update, context, user_id)
    
    async def _show_next_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
        """הצגת המילה הבאה בתרגול"""
        if user_id not in self.active_sessions:
            return
        
        session = self.active_sessions[user_id]
        
        # בדיקה אם הסתיים התרגול
        if session["current_index"] >= len(session["words"]):
            await self._show_practice_summary(update, context, user_id)
            return
        
        # הצגת המילה הנוכחית
        current_word = session["words"][session["current_index"]]
        
        message_text = (
            f"*מילה {session['current_index'] + 1} מתוך {session['total']}*\n\n"
            f"*{current_word['english']}*\n\n"
            "האם אתה יודע את המשמעות של המילה הזו?"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ כן, אני יודע", callback_data=f"practice_know"),
                InlineKeyboardButton("❌ לא, הראה לי", callback_data=f"practice_show")
            ],
            [
                InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # שליחת ההודעה
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message_text, reply_markup=reply_markup, parse_mode='Markdown'
            )
        else:
            await update.effective_message.reply_text(
                message_text, reply_markup=reply_markup, parse_mode='Markdown'
            )
    
    async def handle_practice_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                     callback_data: str) -> None:
        """טיפול בלחיצות על כפתורים בתרגול"""
        user_id = update.effective_user.id
        query = update.callback_query
        
        if user_id not in self.active_sessions:
            await query.answer("סשן התרגול הסתיים או לא קיים.")
            return
        
        session = self.active_sessions[user_id]
        current_word = session["words"][session["current_index"]]
        
        if callback_data == "practice_know":
            # המשתמש ידע את המילה
            session["correct"] += 1
            await query.answer("מצוין! 👍")
            
            # הצגת התרגום והמעבר למילה הבאה
            message_text = (
                f"*{current_word['english']}*\n"
                f"תרגום: {current_word['hebrew']}\n"
                f"חלק דיבר: {current_word['part_of_speech']}\n\n"
                "לחץ על 'המילה הבאה' כדי להמשיך."
            )
            
            keyboard = [
                [InlineKeyboardButton("⏭️ המילה הבאה", callback_data="practice_next")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        elif callback_data == "practice_show":
            # המשתמש לא ידע את המילה
            await query.answer("אין בעיה, הנה התרגום.")
            
            # הצגת התרגום והמעבר למילה הבאה
            message_text = (
                f"*{current_word['english']}*\n"
                f"תרגום: {current_word['hebrew']}\n"
                f"חלק דיבר: {current_word['part_of_speech']}\n\n"
                "לחץ על 'המילה הבאה' כדי להמשיך."
            )
            
            keyboard = [
                [InlineKeyboardButton("⏭️ המילה הבאה", callback_data="practice_next")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        elif callback_data == "practice_next":
            # מעבר למילה הבאה
            session["current_index"] += 1
            await self._show_next_word(update, context, user_id)
    
    async def _show_practice_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
        """הצגת סיכום התרגול"""
        if user_id not in self.active_sessions:
            return
        
        session = self.active_sessions[user_id]
        
        # חישוב אחוז ההצלחה
        success_rate = (session["correct"] / session["total"]) * 100 if session["total"] > 0 else 0
        
        message_text = (
            "*סיכום התרגול*\n\n"
            f"מילים שידעת: {session['correct']} מתוך {session['total']}\n"
            f"אחוז הצלחה: {success_rate:.1f}%\n\n"
            "כל הכבוד על ההשקעה! המשך לתרגל כדי לשפר את אוצר המילים שלך."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 תרגול חדש", callback_data="start_practice")],
            [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # שליחת ההודעה
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message_text, reply_markup=reply_markup, parse_mode='Markdown'
            )
        else:
            await update.effective_message.reply_text(
                message_text, reply_markup=reply_markup, parse_mode='Markdown'
            )
        
        # ניקוי הסשן
        del self.active_sessions[user_id] 