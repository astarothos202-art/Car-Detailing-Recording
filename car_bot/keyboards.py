def get_main_menu():
    """Главное меню"""
    return {
        'inline_keyboard': [
            [{'text': '🚗 Мои авто', 'callback_data': 'cars'}],
            [{'text': '➕ Добавить авто', 'callback_data': 'add_car'}],
            [{'text': '💰 Статистика расходов', 'callback_data': 'stats'}],
            [{'text': '❓ Помощь', 'callback_data': 'help'}]
        ]
    }

def get_car_menu(car_name):
    """Меню авто"""
    return {
        'inline_keyboard': [
            [{'text': '📝 Добавить запись', 'callback_data': f'add_record_{car_name}'}],
            [{'text': '📋 История', 'callback_data': f'records_{car_name}'}],
            [{'text': '✏️ Ред. записи', 'callback_data': f'edit_records_{car_name}'}],
            [{'text': '💰 Расходы', 'callback_data': f'expenses_{car_name}'}],
            [{'text': '❌ Удалить авто', 'callback_data': f'del_{car_name}'}],
            [{'text': '🔙 Назад', 'callback_data': 'cars'}]
        ]
    }

def get_maintenance_types(car_name):
    """Типы работ (18 видов)"""
    from utils import MAINTENANCE_TYPES
    keyboard = []
    for key, type_data in MAINTENANCE_TYPES.items():
        keyboard.append([{'text': type_data['name'], 'callback_data': f'type_{key}_{car_name}'}])
    keyboard.append([{'text': '🔙 Назад', 'callback_data': f'car_{car_name}'}])
    return {'inline_keyboard': keyboard}

def get_currencies_keyboard(car_name, maint_type, mileage, notes):
    """Клавиатура выбора валюты"""
    from utils import CURRENCIES
    keyboard = []
    for code, name in CURRENCIES.items():
        keyboard.append([{'text': name, 'callback_data': f'currency_{code}_{car_name}_{maint_type}_{mileage}_{notes}'}])
    keyboard.append([{'text': '⏭️ Пропустить (без цены)', 'callback_data': f'skip_price_{car_name}_{maint_type}_{mileage}_{notes}'}])
    return {'inline_keyboard': keyboard}

def get_edit_menu(car_name, records):
    """Меню редактирования записей"""
    keyboard = []
    start_idx = max(0, len(records) - 10)
    for i in range(start_idx, len(records)):
        record = records[i]
        date = record['date']
        type_display = get_type_short_name(record['type'])
        keyboard.append([{'text': f"{date} - {type_display}", 'callback_data': f'edit_record_{car_name}_{i}'}])
    keyboard.append([{'text': '🔙 Назад', 'callback_data': f'car_{car_name}'}])
    return {'inline_keyboard': keyboard}

def get_type_short_name(type_code):
    """Сокращенное название типа для меню"""
    from utils import MAINTENANCE_TYPES
    full_name = MAINTENANCE_TYPES.get(type_code, {'name': type_code})['name']
    return full_name[:15] + '...' if len(full_name) > 15 else full_name

def get_record_edit_menu(car_name, record_index):
    """Меню редактирования конкретной записи"""
    return {
        'inline_keyboard': [
            [{'text': '📅 Дата', 'callback_data': f'edit_field_{car_name}_{record_index}_date'}],
            [{'text': '📊 Пробег', 'callback_data': f'edit_field_{car_name}_{record_index}_mileage'}],
            [{'text': '🔧 Тип', 'callback_data': f'edit_field_{car_name}_{record_index}_type'}],
            [{'text': '💰 Цена', 'callback_data': f'edit_field_{car_name}_{record_index}_price'}],
            [{'text': '💱 Валюта', 'callback_data': f'edit_field_{car_name}_{record_index}_currency'}],
            [{'text': '📝 Заметки', 'callback_data': f'edit_field_{car_name}_{record_index}_notes'}],
            [{'text': '❌ Удалить', 'callback_data': f'delete_rec_{car_name}_{record_index}'}],
            [{'text': '🔙 Назад', 'callback_data': f'edit_records_{car_name}'}]
        ]
    }

def get_back_button(callback_data):
    """Кнопка назад"""
    return {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': callback_data}]]}