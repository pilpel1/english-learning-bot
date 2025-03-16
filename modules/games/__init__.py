"""
מודול לניהול משחקים
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from modules.games.memory_game.memory_game import MemoryGame
import json
import os
import random

class GamesModule:
    """מחלקה לניהול משחקים"""
    
    def __init__(self, user_module):
        """
        אתחול מודול המשחקים
        
        Args:
            user_module: מודול ניהול המשתמשים
        """
        self.user_module = user_module
        self.memory_game = MemoryGame()  # יצירת מופע של משחק הזיכרון
        
        # טעינת מאגר המילים המלא (אם קיים)
        self.all_words = []
        words_file_path = "data/words/words_complete_unique_ids.json"
        if os.path.exists(words_file_path):
            try:
                with open(words_file_path, 'r', encoding='utf-8') as f:
                    loaded_words = json.load(f)
                
                # בדיקה והתאמה של מבנה המילים
                for i, word in enumerate(loaded_words):
                    # בדיקה אם המילה מכילה את השדות הנדרשים
                    if isinstance(word, dict) and "english" in word and "hebrew" in word:
                        # הוספת שדה id אם חסר
                        if "id" not in word:
                            word["id"] = i + 1000  # מספר גדול כדי למנוע התנגשויות
                        self.all_words.append(word)
                
            except Exception as e:
                print(f"שגיאה בטעינת קובץ המילים המלא: {e}")
        
        # מילים לרמה קלה
        self.easy_words = [
            {"id": 1, "english": "hello", "hebrew": "שלום"},
            {"id": 2, "english": "goodbye", "hebrew": "להתראות"},
            {"id": 3, "english": "thank you", "hebrew": "תודה"},
            {"id": 4, "english": "please", "hebrew": "בבקשה"},
            {"id": 5, "english": "yes", "hebrew": "כן"},
            {"id": 6, "english": "no", "hebrew": "לא"},
            {"id": 7, "english": "water", "hebrew": "מים"},
            {"id": 8, "english": "food", "hebrew": "אוכל"},
            {"id": 9, "english": "friend", "hebrew": "חבר"},
            {"id": 10, "english": "family", "hebrew": "משפחה"},
            {"id": 11, "english": "house", "hebrew": "בית"},
            {"id": 12, "english": "car", "hebrew": "מכונית"},
            {"id": 13, "english": "book", "hebrew": "ספר"},
            {"id": 14, "english": "school", "hebrew": "בית ספר"},
            {"id": 15, "english": "teacher", "hebrew": "מורה"}
        ]
    
    async def show_games_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת תפריט המשחקים"""
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("🎮 משחק הזיכרון", callback_data="game_memory")],
            [InlineKeyboardButton("🎲 משחק 2", callback_data="game_2")],
            [InlineKeyboardButton("🎯 משחק 3", callback_data="game_3")],
            [InlineKeyboardButton("🎪 משחק 4", callback_data="game_4")],
            [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="מה משחקים עכשיו? 🎮",
            reply_markup=reply_markup
        )
        
        return True  # מציין שהפעולה טופלה בהצלחה
    
    async def show_memory_game_difficulty(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת מסך בחירת רמת קושי למשחק הזיכרון"""
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("🟢 קל", callback_data="memory_difficulty_easy")],
            [InlineKeyboardButton("🟡 בינוני", callback_data="memory_difficulty_medium")],
            [InlineKeyboardButton("🔴 קשה", callback_data="memory_difficulty_hard")],
            [InlineKeyboardButton("🔙 חזרה למשחקים", callback_data="games")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="בחר את רמת הקושי למשחק הזיכרון:\n\n"
                 "🟢 *קל* - מילים בסיסיות וקלות\n"
                 "🟡 *בינוני* - מילים שכבר למדת\n"
                 "🔴 *קשה* - מילים אקראיות מהמאגר המלא",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        return True
    
    async def handle_game_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """טיפול בבחירת משחק"""
        query = update.callback_query
        
        # בדיקה איזה משחק נבחר
        if callback_data == "game_memory":
            # הצגת מסך בחירת רמת קושי
            return await self.show_memory_game_difficulty(update, context)
        
        # טיפול במשחקים אחרים
        game_names = {
            "game_2": "משחק 2",
            "game_3": "משחק 3",
            "game_4": "משחק 4"
        }
        
        game_name = game_names.get(callback_data, "")
        await query.answer(f"{game_name} יהיה זמין בקרוב! 🎮")
        
        return True  # מציין שהפעולה טופלה בהצלחה
    
    async def start_memory_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE, difficulty: str):
        """התחלת משחק הזיכרון ברמת קושי מסוימת"""
        user_id = update.effective_user.id
        words = []
        
        # המרת קוד הקושי לטקסט בעברית
        difficulty_text = {
            "easy": "קל",
            "medium": "בינוני",
            "hard": "קשה"
        }.get(difficulty, "קל")
        
        if difficulty == "easy":
            # רמה קלה - מילים בסיסיות
            words = self.easy_words
        elif difficulty == "medium":
            # רמה בינונית - מילים שהמשתמש למד
            user_profile = await self.user_module.get_user_profile(user_id)
            words = user_profile.get("words_learned", [])
            
            # אם אין מספיק מילים שנלמדו, השלם עם מילים קלות
            if len(words) < 8:
                words = self.easy_words
        elif difficulty == "hard":
            # רמה קשה - מילים אקראיות מהמאגר המלא
            if self.all_words:
                # בחירת 15 מילים אקראיות מהמאגר המלא
                random_words = random.sample(self.all_words, min(15, len(self.all_words)))
                
                # התאמת המילים למבנה הנדרש
                words = []
                for i, word in enumerate(random_words):
                    # בדיקה אם המילה מכילה את כל השדות הנדרשים
                    if "english" in word and "hebrew" in word:
                        # בדיקה אם המילה כבר מכילה שדה id
                        if "id" in word:
                            words.append(word)
                        else:
                            # יצירת עותק של המילה עם שדה id
                            word_copy = word.copy()
                            word_copy["id"] = i + 1000  # מספר גדול כדי למנוע התנגשויות
                            words.append(word_copy)
                
                # אם אין מספיק מילים תקינות, השלם עם מילים קלות
                if len(words) < 8:
                    words = self.easy_words
            else:
                # אם אין מאגר מילים מלא, השתמש במילים קלות
                words = self.easy_words
        
        # התחלת המשחק עם המילים שנבחרו
        await self.memory_game.start_game(update, context, words, difficulty_text)
        return True
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """טיפול בקריאות חוזרות מהמשחקים"""
        
        # בדיקה אם זו קריאה ממשחק הזיכרון
        if callback_data.startswith("memory_card_"):
            return await self.memory_game.handle_callback(update, context)
        
        # בדיקה אם זו בחירת רמת קושי למשחק הזיכרון
        if callback_data.startswith("memory_difficulty_"):
            difficulty = callback_data.split("_")[-1]  # easy, medium, hard
            return await self.start_memory_game(update, context, difficulty)
        
        # אם זו בחירת משחק
        if callback_data.startswith("game_"):
            return await self.handle_game_selection(update, context, callback_data)
        
        # אם זו חזרה לתפריט הראשי
        if callback_data == "back_to_menu":
            # טיפול בחזרה לתפריט הראשי
            return False  # להעביר את הטיפול למודול הראשי
        
        return False  # לא טופל, להעביר למודול אחר
