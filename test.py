from pprint import pprint

import settings
from database import DataBase

database = DataBase(settings.MONGO_HOST, settings.MONGO_PORT)

# database.add_new_user("GOKDSKKFSOFKSEOPFKWEOFKSFPOWKE")
#
# reminder = {'user_id': 'GOKDSKKFSOFKSEOPFKWEOFKSFPOWKE', 'title': 'ПОЙТИ В ДОДО',
#             'todo': ['pizza', 'susi', 'starter']}
# database.add_reminder(reminder)
#
# reminder = {'user_id': 'GOKDSKKFSOFKSEOPFKWEOFKSFPOWKE', 'title': 'кофе купить',
#             'todo': ['Вещи', 'рок', 'поп']}
# database.add_reminder(reminder)

pprint(database.get_users_collection())
pprint(database.get_relations_collection())
pprint(database.get_reminder_collection())
