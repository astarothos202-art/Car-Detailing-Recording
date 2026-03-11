import json
import os
from datetime import datetime


class Database:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load()

    def load(self):
        """Загрузка данных"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save(self):
        """Сохранение данных"""
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_user_cars(self, user_id):
        """Получить авто пользователя"""
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {'cars': {}}
            self.save()
        return self.data[user_id]['cars']

    def add_car(self, user_id, name, mileage, purchase_date=None):
        """Добавить авто с датой покупки"""
        user_id = str(user_id)
        cars = self.get_user_cars(int(user_id))
        if name not in cars:
            car_data = {
                'mileage': mileage,
                'records': [],
                'created': datetime.now().strftime('%Y-%m-%d')
            }
            if purchase_date:
                car_data['purchase_date'] = purchase_date
            cars[name] = car_data
            self.save()
            return True
        return False

    def add_record(self, user_id, car_name, maint_type, mileage, notes, price=None, currency='uah'):
        """Добавить запись с ценой и валютой"""
        user_id = str(user_id)
        cars = self.get_user_cars(int(user_id))
        if car_name in cars:
            record = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'type': maint_type,
                'mileage': mileage,
                'notes': notes
            }
            if price is not None:
                record['price'] = price
                record['currency'] = currency
            cars[car_name]['records'].append(record)
            cars[car_name]['mileage'] = mileage
            self.save()
            return True
        return False

    def edit_record(self, user_id, car_name, record_index, field, value):
        """Редактировать запись"""
        user_id = str(user_id)
        cars = self.get_user_cars(int(user_id))
        if car_name in cars and 0 <= record_index < len(cars[car_name]['records']):
            if field == 'mileage' or field == 'price':
                try:
                    cars[car_name]['records'][record_index][field] = float(value) if field == 'price' else int(value)
                    if field == 'mileage':
                        cars[car_name]['mileage'] = int(value)
                except:
                    return False
            else:
                cars[car_name]['records'][record_index][field] = value
            self.save()
            return True
        return False

    def delete_record(self, user_id, car_name, record_index):
        """Удалить запись"""
        user_id = str(user_id)
        cars = self.get_user_cars(int(user_id))
        if car_name in cars and 0 <= record_index < len(cars[car_name]['records']):
            del cars[car_name]['records'][record_index]
            self.save()
            return True
        return False

    def delete_car(self, user_id, car_name):
        """Удалить авто"""
        try:
            user_id = str(user_id)
            if user_id not in self.data:
                return False
            cars = self.data[user_id].get('cars', {})
            if car_name in cars:
                del cars[car_name]
                self.data[user_id]['cars'] = cars
                self.save()
                return True
            return False
        except Exception as e:
            print(f"Ошибка в delete_car: {e}")
            return False


# Создаем глобальный экземпляр БД
db = Database('data/cars.json')