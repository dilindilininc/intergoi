# app/dbmanager.py
from bson.objectid import ObjectId
import config.config as conf
from pymongo import MongoClient

def get_db():
    client = MongoClient(conf.MONGOURI)
    return client[conf.DBNAME]

class DBManager:
    def __init__(self, db):
        self.db = db
        self.collection_officers = db['officers']
        self.collection_list = db['list']

    def find_officer_by_user_id(self, user_id):
        return self.db["officers"].find_one({"user_id": str(user_id)})

    def find_officer_by_id(self, officer_id):
        return self.collection_officers.find_one({"officer_id": officer_id})

    def add_goy(self, full_name, birth_date, reason):
        new_goy_id = self.db["list"].count_documents({}) + 1  # Уникальный ID для нового гоев
        self.db["list"].insert_one({
            "ID": new_goy_id,
            "FIO": full_name,
            "Birthday": birth_date,
            "Reason": reason
        })
        return new_goy_id

    def delete_goy(self, search_value):
        if isinstance(search_value, int):
            # Удаление по уникальному ID (предполагая, что это целое число)
            result = self.collection_list.delete_one({"ID": search_value})
            return result.deleted_count > 0
        elif isinstance(search_value, str):
            # Удаление по ФИО
            result = self.collection_list.delete_one({"FIO": search_value})
            return result.deleted_count > 0
        return False

    def find_goy_by_full_name(self, full_name):
        # Логика для поиска гоев по ФИО
        return self.collection_list.find_one({"FIO": full_name})

    def add_reason_to_goy(self, goy_id, reason):
        # Сначала получаем текущий документ
        existing_goy = self.collection_list.find_one({"_id": goy_id})

        # Проверяем, является ли поле Reason массивом
        if isinstance(existing_goy.get("Reason"), str):
            # Преобразуем строку в массив
            current_reasons = [existing_goy["Reason"]]
        else:
            current_reasons = existing_goy.get("Reason", [])

        # Добавляем новую причину
        current_reasons.append(reason)

        # Обновляем документ в базе данных
        self.collection_list.update_one(
            {"_id": goy_id},
            {
                "$set": {
                    "Reason": current_reasons  # Устанавливаем массив причин
                }
            }
        )
