import json
from pathlib import Path

USERS_FILE = Path(__file__).parent / "users_chat_id.json"

# === ФУНКЦИИ === 

# Загрузить пользователей
def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Сохранить пользователей
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

# Добавить пользователя (одного)
def add_user(chat_id: int):
    users = load_users()
    if chat_id not in users:
        users.append(chat_id)
        save_users(users)

# Удвлить пользователя (одного)
def remove_user(chat_id: int):
    users = load_users()
    if chat_id in users:
        users.remove(chat_id)
        save_users(users)
