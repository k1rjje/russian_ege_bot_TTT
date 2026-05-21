import requests
import time
from datetime import date, datetime
import threading

TOKEN = "8652125406:AAHz3XQnWvt_RFnvi0WMF15AGiywMwopSjw"

#картимночки
pics = ["pic1.png", "pic2.png", "pic3.png"]
ind = 0

def pics_send(chat_id):
    global ind
    pic = pics[ind]
    with open(pic, "rb") as img:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={"chat_id": chat_id}, files={"photo": img})
    ind = (ind + 1) % len(pics)

def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = {"inline_keyboard": keyboard}
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=data)

def get_updates(offset):
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params={"offset": offset, "timeout": 10})
    return r.json().get("result", [])

#времени нет евфрат уже сохнет
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={text}"
    requests.get(url)

ege = date(2026, 6, 24)
now = datetime.now()
n = (ege - now.date()).days

#обкачка заданий
with open("tasks.txt", "r", encoding="utf-8") as f:
    lines = [x.strip() for x in f if x.strip()]

tasks = []
for i, line in enumerate(lines):
    if line.startswith("Ответ:"):
        answer = line.replace("Ответ:", "").strip()
        task_lines = []
        j = i - 1
        while j >= 0 and not lines[j].startswith("Ответ:"):
            line_text = lines[j]
            if not any(x in line_text for x in ['Тип', '№', 'i']):
                if not line_text.replace('.', '').replace('-', '').isdigit():
                    task_lines.insert(0, line_text)
            j -= 1
        tasks.append({"text": "\n".join(task_lines), "answer": answer})

print(f"обкачано {len(tasks)} заданий")

last_id = 0
cur_id = None

def skolko():
    global last_id
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": last_id + 1, "timeout": 5}
            response = requests.get(url, params=params).json()
            
            for update in response.get("result", []):
                last_id = update["update_id"]
                msg = update.get("message", {})
                text = msg.get("text", "")
                chat_id = msg.get("chat", {}).get("id")
                
                if text == "сколько?" and chat_id:
                    send_message(chat_id, f"До ЕГЭ осталось {n} дней")
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(1)

threading.Thread(target=skolko, daemon=True).start()

#посылка заданий
while cur_id is None:
    updates = get_updates(last_id)
    for upd in updates:
        msg = upd.get("message")
        if msg and msg.get("text"):
            cur_id = msg["chat"]["id"]
            last_id = upd["update_id"] + 1
            break
    time.sleep(1)

for idx, task in enumerate(tasks):
    send(cur_id, task['text'])
    
    correct = False
    while not correct:
        answer = None
        while answer is None:
            updates = get_updates(last_id)
            for upd in updates:
                msg = upd.get("message")
                if msg and msg.get("text") and msg["chat"]["id"] == cur_id:
                    answer = msg["text"].strip().lower()
                    last_id = upd["update_id"] + 1
                    break
                
                callback = upd.get("callback_query")
                if callback and callback["data"] == "show_answer":
                    send(cur_id, f"Правильный ответ: {task['answer']}")
                    last_id = upd["update_id"] + 1
                    correct = True 
                    answer = task["answer"].lower() 
                    break
            time.sleep(1)
        
        if answer == task["answer"].lower():
          send(cur_id, f"ура все верно!!")
          correct = True

        elif answer != task["answer"].lower() and not correct:
            if correct:
                break
            pics_send(cur_id)
            
            keyboard = [[
                {"text": "Попытаться еще раз!", "callback_data": "again"},
                {"text": "Показать ответ", "callback_data": "show_answer"}
            ]]
            send(cur_id, f"неверно :( Попробуй ещё:", keyboard=keyboard)
            
            waiting = True
            while waiting and not correct:
                updates = get_updates(last_id)
                for upd in updates:
                    callback = upd.get("callback_query")
                    if callback and callback["message"]["chat"]["id"] == cur_id:
                        if callback["data"] == "again":
                            send(cur_id, "Введи ответ ещё раз:")
                            last_id = upd["update_id"] + 1
                            waiting = False
                            answer = None
                            break
                        elif callback["data"] == "show_answer":
                            send(cur_id, f"Правильный ответ: {task['answer']}")
                            last_id = upd["update_id"] + 1
                            correct = True
                            waiting = False
                            break
                time.sleep(1)