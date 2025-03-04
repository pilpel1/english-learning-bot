#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
סקריפט לפיצול קובץ המילים הגדול לקבצים קטנים יותר
כל קובץ יכיל 30 מילים
"""

import json
import os
import math
from pathlib import Path

# הגדרת נתיבים
INPUT_FILE = 'data/words/words.json'
OUTPUT_DIR = 'data/words/split'
CHUNK_SIZE = 30  # כמות המילים בכל קובץ

def create_output_dir():
    """יוצר את התיקייה לקבצים המפוצלים אם היא לא קיימת"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"נוצרה תיקייה חדשה: {OUTPUT_DIR}")

def split_words_file():
    """מפצל את קובץ המילים לקבצים קטנים"""
    
    # בדיקה שקובץ הקלט קיים
    if not os.path.exists(INPUT_FILE):
        print(f"שגיאה: קובץ הקלט {INPUT_FILE} לא נמצא!")
        return
    
    # טעינת קובץ המילים
    print(f"טוען את קובץ המילים מ: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        all_words = json.load(f)
    
    # מידע על כמות המילים
    total_words = len(all_words)
    total_chunks = math.ceil(total_words / CHUNK_SIZE)
    print(f"סך הכל {total_words} מילים, יחולקו ל-{total_chunks} קבצים")
    
    # יצירת רשימת מעקב
    tracking_list = []
    
    # פיצול לקבצים
    for chunk_index in range(total_chunks):
        # חישוב האינדקסים של המילים בקטע הנוכחי
        start_idx = chunk_index * CHUNK_SIZE
        end_idx = min(start_idx + CHUNK_SIZE, total_words)
        
        # בחירת המילים לקטע הנוכחי
        chunk_words = all_words[start_idx:end_idx]
        
        # יצירת מטא-נתונים
        first_word = chunk_words[0]["english"]
        last_word = chunk_words[-1]["english"]
        chunk_data = {
            "_meta": {
                "chunk_number": chunk_index + 1,
                "words_range": f"{first_word}-{last_word}",
                "word_count": len(chunk_words),
                "start_index": start_idx,
                "end_index": end_idx - 1
            },
            "words": chunk_words
        }
        
        # שמירת הקובץ
        chunk_filename = f"chunk_{chunk_index+1:03d}.json"
        output_path = os.path.join(OUTPUT_DIR, chunk_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=2)
        
        # הוספה לרשימת המעקב
        tracking_list.append({
            "chunk_number": chunk_index + 1,
            "filename": chunk_filename,
            "word_count": len(chunk_words),
            "words_range": f"{first_word}-{last_word}",
            "status": "created"
        })
        
        if chunk_index % 10 == 0:
            print(f"נוצר קובץ {chunk_index+1}/{total_chunks}: {chunk_filename}")
    
    # שמירת רשימת המעקב
    tracking_file = os.path.join(OUTPUT_DIR, "_tracking.json")
    with open(tracking_file, 'w', encoding='utf-8') as f:
        json.dump(tracking_list, f, ensure_ascii=False, indent=2)
    
    print(f"\nהפיצול הסתיים בהצלחה!")
    print(f"נוצרו {total_chunks} קבצים בתיקייה {OUTPUT_DIR}")
    print(f"נשמרה רשימת מעקב: {tracking_file}")

def main():
    create_output_dir()
    split_words_file()

if __name__ == "__main__":
    main() 