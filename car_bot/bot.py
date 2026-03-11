#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Car Maintenance Bot
Главный файл запуска
"""

import time
import urllib.request
import json
from config import BOT_TOKEN, DATA_FILE
from database import Database
from handlers import handle_callback, handle_message, handle_start

# Инициализация
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
db = Database(DATA_FILE)


def main():
    """Запуск бота"""
    # Проверка токена
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n" + "=" * 50)
        print("ОШИБКА: Токен не установлен!")
        print("Откройте config.py и вставьте токен:")
        print('BOT_TOKEN = "ваш_токен_здесь"')
        print("=" * 50 + "\n")
        return

    print("\n" + "=" * 50)
    print("🚗 Car Maintenance Bot")
    print("✅ Бот запущен!")
    print("=" * 50 + "\n")

    last_update_id = 0

    while True:
        try:
            # Получаем обновления
            url = f"{API_URL}/getUpdates?offset={last_update_id + 1}&timeout=30"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())

                if data['ok']:
                    for update in data['result']:
                        if 'callback_query' in update:
                            handle_callback(API_URL, update['callback_query'])
                        elif 'message' in update:
                            handle_message(API_URL, update['message'])

                        last_update_id = update['update_id']

            time.sleep(1)

        except KeyboardInterrupt:
            print("\n❌ Бот остановлен")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)


if __name__ == '__main__':
    main()