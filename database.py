import pymongo

from settings import MONGO_DB


class DataBase:
    def __init__(self, client_host, client_port):
        self.client = pymongo.MongoClient(client_host, client_port)
        self.current_database = self.client[MONGO_DB]
        self.users_collection = self.current_database["users"]
        self.skills_collection = self.current_database["skills"]
        self.relations_collection = self.current_database["relations"]

    def add_new_user(self, user_id):
        if not self.users_collection.find_one({"user_id": user_id}):
            self.users_collection.insert_one({"user_id": user_id})

    def get_id_by_user_id(self, user_id):
        self.users_collection.find_one({"user_id": user_id})

    def add_skills(self, id, skill_name):
        self.skills_collection.insert_one({skill_name: id})