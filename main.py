import pymorphy2
from flask import Flask, request, jsonify
from phrases import get_error_phrase, get_phrase

import settings
from database import DataBase
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
    user_id = session['user']['user_id']
    command = data['request']['command']

    if session['new']:
        database.add_new_user(session['user']['user_id'])
        reminder_template[session['user']['user_id']] = {"title": "", "reminder_list": []}
        state.set_zero()

        answer_response = {
            "response": {
                'text': get_phrase(state.state, "zero")['text'],
                'tts': get_phrase(state.state, "zero")['tts']
            },
            "session": session,
            "version": version
        }
        return jsonify(answer_response)

    #  Начальное состояние Алисы
    if not (state.is_creating() or state.is_delete() or state.is_using()):
        if 'создать' in command:
            title_from_user = command.split('создать')
            reminder_template[user_id]['title'] = title_from_user[1]
            state.set_creating()
            answer_response = {
                "response": {
                    'text': get_phrase("CREATING", "start_message")["text"].format(title_from_user[1]),
                    'tts': get_phrase("CREATING", "start_message")["tts"].format(title_from_user[1])
                },
                "buttons": [
                    {
                        "title": "Да",
                        "hide": True
                    },
                    {
                        "title": "Нет",
                        "hide": True
                    }
                ],
                "session": session,
                "version": version
            }
            state.set_creating()
            return jsonify(answer_response)

        if 'использовать' in command:
            reminder_from_user = command.split("использовать")
            check_title = database.get_reminders_titles(user_id)
            if reminder_from_user[1] not in check_title:
                answer_response = {
                    "response": {
                        "text": get_error_phrase("not_found_error")["text"].format(reminder_from_user[1]),
                        "tts": get_error_phrase("not_found_error")["tts"].format(reminder_from_user[1]),
                    },
                    "session": session,
                    "version": version,
                    "end_session": True
                }
                return jsonify(answer_response)

            items = database.get_reminder_list(reminder_from_user[1])
            reminder_template[user_id]['title'] = reminder_from_user[1]
            reminder_template[user_id]['reminder_list'] = items

            answer_response = {
                "response": {
                    'text': get_phrase("USING", "start_message")["text"].format(", ".join(items)),
                    'tts': get_phrase("USING", "start_message")["tts"].format(", ".join(items))
                },
                "buttons": [
                    {
                        "title": "Да",
                        "hide": True
                    },
                    {
                        "title": "Нет",
                        "hide": True
                    }
                ],
                "session": session,
                "version": version
            }
            state.set_using()
            return jsonify(answer_response)

        if 'удалить' in command:
            reminder_from_user = command.split("удалить")
            check_title = database.get_reminders_titles(user_id)
            if reminder_from_user[1] not in check_title:
                answer_response = {
                    "response": {
                        "text": get_error_phrase("not_found_error")["text"].format(reminder_from_user[1]),
                        "tts": get_error_phrase("not_found_error")["tts"].format(reminder_from_user[1]),
                    },
                    "session": session,
                    "version": version,
                    "end_session": True
                }
                return jsonify(answer_response)

            reminder_template[user_id]['title'] = reminder_from_user[1]
            state.set_delete()
            answer_response = {
                "response": {
                    'text': get_phrase("DELETE", "start_message")["text"].format(reminder_from_user[1]),
                    'tts': get_phrase("DELETE", "start_message")["tts"].format(reminder_from_user[1])
                },

                "buttons": [
                    {
                        "title": "Да",
                        "hide": True
                    },
                    {
                        "title": "Нет",
                        "hide": True
                    }
                ],
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        if "список напоминалок" in command:
            text, tts = get_phrase("LIST", "not_exists")["text"], get_phrase("LIST", "not_exists")["tts"]
            check_titles = database.get_reminders_titles(user_id)
            if check_titles:
                text, tts = get_phrase("LIST", "exists")["text"].format(", ".join(check_titles)), \
                    get_phrase("LIST", "exists")["tts"].format(", ".join(check_titles))
            answer_response = {
                "response": {
                    'text': text,
                    'tts': tts
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

        answer_response = {
            "response": {
                'text': get_error_phrase()['text'],
                'tts': get_error_phrase()['tts']
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
                    'text': get_phrase(state.get_state(), "first_stage")["text"],
                    'tts': get_phrase(state.get_state(), "first_stage")["tts"]
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
                    'text': get_phrase(state.get_state(), "second_stage")["text"],
                    'tts': get_phrase(state.get_state(), "second_stage")["tts"]
                },
                "session": session,
                "version": version,
                "end_session": True
            }
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

    # Сценарий удаления
    if state.is_delete(1):
        if check_line(command):
            answer_response = {
                "response": {
                    "text": get_phrase(state.get_state(), "first_stage")["text"].format("text"),
                    "tts": get_phrase(state.get_state(), "first_stage")["tts"].format("text"),
                },
                "session": session,
                "version": version,
                "end_session": True
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
                "version": version,
                "end_session": True
            }
            return jsonify(answer_response)

        answer_response = {
            "response": {
                get_error_phrase()
            },
            "session": session,
            "version": version,
            "end_session": True
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

        elif not check_line(command):
            answer_response = {
                "response": {
                    "text": get_phrase(state.get_state(), "first_stage_disagree")["text"],
                    "tts": get_phrase(state.get_state(), "first_stage_disagree")["tts"]
                },
                "session": session,
                "version": version,
                "end_session": True
            }
            return jsonify(answer_response)

        answer_response = {
            "response": {
                get_error_phrase()
            },
            "session": session,
            "version": version,
            "end_session": True
        }
        return jsonify(answer_response)


if __name__ == '__main__':
    app.run(port=6000, debug=True)
