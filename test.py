from pprint import pprint

import settings
from database import DataBase

database = DataBase(settings.MONGO_HOST, settings.MONGO_PORT)

reminder = {'user_id': 'DMASKDOQWEOMAKMWL231ML23KMSKLMFKLAMFSPLA112312313', 'title': 'ПОЙТИ В ДОДО',
            'todo': ['pizza', 'susi', 'starter']}

database.add_reminder(reminder)

pprint(database.get_users_collection())
pprint(database.get_relations_collection())
pprint(database.get_reminder_collection())
