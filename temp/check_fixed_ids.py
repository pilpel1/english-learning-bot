#!/usr/bin/env python3
"""
סקריפט לבדיקת הקובץ המתוקן ולוידוא שאין בו כפילויות ID.
"""

import sys
sys.path.append(".") # כדי שנוכל לייבא את הפונקציה מהקובץ הקודם

from check_duplicate_ids import check_duplicate_ids

def main():
    fixed_file_path = "../data/words/words_fixed.json"
    print(f"בודק את הקובץ המתוקן: {fixed_file_path}")
    
    has_duplicates, duplicates, total_words = check_duplicate_ids(fixed_file_path)
    
    if not has_duplicates:
        print(f"✅ בדיקה הושלמה בהצלחה! אין מזהים כפולים בקובץ המתוקן.")
        print(f"סך הכל נבדקו {total_words} מילים.")
    else:
        print("⚠️ נמצאו מזהים כפולים בקובץ המתוקן!")
        for word_id, words in duplicates.items():
            print(f"מזהה: {word_id}")
            for i, word in enumerate(words, 1):
                print(f"  {i}. {word}")
        
        print(f"\nסך הכל נמצאו {len(duplicates)} מזהים כפולים.")

if __name__ == "__main__":
    main() 