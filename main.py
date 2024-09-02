import logging
import sqlite3
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests

# Настройка логирования
logging.basicConfig(filename='logging.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Инициализация бота
TELEGRAM_BOT_TOKEN = "7071783674:AAFAgvQNXgSnjxnMwH0c6J5dEkktLDcYl4g"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Заголовки для запросов к RapidAPI
RAPIDAPI_KEY = '691262a019msh7aa09ef8ac67bedp1e9193jsne172974c850d'
RAPIDAPI_HOST = 'crypto-update-live.p.rapidapi.com'
HEADERS = {
    'X-RapidAPI-Key': RAPIDAPI_KEY,
    'X-RapidAPI-Host': RAPIDAPI_HOST
}

# Функция для обновления истории запросов в базе данных
def update_user_history_db(user_id, command):
    # Создание соединения и курсора
    conn = sqlite3.connect('request.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_requests (user_id, command) VALUES (?, ?)
    ''', (user_id, command))
    conn.commit()

    # Закрытие соединения
    conn.close()

# Функция /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(chat_id=user_id, text="Привет! Я бот с информацией о криптовалютах. "
                                           "Используйте кнопки ниже для доступа к командам:",
                     reply_markup=get_main_keyboard())
    update_user_history_db(user_id, '/start')
    logging.info(f"Пользователь {user_id} использовал команду /start.")

# Функция /history
@bot.message_handler(commands=['history'])
def show_user_history(message):
    user_id = message.from_user.id
    # Создание соединения и курсора
    conn = sqlite3.connect('request.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT command, timestamp FROM user_requests WHERE user_id=? ORDER BY timestamp DESC LIMIT 10
    ''', (user_id,))
    history = cursor.fetchall()

    if history:
        message_text = "Последние 10 запросов:\n"
        for command, timestamp in history:
            message_text += f"{timestamp}: {command}\n"
    else:
        message_text = "История запросов пуста."

    bot.send_message(chat_id=user_id, text=message_text, reply_markup=get_main_keyboard())
    logging.info(f"Пользователь {user_id} использовал команду /history.")

    # Закрытие соединения
    conn.close()

# Функция /high
@bot.message_handler(commands=['high'])
def show_high_cryptos(message):
    user_id = message.from_user.id
    # Запрос к RapidAPI
    url = "https://crypto-update-live.p.rapidapi.com/coins/list?limit=10"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        message_text = "Топ 10 криптовалют:\n"
        for crypto in data:
            coin_name = data[crypto]['name']
            price = data[crypto]['price']
            symbol = data[crypto]['symbol']
            message_text += f"{coin_name}: {price} ({symbol})\n"
        bot.send_message(chat_id=user_id, text=message_text)
        update_user_history_db(user_id, '/high')
        logging.info(f"Пользователь {user_id} использовал команду /high.")
    else:
        bot.send_message(chat_id=user_id, text="Произошла ошибка при получении данных. "
                                               "Пожалуйста, попробуйте позже.")

# Функция /low
@bot.message_handler(commands=['low'])
def show_low_cryptos(message):
    user_id = message.from_user.id
    # Запрос к RapidAPI
    url = "https://crypto-update-live.p.rapidapi.com/coins/list?limit=10"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        message_text = "Топ 10 криптовалют:\n"
        for crypto in data:
            coin_name = data[crypto]['name']
            price = data[crypto]['price']
            symbol = data[crypto]['symbol']
            message_text += f"{coin_name}: {price} ({symbol})\n"
        bot.send_message(chat_id=user_id, text=message_text)
        update_user_history_db(user_id, '/low')
        logging.info(f"Пользователь {user_id} использовал команду /low.")
    else:
        bot.send_message(chat_id=user_id, text="Произошла ошибка при получении данных. "
                                               "Пожалуйста, попробуйте позже.")

# Функция /custom
@bot.message_handler(commands=['custom'])
def request_custom_range(message):
    user_id = message.from_user.id
    bot.send_message(chat_id=user_id, text="Введите минимальную цену:")
    bot.register_next_step_handler(message, process_min_price_input)

def process_min_price_input(message):
    user_id = message.from_user.id
    try:
        min_price = float(message.text)
        bot.send_message(chat_id=user_id, text="Введите максимальную цену:")
        bot.register_next_step_handler(message, process_max_price_input, min_price)
    except ValueError:
        bot.send_message(chat_id=user_id, text="Некорректный формат. Введите число.")
        request_custom_range(message)

def process_max_price_input(message, min_price):
    user_id = message.from_user.id
    try:
        max_price = float(message.text)
        # Запрос к RapidAPI
        url = f"https://crypto-update-live.p.rapidapi.com/coins/list?limit=100"
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            # Фильтрация данных в заданном диапазоне цен
            filtered_data = {crypto: data[crypto] for crypto in data if min_price <= data[crypto]['price'] <= max_price}

            if not filtered_data:
                bot.send_message(chat_id=user_id, text=f"Нет криптовалют в заданном диапазоне цен: от {min_price} до {max_price}.")
            else:
                message_text = f"Криптовалюты в диапазоне от {min_price} до {max_price}:\n"
                for crypto in filtered_data:
                    coin_name = data[crypto]['name']
                    price = data[crypto]['price']
                    symbol = data[crypto]['symbol']
                    message_text += f"{coin_name}: {price} ({symbol})\n"
                bot.send_message(chat_id=user_id, text=message_text)
                update_user_history_db(user_id, '/custom')
                logging.info(f"Пользователь {user_id} выбрал пользовательский диапазон.")
        else:
            bot.send_message(chat_id=user_id, text="Произошла ошибка при получении данных. "
                                                   "Пожалуйста, попробуйте позже.")
    except ValueError:
        bot.send_message(chat_id=user_id, text="Некорректный формат. Введите число.")
        process_min_price_input(message)

# Функция для получения основной клавиатуры
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = [KeyboardButton('/start'), KeyboardButton('/history'), KeyboardButton('/high'),
               KeyboardButton('/low'), KeyboardButton('/custom')]
    keyboard.add(*buttons)
    return keyboard

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=1)
