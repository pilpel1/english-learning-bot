"""
מודלים לייצוג נתונים בפרויקט בוט למידת אנגלית
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import json
import os
import pymongo
from datetime import datetime


class WordStatus(Enum):
    """סטטוס למידה של מילה"""
    NEW = "new"
    LEARNING = "learning"
    MASTERED = "mastered"


class Word:
    """מחלקה לייצוג מילה באוצר המילים"""
    
    def __init__(self, word_id: str, english: str, hebrew: str = "", 
                 part_of_speech: str = "", difficulty_level: int = 1,
                 examples: List[str] = None, synonyms: List[str] = None,
                 topic_tags: List[str] = None, translation: str = None):
        self.word_id = word_id
        self.english = english
        self.hebrew = hebrew
        self.translation = translation  # תרגום באנגלית (למשל "tenth" עבור "10th")
        self.part_of_speech = part_of_speech
        self.difficulty_level = difficulty_level
        self.examples = examples or []
        self.synonyms = synonyms or []
        self.topic_tags = topic_tags or ["general"]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Word':
        """יצירת אובייקט מילה מתוך מילון"""
        return cls(
            word_id=data.get('word_id', ''),
            english=data.get('english', ''),
            hebrew=data.get('hebrew', ''),
            translation=data.get('translation', None),
            part_of_speech=data.get('part_of_speech', ''),
            difficulty_level=data.get('difficulty_level', 1),
            examples=data.get('examples', []),
            synonyms=data.get('synonyms', []),
            topic_tags=data.get('topic_tags', ['general'])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת האובייקט למילון לשמירה ב-JSON"""
        return {
            'word_id': self.word_id,
            'english': self.english,
            'hebrew': self.hebrew,
            'translation': self.translation,
            'part_of_speech': self.part_of_speech,
            'difficulty_level': self.difficulty_level,
            'examples': self.examples,
            'synonyms': self.synonyms,
            'topic_tags': self.topic_tags
        }
    
    def __str__(self) -> str:
        return f"{self.english}" + (f" ({self.hebrew})" if self.hebrew else "")


class UserWordProgress:
    """מחלקה לייצוג התקדמות משתמש במילה מסוימת"""
    
    def __init__(self, word_id: str, status: WordStatus = WordStatus.NEW, 
                 repetitions: int = 0, success_rate: float = 0.0,
                 next_review: Optional[str] = None):
        self.word_id = word_id
        self.status = status
        self.repetitions = repetitions
        self.success_rate = success_rate
        self.next_review = next_review
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserWordProgress':
        """יצירת אובייקט התקדמות מילה מתוך מילון"""
        return cls(
            word_id=data.get('word_id', ''),
            status=WordStatus(data.get('status', 'new')),
            repetitions=data.get('repetitions', 0),
            success_rate=data.get('success_rate', 0.0),
            next_review=data.get('next_review', None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת האובייקט למילון לשמירה ב-JSON"""
        return {
            'word_id': self.word_id,
            'status': self.status.value,
            'repetitions': self.repetitions,
            'success_rate': self.success_rate,
            'next_review': self.next_review
        }


class WordsRepository:
    """מחלקה לניהול אוצר המילים"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.words = {}  # word_id -> Word
        self._load_words()
    
    def _load_words(self) -> None:
        """טעינת המילים מקובץ JSON"""
        if not os.path.exists(self.json_file_path):
            self.words = {}
            return
        
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                words_data = json.load(file)
                for word_data in words_data:
                    word = Word.from_dict(word_data)
                    self.words[word.word_id] = word
        except Exception as e:
            print(f"שגיאה בטעינת קובץ המילים: {e}")
            self.words = {}
    
    def get_word(self, word_id: str) -> Optional[Word]:
        """קבלת מילה לפי מזהה"""
        return self.words.get(word_id)
    
    def get_word_by_english(self, english: str) -> Optional[Word]:
        """חיפוש מילה לפי הטקסט באנגלית"""
        for word in self.words.values():
            if word.english.lower() == english.lower():
                return word
        return None
    
    def search_words(self, query: str, limit: int = 10) -> List[Word]:
        """חיפוש מילים לפי מחרוזת חיפוש"""
        query = query.lower()
        results = []
        
        for word in self.words.values():
            if query in word.english.lower():
                results.append(word)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_words_by_difficulty(self, level: int, limit: int = 10) -> List[Word]:
        """קבלת מילים לפי רמת קושי"""
        results = []
        for word in self.words.values():
            if word.difficulty_level == level:
                results.append(word)
                if len(results) >= limit:
                    break
        return results
    
    def get_random_words(self, count: int, difficulty: Optional[int] = None, 
                        topics: Optional[List[str]] = None) -> List[Word]:
        """קבלת מילים אקראיות לפי פילטרים אופציונליים"""
        import random
        
        filtered_words = list(self.words.values())
        
        if difficulty is not None:
            filtered_words = [w for w in filtered_words if w.difficulty_level == difficulty]
            
        if topics:
            filtered_words = [w for w in filtered_words 
                              if any(topic in w.topic_tags for topic in topics)]
        
        return random.sample(filtered_words, min(count, len(filtered_words)))


class UserRepository:
    """מחלקה לשמירת ושליפת נתוני משתמשים מ-MongoDB"""
    
    def __init__(self, mongo_uri: str = None):
        """
        אתחול חיבור למסד הנתונים
        
        Args:
            mongo_uri: כתובת החיבור ל-MongoDB
        """
        self.mongo_uri = mongo_uri
        self.client = None
        self.db = None
        self.users_collection = None
        
        if self.mongo_uri:
            try:
                self.client = pymongo.MongoClient(self.mongo_uri)
                self.db = self.client.english_learning_bot
                self.users_collection = self.db.users
            except Exception as e:
                print(f"שגיאה בהתחברות ל-MongoDB: {e}")
                # במקרה של שגיאה נשתמש במאגר זמני בזיכרון
                self.users_collection = {}
        else:
            # אם לא סופק URI, השתמש במאגר זמני בזיכרון
            self.users_collection = {}
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        קבלת מידע על משתמש לפי מזהה
        
        Args:
            user_id: מזהה המשתמש בטלגרם
            
        Returns:
            מילון עם פרטי המשתמש או משתמש חדש אם לא קיים
        """
        if isinstance(self.users_collection, dict):
            user_data = self.users_collection.get(user_id)
        else:
            user_data = self.users_collection.find_one({"user_id": user_id})
        
        if not user_data:
            # יצירת משתמש חדש
            user_data = self._create_new_user(user_id)
        
        return user_data
    
    def _create_new_user(self, user_id: int) -> Dict[str, Any]:
        """
        יצירת רשומת משתמש חדשה
        
        Args:
            user_id: מזהה המשתמש בטלגרם
            
        Returns:
            מילון עם פרטי המשתמש החדש
        """
        new_user = {
            "user_id": user_id,
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
        
        self.save_user(new_user)
        return new_user
    
    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """
        שמירת נתוני משתמש
        
        Args:
            user_data: מילון עם פרטי המשתמש
            
        Returns:
            בוליאני המציין אם השמירה הצליחה
        """
        try:
            user_id = user_data["user_id"]
            
            if isinstance(self.users_collection, dict):
                self.users_collection[user_id] = user_data
            else:
                # בדיקה אם המשתמש כבר קיים ועדכון
                result = self.users_collection.update_one(
                    {"user_id": user_id},
                    {"$set": user_data},
                    upsert=True
                )
                return result.acknowledged
            
            return True
        except Exception as e:
            print(f"שגיאה בשמירת נתוני משתמש: {e}")
            return False
    
    def update_user_word_progress(self, user_id: int, word_progress: UserWordProgress) -> bool:
        """
        עדכון התקדמות של מילה עבור משתמש
        
        Args:
            user_id: מזהה המשתמש בטלגרם
            word_progress: אובייקט התקדמות המילה
            
        Returns:
            בוליאני המציין אם העדכון הצליח
        """
        user_data = self.get_user(user_id)
        
        # חיפוש מילה קיימת ברשימת ההתקדמויות
        word_found = False
        if "word_progress" not in user_data:
            user_data["word_progress"] = []
        
        for i, wp in enumerate(user_data.get("word_progress", [])):
            if wp.get("word_id") == word_progress.word_id:
                user_data["word_progress"][i] = word_progress.to_dict()
                word_found = True
                break
        
        # אם המילה לא נמצאה, הוסף אותה
        if not word_found:
            user_data["word_progress"].append(word_progress.to_dict())
        
        # עדכון מונה המילים שנלמדו
        mastered_count = 0
        for wp in user_data.get("word_progress", []):
            if wp.get("status") == WordStatus.MASTERED.value:
                mastered_count += 1
        
        user_data["progress"]["words_mastered"] = mastered_count
        
        # שמירת המשתמש
        return self.save_user(user_data)
    
    def get_user_word_progress(self, user_id: int, word_id: str) -> Optional[UserWordProgress]:
        """
        קבלת התקדמות של מילה מסוימת עבור משתמש
        
        Args:
            user_id: מזהה המשתמש בטלגרם
            word_id: מזהה המילה
            
        Returns:
            אובייקט UserWordProgress אם נמצא, אחרת None
        """
        user_data = self.get_user(user_id)
        
        for wp_data in user_data.get("word_progress", []):
            if wp_data.get("word_id") == word_id:
                return UserWordProgress.from_dict(wp_data)
        
        # אם לא נמצאה התקדמות, החזר אובייקט חדש
        return UserWordProgress(word_id) 