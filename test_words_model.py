"""
סקריפט בדיקה פשוט למודלים של המילים
"""

from models import Word, WordsRepository
import json
import os


def main():
    # בדיקת קיום קובץ המילים
    words_file = 'data/words/words.json'
    if not os.path.exists(words_file):
        print(f"קובץ המילים {words_file} לא נמצא")
        return
    
    print(f"טוען מילים מהקובץ: {words_file}")
    repo = WordsRepository(words_file)
    
    # מידע כללי
    word_count = len(repo.words)
    print(f"מספר מילים שנטענו: {word_count}")
    
    if word_count == 0:
        print("לא נמצאו מילים בקובץ")
        return
    
    # מציג מספר מילים לדוגמה
    print("\nמילים לדוגמה:")
    sample_count = min(5, word_count)
    sample_words = list(repo.words.values())[:sample_count]
    
    for i, word in enumerate(sample_words, 1):
        print(f"{i}. {word.english}" + 
              (f" (תרגום אנגלי: {word.translation})" if word.translation else "") +
              (f" - {word.hebrew}" if word.hebrew else ""))
    
    # בדיקת פונקציונליות חיפוש
    print("\nחיפוש מילים:")
    search_term = input("הקלד מילה לחיפוש (או הקש Enter לדילוג): ")
    
    if search_term:
        results = repo.search_words(search_term)
        print(f"נמצאו {len(results)} תוצאות עבור '{search_term}':")
        
        for i, word in enumerate(results, 1):
            print(f"{i}. {word.english}" + 
                  (f" (תרגום אנגלי: {word.translation})" if word.translation else "") +
                  (f" - {word.hebrew}" if word.hebrew else ""))
    
    # בדיקת קבלת מילים אקראיות
    print("\nמילים אקראיות:")
    random_words = repo.get_random_words(5)
    for i, word in enumerate(random_words, 1):
        print(f"{i}. {word.english}" + 
              (f" (תרגום אנגלי: {word.translation})" if word.translation else ""))


if __name__ == "__main__":
    main() 