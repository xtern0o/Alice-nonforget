import pymorphy2
from flask import Flask, request, jsonify

import settings
from database import DataBase
from functions import send_help_message, create_buttons
from phrases import get_error_phrase, get_phrase
from states import States
from validators import check_line

app = Flask(__name__)

state = States()
database = DataBase(settings.MONGO_HOST, settings.MONGO_PORT)

morph = pymorphy2.MorphAnalyzer(lang="ru")
reminder_template = {}
POS_LIST = ['COMP', 'ADVB', 'NPRO', 'PRED', 'CONJ', 'PRCL', 'INTJ']


@app.route('/post', methods=['POST'])
def main():
    global reminder_template
    data = request.json
    session = data['session']
    version = data['version']
    if 'user' not in session.keys():
        answer_response = {
            "response": {
                'text': f"OK",
                'tts': f"OK"
            },
            "session": session,
            "version": version
        }
        return jsonify(answer_response)
    user_id = session['user']['user_id']
    command = data['request']['command']

    if command in ("стоп", "выход", "выйти", "пока"):
        state.set_exit()
        answer_response = {
            "response": {
                "text": get_phrase("EXIT", "stop")["text"],
                "tts": get_phrase("EXIT", "stop")["tts"],
                "buttons": []
            },
            "session": session,
            "version": version
        }
        answer_response = create_buttons(*[{"title": "Да", "hide": True}, {"title": "Нет", "hide": True}],
                                         **answer_response)
        state.set_stage(2)
        return jsonify(answer_response)

    if state.is_exit(2):
        if command == "да":
            answer_response = {
                "response": get_phrase("EXIT", "bye"),
                "session": session,
                "version": version
            }
            return answer_response
        if command == "нет":
            answer_response = {
                "response": {
                    "text": get_phrase("EXIT", "cancel")["text"],
                    "tts": get_phrase("EXIT", "cancel")["tts"],
                    'buttons': [
                        {
                            "title": "Создать",
                            "hide": True
                        },
                        {
                            "title": "Использовать",
                            "hide": True
                        },
                        {
                            "title": "Удалить",
                            "hide": True
                        },
                        {
                            "title": "Стоп",
                            "hide": True,
                        }
                    ]
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

    if session['new']:
        database.add_new_user(session['user']['user_id'])
        reminder_template[session['user']['user_id']] = {"title": "", "reminder_list": []}
        state.set_zero()

        answer_response = {
            "response": {
                'text': get_phrase(state.state, "zero")['text'],
                'tts': get_phrase(state.state, "zero")['tts'],
                'buttons': [
                    {
                        "title": "Создать",
                        "hide": True
                    },
                    {
                        "title": "Использовать",
                        "hide": True
                    },
                    {
                        "title": "Удалить",
                        "hide": True
                    },
                    {
                        "title": "Стоп",
                        "hide": False,
                    }
                ],
            },
            "session": session,
            "version": version
        }
        return jsonify(answer_response)

    if command in ("помощь", "что ты умеешь", "какие есть команды", "что делать"):
        state.set_zero()
        return send_help_message("test", "test", session, version)
    else:
        #  Начальное состояние Алисы
        if not (state.is_creating() or state.is_delete() or state.is_using()):
            if command == 'создать':
                state.set_creating(10)
                answer_response = {
                    "response": {
                        'text': get_phrase(state.get_state(), "start_message_alt")['text'],
                        'tts': get_phrase(state.get_state(), "start_message_alt")['tts']
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            if 'создать' in command:
                title_from_user = command.split('создать')
                reminder_template[user_id]['title'] = title_from_user[1]
                state.set_creating()
                answer_response = {
                    "response": {
                        'text': f"Создала напоминалку с названием {title_from_user[1]}. Всё верно?",
                        'tts': f"Создала напоминалку с названием {title_from_user[1]}. Всё верно?"
                    },
                    "session": session,
                    "version": version
                }
                state.set_creating()
                return jsonify(answer_response)

            if command == 'использовать':
                state.set_using(10)
                answer_response = {
                    "response": get_phrase(state.get_state(), "qwertyuiop"),
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            if 'использовать' in command:
                reminder_from_user = command.split()
                if len(reminder_from_user) != 1:
                    title = command.replace('использовать', '').replace('напоминалку', '').strip()
                    items = database.get_reminder_list(title)
                    reminder_template[user_id] = {}
                    reminder_template[user_id]['title'] = title
                    reminder_template[user_id]['reminder_list'] = items

                    answer_response = {
                        "response": {
                            'text': f"Напоминалка {reminder_from_user[1]}. Не забудьте: {', '.join(items)}. Мне повторить?",
                            'tts': f"Напоминалка {reminder_from_user[1]}. Не забудьте: {', '.join(items)}. Мне повторить?",
                            'buttons': [
                                {
                                    "title": "Да",
                                    "hide": True
                                },
                                {
                                    "title": "Нет",
                                    "hide": True
                                }
                            ],
                        },
                        "session": session,
                        "version": version
                    }
                    state.set_using()
                    return jsonify(answer_response)
                answer_response = {
                    "response": {
                        'text': f"Вы не назвали название напоминалки, которую хотите использовать",
                        'tts': f"Вы не назвали название напоминалки, которую хотите использовать"
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            if command == 'удалить':
                state.set_delete()
                answer_response = {
                    "response": {
                        'text': 'Назовите название напоминалки, которую вы хотите удалить',
                        'tts': 'Назовите название напоминалки, которую вы хотите удалить'
                    },

                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            answer_response = {
                "response": {
                    'text': get_phrase("ZERO", "zero")['text'],
                    'tts': get_phrase("ZERO", "zero")['tts'],
                    'buttons': [
                        {
                            "title": "Создать",
                            "hide": True
                        },
                        {
                            "title": "Использовать",
                            "hide": True
                        },
                        {
                            "title": "Удалить",
                            "hide": True
                        },
                        {
                            "title": "Стоп",
                            "hide": False,
                        }
                    ],
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        # Сценарий создания
        if state.is_creating(1):
            if check_line(command):
                answer_response = {
                    "response": {
                        'text': "Теперь перечислите всё, что вы бы не хотели забыть.",
                        'tts': "Теперь перечислите всё, что вы бы не хотели забыть.",
                    },

                    "session": session,
                    "version": version
                }
                state.set_stage(2)
                return jsonify(answer_response)

        if state.is_creating(2):
            if command:
                words_of_user = set([word for word in command.split() if morph.parse(word)[0].tag.POS not in POS_LIST])
                [reminder_template[user_id]["reminder_list"].append(word) for word in words_of_user]
                database.add_reminder(user_id, reminder_template)
                answer_response = {
                    "response": {
                        'text': "Отлично! Теперь вы можете использовать напоминалку когда захотите.",
                        'tts': "Отлично! Теперь вы можете использовать напоминалку когда захотите.",
                    },
                    "session": session,
                    "version": version
                }
                state.set_zero()
                reminder_template.pop(user_id)
                return jsonify(answer_response)

            answer_response = {
                "response": {
                    'text': get_error_phrase()["text"],
                    'tts': get_error_phrase()["tts"],
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        if state.is_creating(10):
            if command:
                reminder_template[user_id]["title"] = command
                answer_response = {
                    "response": {
                        'text': get_phrase(state.get_state(), "first_stage_alt")['text'].format(command),
                        'tts': get_phrase(state.get_state(), "first_stage_alt")['tts'].format(command),
                        "buttons": [
                            {
                                "title": "Да",
                                "hide": True
                            },
                            {
                                "title": "Нет",
                                "hide": True
                            }
                        ]
                    },
                    "session": session,
                    "version": version
                }
                state.set_stage(11)
                return jsonify(answer_response)
            answer_response = {
                "response": {
                    'text': get_error_phrase()["text"],
                    'tts': get_error_phrase()["tts"],
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        if state.is_creating(11):
            if command == "да":
                answer_response = {
                    "response": {
                        'text': "Теперь перечислите всё, что вы бы не хотели забыть.",
                        'tts': "Теперь перечислите всё, что вы бы не хотели забыть.",
                    },
                    "session": session,
                    "version": version
                }
                state.set_stage(2)
                return jsonify(answer_response)
            if command == "нет":
                answer_pesponse = {
                    "response": {
                        "text": "Хорошо, повторите ввод",
                        "tts": "Поняла, повторите название"
                    },
                    "version": version,
                    "session": session
                }
                state.set_stage(10)
                return jsonify(answer_pesponse)

        # Сценарий удаления
        if state.is_delete(1):
            if command in database.get_reminders_titles(user_id):
                reminder_template[user_id]["title"] = command
                answer_response = {
                    "response": {
                        "text": f'Вы уверены что хотите удалить напоминалку {command}?',
                        "tts": f'Вы уверены что хотите удалить напоминалку {command}?',
                        "buttons": [
                            {
                                "title": "Да",
                                "hide": True
                            },
                            {
                                "title": "Нет",
                                "hide": True
                            }
                        ]
                    },
                    "session": session,
                    "version": version
                }

                state.set_stage(2)
                return jsonify(answer_response)

            answer_response = {
                "response": {
                    'text': get_error_phrase("not_found_error")["text"].format(command),
                    'tts': get_error_phrase("not_found_error")["tts"].format(command),
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        if state.is_delete(2):
            if check_line(command):
                answer_response = {
                    "response": {
                        "text": f'Напоминалка {reminder_template[user_id]["title"]} удалена',
                        "tts": f'Напоминалка {reminder_template[user_id]["title"]} удалена',
                        'buttons': [
                            {
                                "title": "Создать",
                                "hide": True
                            },
                            {
                                "title": "Использовать",
                                "hide": True
                            },
                            {
                                "title": "Удалить",
                                "hide": True
                            },
                            {
                                "title": "Стоп",
                                "hide": False,
                            }
                        ],
                    },
                    "session": session,
                    "version": version
                }

                database.delete_reminder(user_id, reminder_template[user_id]["title"])
                state.set_zero()
                return jsonify(answer_response)

            if not check_line(command):
                answer_response = {
                    "response": {
                        "text": get_phrase(state.get_state(), "first_stage_disagree")["text"],
                        "tts": get_phrase(state.get_state(), "first_stage_disagree")["tts"],
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            answer_response = {
                "response": {
                    get_error_phrase()
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        # если пользователь решит повторить список айтемов, мб стоит сделать по-другому, не меняя стейж
        if state.is_using(1):
            if check_line(command):
                items = reminder_template[user_id]['reminder_list']
                answer_response = {
                    "response": {
                        "text": get_phrase(state.get_state(), "first_stage")["text"].format(", ".join(items)),
                        "tts": get_phrase(state.get_state(), "first_stage")["tts"].format(", ".join(items)),
                        'buttons': [
                            {
                                "title": "Да",
                                "hide": True
                            },
                            {
                                "title": "Нет",
                                "hide": True
                            }
                        ],
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)
            answer_response = {
                "response": get_phrase(state.get_state(), "first_stage_disagree"),
                "session": session,
                "version": version
            }
            state.set_zero()
            return jsonify(answer_response)

        if state.is_using(10):
            pass


if __name__ == '__main__':
    app.run(port=6000, debug=True)
