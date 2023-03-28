from flask import Flask, request, jsonify
from phrases import get_error_phrase, get_phrase

import settings
from database import DataBase
from states import States
from validators import check_line

app = Flask(__name__)

state = States()
database = DataBase(settings.MONGO_HOST, settings.MONGO_PORT)

reminder_template = {}


@app.route('/post', methods=['POST'])
def main():
    global reminder_template
    data = request.json
    session = data['session']
    version = data['version']
    user_id = session['user']['user_id']
    command = data['request']['command']

    try:

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
                            "title": "СТОП",
                            "hide": False,
                        }
                    ],
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        if command in ("стоп", "выход", "выйти", "пока"):
            state.set_exit()
            answer_response = {
                "response": {
                    "text": get_phrase("EXIT", "stop")["text"],
                    "tts": get_phrase("EXIT", "stop")["tts"],
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
                                "title": "СТОП",
                                "hide": False,
                            }
                        ]
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)


        if (state.is_delete(1) or state.is_using(1)) and command == "назад":
            state.set_zero()
            answer_response = {
                "response": {
                    "text": get_phrase(state.get_state(), "restart")["text"],
                    "tts": get_phrase(state.get_state(), "restart")["tts"],
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
                        }
                    ],
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        #  Начальное состояние Алисы
        if not (state.is_creating() or state.is_delete() or state.is_using()):
            if command == 'создать':
                state.set_creating()
                answer_response = {
                    "response": {
                        'text': get_phrase(state.get_state(), "start_message")['text'],
                        'tts': get_phrase(state.get_state(), "start_message")['tts']
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            if command == 'использовать':
                state.set_using()
                answer_response = {
                    "response": {
                        'text': get_phrase(state.get_state(), "start_message")['text'].format(", ".join(database.get_reminders_titles(user_id))),
                        'tts': get_phrase(state.get_state(), "start_message")['tts'].format(", ".join(database.get_reminders_titles(user_id)))
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            if command == 'удалить':
                state.set_delete()
                answer_response = {
                    "response": {
                        'text': get_phrase(state.get_state(), "start_message")['text'],
                        'tts': get_phrase(state.get_state(), "start_message")['tts']
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            answer_response = {
                "response": {
                    'text': get_phrase(state.get_state(), "first_stage")['text'],
                    'tts': get_phrase(state.get_state(), "first_stage")['tts']
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        # Сценарий создания
        if state.is_creating(1):
            if command:
                reminder_template[user_id]["title"] = command
                answer_response = {
                    "response": {
                        'text': get_phrase(state.get_state(), "first_stage")['text'].format(command),
                        'tts': get_phrase(state.get_state(), "first_stage")['tts'].format(command),
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
                    'text': get_error_phrase()["text"],
                    'tts': get_error_phrase()["tts"],
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        if state.is_creating(2):
            if check_line(command):
                answer_response = {
                    "response": {
                        "text": get_phrase(state.get_state(),
                                           "second_stage")["text"].format(reminder_template[user_id]["title"]),
                        "tts": get_phrase(state.get_state(),
                                           "second_stage")["tts"].format(reminder_template[user_id]["title"]),
                    },
                    "session": session,
                    "version": version
                }
                state.set_stage(3)
                return jsonify(answer_response)

            if not check_line(command):
                answer_response = {
                    "response": get_phrase(state.get_state(), "first_stage_disagree"),
                    "session": session,
                    "version": version
                }
                state.set_stage(1)
                return jsonify(answer_response)

        if state.is_creating(3):
            if command:
                if command != 'всё':
                    item = command
                    reminder_template[user_id]["reminder_list"].append(item)
                    answer_response = {
                        "response": get_phrase(state.get_state(), "third_stage_items"),
                        "session": session,
                        "version": version
                    }
                    return jsonify(answer_response)

                if reminder_template[user_id]["reminder_list"]:
                    database.add_reminder(user_id, reminder_template)
                    state.set_stage(4)
                    answer_response = {
                        "response": {
                            "text": get_phrase(state.get_state(), "third_stage_finish")["text"],
                            "tts": get_phrase(state.get_state(), "third_stage_finish")["tts"],
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
                                }
                            ],
                        },
                        "session": session,
                        "version": version
                    }
                    state.set_zero()
                    return jsonify(answer_response)
                answer_response = {
                    "response": get_error_phrase("empty_error"),
                    "version": version,
                    "session": session
                }
                return jsonify(answer_response)

            answer_response = {
                "response": get_error_phrase(),
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        # Сценарий удаления
        if state.is_delete(1):
            if command in database.get_reminders_titles(user_id):
                reminder_template[user_id]["title"] = command
                answer_response = {
                    "response": {
                        "text": get_phrase(state.get_state(), "first_stage")["text"].format(reminder_template[user_id]["title"]),
                        "tts": get_phrase(state.get_state(), "first_stage")["tts"].format(reminder_template[user_id]["title"]),
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
                    'buttons': [
                        {
                            "title": "назад",
                            "hide": True
                        }
                    ]
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        if state.is_delete(2):
            if check_line(command):
                answer_response = {
                    "response": {
                        "text": get_phrase(state.get_state(), "second_stage")["text"].format("text"),
                        "tts": get_phrase(state.get_state(), "second_stage")["tts"].format("text"),
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
                            }
                        ],
                    },
                    "session": session,
                    "version": version
                }

                database.delete_reminder(user_id, reminder_template["title"])

                database.delete_reminder(user_id, reminder_template[user_id]["title"])
                state.set_zero()
                return jsonify(answer_response)

            if not check_line(command):
                answer_response = {
                    "response": {
                        "text": get_phrase(state.get_state(), "first_stage_disagree")["text"],
                        "tts": get_phrase(state.get_state(), "first_stage_disagree")["tts"],
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
                            }
                        ],
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            answer_response = {
                "response": get_error_phrase(),
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        # тут обработка начального состояния, без доп. проверок.
        if state.is_using(1):
            if command in database.get_reminders_titles(user_id):
                reminder_template[user_id]["title"] = command

                # тут уже вывод всех айтемов пользователя
                title = reminder_template[user_id]["title"]
                items = database.get_reminder_list(title)
                answer_response = {
                    "response": {
                        "text": get_phrase(state.get_state(), "first_stage")["text"].format(title, ", ".join(items)),
                        "tts": get_phrase(state.get_state(), "first_stage")["tts"].format(title, ", ".join(items)),
                        'buttons': [
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
            return jsonify(
                {
                    "response": {
                        "text": get_error_phrase("not_found_error")["text"].format(command),
                        "tts": get_error_phrase("not_found_error")["tts"].format(command),
                        "buttons": [
                            {
                                "title": "назад",
                                "hide": True
                            }
                        ]
                    },
                    "session": session,
                    "version": version
                }
            )

        # если пользователь решит повторить список айтемов, мб стоит сделать по-другому, не меняя стейж
        if state.is_using(2):
            if check_line(command):
                items = database.get_reminder_list(reminder_template[user_id]['title'])
                answer_response = {
                    "response": {
                        "text": get_phrase(state.get_state(), "second_stage")["text"].format(", ".join(items)),
                        "tts": get_phrase(state.get_state(), "second_stage")["tts"].format(", ".join(items)),
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
                state.set_zero()
                return jsonify(answer_response)

            elif not check_line(command):
                answer_response = {
                    "response": {
                        "text": get_phrase(state.get_state(), "second_stage_disagree")["text"],
                        "tts": get_phrase(state.get_state(), "second_stage_disagree")["tts"],
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
                            }
                        ],
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

    except Exception:
        answer_response = {
            "response": get_error_phrase(),
            "session": session,
            "version": version
        }


if __name__ == '__main__':
    app.run(port=6000, debug=True)
