#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
סקריפט לאיחוד קבצי המילים המפוצלים חזרה לקובץ אחד
לאחר שהושלמו עם תרגומים ודוגמאות

גרסה משופרת - כוללת בדיקות תקינות מקיפות לפני האיחוד
"""

import json
import os
import glob
from pathlib import Path
import sys

# הגדרת נתיבים
INPUT_DIR = 'data/words/split'
OUTPUT_FILE = 'data/words/words_complete.json'
TRACKING_FILE = 'data/words/split/_tracking.json'
# קובץ לוג לתיעוד בעיות
VALIDATION_LOG = 'data/words/validation_issues.log'

def validate_word_entry(word_data, filename, word_index):
    """
    בודק תקינות של רשומת מילה בודדת
    מחזיר (תקין, רשימת בעיות)
    """
    issues = []
    required_fields = ["word_id", "english", "hebrew", "part_of_speech"]
    
    # בדיקה שכל השדות הנדרשים קיימים
    for field in required_fields:
        if field not in word_data:
            issues.append(f"חסר שדה חובה: {field}")
    
    # בדיקה שיש תרגום (hebrew) ואינו ריק
    if "hebrew" in word_data:
        if word_data["hebrew"] is None or word_data["hebrew"].strip() == "":
            issues.append("שדה 'hebrew' ריק")
    
    # בדיקה שיש לפחות דוגמה אחת
    if "examples" not in word_data or not word_data["examples"] or len(word_data["examples"]) == 0:
        issues.append("אין דוגמאות שימוש")
    
    # בדיקה שחלק הדיבור תקין
    valid_pos = [
        # חלקי דיבר סטנדרטיים
        "noun", "verb", "adjective", "adverb", "pronoun", "preposition", 
        "conjunction", "interjection", "determiner", "numeral",
        
        # חלקי דיבר נוספים (מורחבים)
        "phrase", "expression", "abbreviation", "ordinal", "idiom", 
        "noun/verb", "adjective/noun", "verb/noun", "adjective/adverb",
        "preposition/adverb", "noun/adjective", "verb/adjective",
        "auxiliary", "modal", "article", "particle", "exclamation",
        "contraction", "acronym", "suffix", "prefix",
        
        # חלקי דיבר נוספים מהלוג האחרון
        "proper noun", "modal verb", "number", "proper noun", 
        "adjective verb", "adjective/ verb", " adjective/verb", "adjective/verb "
    ]
    if "part_of_speech" in word_data and word_data["part_of_speech"] not in valid_pos:
        issues.append(f"חלק דיבר לא חוקי: {word_data['part_of_speech']}")
    
    return len(issues) == 0, issues

def validate_chunk_file(file_path):
    """
    בודק תקינות של קובץ צ'אנק שלם
    מחזיר (תקין, מספר מילים תקינות, רשימת בעיות)
    """
    filename = os.path.basename(file_path)
    all_issues = []
    valid_words_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                chunk_data = json.load(f)
            except json.JSONDecodeError as e:
                return False, 0, [f"שגיאת JSON בקובץ: {str(e)}"]
        
        # בדיקת מבנה הקובץ
        if "_meta" not in chunk_data:
            all_issues.append("חסר מידע מטה (_meta) בקובץ")
        
        if "words" not in chunk_data:
            all_issues.append("חסר מערך המילים (words) בקובץ")
            return False, 0, all_issues
        
        # בדיקת כל מילה במערך
        for i, word_data in enumerate(chunk_data["words"]):
            is_valid, issues = validate_word_entry(word_data, filename, i)
            if not is_valid:
                all_issues.append(f"בעיות במילה {word_data.get('english', f'#אינדקס{i}')} (אינדקס {i}):")
                for issue in issues:
                    all_issues.append(f"  - {issue}")
            else:
                valid_words_count += 1
                
        return len(all_issues) == 0, valid_words_count, all_issues
        
    except Exception as e:
        return False, 0, [f"שגיאה בבדיקת הקובץ: {str(e)}"]

def merge_words_files():
    """מאחד את הקבצים המפוצלים לקובץ אחד אחרי בדיקת תקינות"""
    
    # בדיקה שתיקיית הקלט קיימת
    if not os.path.exists(INPUT_DIR):
        print(f"שגיאה: תיקיית הקלט {INPUT_DIR} לא נמצאה!")
        return False
    
    # מחיקת קובץ לוג קודם אם קיים
    if os.path.exists(VALIDATION_LOG):
        os.remove(VALIDATION_LOG)
    
    # טעינת קובץ המעקב
    if os.path.exists(TRACKING_FILE):
        print(f"טוען מידע מעקב מ: {TRACKING_FILE}")
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            tracking_data = json.load(f)
        
        # מיון הקבצים לפי מספר הקטע
        chunk_files = sorted(tracking_data, key=lambda x: x["chunk_number"])
    else:
        # אם אין קובץ מעקב, מוצאים את כל קבצי ה-JSON בתיקייה
        print(f"קובץ מעקב לא נמצא, קורא את כל קבצי ה-JSON מהתיקייה")
        chunk_files_paths = glob.glob(os.path.join(INPUT_DIR, "chunk_*.json"))
        chunk_files = [{"filename": os.path.basename(path), "chunk_number": int(os.path.basename(path).split("_")[1].split(".")[0])} 
                       for path in chunk_files_paths]
        chunk_files = sorted(chunk_files, key=lambda x: x["chunk_number"])
    
    # בדיקת תקינות של כל הקבצים
    print(f"\nמתחיל בדיקת תקינות של {len(chunk_files)} קבצים...")
    
    all_valid = True
    invalid_files = []
    missing_files = []
    total_valid_words = 0
    
    # פתיחת קובץ לוג
    log_file = open(VALIDATION_LOG, 'w', encoding='utf-8')
    log_file.write(f"=== דוח בדיקת תקינות קבצי מילים ===\n\n")
    
    for i, chunk_info in enumerate(chunk_files):
        filename = chunk_info["filename"]
        file_path = os.path.join(INPUT_DIR, filename)
        
        if not os.path.exists(file_path):
            print(f"אזהרה: הקובץ {filename} לא נמצא!")
            missing_files.append(filename)
            log_file.write(f"\n=== קובץ חסר: {filename} ===\n")
            all_valid = False
            continue
        
        # בדיקת תקינות הקובץ
        is_valid, valid_count, issues = validate_chunk_file(file_path)
        total_valid_words += valid_count
        
        if not is_valid:
            all_valid = False
            invalid_files.append(filename)
            log_file.write(f"\n=== בעיות בקובץ: {filename} ===\n")
            for issue in issues:
                log_file.write(f"{issue}\n")
        
        # הצגת התקדמות
        if (i+1) % 10 == 0 or i == len(chunk_files) - 1:
            print(f"נבדק {i+1}/{len(chunk_files)}: {filename} - {'תקין' if is_valid else 'לא תקין'}")
    
    log_file.write(f"\n=== סיכום ===\n")
    log_file.write(f"סך הכל קבצים: {len(chunk_files)}\n")
    log_file.write(f"קבצים חסרים: {len(missing_files)}\n")
    log_file.write(f"קבצים לא תקינים: {len(invalid_files)}\n")
    log_file.write(f"מילים תקינות: {total_valid_words}\n")
    log_file.close()
    
    # הצגת סיכום
    print("\n=== סיכום בדיקת תקינות ===")
    print(f"סך הכל קבצים: {len(chunk_files)}")
    print(f"קבצים חסרים: {len(missing_files)}")
    print(f"קבצים לא תקינים: {len(invalid_files)}")
    print(f"מילים תקינות: {total_valid_words}")
    print(f"דוח מפורט נשמר ב: {VALIDATION_LOG}")
    
    # שאלה אם להמשיך אם יש קבצים לא תקינים
    if not all_valid:
        print("\nמצאנו בעיות בבדיקת התקינות!")
        response = input("\nהאם להמשיך לאיחוד הקבצים למרות הבעיות? (כ/ל): ")
        if response.lower() not in ["כ", "כן", "y", "yes"]:
            print("האיחוד בוטל לפי בקשתך.")
            return False
        print("\nממשיך באיחוד הקבצים למרות הבעיות...")
    
    # איסוף כל המילים
    all_words = []
    total_files = len(chunk_files)
    processed_files = 0
    
    print(f"\nמאחד {total_files} קבצים...")
    
    for i, chunk_info in enumerate(chunk_files):
        filename = chunk_info["filename"]
        file_path = os.path.join(INPUT_DIR, filename)
        
        if not os.path.exists(file_path):
            print(f"אזהרה: הקובץ {file_path} לא נמצא, מדלג...")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
            
            # הוספת המילים למערך הכולל
            if "words" in chunk_data:
                all_words.extend(chunk_data["words"])
                processed_files += 1
            else:
                print(f"אזהרה: לא נמצאו מילים בקובץ {filename}")
            
            if (i+1) % 10 == 0 or i == len(chunk_files) - 1:
                print(f"עובד על קובץ {i+1}/{total_files}: {filename}")
        
        except Exception as e:
            print(f"שגיאה בקריאת הקובץ {filename}: {str(e)}")
    
    # שמירת כל המילים לקובץ אחד
    print(f"שומר {len(all_words)} מילים לקובץ: {OUTPUT_FILE}")
    
    # וידוא שתיקיית היעד קיימת
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_words, f, ensure_ascii=False, indent=2)
    
    print(f"\nהאיחוד הסתיים בהצלחה!")
    print(f"הקובץ המאוחד נשמר ב: {OUTPUT_FILE}")
    print(f"עובדו {processed_files} מתוך {total_files} קבצים")
    print(f"סך הכל {len(all_words)} מילים נשמרו")
    
    return True

def main():
    print("===== תוכנית לאיחוד קבצי מילים =====")
    print(f"תיקיית קלט: {INPUT_DIR}")
    print(f"קובץ פלט: {OUTPUT_FILE}")
    
    response = input("\nהאם להתחיל בתהליך האיחוד? (כ/ל): ")
    if response.lower() in ["כ", "כן", "y", "yes"]:
        merge_words_files()
    else:
        print("האיחוד בוטל.")

if __name__ == "__main__":
    main() 