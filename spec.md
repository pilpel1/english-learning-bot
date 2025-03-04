# איפיון מפורט לבוט טלגרם ללימוד אנגלית

## 1. סקירה כללית

הבוט המתוכנן יהיה כלי אינטראקטיבי ללימוד אנגלית בטלגרם, המבוסס על מאגר של כ-4,300 מילים. הבוט ישלב יכולות LLM באמצעות ה-API של Gemini ויציע מגוון פעילויות לימודיות שיסייעו למשתמשים לשפר את אוצר המילים, הדקדוק והשימוש בשפה האנגלית.

## 2. סיפורי משתמש

### משתמש חדש
- **בתור** משתמש חדש
- **אני רוצה** להירשם לבוט בקלות
- **כדי** להתחיל ללמוד אנגלית מיד

### מעקב אחר התקדמות
- **בתור** לומד קבוע
- **אני רוצה** לראות את ההתקדמות שלי
- **כדי** לדעת איפה אני עומד ומה עוד נשאר לי ללמוד

### אימון יומי
- **בתור** משתמש מחויב
- **אני רוצה** לקבל משימה יומית
- **כדי** לשמור על רצף לימודי

### תרגול מילים חדשות
- **בתור** לומד אנגלית
- **אני רוצה** ללמוד מילים חדשות בהקשרים שונים
- **כדי** לזכור אותן טוב יותר

### תרגול כתיבה
- **בתור** לומד אנגלית
- **אני רוצה** לכתוב טקסטים קצרים ולקבל משוב
- **כדי** לשפר את יכולת הכתיבה שלי

### משחקי מילים
- **בתור** לומד אנגלית
- **אני רוצה** לשחק משחקים אינטראקטיביים
- **כדי** ללמוד בצורה כיפית ומעניינת

### התאמה אישית
- **בתור** לומד עם צרכים ספציפיים
- **אני רוצה** להתאים את הלימוד לתחומי העניין שלי
- **כדי** שהלימוד יהיה רלוונטי עבורי

## 3. ארכיטקטורה טכנית

### 3.1 טכנולוגיות מרכזיות

1. **Python** - שפת התכנות העיקרית
2. **python-telegram-bot** - ספריית Python לעבודה עם Telegram Bot API
3. **Google Gemini API** - שירות ה-LLM לשילוב יכולות AI
4. **MongoDB** - מסד נתונים לשמירת נתוני משתמשים והתקדמות
5. **Redis** - לניהול מצבי שיחה (session states) וקאשינג
6. **Flask** (אופציונלי) - לניהול ממשק ניהול אם יידרש

### 3.2 מבנה הנתונים

#### מסד נתונים מילים
```json
{
  "word_id": "unique_id",
  "english": "example",
  "hebrew": "דוגמה",
  "part_of_speech": "noun",
  "difficulty_level": 2,
  "examples": [
    "This is an example sentence.",
    "Can you give me an example?"
  ],
  "synonyms": ["sample", "instance", "illustration"],
  "topic_tags": ["general", "academic"]
}
```

#### נתוני משתמש
```json
{
  "user_id": "telegram_user_id",
  "username": "username",
  "join_date": "2025-02-26",
  "current_level": 3,
  "learning_preferences": {
    "preferred_topics": ["business", "travel"],
    "daily_goal": 10,
    "preferred_activities": ["flashcards", "stories"]
  },
  "progress": {
    "words_mastered": 150,
    "words_learning": [
      {
        "word_id": "word_unique_id",
        "status": "learning", // "new", "learning", "mastered"
        "repetitions": 5,
        "next_review": "2025-02-28",
        "success_rate": 0.8
      }
    ],
    "daily_streaks": 7,
    "total_practice_time": 840, // minutes
    "achievement_badges": ["7_day_streak", "100_words_mastered"]
  },
  "session_data": {
    "current_activity": "flashcards",
    "current_word_set": ["word_id_1", "word_id_2"],
    "conversation_context": {}
  }
}
```

#### סטטיסטיקות שימוש
```json
{
  "date": "2025-02-26",
  "total_users": 120,
  "active_users": 85,
  "activities_completed": {
    "flashcards": 250,
    "stories": 42,
    "writing_challenges": 36
  },
  "popular_words": [
    {"word_id": "id1", "attempts": 56},
    {"word_id": "id2", "attempts": 48}
  ],
  "difficult_words": [
    {"word_id": "id3", "success_rate": 0.4},
    {"word_id": "id4", "success_rate": 0.45}
  ]
}
```

## 4. פיצ'רים ופונקציונליות

### 4.1 מודול הרשמה והתחלה

1. ברכת פתיחה והסבר קצר על הבוט
2. איסוף פרטים ראשוניים: שם, רמת אנגלית נוכחית, מטרות לימוד
3. בדיקת רמה ראשונית (אופציונלי) לקביעת נקודת התחלה
4. הצגת מדריך קצר לשימוש בבוט
5. הצעת פעילות ראשונה

### 4.2 מערכת למידה ותרגול

#### 4.2.1 כרטיסיות זיכרון (Flashcards)
- הצגת מילה באנגלית וביקוש תרגום
- הצגת מילה בעברית וביקוש תרגום
- תמיכה בלימוד הדרגתי (spaced repetition)
- מתן משוב מידי על תשובות

#### 4.2.2 משחקי מילים
- מילה חסרה במשפט
- התאמת מילים לתמונות או הגדרות
- משחקי זיכרון (memory matching)
- תחרויות נגד הזמן
- משחק "תלייה" עם מילים מאוצר המילים הנלמד

#### 4.2.3 סיפורים אינטראקטיביים
- יצירת סיפורים קצרים עם מילים מהמאגר
- סיפורים מותאמים אישית לפי תחומי עניין
- שאלות הבנה בסוף כל סיפור
- אפשרות להשלמת מילים חסרות בסיפור

#### 4.2.4 אתגרי כתיבה
- נושאים יומיים לכתיבת טקסט קצר
- הנחייה לשימוש במילים ספציפיות מהמאגר
- משוב אוטומטי על שימוש במילים, דקדוק, מבנה משפטים
- דירוג רמת הכתיבה והצעות לשיפור

#### 4.2.5 צ'אט אינטראקטיבי
- שיחות חופשיות עם הבוט בנושאים שונים
- שילוב מילים חדשות בתוך השיחה
- תיקון טעויות בזמן אמת
- התאמת רמת השיחה לרמת המשתמש

### 4.3 מערכת מעקב והתקדמות

1. דוח יומי על מילים שנלמדו
2. גרף התקדמות שבועי/חודשי
3. סטטיסטיקות ביצועים לפי סוגי פעילויות
4. זיהוי נקודות חוזק וחולשה
5. תגים והישגים למוטיבציה
6. התראות על מילים שצריך לחזור עליהן

### 4.4 מודול התאמה אישית

1. בחירת תחומי עניין לכיוון הלימוד
2. קביעת יעדים יומיים/שבועיים
3. בחירת פעילויות מועדפות
4. קביעת זמני תרגול ותזכורות
5. התאמת קצב הלימוד

## 5. תזרים עבודה (Workflow)

### 5.1 תזרים כללי

1. המשתמש מתחיל שיחה עם הבוט
2. הבוט מזהה אם מדובר במשתמש חדש או חוזר
3. למשתמש חדש: הבוט מציג תהליך הרשמה
4. למשתמש חוזר: הבוט טוען את הפרופיל והמצב הקודם
5. הבוט מציע פעילות הבאה, בהתבסס על:
   - תוכנית הלימודים
   - ההתקדמות הקודמת
   - העדפות המשתמש
   - הזמן שחלף מאז הפעילות האחרונה
6. המשתמש בוחר פעילות או מבקש אפשרויות אחרות
7. הבוט מנהל את הפעילות שנבחרה
8. בסיום הפעילות, הבוט מעדכן את נתוני ההתקדמות
9. הבוט מציע פעילות הבאה או מסכם את ההישגים

### 5.2 תזרים פעילות לימוד מילים

```
START
|
v
+-------------------+
| הצגת מילה חדשה   |
+-------------------+
|
v
+-------------------+
| הסבר + דוגמאות   |
+-------------------+
|
v
+-------------------+
| בקשת תרגום/זיהוי |
+-------------------+
|
v
+-------------------+
| בדיקת תשובה      |
+-------------------+
|       |
v       v
+-------+   +-------+
| נכון  |   | שגוי  |
+-------+   +-------+
|           |
v           v
+-------+   +-------+
| חיזוק |   | הסבר  |
+-------+   +-------+
|           |
v           v
+-------------------+
| עדכון סטטיסטיקות |
+-------------------+
|
v
+-------------------+
| בחירת מילה הבאה  |
+-------------------+
|
v
END
```

### 5.3 תזרים אתגר כתיבה

```
START
|
v
+-------------------+
| הצגת נושא כתיבה  |
+-------------------+
|
v
+-------------------+
| דרישות (מילים    |
| לשימוש, אורך)    |
+-------------------+
|
v
+-------------------+
| קבלת טקסט        |
| מהמשתמש          |
+-------------------+
|
v
+-------------------+
| ניתוח הטקסט      |
| (Gemini API)      |
+-------------------+
|
v
+-------------------+
| משוב על:          |
| - שימוש במילים    |
| - דקדוק           |
| - מבנה            |
| - מקוריות         |
+-------------------+
|
v
+-------------------+
| הצעות לשיפור     |
+-------------------+
|
v
+-------------------+
| שמירת הטקסט      |
| בפורטפוליו       |
+-------------------+
|
v
+-------------------+
| עדכון סטטיסטיקות |
+-------------------+
|
v
END
```

## 6. שימוש ב-Gemini API

### 6.1 משימות עיקריות

1. **ייצור תוכן דינמי**:
   - יצירת סיפורים עם מילים ספציפיות
   - יצירת תרגילים מותאמים אישית
   - יצירת הסברים מפורטים למילים ומונחים

2. **ניתוח תוכן משתמש**:
   - בדיקת תרגומים וכתיבה חופשית
   - זיהוי טעויות דקדוקיות
   - הערכת רמת הכתיבה

3. **שיחה אינטראקטיבית**:
   - ניהול שיחות על נושאים שונים
   - התאמת רמת השיחה לרמת המשתמש
   - שילוב מילים חדשות בתוך ההקשר

### 6.2 פרומפטים לדוגמה

#### יצירת סיפור
```
ייצר סיפור קצר (100-150 מילים) ברמת קריאה {reading_level} 
המשלב את המילים הבאות: {word_list}.
הסיפור צריך לעסוק בנושא {topic} ולכלול דיאלוג.
הקפד שהשימוש במילים יהיה טבעי ובהקשר נכון.
```

#### ניתוח טקסט שנכתב
```
הטקסט הבא נכתב על ידי לומד אנגלית:
{user_text}

נתח את הטקסט וספק משוב על:
1. שימוש נכון במילים: {words_to_use}
2. דיוק דקדוקי (סמן טעויות ותקן אותן)
3. מבנה משפטים ופסקאות
4. הצעות ספציפיות לשיפור (3-5 הצעות)
5. תן ציון כללי (1-10) והסבר קצר

התשובה צריכה להיות מנוסחת בצורה מעודדת ובונה.
```

#### דיאלוג לימודי
```
נהל שיחה בנושא {topic} עם לומד אנגלית ברמה {level}.
כלול את המילים הבאות בתשובותיך בצורה טבעית: {word_list}.
אורך התשובות שלך צריך להיות {response_length}.
אם המשתמש עושה טעויות, תקן אותן בעדינות.
שאל שאלות שיעודדו שימוש במילים מ-{word_list}.

ההודעה האחרונה של המשתמש: {user_message}
הקשר השיחה הקודם: {conversation_history}
```

## 7. ממשק משתמש

### 7.1 פקודות בוט עיקריות

- `/start` - התחלת שימוש בבוט / חזרה לתפריט ראשי
- `/help` - הסבר על השימוש בבוט
- `/profile` - צפייה בפרופיל אישי והתקדמות
- `/practice` - התחלת תרגול מילים
- `/game` - משחקי מילים
- `/story` - קריאת סיפור אינטראקטיבי
- `/write` - אתגר כתיבה
- `/chat` - צ'אט אינטראקטיבי
- `/daily` - אתגר יומי
- `/settings` - הגדרות והתאמה אישית

### 7.2 מבנה תפריטים

#### תפריט ראשי
- 🔤 תרגול מילים
- 🎮 משחקים
- 📚 סיפורים
- ✍️ אתגרי כתיבה
- 💬 צ'אט אינטראקטיבי
- 📊 סטטיסטיקות והתקדמות
- ⚙️ הגדרות

#### תפריט משחקים
- 🎯 השלמת משפטים
- 🧩 זיהוי מילים לפי הגדרה
- 🎭 משחק תפקידים
- ⏱ אתגר זמן
- 🎪 משחק תלייה

#### תפריט הגדרות
- 🎯 יעדים יומיים
- 📋 תחומי עניין
- 🔔 תזכורות
- 🎚 רמת קושי
- 🎨 העדפות לימוד

## 8. לוגיקה עסקית

### 8.1 אלגוריתם למידה ספציפי (Spaced Repetition)

מערכת ה-Spaced Repetition תעקוב אחר תהליך הלמידה של כל מילה:

1. מילה חדשה מוצגת למשתמש
2. לאחר הצגה ראשונה, המילה תופיע שוב אחרי 4 שעות
3. אם המשתמש זוכר נכון, המרווח מוכפל (8 שעות, 16 שעות, וכו')
4. אם המשתמש טועה, המרווח מתקצר ב-50%
5. מילה נחשבת "מוטמעת" אחרי 5 תשובות נכונות ברציפות
6. מילים "מוטמעות" עוברות לבדיקות תקופתיות (פעם בשבוע, בחודש וכו')

### 8.2 המלצות תוכן אישיות

הבוט ישתמש באלגוריתם המלצות להצעת פעילויות הבאות:

1. ניתוח דפוסי למידה אישיים
2. זיהוי זמני למידה מועדפים
3. זיהוי סוגי פעילויות עם הצלחה גבוהה
4. התחשבות במשך זמן פעילות אחרונה
5. שקלול ביצועים קודמים בפעילויות דומות

### 8.3 מערכת התראות והתזכורות

1. תזכורות יומיות בזמנים שהמשתמש בחר
2. התראות על מילים שצריך לחזור עליהן
3. חיזוקים חיוביים על התקדמות
4. התראות על ירידה בפעילות
5. תזכורות על אתגרים ומשימות מיוחדות

## 9. תהליך פיתוח

### 9.1 שלבי פיתוח מומלצים

1. **שלב 1: מבנה בסיסי**
   - הקמת מבנה הבוט הבסיסי
   - חיבור ל-Telegram API
   - יצירת מערכת ניהול מצבי שיחה
   - הגדרת פקודות בסיסיות

2. **שלב 2: מסד נתונים**
   - הקמת מסד הנתונים
   - ייבוא אוצר המילים (4,300 מילים)
   - מערכת ניהול פרופילי משתמשים

3. **שלב 3: פונקציונליות בסיסית**
   - הרשמת משתמשים
   - תרגול בסיסי של מילים (flashcards)
   - מעקב אחר התקדמות ראשונית

4. **שלב 4: אינטגרציה עם Gemini API**
   - הטמעת ה-API
   - יצירת פרומפטים בסיסיים
   - יצירת מערכת ניתוח תשובות משתמש

5. **שלב 5: הוספת פעילויות מתקדמות**
   - משחקים מורכבים יותר
   - סיפורים אינטראקטיביים
   - אתגרי כתיבה
   - צ'אט אינטראקטיבי

6. **שלב 6: התאמה אישית**
   - מערכת העדפות מתקדמת
   - אלגוריתם המלצות
   - התאמת קושי אוטומטית

7. **שלב 7: בדיקות ומשוב**
   - בדיקות ביצועים
   - איסוף משוב ממשתמשים
   - שיפורים ותיקונים

### 9.2 קוד לדוגמה - מבנה בסיסי

```python
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import logging
import os
import json
import pymongo
import redis
import google.generativeai as genai
from datetime import datetime, timedelta

# Configuration
API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")
REDIS_URI = os.environ.get("REDIS_URI")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize MongoDB
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["english_learning_bot"]
users_collection = db["users"]
words_collection = db["words"]
stats_collection = db["statistics"]

# Initialize Redis
redis_client = redis.Redis.from_url(REDIS_URI)

# User states
class UserState:
    IDLE = "idle"
    REGISTERING = "registering"
    PRACTICING = "practicing"
    PLAYING_GAME = "playing_game"
    READING_STORY = "reading_story"
    WRITING = "writing"
    CHATTING = "chatting"
    SETTINGS = "settings"

# Helper functions
async def get_user_data(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        return None
    return user

async def save_user_data(user_data):
    users_collection.replace_one(
        {"user_id": user_data["user_id"]},
        user_data,
        upsert=True
    )

async def get_random_words(count, difficulty=None, topics=None):
    query = {}
    if difficulty:
        query["difficulty_level"] = difficulty
    if topics:
        query["topic_tags"] = {"$in": topics}
    
    words = list(words_collection.aggregate([
        {"$match": query},
        {"$sample": {"size": count}}
    ]))
    
    return words

async def generate_story(words, topic, level):
    prompt = f"""
    ייצר סיפור קצר (150-200 מילים) ברמת קריאה {level} 
    המשלב את המילים הבאות: {', '.join(words)}.
    הסיפור צריך לעסוק בנושא {topic} ולכלול דיאלוג.
    הקפד שהשימוש במילים יהיה טבעי ובהקשר נכון.
    """
    
    response = model.generate_content(prompt)
    return response.text

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await get_user_data(user.id)
    
    if not user_data:
        # New user
        await update.message.reply_text(
            f"ברוך הבא, {user.first_name}! אני בוט ללימוד אנגלית. "\
            "אני אעזור לך לשפר את אוצר המילים והכישורים שלך באנגלית."
        )
        
        # Create new user profile
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "current_level": 1,
            "learning_preferences": {
                "preferred_topics": [],
                "daily_goal": 10,
                "preferred_activities": []
            },
            "progress": {
                "words_mastered": 0,
                "words_learning": [],
                "daily_streaks": 0,
                "total_practice_time": 0,
                "achievement_badges": []
            },
            "session_data": {
                "current_activity": None,
                "current_word_set": [],
                "conversation_context": {}
            }
        }
        
        await save_user_data(user_data)
        
        # Start registration process
        context.user_data["state"] = UserState.REGISTERING
        await update.message.reply_text(
            "בוא נתחיל בהגדרת הפרופיל שלך. "\
            "מהי רמת האנגלית שלך? (מתחיל/בינוני/מתקדם)"
        )
    else:
        # Returning user
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
        
        # Calculate streak and update if needed
        last_active = datetime.strptime(user_data.get("last_active", user_data["join_date"]), "%Y-%m-%d")
        today = datetime.now().date()
        yesterday = (datetime.now() - timedelta(days=1)).date()
        
        if last_active.date() == yesterday:
            user_data["progress"]["daily_streaks"] += 1
        elif last_active.date() != today:
            user_data["progress"]["daily_streaks"] = 1
            
        user_data["last_active"] = today.strftime("%Y-%m-%d")
        await save_user_data(user_data)
        
        await update.message.reply_text(
            f"שלום {user.first_name}! " \
            f"סטריק יומי: 🔥 {user_data['progress']['daily_streaks']} ימים\n" \
            f"מילים שנלמדו: {user_data['progress']['words_mastered']} מתוך 4,300\n\n" \
            "מה תרצה לעשות היום?",
            reply_markup=reply_markup
        )
        
        context.user_data["state"] = UserState.IDLE

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    הבוט ללימוד אנגלית - פקודות עיקריות:
    
    /start - התחל שיחה עם הבוט או חזור לתפריט הראשי
    /help - הצג הודעת עזרה זו
    /profile - צפה בפרופיל שלך והתקדמות
    /practice - התחל תרגול מילים
    /game - שחק משחקי מילים
    /story - קרא סיפור אינטראקטיבי
    /write - התחל אתגר כתיבה
    /chat - התחל צ'אט אינטראקטיבי
    /daily - קבל את האתגר היומי
    /settings - שנה הגדרות אישיות
    """
    
    await update.message.reply_text(help_text)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await get_user_data(user.id)
    
    if not user_data:
        await update.message.reply_text(
            "נראה שעדיין לא נרשמת. השתמש בפקודה /start כדי להתחיל."
        )
        return
    
    # Calculate progress percentage
    progress_percent = (user_data["progress"]["words_mastered"] / 4300) * 100
    
    # Get recent activity
    recent_activities = user_data.get("recent_activities", [])
    recent_activity_text = "\n".join([f"- {activity}" for activity in recent_activities[-3:]]) if recent_activities else "אין פעילות אחרונה"
    
    # Format badges
    badges = user_data["progress"]["achievement_badges"]
    badge_text = ", ".join(badges) if badges else "אין עדיין הישגים"
    
    profile_text = f"""
    📊 הפרופיל שלך:
    
    👤 שם: {user.first_name}
    📅 הצטרפת בתאריך: {user_data["join_date"]}
    🔥 סטריק יומי: {user_data["progress"]["daily_streaks"]} ימים
    
    📚 התקדמות:
    - מילים שנלמדו: {user_data["progress"]["words_mastered"]} / 4300 ({progress_percent:.1f}%)
    - זמן לימוד כולל: {user_data["progress"]["total_practice_time"]} דקות
    
    🏆 הישגים:
    {badge_text}
    
    🔍 פעילות אחרונה:
    {recent_activity_text}
    """
    
    # Add inline buttons for more detailed stats
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
    
    await update.message.reply_text(profile_text, reply_markup=reply_markup)

# Callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_data = await get_user_data(user.id)
    
    if query.data == "practice":
        # Start word practice session
        words = await get_random_words(10, 
                                       difficulty=user_data.get("current_level", 1),
                                       topics=user_data.get("learning_preferences", {}).get("preferred_topics", []))
        
        context.user_data["current_words"] = words
        context.user_data["current_word_index"] = 0
        context.user_data["state"] = UserState.PRACTICING
        
        await show_next_word(query.message, context)
        
    elif query.data == "games":
        # Show games menu
        keyboard = [
            [
                InlineKeyboardButton("🎯 השלמת משפטים", callback_data="game_complete_sentence"),
                InlineKeyboardButton("🧩 זיהוי מילים", callback_data="game_word_definition")
            ],
            [
                InlineKeyboardButton("🎭 משחק תפקידים", callback_data="game_role_play"),
                InlineKeyboardButton("⏱ אתגר זמן", callback_data="game_time_challenge")
            ],
            [
                InlineKeyboardButton("🎪 משחק תלייה", callback_data="game_hangman"),
                InlineKeyboardButton("🔙 חזרה", callback_data="back_to_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("בחר משחק:", reply_markup=reply_markup)
        
    # Add more callback handlers for other buttons...

# Helper function for word practice
async def show_next_word(message, context):
    words = context.user_data["current_words"]
    index = context.user_data["current_word_index"]
    
    if index >= len(words):
        # Practice session completed
        await message.edit_text(
            "כל הכבוד! סיימת את מפגש התרגול.\n\n"
            "רוצה לתרגל עוד מילים?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ כן", callback_data="practice")],
                [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
            ])
        )
        return
    
    current_word = words[index]
    
    # Show word with definition and example
    word_text = f"""
    📝 מילה: {current_word['english']}
    🔤 תרגום: {current_word['hebrew']}
    📋 חלק דיבור: {current_word['part_of_speech']}
    
    📚 דוגמאות:
    - {current_word['examples'][0]}
    """
    
    if len(current_word['examples']) > 1:
        word_text += f"- {current_word['examples'][1]}\n"
    
    if current_word.get('synonyms'):
        word_text += f"\n🔄 מילים נרדפות: {', '.join(current_word['synonyms'])}"
    
    # Add buttons for user response
    keyboard = [
        [
            InlineKeyboardButton("✅ זכרתי", callback_data="word_remembered"),
            InlineKeyboardButton("❌ לא זכרתי", callback_data="word_forgot")
        ],
        [
            InlineKeyboardButton("⏭️ המילה הבאה", callback_data="next_word")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.edit_text(word_text, reply_markup=reply_markup)

# Main function
def main():
    # Create application
    application = ApplicationBuilder().token(API_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    # Add more command handlers...
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for chat
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Start the Bot
    application.run_polling()

# Message handler for regular messages
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text
    state = context.user_data.get("state", UserState.IDLE)
    
    if state == UserState.REGISTERING:
        # Process registration steps
        registration_step = context.user_data.get("registration_step", 1)
        
        if registration_step == 1:
            # Process level selection
            level_map = {"מתחיל": 1, "בינוני": 2, "מתקדם": 3}
            selected_level = level_map.get(message_text.strip().lower(), 1)
            
            user_data = await get_user_data(user.id)
            user_data["current_level"] = selected_level
            await save_user_data(user_data)
            
            context.user_data["registration_step"] = 2
            await update.message.reply_text(
                "מצוין! באילו נושאים אתה מתעניין? "\
                "(לדוגמה: עסקים, טכנולוגיה, נסיעות, ספרות, מדע...)\n"\
                "אנא רשום עד 5 נושאים, מופרדים בפסיקים."
            )
        
        elif registration_step == 2:
            # Process topics
            topics = [topic.strip() for topic in message_text.split(",")]
            topics = topics[:5]  # Limit to 5 topics
            
            user_data = await get_user_data(user.id)
            user_data["learning_preferences"]["preferred_topics"] = topics
            await save_user_data(user_data)
            
            context.user_data["registration_step"] = 3
            await update.message.reply_text(
                "מעולה! כמה מילים חדשות היית רוצה ללמוד בכל יום? (מספר בין 5-20)"
            )
        
        elif registration_step == 3:
            # Process daily goal
            try:
                goal = int(message_text.strip())
                goal = max(5, min(20, goal))  # Ensure between 5-20
            except ValueError:
                goal = 10  # Default if not a number
            
            user_data = await get_user_data(user.id)
            user_data["learning_preferences"]["daily_goal"] = goal
            await save_user_data(user_data)
            
            # Finish registration
            context.user_data["state"] = UserState.IDLE
            del context.user_data["registration_step"]
            
            keyboard = [
                [
                    InlineKeyboardButton("🔤 תרגול מילים", callback_data="practice"),
                    InlineKeyboardButton("🎮 משחקים", callback_data="games")
                ],
                [
                    InlineKeyboardButton("📚 סיפורים", callback_data="stories"),
                    InlineKeyboardButton("✍️ אתגרי כתיבה", callback_data="writing")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"מצוין! ההרשמה הושלמה. יעד יומי: {goal} מילים חדשות.\n\n"\
                "הבוט מוכן לעזור לך ללמוד אנגלית. מה תרצה לעשות עכשיו?",
                reply_markup=reply_markup
            )
    
    elif state == UserState.WRITING:
        # Process writing challenge submission
        writing_prompt = context.user_data.get("writing_prompt")
        required_words = context.user_data.get("required_words", [])
        
        # Use Gemini API to analyze the text
        prompt = f"""
        הטקסט הבא נכתב על ידי לומד אנגלית:
        {message_text}
        
        נתח את הטקסט וספק משוב על:
        1. שימוש נכון במילים: {', '.join(required_words)}
        2. דיוק דקדוקי (סמן טעויות ותקן אותן)
        3. מבנה משפטים ופסקאות
        4. הצעות ספציפיות לשיפור (3-5 הצעות)
        5. תן ציון כללי (1-10) והסבר קצר
        
        התשובה צריכה להיות מנוסחת בצורה מעודדת ובונה.
        """
        
        response = model.generate_content(prompt)
        feedback = response.text
        
        # Save the writing submission
        user_data = await get_user_data(user.id)
        if "writings" not in user_data:
            user_data["writings"] = []
            
        user_data["writings"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "prompt": writing_prompt,
            "text": message_text,
            "feedback": feedback
        })
        
        # Update practice time
        user_data["progress"]["total_practice_time"] += 10  # Estimate 10 minutes
        await save_user_data(user_data)
        
        # Send feedback
        await update.message.reply_text(
            f"תודה על הטקסט שלך! הנה המשוב:\n\n{feedback}\n\n"\
            "רוצה לנסות אתגר כתיבה נוסף?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ כן", callback_data="writing")],
                [InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_menu")]
            ])
        )
        
        # Reset state
        context.user_data["state"] = UserState.IDLE
        if "writing_prompt" in context.user_data:
            del context.user_data["writing_prompt"]
        if "required_words" in context.user_data:
            del context.user_data["required_words"]
    
    elif state == UserState.CHATTING:
        # Handle interactive chat
        user_data = await get_user_data(user.id)
        level = user_data.get("current_level", 1)
        
        # Get appropriate words to include in the response
        recent_words = await get_random_words(3, difficulty=level)
        words_to_include = [word["english"] for word in recent_words]
        
        # Get chat history
        chat_history = context.user_data.get("chat_history", [])
        
        # Prepare prompt for Gemini
        prompt = f"""
        נהל שיחה בנושא כללי עם לומד אנגלית ברמה {level} (1=מתחיל, 2=בינוני, 3=מתקדם).
        כלול את המילים הבאות בתשובותיך בצורה טבעית: {', '.join(words_to_include)}.
        ודא שהתשובה שלך תהיה ברמה המתאימה ללומד.
        אם המשתמש עושה טעויות, תקן אותן בעדינות.
        שאל שאלות שיעודדו המשך שיחה.
        
        הקשר השיחה הקודם:
        {' '.join(chat_history[-5:]) if chat_history else 'אין'}
        
        ההודעה האחרונה של המשתמש: {message_text}
        """
        
        response = model.generate_content(prompt)
        bot_reply = response.text
        
        # Update chat history
        chat_history.append(f"User: {message_text}")
        chat_history.append(f"Bot: {bot_reply}")
        context.user_data["chat_history"] = chat_history
        
        # Update user statistics
        user_data["progress"]["total_practice_time"] += 2  # Estimate 2 minutes per exchange
        
        # Record newly used words
        for word in words_to_include:
            word_entry = words_collection.find_one({"english": word})
            if word_entry:
                word_id = str(word_entry["_id"])
                word_learning_entry = next((w for w in user_data["progress"]["words_learning"] if w["word_id"] == word_id), None)
                
                if not word_learning_entry:
                    user_data["progress"]["words_learning"].append({
                        "word_id": word_id,
                        "status": "new", 
                        "repetitions": 1,
                        "next_review": (datetime.now() + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
                        "success_rate": 0.0
                    })
                else:
                    word_learning_entry["repetitions"] += 1
        
        await save_user_data(user_data)
        
        # Send response with option to continue or exit chat
        keyboard = [
            [InlineKeyboardButton("🔚 סיים צ'אט", callback_data="end_chat")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(bot_reply, reply_markup=reply_markup)
    
    # Handle other states...

if __name__ == "__main__":
    main()
```

## 10. שיקולי אבטחה ופרטיות

### 10.1 אבטחת נתונים
1. אחסון מאובטח של API tokens (שימוש ב-environment variables)
2. הצפנת נתוני משתמשים רגישים
3. גיבוי תקופתי של מסד הנתונים
4. הגבלת הרשאות גישה למסד הנתונים

### 10.2 פרטיות משתמשים
1. איסוף מינימלי של מידע אישי
2. מדיניות פרטיות ברורה המוצגת למשתמשים
3. אפשרות למחיקת חשבון וכל המידע הקשור
4. הגבלת השימוש במידע משתמשים רק למטרות שיפור הבוט

### 10.3 מניעת שימוש לרעה
1. ניטור וזיהוי דפוסי שימוש חריגים
2. הגבלת מספר הבקשות ליום למניעת שימוש לרעה במשאבים
3. פילטרים לתוכן לא ראוי במשוב משתמשים
4. מערכת דיווח על תקלות ובעיות

## 11. אתגרים פוטנציאליים ופתרונות

### 11.1 יכולות מוגבלות של Gemini API
- **אתגר**: API עלול להיות מוגבל באינטראקטיביות או בהבנת הקשר
- **פתרון**: שמירת הקשר שיחה והעברתו עם כל בקשה; יצירת פרומפטים מפורטים ומדויקים

### 11.2 דיוק בתיקון טעויות
- **אתגר**: הבוט עלול לטעות בזיהוי או תיקון שגיאות
- **פתרון**: שילוב מערכות בדיקת איות ודקדוק ייעודיות בנוסף ל-LLM

### 11.3 עומס משאבים
- **אתגר**: שימוש רב ב-API עלול ליצור עלויות גבוהות
- **פתרון**: מטמון (caching) לתשובות נפוצות; אופטימיזציה של מספר הבקשות; הגבלת שימוש

### 11.4 התמודדות עם רמות שונות של משתמשים
- **אתגר**: משתמשים ברמות שונות מאוד
- **פתרון**: מערכת דינמית להתאמת רמת קושי; מבחני רמה תקופתיים

## 12. מדדי הצלחה

### 12.1 מדדי שימוש
1. מספר משתמשים פעילים יומי/שבועי/חודשי
2. שימור משתמשים לאורך זמן
3. אורך ממוצע של סשן למידה
4. מספר פעילויות שהושלמו

### 12.2 מדדי למידה
1. מספר מילים שנלמדו לפי משתמש
2. שיפור באחוזי הצלחה לאורך זמן
3. עקביות הלמידה (סטריקים)
4. שיפור במבחני רמה תקופתיים

### 12.3 מדדי ביצועי מערכת
1. זמן תגובה ממוצע
2. אחוז שגיאות ותקלות
3. יציבות המערכת תחת עומס
4. צריכת משאבים ועלויות תפעול

## 13. תחזוקה ושדרוגים עתידיים

### 13.1 תחזוקה שוטפת
1. ניטור ביצועים ותיקון באגים
2. עדכוני אבטחה תקופתיים
3. גיבוי מסד נתונים
4. ניתוח נתוני שימוש לשיפור חוויית המשתמש

### 13.2 שדרוגים פוטנציאליים
1. **הוספת אפיוני שמע** - תמיכה בקלט/פלט קולי לשיפור מיומנויות הגייה והאזנה
2. **תמיכה בפלטפורמות נוספות** - WhatsApp, Discord, או אפליקציה עצמאית
3. **שילוב עם חומרי למידה חיצוניים** - ספרים, סרטונים, פודקאסטים
4. **יכולות AI מתקדמות יותר** - הטמעת מודלים מתקדמים יותר כשיהיו זמינים
5. **למידה חברתית** - אפשרות ללמוד עם חברים ולהתחרות ביניהם

## 14. סיכום

הבוט המתוכנן יהיה כלי עוצמתי ללימוד אנגלית, המשלב את היכולות המתקדמות של Gemini API עם שיטות לימוד מבוססות מחקר. הוא מציע מגוון רחב של פעילויות אינטראקטיביות, התאמה אישית, ומעקב אחר התקדמות, שיאפשרו למשתמשים ללמוד אנגלית בצורה יעילה ומהנה.

האיפיון המפורט שהוצג כולל את כל הרכיבים הדרושים לפיתוח הבוט, החל מסיפורי המשתמש ועד לקוד לדוגמה, ומדדי הצלחה. הוא מתייחס גם לאתגרים פוטנציאליים ומציע פתרונות אפשריים.

התוכנית המדורגת לפיתוח מאפשרת יישום הדרגתי, כאשר ניתן להתחיל עם גרסה בסיסית ולהוסיף תכונות מתקדמות לאורך זמן, בהתאם למשוב המשתמשים וצרכי המערכת.