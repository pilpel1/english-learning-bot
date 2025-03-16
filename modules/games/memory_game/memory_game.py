"""
מודול למשחק זיכרון - לימוד מילים באנגלית
"""

from typing import List, Dict, Tuple, Optional
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

class MemoryGame:
    """מחלקה למשחק זיכרון"""
    
    def __init__(self):
        """אתחול המשחק"""
        self.active_games = {}  # מילון לשמירת מצב המשחק לכל משתמש
    
    async def start_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE, words: List[Dict]) -> None:
        """התחלת משחק חדש"""
        user_id = update.effective_user.id
        
        # בחירת 8 מילים אקראיות מהרשימה (אם יש מספיק)
        selected_words = random.sample(words, min(8, len(words)))
        
        # יצירת רשימת כרטיסיות - כל מילה מופיעה פעמיים (אנגלית ועברית)
        cards = []
        for word in selected_words:
            cards.append({"type": "english", "text": word["english"], "pair_id": word["id"]})
            cards.append({"type": "hebrew", "text": word["hebrew"], "pair_id": word["id"]})
        
        # ערבוב הכרטיסיות
        random.shuffle(cards)
        
        # יצירת מצב משחק חדש
        self.active_games[user_id] = {
            "cards": cards,
            "flipped": [],  # כרטיסיות שנחשפו בתור הנוכחי
            "matched": [],  # כרטיסיות שכבר נמצאו להן זוגות
            "clicks": 0,    # מספר הלחיצות
            "message_id": None,  # מזהה ההודעה של המשחק
        }
        
        # שליחת לוח המשחק
        message = await update.effective_message.reply_text(
            "🎮 *משחק הזיכרון*\n"
            "מצאו זוגות של מילים באנגלית והתרגום שלהן בעברית.\n"
            "מספר לחיצות: 0",
            reply_markup=self._create_game_keyboard(user_id),
            parse_mode="Markdown"
        )
        
        # שמירת מזהה ההודעה
        self.active_games[user_id]["message_id"] = message.message_id
    
    def _create_game_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """יצירת מקלדת למשחק"""
        game_state = self.active_games.get(user_id)
        if not game_state:
            # אם אין משחק פעיל, החזר מקלדת ריקה
            keyboard = [[InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]]
            return InlineKeyboardMarkup(keyboard)
        
        # בניית לוח המשחק 4x4
        keyboard = []
        cards = game_state["cards"]
        flipped = game_state["flipped"]
        matched = game_state["matched"]
        
        for i in range(0, 16, 4):
            row = []
            for j in range(4):
                idx = i + j
                if idx < len(cards):
                    card = cards[idx]
                    card_id = idx
                    
                    # קביעת הטקסט שיוצג על הכפתור
                    if card_id in flipped or card_id in matched:
                        # כרטיסייה חשופה
                        button_text = card["text"]
                    else:
                        # כרטיסייה מוסתרת
                        button_text = "❓"
                    
                    row.append(InlineKeyboardButton(
                        button_text, 
                        callback_data=f"memory_card_{card_id}"
                    ))
                else:
                    # אם אין מספיק כרטיסיות, הוסף כפתור ריק
                    row.append(InlineKeyboardButton(" ", callback_data="memory_empty"))
            
            keyboard.append(row)
        
        # הוספת כפתור חזרה לתפריט
        keyboard.append([InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """טיפול בלחיצות על כפתורים במשחק"""
        query = update.callback_query
        user_id = update.effective_user.id
        callback_data = query.data
        
        # בדיקה אם זו לחיצה על כרטיסייה
        if not callback_data.startswith("memory_card_"):
            # אם זה לא כרטיסייה, החזר False כדי שהמודול הראשי יטפל בזה
            return False
        
        # בדיקה אם יש משחק פעיל למשתמש
        if user_id not in self.active_games:
            await query.answer("אין משחק פעיל. התחל משחק חדש.")
            return True
        
        game_state = self.active_games[user_id]
        
        # חילוץ מזהה הכרטיסייה
        card_id = int(callback_data.split("_")[-1])
        
        # בדיקה אם הכרטיסייה כבר חשופה או כבר נמצא לה זוג
        if card_id in game_state["flipped"] or card_id in game_state["matched"]:
            await query.answer("כרטיסייה זו כבר חשופה!")
            return True
        
        # הוספת הכרטיסייה לרשימת הכרטיסיות החשופות
        game_state["flipped"].append(card_id)
        game_state["clicks"] += 1
        
        # עדכון הודעת המשחק
        await self._update_game_message(context, user_id)
        
        # בדיקה אם יש שתי כרטיסיות חשופות
        if len(game_state["flipped"]) == 2:
            # בדיקה אם הכרטיסיות מתאימות
            card1 = game_state["cards"][game_state["flipped"][0]]
            card2 = game_state["cards"][game_state["flipped"][1]]
            
            if card1["pair_id"] == card2["pair_id"] and card1["type"] != card2["type"]:
                # התאמה! הוספת הכרטיסיות לרשימת ההתאמות
                game_state["matched"].extend(game_state["flipped"])
                game_state["flipped"] = []
                
                # בדיקה אם המשחק הסתיים
                if len(game_state["matched"]) == len(game_state["cards"]):
                    await self._end_game(context, user_id)
                else:
                    await query.answer("מצאת התאמה! 🎉")
                    await self._update_game_message(context, user_id)
            else:
                # אין התאמה, המתנה של 3 שניות ואז הפיכת הכרטיסיות בחזרה
                await query.answer("אין התאמה, נסה שוב.")
                await self._update_game_message(context, user_id)
                
                # המתנה של 3 שניות
                await asyncio.sleep(3)
                
                # הפיכת הכרטיסיות בחזרה
                game_state["flipped"] = []
                await self._update_game_message(context, user_id)
        else:
            # רק כרטיסייה אחת חשופה
            await query.answer("בחר כרטיסייה נוספת.")
        
        return True
    
    async def _update_game_message(self, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
        """עדכון הודעת המשחק"""
        game_state = self.active_games.get(user_id)
        if not game_state or not game_state.get("message_id"):
            return
        
        try:
            # עדכון ההודעה
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=game_state["message_id"],
                text=f"🎮 *משחק הזיכרון*\n"
                     f"מצאו זוגות של מילים באנגלית והתרגום שלהן בעברית.\n"
                     f"מספר לחיצות: {game_state['clicks']}",
                reply_markup=self._create_game_keyboard(user_id),
                parse_mode="Markdown"
            )
        except Exception as e:
            # אם השגיאה היא שההודעה לא השתנתה, נתעלם ממנה
            if "Message is not modified" not in str(e):
                print(f"שגיאה בעדכון הודעת המשחק: {e}")
    
    async def _end_game(self, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
        """סיום המשחק"""
        game_state = self.active_games.get(user_id)
        if not game_state:
            return
        
        clicks = game_state["clicks"]
        
        # הערכת הביצועים
        if clicks <= 20:
            performance = "מדהים! 🌟🌟🌟"
        elif clicks <= 30:
            performance = "מצוין! 🌟🌟"
        elif clicks <= 40:
            performance = "טוב מאוד! 🌟"
        else:
            performance = "כל הכבוד! 👏"
        
        # שליחת הודעת סיום
        try:
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=game_state["message_id"],
                text=f"🎮 *משחק הזיכרון - סיום!*\n\n"
                     f"הצלחת למצוא את כל הזוגות תוך *{clicks}* לחיצות!\n"
                     f"{performance}\n\n"
                     f"רוצה לשחק שוב?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 משחק חדש", callback_data="game_memory")],
                    [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
                ]),
                parse_mode="Markdown"
            )
        except Exception as e:
            # אם השגיאה היא שההודעה לא השתנתה, נתעלם ממנה
            if "Message is not modified" not in str(e):
                print(f"שגיאה בשליחת הודעת סיום המשחק: {e}")
        
        # מחיקת המשחק מהמשחקים הפעילים
        del self.active_games[user_id] 