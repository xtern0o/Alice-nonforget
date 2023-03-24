import pymongo
from bson import ObjectId

from settings import MONGO_DB


class DataBase:
    def __init__(self, client_host: str, client_port: int) -> None:
        self.client = pymongo.MongoClient(client_host, client_port)
        self.current_database = self.client[MONGO_DB]
        self.users_collection = self.current_database['users']
        self.reminder_collection = self.current_database['reminder']
        self.relations_collection = self.current_database['relations']

    def add_new_user(self, user_id: str) -> None:
        if not self.users_collection.find_one({'user_id': user_id}):
            self.users_collection.insert_one(
                {
                    'user_id': user_id,
                    'scenery': {
                        'state': '',
                        'stage': 0,
                    },
                }
            )
            self.relations_collection.insert_one(
                {
                    'user_id': user_id,
                    'reminders_ids': [],
                }
            )

    def get_state(self, user_id: str) -> str:
        return self.users_collection.find_one(
            {
                'user_id': user_id,
            }
        )['scenery']['state']

    def get_stage(self, user_id: str) -> str:
        return self.users_collection.find_one(
            {
                'user_id': user_id,
            }
        )['scenery']['stage']

    def set_state(self, user_id: str, state: str) -> None:
        self.users_collection.update_one(
            {
                'user_id': user_id,
            },
            {
                '$push': {
                    'scenery': {
                        'state': state,
                        'stage': self.get_stage(user_id),
                    },
                },
            }
        )

    def set_stage(self, user_id: str, stage: int) -> None:
        self.users_collection.update_one(
            {
                'user_id': user_id,
            },
            {
                '$push': {
                    'scenery': {
                        'state': self.get_state(user_id),
                        'stage': stage,
                    },
                },
            }
        )

    def add_reminder(self, reminder: dict) -> None:
        user_id = reminder['user_id']
        reminder_id = self.reminder_collection.insert_one(
            {
                'title': reminder['title'],
                'todo_list': reminder['todo_list'],
            }
        ).inserted_id
        self.relations_collection.update_one(
            {
                'user_id': user_id,
            },
            {
                '$push': {
                    'reminders_ids': reminder_id,
                },
            }
        )

    def get_reminders_ids(self, user_id: str) -> list:
        return list(self.relations_collection.find_one(
            {
                'user_id': user_id,
            },
        )['reminders_ids'])

    def delete_reminder(self, user_id: str, title: str) -> None:
        self.relations_collection.update_one(
            {
                'user_id': user_id
            },
            {
                '$pull': {
                    'reminders_ids': self.get_id_by_title(title),
                },
            }
        )
        self.reminder_collection.delete_one(
            {
                'title': title,
            }
        )

    def get_id_by_title(self, title: str) -> str:
        return self.reminder_collection.find_one(
            {
                'title': title,
            }
        )['_id']

    def get_reminders_titles(self, user_id: str) -> list:
        reminders_titles = list()
        for reminder_id in self.get_reminders_ids(user_id):
            reminders_titles.append(self.get_reminder_title(reminder_id))
        return reminders_titles

    def get_reminders_ids(self, user_id: str) -> list:
        return list(self.relations_collection.find_one(
            {
                'user_id': user_id,
            }
        )['reminders_ids'])

    def get_reminder_title(self, reminder_id: ObjectId) -> str:
        return self.reminder_collection.find_one(
            {
                '_id': reminder_id,
            }
        )['title']

    def get_todo_list(self, title: str) -> list:
        return self.reminder_collection.find_one(
            {
                'title': title,
            }
        )['todo_list']

    def get_users_collection(self) -> list:
        return list(self.users_collection.find())

    def get_relations_collection(self) -> list:
        return list(self.relations_collection.find())

    def get_reminder_collection(self) -> list:
        return list(self.reminder_collection.find())
