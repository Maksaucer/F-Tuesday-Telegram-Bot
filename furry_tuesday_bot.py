import telebot
import schedule
import time
import requests
from requests.auth import HTTPBasicAuth

TOKEN = 'MY_TOKEN'
E621_API_KEY = 'API_KEY'
USERNAME = "MY_NAME"

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Переменная для хранения chat_id
chat_id = 712363460 # None

# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def start(message):
    global chat_id
    chat_id = message.chat.id
    print(f'Chat ID: {chat_id}')
    bot.send_message(chat_id, 'Привет! Я бот, который отправляет самую популярную картинку с e621. Просто напиши /porn и я ее отправлю!')

# Функция для обработки команды /porn
@bot.message_handler(commands=['porn'])
def porn(nessage):
    send_image()

# Функция для получения самой популярной картинки с e621.net
def get_most_image_data():
    url = 'https://e621.net/posts.json'

    headers = {
        'User-Agent': 'FurryTuesdayBot/1.0 (by @F@maksaucer)',
        'Host': 'e621.net'
    }

    params = {
        'limit': 1,
        'tags': 'order:score date:day'
    }

    try:
        response = requests.get(
            url, 
            headers=headers,
            params=params,
            auth=HTTPBasicAuth(USERNAME, E621_API_KEY),  # Авторизация
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')
    return None


# Функция для отправки картинки
def send_image():
    if chat_id is not None:
        image_data = get_most_image_data()
        if image_data:
            print(image_data['posts'][0]['sample']['url'])
            try:            
                bot.send_photo(
                    chat_id, 
                    image_data['posts'][0]['sample']['url'],  
                    (f"https://e621.net/posts/{image_data['posts'][0]['id']}")
                )
                print(f'Sent image to {chat_id}')
            except Exception as e:
                print(f'Failed to send image to {chat_id}: {e}')
        else:
            print(f'Failed to get image URL')

# Расписание для отправки картинки каждые 10 секунд
#schedule.every(30).seconds.do(send_image)

# Запуск бота
bot.polling()

# Запуск расписания
while True:
    schedule.run_pending()
    time.sleep(1)