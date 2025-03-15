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
    
    # הוספת WordStatus כמשתנה סטטי של המחלקה
    WordStatus = WordStatus
    
    def __init__(self, data_dir="data/users"):
        """
        אתחול מאגר המשתמשים
        
        Args:
            data_dir: תיקיית הנתונים לשמירת קבצי המשתמשים
        """
        self.data_dir = data_dir
        # יצירת התיקייה אם לא קיימת
        os.makedirs(data_dir, exist_ok=True)
    
    def _get_user_file_path(self, user_id: int) -> str:
        """מחזיר את הנתיב לקובץ המשתמש"""
        return os.path.join(self.data_dir, f"user_{user_id}.json")
    
    async def get_user(self, user_id: int) -> Dict:
        """קבלת פרופיל משתמש לפי מזהה"""
        file_path = self._get_user_file_path(user_id)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading user file: {e}")
        return None
    
    async def save_user(self, user_profile: Dict) -> bool:
        """שמירת פרופיל משתמש"""
        try:
            file_path = self._get_user_file_path(user_profile["user_id"])
            # שמירה עם פירמוט יפה לקריאות
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_profile, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user file: {e}")
            return False
    
    async def update_user_word_progress(self, user_id: int, word_progress: UserWordProgress) -> bool:
        """עדכון התקדמות המשתמש במילה"""
        try:
            user_data = await self.get_user(user_id)  # הוספת await כאן
            
            if not user_data:
                user_data = {"user_id": user_id, "word_progress": []}
            
            if "word_progress" not in user_data:
                user_data["word_progress"] = []
            
            # עדכון או הוספת התקדמות המילה
            updated = False
            for wp in user_data["word_progress"]:
                if wp["word_id"] == word_progress.word_id:
                    wp.update(word_progress.to_dict())
                    updated = True
                    break
            
            if not updated:
                user_data["word_progress"].append(word_progress.to_dict())
            
            # עדכון מונה המילים שנלמדו
            mastered_count = 0
            for wp in user_data["word_progress"]:
                if wp["status"] == WordStatus.MASTERED.value:
                    mastered_count += 1
            
            user_data["progress"] = {"words_mastered": mastered_count}
            
            # שמירת הנתונים המעודכנים
            return await self.save_user(user_data)
            
        except Exception as e:
            print(f"Error updating word progress: {e}")
            return False
    
    async def get_user_word_progress(self, user_id: int, word_id: str) -> Optional[UserWordProgress]:
        """
        קבלת התקדמות של מילה מסוימת עבור משתמש
        
        Args:
            user_id: מזהה המשתמש בטלגרם
            word_id: מזהה המילה
            
        Returns:
            אובייקט UserWordProgress אם נמצא, אחרת None
        """
        user_data = await self.get_user(user_id)
        
        # אם אין נתונים למשתמש, מחזירים התקדמות חדשה
        if not user_data:
            return UserWordProgress(word_id)
        
        # חיפוש התקדמות קיימת
        for wp_data in user_data.get("word_progress", []):
            if wp_data["word_id"] == word_id:
                return UserWordProgress.from_dict(wp_data)
        
        # אם לא נמצאה התקדמות, מחזירים התקדמות חדשה
        return UserWordProgress(word_id) 