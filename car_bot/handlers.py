import json
import urllib.request
import urllib.parse
from database import db
from keyboards import *
from utils import format_records, get_type_name, validate_mileage, validate_price, get_currency_symbol

# Хранилища состояний
user_states = {}
user_data = {}


def send_message(api_url, chat_id, text, keyboard=None):
    """Отправка сообщения"""
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if keyboard:
        data['reply_markup'] = json.dumps(keyboard)

    data_bytes = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(f"{api_url}/sendMessage", data=data_bytes, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False


def edit_message(api_url, chat_id, message_id, text, keyboard=None):
    """Редактирование сообщения"""
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if keyboard:
        data['reply_markup'] = json.dumps(keyboard)

    data_bytes = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(f"{api_url}/editMessageText", data=data_bytes, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print(f"Ошибка редактирования: {e}")
        return False


def answer_callback(api_url, callback_id):
    """Ответ на callback"""
    try:
        urllib.request.urlopen(f"{api_url}/answerCallbackQuery?callback_query_id={callback_id}")
    except:
        pass


def handle_start(api_url, chat_id):
    """Обработка /start"""
    welcome_text = (
        "🚗 Добро пожаловать в бот учета обслуживания автомобиля!\n\n"
        "Я помогу отслеживать:\n"
        "• Все работы по авто\n"
        "• Расходы в разных валютах (₴, $, €, kr)\n"
        "• Дату покупки авто\n"
        "• Историю обслуживания\n\n"
        "Выберите действие в меню:"
    )
    send_message(api_url, chat_id, welcome_text, get_main_menu())


def get_car_expenses(car_name, records):
    """Получить расходы по автомобилю"""
    if not records:
        return "Нет записей"

    text = f"💰 РАСХОДЫ ПО {car_name}\n\n"
    total_by_currency = {}

    for i, record in enumerate(records, 1):
        if record.get('price'):
            type_name = get_type_name(record['type'])
            currency = record.get('currency', 'uah')
            price = record['price']
            symbol = get_currency_symbol(currency)
            text += f"{i}. {record['date']} - {type_name}\n"
            text += f"   {price} {symbol}\n"

            if currency not in total_by_currency:
                total_by_currency[currency] = 0
            total_by_currency[currency] += price

    if total_by_currency:
        text += "\n💰 ВСЕГО:\n"
        for currency, amount in total_by_currency.items():
            symbol = get_currency_symbol(currency)
            text += f"   {amount} {symbol}\n"
    else:
        text += "Нет расходов"

    return text


def get_total_expenses(user_id):
    """Получить общие расходы пользователя"""
    cars = db.get_user_cars(user_id)
    if not cars:
        return "Нет авто для статистики"

    text = "💰 ОБЩАЯ СТАТИСТИКА РАСХОДОВ\n\n"
    total_by_currency = {}

    for car_name, car_data in cars.items():
        text += f"🚗 {car_name}:\n"
        car_total = {}
        for record in car_data.get('records', []):
            if record.get('price'):
                currency = record.get('currency', 'uah')
                price = record['price']
                if currency not in car_total:
                    car_total[currency] = 0
                car_total[currency] += price

                if currency not in total_by_currency:
                    total_by_currency[currency] = 0
                total_by_currency[currency] += price

        if car_total:
            for currency, amount in car_total.items():
                symbol = get_currency_symbol(currency)
                text += f"   {amount} {symbol}\n"
        else:
            text += "   Нет расходов\n"
        text += "\n"

    if total_by_currency:
        text += "💰 ИТОГО ПО ВСЕМ АВТО:\n"
        for currency, amount in total_by_currency.items():
            symbol = get_currency_symbol(currency)
            text += f"   {amount} {symbol}\n"

    return text


def handle_callback(api_url, callback):
    """Обработка callback запросов"""
    callback_id = callback['id']
    chat_id = callback['message']['chat']['id']
    message_id = callback['message']['message_id']
    user_id = callback['from']['id']
    data = callback['data']

    answer_callback(api_url, callback_id)

    # Главное меню
    if data == 'main_menu':
        edit_message(api_url, chat_id, message_id, "🚗 Главное меню", get_main_menu())

    # Статистика расходов
    elif data == 'stats':
        text = get_total_expenses(user_id)
        edit_message(api_url, chat_id, message_id, text,
                     {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': 'main_menu'}]]})

    # Мои автомобили
    elif data == 'cars':
        cars = db.get_user_cars(user_id)
        if not cars:
            edit_message(api_url, chat_id, message_id,
                         "У вас пока нет автомобилей.",
                         {'inline_keyboard': [
                             [{'text': '➕ Добавить авто', 'callback_data': 'add_car'}],
                             [{'text': '🔙 Главное меню', 'callback_data': 'main_menu'}]
                         ]})
            return

        text = "🚗 Ваши автомобили:\n\n"
        keyboard = {'inline_keyboard': []}
        for car_name, car_data in cars.items():
            purchase_info = ""
            if car_data.get('purchase_date'):
                purchase_info = f" (с {car_data['purchase_date']})"
            text += f"• {car_name}{purchase_info}\n"
            text += f"  Пробег: {car_data['mileage']} км\n"
            text += f"  Записей: {len(car_data['records'])}\n\n"
            keyboard['inline_keyboard'].append([{'text': f"🚗 {car_name}", 'callback_data': f'car_{car_name}'}])

        keyboard['inline_keyboard'].append([{'text': '➕ Добавить авто', 'callback_data': 'add_car'}])
        keyboard['inline_keyboard'].append([{'text': '🔙 Главное меню', 'callback_data': 'main_menu'}])
        edit_message(api_url, chat_id, message_id, text, keyboard)

    # Добавление авто
    elif data == 'add_car':
        user_states[user_id] = 'add_car_name'
        edit_message(api_url, chat_id, message_id,
                     "Введите название автомобиля:",
                     {'inline_keyboard': [[{'text': '🔙 Отмена', 'callback_data': 'cars'}]]})

    # Помощь
    elif data == 'help':
        help_text = (
            "❓ ПОМОЩЬ\n\n"
            "Команды:\n"
            "/start - Начать работу\n\n"
            "Возможности:\n"
            "• Добавление авто с датой покупки\n"
            "• Запись работ с ценами в разных валютах\n"
            "• Просмотр истории и расходов\n"
            "• Редактирование записей\n\n"
            "Поддерживаемые валюты:\n"
            "🇺🇦 Гривна (₴)\n"
            "🇺🇸 Доллар ($)\n"
            "🇪🇺 Евро (€)\n"
            "🇸🇪 Шведская крона (kr)"
        )
        edit_message(api_url, chat_id, message_id, help_text,
                     {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': 'main_menu'}]]})

    # Меню конкретного авто
    elif data.startswith('car_'):
        car_name = data[4:]
        cars = db.get_user_cars(user_id)
        if car_name not in cars:
            edit_message(api_url, chat_id, message_id, "Автомобиль не найден",
                         {'inline_keyboard': [[{'text': '🔙 К списку', 'callback_data': 'cars'}]]})
            return

        car_data = cars[car_name]
        text = f"🚗 {car_name}\n"
        if car_data.get('purchase_date'):
            text += f"📅 Куплен: {car_data['purchase_date']}\n"
        text += f"📊 Текущий пробег: {car_data['mileage']} км\n"
        text += f"📝 Всего записей: {len(car_data['records'])}\n"

        edit_message(api_url, chat_id, message_id, text, get_car_menu(car_name))

    # Расходы по конкретному авто
    elif data.startswith('expenses_'):
        car_name = data[9:]
        cars = db.get_user_cars(user_id)
        records = cars.get(car_name, {}).get('records', [])
        text = get_car_expenses(car_name, records)
        edit_message(api_url, chat_id, message_id, text,
                     {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': f'car_{car_name}'}]]})

    # Добавление записи
    elif data.startswith('add_record_'):
        car_name = data[11:]
        user_data[user_id] = {'car': car_name}
        edit_message(api_url, chat_id, message_id, "Выберите тип работ:", get_maintenance_types(car_name))

    # Выбор типа работ
    elif data.startswith('type_'):
        parts = data.split('_')
        type_code = parts[1]
        car_name = '_'.join(parts[2:])
        user_data[user_id] = {'car': car_name, 'type': type_code}
        user_states[user_id] = 'add_record_mileage'
        edit_message(api_url, chat_id, message_id, "Введите текущий пробег (км):")

    # Просмотр записей
    elif data.startswith('records_'):
        car_name = data[8:]
        cars = db.get_user_cars(user_id)
        records = cars.get(car_name, {}).get('records', [])
        text = format_records(records)
        if not records:
            text = f"У автомобиля {car_name} пока нет записей."
        edit_message(api_url, chat_id, message_id, text,
                     {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': f'car_{car_name}'}]]})

    # Редактирование записей (список)
    elif data.startswith('edit_records_'):
        car_name = data[13:]
        cars = db.get_user_cars(user_id)
        records = cars.get(car_name, {}).get('records', [])
        if not records:
            edit_message(api_url, chat_id, message_id, "Нет записей для редактирования",
                         {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': f'car_{car_name}'}]]})
        else:
            edit_message(api_url, chat_id, message_id, "Выберите запись для редактирования:",
                         get_edit_menu(car_name, records))

    # Редактирование конкретной записи
    elif data.startswith('edit_record_'):
        parts = data.split('_')
        car_name = parts[2]
        record_index = int(parts[3])
        cars = db.get_user_cars(user_id)
        records = cars.get(car_name, {}).get('records', [])

        if 0 <= record_index < len(records):
            record = records[record_index]
            text = f"📝 Запись #{record_index + 1}\n"
            text += f"📅 Дата: {record['date']}\n"
            text += f"🔧 Тип: {get_type_name(record['type'])}\n"
            text += f"📊 Пробег: {record['mileage']} км\n"
            if record.get('price'):
                currency = record.get('currency', 'uah')
                symbol = get_currency_symbol(currency)
                text += f"💰 Цена: {record['price']} {symbol}\n"
            if record.get('notes'):
                text += f"📝 Заметки: {record['notes']}"

            edit_message(api_url, chat_id, message_id, text, get_record_edit_menu(car_name, record_index))
        else:
            edit_message(api_url, chat_id, message_id, "Запись не найдена",
                         {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': f'edit_records_{car_name}'}]]})

    # Редактирование поля записи
    elif data.startswith('edit_field_'):
        parts = data.split('_')
        car_name = parts[2]
        record_index = int(parts[3])
        field = parts[4]
        user_data[user_id] = {'car': car_name, 'index': record_index, 'field': field}
        user_states[user_id] = 'edit_record'

        field_names = {
            'date': 'дату (ГГГГ-ММ-ДД)',
            'mileage': 'пробег',
            'type': 'тип работ',
            'price': 'цену',
            'currency': 'валюту (uah/usd/eur/sek)',
            'notes': 'заметки'
        }
        edit_message(api_url, chat_id, message_id,
                     f"Введите новое значение для поля '{field_names.get(field, field)}':")

    # Удаление записи
    elif data.startswith('delete_rec_'):
        parts = data.split('_')
        car_name = parts[2]
        record_index = int(parts[3])

        keyboard = {
            'inline_keyboard': [
                [{'text': '✅ Да', 'callback_data': f'confirm_delete_rec_{car_name}_{record_index}'},
                 {'text': '❌ Нет', 'callback_data': f'edit_record_{car_name}_{record_index}'}]
            ]
        }
        edit_message(api_url, chat_id, message_id, "Удалить эту запись?", keyboard)

    # Подтверждение удаления записи
    elif data.startswith('confirm_delete_rec_'):
        parts = data.split('_')
        car_name = parts[3]
        record_index = int(parts[4])

        if db.delete_record(user_id, car_name, record_index):
            edit_message(api_url, chat_id, message_id, "✅ Запись удалена",
                         {'inline_keyboard': [
                             [{'text': '🔙 К списку записей', 'callback_data': f'edit_records_{car_name}'}]]})
        else:
            edit_message(api_url, chat_id, message_id, "❌ Ошибка при удалении",
                         {'inline_keyboard': [
                             [{'text': '🔙 Назад', 'callback_data': f'edit_record_{car_name}_{record_index}'}]]})

    # Выбор валюты для цены
    elif data.startswith('currency_'):
        parts = data.split('_')
        currency = parts[1]
        car_name = parts[2]
        maint_type = parts[3]
        mileage = int(parts[4])
        notes = parts[5] if len(parts) > 5 else ''

        # Получаем цену из сохраненных данных
        price = user_data.get(user_id, {}).get('price')

        if price and db.add_record(user_id, car_name, maint_type, mileage, notes, price, currency):
            symbol = get_currency_symbol(currency)
            send_message(api_url, chat_id,
                         f"✅ Запись добавлена!\n💰 Цена: {price} {symbol}",
                         {'inline_keyboard': [[{'text': '🔙 К автомобилю', 'callback_data': f'car_{car_name}'}]]})
        else:
            send_message(api_url, chat_id, "❌ Ошибка при добавлении записи",
                         {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': f'car_{car_name}'}]]})

        del user_states[user_id]
        del user_data[user_id]

    # Пропустить цену
    elif data.startswith('skip_price_'):
        parts = data.split('_')
        car_name = parts[2]
        maint_type = parts[3]
        mileage = int(parts[4])
        notes = parts[5] if len(parts) > 5 else ''

        if db.add_record(user_id, car_name, maint_type, mileage, notes):
            send_message(api_url, chat_id, "✅ Запись добавлена без цены",
                         {'inline_keyboard': [[{'text': '🔙 К автомобилю', 'callback_data': f'car_{car_name}'}]]})
        else:
            send_message(api_url, chat_id, "❌ Ошибка при добавлении записи",
                         {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': f'car_{car_name}'}]]})

        del user_states[user_id]
        del user_data[user_id]

    # Удаление авто
    elif data.startswith('del_'):
        car_name = data[4:]
        keyboard = {
            'inline_keyboard': [
                [{'text': '✅ Да', 'callback_data': f'yes_del_{car_name}'},
                 {'text': '❌ Нет', 'callback_data': f'car_{car_name}'}]
            ]
        }
        edit_message(api_url, chat_id, message_id,
                     f"Точно удалить {car_name}?", keyboard)

    elif data.startswith('yes_del_'):
        car_name = data[8:]
        try:
            if db.delete_car(user_id, car_name):
                edit_message(api_url, chat_id, message_id,
                             f"✅ {car_name} удален",
                             {'inline_keyboard': [[{'text': '🔙 К списку', 'callback_data': 'cars'}]]})
            else:
                edit_message(api_url, chat_id, message_id,
                             f"❌ Ошибка",
                             {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': f'car_{car_name}'}]]})
        except Exception as e:
            edit_message(api_url, chat_id, message_id,
                         f"❌ Ошибка: {e}",
                         {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': 'cars'}]]})


def handle_message(api_url, message):
    """Обработка текстовых сообщений"""
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    text = message.get('text', '')

    # Команда /start
    if text == '/start':
        handle_start(api_url, chat_id)
        return

    # Обработка состояний
    if user_id in user_states:
        state = user_states[user_id]

        # Добавление названия авто
        if state == 'add_car_name':
            user_data[user_id] = {'name': text}
            user_states[user_id] = 'add_car_mileage'
            send_message(api_url, chat_id, "Введите текущий пробег (км):")

        # Добавление пробега авто
        elif state == 'add_car_mileage':
            mileage = validate_mileage(text)
            if mileage is not None:
                user_data[user_id]['mileage'] = mileage
                user_states[user_id] = 'add_car_date'
                send_message(api_url, chat_id, "Введите дату покупки (ГГГГ-ММ-ДД) или отправьте '-' если не знаете:")
            else:
                send_message(api_url, chat_id, "❌ Введите корректное число!")

        # Добавление даты покупки авто
        elif state == 'add_car_date':
            car_name = user_data[user_id]['name']
            mileage = user_data[user_id]['mileage']

            if text == '-':
                if db.add_car(user_id, car_name, mileage):
                    send_message(api_url, chat_id, f"✅ Автомобиль {car_name} добавлен!",
                                 {'inline_keyboard': [[{'text': '🔙 В меню', 'callback_data': 'main_menu'}]]})
                else:
                    send_message(api_url, chat_id, "❌ Автомобиль уже существует")
            else:
                # Проверяем формат даты
                try:
                    # Простая проверка формата
                    if len(text) == 10 and text[4] == '-' and text[7] == '-':
                        if db.add_car(user_id, car_name, mileage, text):
                            send_message(api_url, chat_id, f"✅ Автомобиль {car_name} добавлен с датой {text}!",
                                         {'inline_keyboard': [[{'text': '🔙 В меню', 'callback_data': 'main_menu'}]]})
                        else:
                            send_message(api_url, chat_id, "❌ Автомобиль уже существует")
                    else:
                        send_message(api_url, chat_id, "❌ Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                except:
                    send_message(api_url, chat_id, "❌ Неверный формат даты!")

            del user_states[user_id]
            del user_data[user_id]

        # Добавление пробега для записи
        elif state == 'add_record_mileage':
            mileage = validate_mileage(text)
            if mileage is not None:
                user_data[user_id]['mileage'] = mileage
                user_states[user_id] = 'add_record_notes'
                send_message(api_url, chat_id, "Введите заметки (или отправьте '-' если не нужно):")
            else:
                send_message(api_url, chat_id, "❌ Введите корректное число!")

        # Добавление заметок для записи
        elif state == 'add_record_notes':
            notes = text if text != '-' else ''
            user_data[user_id]['notes'] = notes
            user_states[user_id] = 'add_record_price'
            send_message(api_url, chat_id, "Введите цену (число) или отправьте '-' чтобы пропустить:")

        # Добавление цены для записи
        elif state == 'add_record_price':
            data = user_data.get(user_id, {})
            car_name = data.get('car')
            maint_type = data.get('type')
            mileage = data.get('mileage')
            notes = data.get('notes', '')

            if text == '-':
                # Пропускаем цену
                if db.add_record(user_id, car_name, maint_type, mileage, notes):
                    send_message(api_url, chat_id, "✅ Запись добавлена без цены!",
                                 {'inline_keyboard': [
                                     [{'text': '🔙 К автомобилю', 'callback_data': f'car_{car_name}'}]]})
                else:
                    send_message(api_url, chat_id, "❌ Ошибка при добавлении записи",
                                 {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': f'car_{car_name}'}]]})
                del user_states[user_id]
                del user_data[user_id]
            else:
                price = validate_price(text)
                if price is not None:
                    user_data[user_id]['price'] = price
                    # Показываем выбор валюты
                    from keyboards import get_currencies_keyboard
                    keyboard = get_currencies_keyboard(car_name, maint_type, mileage, notes)
                    send_message(api_url, chat_id, "Выберите валюту:", keyboard)
                else:
                    send_message(api_url, chat_id, "❌ Введите корректную цену (число)!")

        # Редактирование записи
        elif state == 'edit_record':
            data = user_data.get(user_id, {})
            car_name = data.get('car')
            record_index = data.get('index')
            field = data.get('field')

            if field == 'mileage' or field == 'price':
                value = validate_price(text) if field == 'price' else validate_mileage(text)
                if value is None:
                    send_message(api_url, chat_id, f"❌ Введите число!")
                    return
            else:
                value = text

            if db.edit_record(user_id, car_name, record_index, field, value):
                send_message(api_url, chat_id, "✅ Запись обновлена!",
                             {'inline_keyboard': [
                                 [{'text': '🔙 К записи', 'callback_data': f'edit_record_{car_name}_{record_index}'}]]})
            else:
                send_message(api_url, chat_id, "❌ Ошибка при обновлении",
                             {'inline_keyboard': [
                                 [{'text': '🔙 Назад', 'callback_data': f'edit_record_{car_name}_{record_index}'}]]})

            del user_states[user_id]
            del user_data[user_id]

    else:
        # Если нет состояния - показываем главное меню
        send_message(api_url, chat_id, "Используйте кнопки меню или команду /start", get_main_menu())