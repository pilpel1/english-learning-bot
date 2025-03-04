#!/usr/bin/env python3
"""
סקריפט לתיקון מזהים כפולים במסד הנתונים.
"""

import json
import os
import uuid
from collections import defaultdict
from typing import Dict, List, Set, Tuple

def fix_duplicate_ids(words_file_path: str, output_file_path: str) -> Tuple[int, List[Dict]]:
    """
    מתקן מזהים כפולים במסד הנתונים ושומר את התוצאה לקובץ חדש.
    
    Args:
        words_file_path: נתיב לקובץ המילים המקורי
        output_file_path: נתיב לשמירת הקובץ המתוקן
        
    Returns:
        מספר המזהים שתוקנו ורשימה של הדיווחים על התיקונים שבוצעו
    """
    if not os.path.exists(words_file_path):
        print(f"שגיאה: הקובץ {words_file_path} לא נמצא!")
        return 0, []
    
    try:
        with open(words_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"שגיאה: הקובץ {words_file_path} אינו קובץ JSON תקין!")
        return 0, []
    
    # בדיקה אם המבנה הוא מערך ישירות או אובייקט עם שדה 'words'
    if isinstance(data, list):
        words = data
    elif isinstance(data, dict) and 'words' in data:
        words = data.get('words', [])
    else:
        print(f"שגיאה: הקובץ {words_file_path} אינו במבנה הצפוי!")
        return 0, []
    
    # איסוף כל המזהים
    id_to_indexes = defaultdict(list)  # מזהה -> רשימת האינדקסים של המילים עם מזהה זה
    used_ids = set()
    
    # שלב 1: מיפוי מזהים לאינדקסים
    for i, word in enumerate(words):
        word_id = word.get('word_id', '')
        if word_id:
            id_to_indexes[word_id].append(i)
    
    # שלב 2: מצא מזהים כפולים ותקן אותם
    fixed_count = 0
    fix_reports = []
    
    for word_id, indexes in id_to_indexes.items():
        if len(indexes) > 1:  # נמצא מזהה כפול
            # משאיר את המופע הראשון כמו שהוא
            first_index = indexes[0]
            first_word = words[first_index]['english']
            used_ids.add(word_id)
            
            # מייצר מזהים חדשים עבור שאר המופעים
            for duplicate_index in indexes[1:]:
                old_id = words[duplicate_index]['word_id']
                word_english = words[duplicate_index]['english']
                
                # יצירת מזהה חדש
                new_id = str(uuid.uuid4())
                while new_id in used_ids:  # וידוא שהמזהה החדש אינו קיים
                    new_id = str(uuid.uuid4())
                
                words[duplicate_index]['word_id'] = new_id
                used_ids.add(new_id)
                fixed_count += 1
                
                # שמירת דוח התיקון
                fix_reports.append({
                    'word': word_english,
                    'old_id': old_id,
                    'new_id': new_id
                })
    
    # שמירת הנתונים המתוקנים לקובץ חדש
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
        print(f"הנתונים המתוקנים נשמרו בהצלחה לקובץ: {output_file_path}")
    except Exception as e:
        print(f"שגיאה בשמירת הקובץ: {e}")
    
    return fixed_count, fix_reports

def main():
    input_file_path = "../data/words/words_complete.json"
    output_file_path = "../data/words/words_fixed.json"
    
    # בדיקה אם הקובץ קיים
    if not os.path.exists(input_file_path):
        print(f"הקובץ {input_file_path} לא נמצא. מנסה נתיב אחר...")
        input_file_path = "C:/pyth/projects/english-learning-bot/data/words/words_complete.json"
        output_file_path = "C:/pyth/projects/english-learning-bot/data/words/words_fixed.json"
        if not os.path.exists(input_file_path):
            print(f"הקובץ {input_file_path} לא נמצא גם כן.")
            return
    
    print(f"מתקן מזהים כפולים בקובץ: {input_file_path}")
    fixed_count, fix_reports = fix_duplicate_ids(input_file_path, output_file_path)
    
    if fixed_count == 0:
        print("לא נמצאו מזהים כפולים לתיקון.")
    else:
        print(f"✅ תוקנו {fixed_count} מזהים כפולים.")
        print("\nפירוט התיקונים:")
        for i, report in enumerate(fix_reports, 1):
            print(f"{i}. המילה '{report['word']}' שונתה ממזהה {report['old_id']} למזהה {report['new_id']}")

if __name__ == "__main__":
    main() 