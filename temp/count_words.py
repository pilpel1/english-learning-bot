#!/usr/bin/env python
import json

with open('data/words/words.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'מספר המילים בקובץ: {len(data)}')
    
    # הצגת 5 המילים הראשונות
    print("\nדוגמאות למילים:")
    for i, word in enumerate(data[:5]):
        print(f"{i+1}. {word['english']}") 