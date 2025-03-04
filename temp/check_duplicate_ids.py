#!/usr/bin/env python3
"""
סקריפט חד פעמי לבדיקת כפילויות ב-ID של מילים במסד הנתונים המאוחד.
"""

import json
from collections import defaultdict
import os
from typing import Dict, List, Tuple

def check_duplicate_ids(words_file_path: str) -> Tuple[bool, Dict[str, List[str]], int]:
    """
    בודק אם יש מזהים כפולים במסד הנתונים.
    
    Args:
        words_file_path: נתיב לקובץ ה-JSON המאוחד של המילים
        
    Returns:
        צמד של:
        - דגל בוליאני שמציין אם נמצאו כפילויות
        - מילון של מזהים כפולים (מפתח: מזהה, ערך: רשימת המילים עם מזהה זה)
        - מספר כולל של מילים שנבדקו
    """
    if not os.path.exists(words_file_path):
        print(f"שגיאה: הקובץ {words_file_path} לא נמצא!")
        return True, {}, 0
    
    try:
        with open(words_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"שגיאה: הקובץ {words_file_path} אינו קובץ JSON תקין!")
        return True, {}, 0
    
    # בדיקה אם המבנה הוא מערך ישירות או אובייקט עם שדה 'words'
    if isinstance(data, list):
        words = data
    elif isinstance(data, dict) and 'words' in data:
        words = data.get('words', [])
    else:
        print(f"שגיאה: הקובץ {words_file_path} אינו במבנה הצפוי!")
        return True, {}, 0
    
    # מילון לאיסוף מזהים כפולים (מפתח: מזהה, ערך: רשימת מילים)
    duplicates = defaultdict(list)
    
    # מילון לאיסוף כל המזהים (מפתח: מזהה, ערך: מילה באנגלית)
    all_ids = {}
    
    for word in words:
        word_id = word.get('word_id', '')
        english = word.get('english', '')
        
        if not word_id:
            print(f"אזהרה: נמצאה מילה ללא מזהה: {english}")
            continue
        
        if word_id in all_ids:
            duplicates[word_id].append(english)
            # הוסף את המילה הראשונה לרשימת הכפילויות אם זו הפעם הראשונה שמצאנו כפילות
            if len(duplicates[word_id]) == 1:
                duplicates[word_id].append(all_ids[word_id])
        
        all_ids[word_id] = english
    
    return bool(duplicates), duplicates, len(all_ids)

def main():
    words_file_path = "../data/words/words_complete.json"
    
    # בדיקה אם הקובץ קיים
    if not os.path.exists(words_file_path):
        print(f"הקובץ {words_file_path} לא נמצא. מנסה נתיב אחר...")
        words_file_path = "C:/pyth/projects/english-learning-bot/data/words/words_complete.json"
        if not os.path.exists(words_file_path):
            print(f"הקובץ {words_file_path} לא נמצא גם כן.")
            return
    
    print(f"בודק את הקובץ: {words_file_path}")
    has_duplicates, duplicates, total_words = check_duplicate_ids(words_file_path)
    
    if not has_duplicates:
        print("✅ בדיקה הושלמה בהצלחה! אין מזהים כפולים במסד הנתונים.")
        print(f"סך הכל נבדקו {total_words} מילים.")
    else:
        print("⚠️ נמצאו מזהים כפולים!")
        for word_id, words in duplicates.items():
            print(f"מזהה: {word_id}")
            for i, word in enumerate(words, 1):
                print(f"  {i}. {word}")
        
        print(f"\nסך הכל נמצאו {len(duplicates)} מזהים כפולים.")

if __name__ == "__main__":
    main() 