# פרויקט בוט ללימוד אנגלית

פרויקט זה מיישם בוט טלגרם אינטראקטיבי ללימוד אנגלית, המבוסס על מאגר של כ-4,300 מילים. הבוט ישלב יכולות AI באמצעות ה-API של Gemini ויציע מגוון פעילויות לימודיות.

## הכנת קובץ המילים

כדי להכין את קובץ המילים מקובץ Word, יש לבצע את הצעדים הבאים:

### צעד 1: המרת קובץ Word לטקסט פשוט

1. פתח את קובץ ה-Word שמכיל את המילים
2. בחר "שמור בשם" ובחר בפורמט "Text Document (*.txt)"
3. שמור את הקובץ בתיקיית `data` של הפרויקט בשם `words.txt`
4. ודא שכל מילה נמצאת בשורה נפרדת

### צעד 2: המרת הטקסט לפורמט JSON

השתמש בסקריפט `process_words.py` כדי להמיר את קובץ הטקסט לפורמט JSON:

```
python data/process_words.py process data/words.txt data/words/words.json
```

### צעד 3: הוספת תרגומים (בעתיד)

ניתן להכין קובץ CSV עם תרגומים בפורמט:
```
english_word,תרגום_עברי
```

ואז להוסיף את התרגומים באמצעות:
```
python data/process_words.py translate data/words/words.json data/translations.csv data/words/words_with_translations.json
```

### צעד 4: הוספת מידע נוסף (בעתיד)

ניתן להוסיף מידע נוסף על המילים (חלק דיבור, דוגמאות, מילים נרדפות) באמצעות קובץ JSON בפורמט המתאים:
```
python data/process_words.py info data/words/words_with_translations.json data/word_info.json data/words/complete_words.json
```

## מבנה הנתונים

מבנה הנתונים של כל מילה בקובץ ה-JSON הסופי:

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

## הפעלת הבוט

הוראות להפעלת הבוט יתווספו בהמשך הפיתוח. 