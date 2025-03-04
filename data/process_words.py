import json
import uuid
import argparse
import os
import re
from typing import List, Dict, Any, Optional, Tuple

def read_words_from_file(file_path: str) -> List[Tuple[str, Optional[str]]]:
    """
    קריאת מילים מקובץ טקסט - כל מילה בשורה חדשה
    מחזיר רשימה של טאפלים (מילה, תרגום אופציונלי)
    """
    words_with_translations = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:  # דילוג על שורות ריקות
                continue
                
            # בדיקה אם יש מבנה של "מילה - תרגום" (למשל "10th - tenth")
            if ' - ' in line:
                parts = line.split(' - ', 1)
                word = parts[0].strip()
                translation = parts[1].strip() if len(parts) > 1 else None
                words_with_translations.append((word, translation))
            else:
                # מילה רגילה ללא תרגום
                words_with_translations.append((line, None))
    
    return words_with_translations

def create_word_object(word: str, translation: Optional[str] = None, word_id: Optional[str] = None) -> Dict[str, Any]:
    """יצירת אובייקט מילה בפורמט המבוקש"""
    if not word_id:
        word_id = str(uuid.uuid4())  # יצירת מזהה ייחודי
    
    # זיהוי אם המילה היא מספר סודר (כמו 1st, 2nd וכו')
    is_ordinal = bool(re.match(r'^\d+(st|nd|rd|th)$', word))
    
    # הגדרת חלק דיבור אוטומטי לפי דפוסים (פשוט מאוד)
    part_of_speech = "ordinal" if is_ordinal else ""
    
    # הגדרת תגיות אוטומטיות
    topic_tags = ["general"]
    if is_ordinal:
        topic_tags.append("numbers")
    
    return {
        "word_id": word_id,
        "english": word,
        "translation": translation,  # שמירת התרגום האנגלי אם יש (למשל "tenth" ל-"10th")
        "hebrew": "",  # יתמלא בעתיד עם תרגום לעברית
        "part_of_speech": part_of_speech,
        "difficulty_level": 1,  # ברירת מחדל
        "examples": [],  # יתמלא בעתיד
        "synonyms": [],  # יתמלא בעתיד
        "topic_tags": topic_tags
    }

def process_words_file(input_file: str, output_file: str):
    """עיבוד קובץ מילים וייצוא לפורמט JSON"""
    words_with_translations = read_words_from_file(input_file)
    
    word_objects = []
    for word, translation in words_with_translations:
        word_objects.append(create_word_object(word, translation))
    
    # שמירה לקובץ JSON מסודר
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(word_objects, json_file, ensure_ascii=False, indent=2)
    
    print(f"נוצר קובץ JSON עם {len(word_objects)} מילים.")
    print(f"נתיב הקובץ: {os.path.abspath(output_file)}")

def merge_translations(words_file: str, translations_file: str, output_file: str):
    """
    מיזוג קובץ מילים עם קובץ תרגומים
    הקובץ translations_file צריך להיות בפורמט:
    english_word,hebrew_translation
    """
    # טעינת הנתונים הקיימים
    with open(words_file, 'r', encoding='utf-8') as file:
        words_data = json.load(file)
    
    # יצירת מילון עבור קלות חיפוש
    words_dict = {item['english']: item for item in words_data}
    
    # קריאת תרגומים
    with open(translations_file, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(',', 1)
            if len(parts) == 2:
                eng_word, heb_translation = parts
                eng_word = eng_word.strip()
                if eng_word in words_dict:
                    words_dict[eng_word]['hebrew'] = heb_translation.strip()
    
    # עדכון הרשימה המקורית
    updated_words = list(words_dict.values())
    
    # שמירה לקובץ
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(updated_words, file, ensure_ascii=False, indent=2)
    
    print(f"עודכן קובץ JSON עם תרגומים.")

def add_examples_and_info(words_file: str, info_file: str, output_file: str):
    """
    הוספת מידע נוסף למילים (חלק דיבור, דוגמאות, נרדפות, רמת קושי)
    הקובץ info_file צריך להיות בפורמט JSON מיוחד
    """
    # טעינת הנתונים הקיימים
    with open(words_file, 'r', encoding='utf-8') as file:
        words_data = json.load(file)
    
    # יצירת מילון עבור קלות חיפוש
    words_dict = {item['english']: item for item in words_data}
    
    # קריאת מידע נוסף
    with open(info_file, 'r', encoding='utf-8') as file:
        info_data = json.load(file)
    
    # עדכון המידע
    for word_info in info_data:
        if word_info['english'] in words_dict:
            word = words_dict[word_info['english']]
            
            # עדכון שדות אם קיימים במידע החדש
            if 'part_of_speech' in word_info:
                word['part_of_speech'] = word_info['part_of_speech']
            
            if 'examples' in word_info and word_info['examples']:
                word['examples'] = word_info['examples']
            
            if 'synonyms' in word_info and word_info['synonyms']:
                word['synonyms'] = word_info['synonyms']
            
            if 'difficulty_level' in word_info:
                word['difficulty_level'] = word_info['difficulty_level']
                
            if 'topic_tags' in word_info and word_info['topic_tags']:
                word['topic_tags'] = word_info['topic_tags']
    
    # עדכון הרשימה המקורית
    updated_words = list(words_dict.values())
    
    # שמירה לקובץ
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(updated_words, file, ensure_ascii=False, indent=2)
    
    print(f"עודכן קובץ JSON עם מידע נוסף.")

def main():
    parser = argparse.ArgumentParser(description="כלי עיבוד אוצר מילים")
    
    subparsers = parser.add_subparsers(dest="command", help="פקודה לביצוע")
    
    # פקודה להמרת קובץ טקסט ל-JSON
    process_parser = subparsers.add_parser("process", help="המרת קובץ טקסט לפורמט JSON")
    process_parser.add_argument("input_file", help="נתיב לקובץ הקלט")
    process_parser.add_argument("output_file", help="נתיב לקובץ הפלט")
    
    # פקודה למיזוג תרגומים
    translate_parser = subparsers.add_parser("translate", help="מיזוג קובץ מילים עם תרגומים")
    translate_parser.add_argument("words_file", help="נתיב לקובץ המילים")
    translate_parser.add_argument("translations_file", help="נתיב לקובץ התרגומים")
    translate_parser.add_argument("output_file", help="נתיב לקובץ הפלט")
    
    # פקודה להוספת מידע נוסף
    info_parser = subparsers.add_parser("info", help="הוספת מידע נוסף למילים")
    info_parser.add_argument("words_file", help="נתיב לקובץ המילים")
    info_parser.add_argument("info_file", help="נתיב לקובץ המידע הנוסף")
    info_parser.add_argument("output_file", help="נתיב לקובץ הפלט")
    
    args = parser.parse_args()
    
    if args.command == "process":
        process_words_file(args.input_file, args.output_file)
    elif args.command == "translate":
        merge_translations(args.words_file, args.translations_file, args.output_file)
    elif args.command == "info":
        add_examples_and_info(args.words_file, args.info_file, args.output_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 