"""
מודול לניהול משתמשים ופרופילים
"""

from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum, auto
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

class UserStates(Enum):
    """מצבי שיחה הקשורים למשתמש"""
    MAIN_MENU = auto()
    REGISTRATION = auto()
    SETTINGS = auto()
    PRACTICING = auto()

class UserModule:
    """מחלקה לניהול משתמשים ופרופילים"""
    
    def __init__(self, user_repo):
        """
        אתחול מודול המשתמש
        
        Args:
            user_repo: מאגר נתוני המשתמשים
        """
        self.user_repo = user_repo
    
    async def get_user_profile(self, user_id: int) -> Dict:
        """קבלת פרופיל משתמש לפי מזהה"""
        user_profile = await self.user_repo.get_user(user_id)
        
        if not user_profile:
            # יצירת פרופיל חדש למשתמש - פשוט אבל עם כל המידע החשוב
            user_profile = {
                "user_id": user_id,
                "join_date": datetime.now().strftime("%Y-%m-%d"),
                "words_knowledge": {},  # מילון שבו המפתח הוא מזהה המילה והערך הוא רמת הידע (-N עד +N)
                "daily_streak": 0,
                "last_practice": None,
                "total_practice_time": 0,
                "session_data": {
                    "current_word_set": [],
                    "current_word_index": 0,
                    "conversation_context": {}
                }
            }
            await self.save_user_profile(user_profile)
        
        return user_profile
    
    async def save_user_profile(self, user_profile: Dict) -> bool:
        """
        שמירת פרופיל משתמש
        
        Args:
            user_profile: פרופיל המשתמש לשמירה
            
        Returns:
            האם השמירה הצליחה
        """
        try:
            return await self.user_repo.save_user(user_profile)
        except Exception as e:
            print(f"Error in save_user_profile: {e}")
            return False
    
    def ensure_session_data(self, user_profile: Dict) -> Dict:
        """
        וידוא שהמשתמש מכיל את כל הנתונים הדרושים למפגש הנוכחי
        
        Args:
            user_profile: פרופיל המשתמש
            
        Returns:
            פרופיל המשתמש המעודכן
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
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> UserStates:
        """טיפול בפקודת ההתחלה /start"""
        welcome_text = f"""
ברוך הבא לבוט לימוד האנגלית, {update.effective_user.first_name}! 🎉

אני כאן כדי לעזור לך ללמוד אנגלית בצורה מהנה ואפקטיבית.
"""
        
        keyboard = [[InlineKeyboardButton("בוא נתחיל! 🚀", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        return UserStates.MAIN_MENU
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> UserStates:
        """הצגת התפריט הראשי"""
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        
        # חישוב סטטיסטיקות בסיסיות
        words_knowledge = user_profile.get("words_knowledge", {})
        words_learned = sum(1 for score in words_knowledge.values() if score > 0)
        daily_streak = user_profile.get("daily_streak", 0)
        
        menu_text = f"""
📚 *תפריט ראשי*

👋 שלום {user.first_name}!

📊 *ההתקדמות שלך*:
• מילים שלמדת: {words_learned}
• סטריק יומי: {daily_streak} ימים
• זמן למידה כולל: {user_profile.get("total_practice_time", 0)} דקות

מה תרצה לעשות היום?
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎯 תרגול מילים", callback_data="practice"),
                InlineKeyboardButton("🎮 משחקים", callback_data="games")
            ],
            [
                InlineKeyboardButton("📖 סיפורים", callback_data="stories"),
                InlineKeyboardButton("✍️ כתיבה", callback_data="writing")
            ],
            [
                InlineKeyboardButton("⚙️ הגדרות", callback_data="settings")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text=menu_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                text=menu_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        return UserStates.MAIN_MENU
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """טיפול בפקודת הפרופיל /profile"""
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        user_profile = self.ensure_session_data(user_profile)
        await self.save_user_profile(user_profile)
        
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
                InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="back_to_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text=profile_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                profile_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def home_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> UserStates:
        """טיפול בפקודת הבית /home"""
        return await self.show_main_menu(update, context)
    
    async def handle_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> UserStates:
        """
        טיפול בתהליך הרישום
        
        Args:
            update: עדכון מטלגרם
            context: הקשר השיחה
            callback_data: נתוני הכפתור שנלחץ
            
        Returns:
            מצב השיחה הבא
        """
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        
        # טיפול בבחירת רמה
        if callback_data.startswith("register_"):
            level = callback_data.replace("register_", "")
            user_profile["level"] = level
            await self.save_user_profile(user_profile)
            
            # הודעת אישור רישום
            level_emoji = {
                "beginner": "🔰",
                "intermediate": "🔶",
                "advanced": "🔷"
            }
            
            level_hebrew = {
                "beginner": "מתחיל",
                "intermediate": "בינוני",
                "advanced": "מתקדם"
            }
            
            registration_text = f"""
✅ *הרישום הושלם בהצלחה!*

בחרת ברמה: {level_emoji.get(level, '')} {level_hebrew.get(level, level)}

אני אתאים את התרגולים והפעילויות לרמה שבחרת.
בכל שלב תוכל לשנות את הרמה בהגדרות.

בוא נתחיל!
"""
            
            keyboard = [
                [InlineKeyboardButton("🚀 למידה ראשונה", callback_data="first_practice")],
                [InlineKeyboardButton("🏠 לתפריט הראשי", callback_data="back_to_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text=registration_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return UserStates.MAIN_MENU
        
        # טיפול בלמידה ראשונה
        elif callback_data == "first_practice":
            await update.callback_query.answer()
            # כאן יש להפנות למודול התרגול
            return UserStates.PRACTICING
        
        return UserStates.MAIN_MENU
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> Optional[UserStates]:
        """
        טיפול בלחיצות על כפתורים הקשורים למשתמש
        
        Args:
            update: עדכון מטלגרם
            context: הקשר השיחה
            callback_data: נתוני הכפתור שנלחץ
            
        Returns:
            מצב השיחה הבא או None אם הכפתור לא טופל
        """
        if callback_data == "back_to_menu":
            await self.show_main_menu(update, context)
            return UserStates.MAIN_MENU
        
        return None
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> Optional[UserStates]:
        """
        טיפול בלחיצות על כפתורים הקשורים למשתמש
        
        Args:
            update: עדכון מטלגרם
            context: הקשר השיחה
            callback_data: נתוני הכפתור שנלחץ
            
        Returns:
            מצב השיחה הבא או None אם הכפתור לא טופל
        """
        # טיפול בכפתורים הקשורים לרישום
        if callback_data.startswith("register_") or callback_data == "first_practice":
            return await self.handle_registration(update, context, callback_data)
        
        # טיפול בכפתורים הקשורים לפרופיל
        elif callback_data == "profile":
            await self.profile_command(update, context)
            return UserStates.MAIN_MENU
        
        # טיפול בכפתורים הקשורים לסטטיסטיקות
        elif callback_data == "detailed_stats":
            user = update.effective_user
            user_profile = await self.get_user_profile(user.id)
            
            stats_text = f"""
📊 *סטטיסטיקות מפורטות*:

⏱️ זמן למידה ממוצע: 15 דקות ביום
📆 ימי למידה רצופים: {user_profile["progress"]["daily_streaks"]}
🔄 מילים שנלמדו השבוע: 35
📈 קצב למידה: 5 מילים ביום
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 חזרה לפרופיל", callback_data="profile")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text=stats_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return UserStates.MAIN_MENU
        
        # טיפול בכפתורים הקשורים להיסטוריית למידה
        elif callback_data == "learning_history":
            history_text = """
🗓️ *היסטוריית למידה*:

📆 *היום*:
- למדת 5 מילים חדשות
- השלמת 2 תרגולים

📆 *אתמול*:
- למדת 7 מילים חדשות
- השלמת משחק אחד

📆 *השבוע*:
- למדת 35 מילים חדשות
- השלמת 12 פעילויות
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 חזרה לפרופיל", callback_data="profile")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text=history_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return UserStates.MAIN_MENU
        
        # אם הגענו לכאן, הכפתור לא טופל
        return None 