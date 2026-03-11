# Валюты
CURRENCIES = {
    'uah': '🇺🇦 Гривна (₴)',
    'usd': '🇺🇸 Доллар ($)',
    'eur': '🇪🇺 Евро (€)',
    'sek': '🇸🇪 Шведская крона (kr)'
}

# Расширенные типы деталей (18 видов)
MAINTENANCE_TYPES = {
    '1': {'name': '🛢️ Замена масла', 'icon': '🛢️'},
    '2': {'name': '🔧 Замена масляного фильтра', 'icon': '🔧'},
    '3': {'name': '💨 Замена воздушного фильтра', 'icon': '💨'},
    '4': {'name': '🚗 Замена салонного фильтра', 'icon': '🚗'},
    '5': {'name': '⛽ Замена топливного фильтра', 'icon': '⛽'},
    '6': {'name': '🛑 Замена тормозных колодок', 'icon': '🛑'},
    '7': {'name': '💧 Замена тормозной жидкости', 'icon': '💧'},
    '8': {'name': '❄️ Замена охлаждающей жидкости', 'icon': '❄️'},
    '9': {'name': '⚙️ Замена масла в КПП', 'icon': '⚙️'},
    '10': {'name': '⏱️ Замена ремня ГРМ', 'icon': '⏱️'},
    '11': {'name': '🔋 Замена аккумулятора', 'icon': '🔋'},
    '12': {'name': '🛞 Замена шин', 'icon': '🛞'},
    '13': {'name': '🔌 Свечи зажигания', 'icon': '🔌'},
    '14': {'name': '🔩 Амортизаторы', 'icon': '🔩'},
    '15': {'name': '⚡ Генератор/Стартер', 'icon': '⚡'},
    '16': {'name': '🌡️ Термостат/Радиатор', 'icon': '🌡️'},
    '17': {'name': '🔧 Ремонт подвески', 'icon': '🔧'},
    '18': {'name': '📌 Другое', 'icon': '📌'}
}


def get_type_name(type_code):
    """Получить название типа работы"""
    return MAINTENANCE_TYPES.get(type_code, {'name': type_code})['name']


def get_currency_symbol(currency_code):
    """Получить символ валюты"""
    symbols = {
        'uah': '₴',
        'usd': '$',
        'eur': '€',
        'sek': 'kr'
    }
    return symbols.get(currency_code, '₴')


def format_records(records):
    """Форматирование записей с ценами"""
    if not records:
        return "Нет записей"

    text = ""
    total_cost = 0
    total_by_currency = {}

    for i, record in enumerate(reversed(records[-20:]), 1):
        type_name = get_type_name(record['type'])
        text += f"{i}. {record['date']} - {type_name}\n"
        text += f"   Пробег: {record['mileage']} км\n"

        # Добавляем цену если есть
        if record.get('price'):
            price = record['price']
            currency = record.get('currency', 'uah')
            symbol = get_currency_symbol(currency)
            text += f"   💰 Цена: {price} {symbol}\n"

            # Считаем общую сумму по валютам
            if currency not in total_by_currency:
                total_by_currency[currency] = 0
            total_by_currency[currency] += price

        if record.get('notes'):
            text += f"   📝 {record['notes']}\n"
        text += "\n"

    # Добавляем итоговую сумму
    if total_by_currency:
        text += "💰 ИТОГО:\n"
        for currency, amount in total_by_currency.items():
            symbol = get_currency_symbol(currency)
            text += f"   {amount} {symbol}\n"

    return text


def validate_mileage(value):
    """Проверка пробега"""
    try:
        mileage = int(value)
        if mileage >= 0 and mileage < 999999:
            return mileage
        return None
    except:
        return None


def validate_price(value):
    """Проверка цены"""
    try:
        price = float(value)
        if price >= 0 and price < 9999999:
            return round(price, 2)
        return None
    except:
        return None