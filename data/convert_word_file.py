#!/usr/bin/env python
"""
סקריפט להמרת קובץ המילים מטקסט ל-JSON
השתמש בסקריפט הזה אחרי שהכנת קובץ טקסט מקובץ ה-Word שלך
"""

import os
import sys
import subprocess

# בדיקה שהתיקיות הנדרשות קיימות
if not os.path.exists('data/words'):
    os.makedirs('data/words')

# קובץ הקלט - קובץ הטקסט שיצרת מקובץ ה-Word
input_file = 'data/words.txt'

# בדיקה שקובץ הקלט קיים
if not os.path.exists(input_file):
    print(f"שגיאה: קובץ הקלט {input_file} לא נמצא!")
    print("אנא המר את קובץ ה-Word לקובץ טקסט ושמור אותו בנתיב: data/words.txt")
    sys.exit(1)

# קובץ הפלט - קובץ ה-JSON שייווצר
output_file = 'data/words/words.json'

print("מתחיל בהמרת קובץ המילים...")

# הרצת פקודת ההמרה
process = subprocess.run(
    ['python', 'data/process_words.py', 'process', input_file, output_file],
    capture_output=True, 
    text=True
)

# בדיקה שהפקודה הצליחה
if process.returncode == 0:
    print("קובץ המילים הומר בהצלחה!")
    print(f"נתיב קובץ ה-JSON: {os.path.abspath(output_file)}")
    print(f"מספר המילים שעובדו: {sum(1 for line in open(input_file, 'r', encoding='utf-8') if line.strip())}")
    
    print("\nהמידע הבא יתווסף בשלבים הבאים:")
    print("1. תרגום לעברית")
    print("2. חלק דיבור (שם עצם, פועל וכו')")
    print("3. רמת קושי")
    print("4. דוגמאות")
    print("5. מילים נרדפות")
else:
    print("שגיאה בהמרת הקובץ:")
    print(process.stderr)
    sys.exit(1)