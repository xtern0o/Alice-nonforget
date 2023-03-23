import pymongo

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
                '$set': {
                    'user_id': user_id,
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
                '$set': {
                    'user_id': user_id,
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
                'todo': reminder['todo'],
            }
        ).inserted_id
        self.relations_collection.update_one(
            {
                'user_id': user_id,
            },
            {
                '$set': {
                    'user_id': user_id,
                    'reminders_ids': self.get_reminders_ids(user_id).append(reminder_id),
                },
            }
        )

    def get_reminders_ids(self, user_id: str) -> list:
        return self.relations_collection.find_one(
            {
                'user_id': user_id
            }
        )['reminders_ids']

    def get_users_collection(self) -> list:
        return list(self.users_collection.find())

    def get_relations_collection(self) -> list:
        return list(self.relations_collection.find())

    def get_reminder_collection(self) -> list:
        return list(self.reminder_collection.find())
