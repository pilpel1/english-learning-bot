"""
מודול לניהול משחקים
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from modules.games.memory_game.memory_game import MemoryGame

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
    
    async def show_games_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת תפריט המשחקים"""
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("🎮 משחק הזיכרון", callback_data="game_memory")],
            [InlineKeyboardButton("🎲 משחק 2", callback_data="game_2")],
            [InlineKeyboardButton("🎯 משחק 3", callback_data="game_3")],
            [InlineKeyboardButton("🎪 משחק 4", callback_data="game_4")],
            [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="מה משחקים עכשיו? 🎮",
            reply_markup=reply_markup
        )
        
        return True  # מציין שהפעולה טופלה בהצלחה
    
    async def handle_game_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """טיפול בבחירת משחק"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # בדיקה איזה משחק נבחר
        if callback_data == "game_memory":
            # הפעלת משחק הזיכרון
            user_profile = await self.user_module.get_user_profile(user_id)
            words = user_profile.get("words_learned", [])
            
            # אם אין מספיק מילים, הוסף מילים לדוגמה
            if len(words) < 8:
                sample_words = [
                    {"id": 1, "english": "hello", "hebrew": "שלום"},
                    {"id": 2, "english": "goodbye", "hebrew": "להתראות"},
                    {"id": 3, "english": "thank you", "hebrew": "תודה"},
                    {"id": 4, "english": "please", "hebrew": "בבקשה"},
                    {"id": 5, "english": "yes", "hebrew": "כן"},
                    {"id": 6, "english": "no", "hebrew": "לא"},
                    {"id": 7, "english": "water", "hebrew": "מים"},
                    {"id": 8, "english": "food", "hebrew": "אוכל"},
                    {"id": 9, "english": "friend", "hebrew": "חבר"},
                    {"id": 10, "english": "family", "hebrew": "משפחה"}
                ]
                words = sample_words
            
            # התחלת משחק חדש
            await self.memory_game.start_game(update, context, words)
            return True
        
        # טיפול במשחקים אחרים
        game_names = {
            "game_2": "משחק 2",
            "game_3": "משחק 3",
            "game_4": "משחק 4"
        }
        
        game_name = game_names.get(callback_data, "")
        await query.answer(f"{game_name} יהיה זמין בקרוב! 🎮")
        
        return True  # מציין שהפעולה טופלה בהצלחה
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """טיפול בקריאות חוזרות מהמשחקים"""
        
        # בדיקה אם זו קריאה ממשחק הזיכרון
        if callback_data.startswith("memory_card_"):
            return await self.memory_game.handle_callback(update, context)
        
        # אם זו בחירת משחק
        if callback_data.startswith("game_"):
            return await self.handle_game_selection(update, context, callback_data)
        
        # אם זו חזרה לתפריט הראשי
        if callback_data == "back_to_menu":
            # טיפול בחזרה לתפריט הראשי
            return False  # להעביר את הטיפול למודול הראשי
        
        return False  # לא טופל, להעביר למודול אחר
