from groq import Groq
from config import GROQ_API_KEY, CONFIG

import numpy as np
import cv2
import json


client = Groq(api_key=GROQ_API_KEY)


def create_quiz(text: str, lang: str ="UA"):
    ua_p = f"""
Роль: Експерт з аналізу емоційних станів  
Завдання: На основі тексту сформулювати 1 питання про емоції персонажів та 4 варіанти відповідей українською мовою.  

Інструкції:  
1. Проаналізуй контекст та визнач домінуючу емоцію персонажа.  
2. Сформулюй одне питання у форматі: "Як почувається [персонаж]?"  
3. Створи список з 4 варіантів відповідей:  
   - Перший варіант(Answer[0]) є правильний: точна назва емоції.  
   - Інші варіанти: неправильні емоції.  
   - Використовуй лише заздалегідь визначені емоції. Ось список емоцій, які можна використовувати: смуток, тривога, злість, розгубленість, радість, роздратування, здивування, вдячність, полегшення, розчарування, зніяковіння, подив, страх, сонливість, захоплення, гордість, провина, сором, прощення. 
4. Напиши пояснення. Чому персонаж відчуває саме таку емоцію. Зроби це суцільним текстом, до 50 слів. Пояснення у форматі: "[Персонаж] відчуває [емоція], оскільки ...".
5. Виведи строго у форматі: {{"Question": "...?", "Answer": ["...", "...", "...", "..."], "Explanation": "..."}}  
6. Використовуй прості емоції, такі як: "радість", "злість" тощо.  
7. Заборонено додавати коментарі, пояснення чи інші елементи.  
8. Відповідь українською мовою.  

Приклад відповіді:  
{{"Question": "Як почувається Марія?", "Answer": ["Щаслива", "Розгублена", "Розчарована", "Налякана"], "Explanation": "Вона щаслива, оскільки допомогла іншій людині"}}  

Текст для аналізу: {text}"""

    eng_p = f"""
Role: Expert in Emotional State Analysis
Task: Based on the text, formulate 1 question about characters' emotions and 4 answer options in English

Instructions:
1. Analyze the context and identify the character's dominant emotion
2. Formulate one question in the format: "How does [character] feel?"
3. Create a list of 4 answer options:
   - First option(Answer[0] is correct: precise emotion name
   - Other options:  incorrect emotions
   - Use only prepared emotions. Here's a list of emotions you can use: sadness, anxiety, anger, confusion, joy, irritation, amazement, appreciation, relief, disappointment, embarrassment, surprise, fear, drowsiness, fascination, pride, fault, shame, forgiveness;
4. Write an explanation. Why the character feels this emotion. Make it a solid text, up to 50 words. Explanation in the format: “[The character] feels [the emotion] because...” 
5. Output strictly in the format: {{"Question": "...?", "Answer": ["...", "...", "...", "..."], "Explanation": "..."}}
6. Use simple emotions like: “Joy, anger, etc.”
7. Do not add comments, explanations, or other elements
8. Answers must be in English

Response example:
{{Question: "How does Maria feel?"|Answer: ["Happy", "Confused", "Disappointed", "Scared"], "Explanation": "She is happy because she helped another person"}}

Text for analysis: {text}
"""

    return json.loads(client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": ua_p if lang == "UA" else eng_p,
        }
    ],
    model="llama-3.3-70b-versatile",
).choices[0].message.content)

def create_novel(text: str, lang: str = "UA"):
    ua_p = f"""
Твоє завдання перефразувати текст, але залишити її у тому самому обсязі. Заборонено додавати коментарі, пояснення чи інші елементи. Тільки відповідь у форматі {{"text": "..."}}.
Текст: {text}
"""

    eng_p = f"""
Your task is to paraphrase the text, but keep it the same. Do not add comments, explanations or other elements. Only answer in the format {{"text": "..."}}.
Text: {text}
"""

    return json.loads(client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": ua_p if lang == "UA" else eng_p,
        }
    ],
    model="llama-3.3-70b-versatile",
).choices[0].message.content)

def process_image(frame: bytes, target_emotion: str, model, face_cascade) -> bool:
    try:
        nparr = np.frombuffer(frame, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (48, 48))
            face_roi = face_roi.reshape(1, 48, 48, 1).astype('float32')/255
            
            prediction = model.predict(face_roi)
            emotion = CONFIG['emotion_labels'][np.argmax(prediction)]
            
            if CONFIG['display_processing']:
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
                cv2.putText(img, emotion, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)
                cv2.imshow('Server Processing', img)
                cv2.waitKey(1)
            
            if emotion == target_emotion:
                return True
        return False
    except Exception as e:
        print(f"Processing error: {e}")
        return False

if __name__ == "__main__":
    res = create_novel(
        text="Niko and Tora finished their crunchy snack and decided to play hide-and-seek. Niko ran ahead, eyes sparkling as he searched for the perfect hiding spot. He spotted a leafy bush and crawled under quietly, trying not to giggle. But minutes passed, and Tora didn't come. Niko peeked from behind the leaves. Still no Tora. He felt his excitement slowly fade. Just then, he heard Tora’s gentle voice from behind a nearby tree.",
        lang="ENG"
    )
    print(res["text"])
