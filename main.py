from flask import Flask, request, jsonify

import settings
from database import DataBase
from states import States

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
    if session['new']:
        database.add_new_user(session['user']['user_id'])
        reminder_template[session['user']['user_id']] = {"title": "", "reminder_list": []}
        state.set_zero()

        answer_response = {
            "response": {
                'text': 'Вы запустили навык "незабывайка".'
                        ' Вы хотите создать новый сценарий, запустить или удалить существующий?',
                'tts': 'Приветствую вас в навыке "незабывайка". Хотите создать сценарий или применить существующий?',
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
            answer_response = {
                "response": {
                    'text': 'Напишите название нового навыка',
                    'tts': 'Произнесите название для нового навыка',
                },
                "session": session,
                "version": version
            }
            state.set_creating()
            return jsonify(answer_response)

        if command == 'использовать':
            answer_response = {
                "response": {
                    'text': 'Напишите название навыка',
                    'tts': 'Произнесите название навыка',
                },
                "session": session,
                "version": version
            }
            state.set_using()
            return jsonify(answer_response)

        if command == 'удалить':
            answer_response = {
                "response": {
                    'text': 'Напишите название навыка для удаления',
                    'tts': 'Произнесите название навыка для удаления',
                },
                "session": session,
                "version": version
            }
            state.set_delete()
            return jsonify(answer_response)

        answer_response = {
            "response": {
                'text': 'Некорректная команда. Повторите ввод',
                'tts': 'Я не распознала вашу команду. Повторите, пожалуйста',
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
                    "text": f'Название сценария "{reminder_template[user_id]["title"]}"',
                    "tts": f'Я вас правильно поняла? Название нового сценария "{reminder_template[user_id]["title"]}"',
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
                'text': 'Некорректный ввод. Повторите, пожалуйста',
                'tts': 'Я вас не поняла, повторите еще раз',
            },
            "session": session,
            "version": version
        }
        return jsonify(answer_response)

    if state.is_creating(2):
        if command == 'да' or 'да' in command and 'нет' not in command:
            answer_response = {
                "response": {
                    "text": 'Теперь вводите предметы по порядку. Закончить последовательность можно ключевым словом '
                            '"Всё"',
                    "tts": 'Поняла. Теперь произнесите предметы по порядку. Закончите ключевым словом "Всё"'
                },
                "session": session,
                "version": version
            }
            state.set_stage(3)
            return jsonify(answer_response)

        if command == 'нет' or 'нет' in command and 'да' not in command:
            answer_response = {
                "response": {
                    "text": 'Без бэ. Опвторите ввод названия',
                    "tts": 'Да без бэ. Повторите название'
                },
                "session": session,
                "version": version
            }
            state.set_stage(1)
            return jsonify(answer_response)

    if state.is_creating(3):
        if command:
            if command != 'всё':
                item = command
                # TODO: some validation of item at this step
                reminder_template[user_id]["reminder_list"].append(item)
                answer_response = {
                    "response": {
                        "text": "Дальше",
                        "tts": "Записала"
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            database.add_reminder(user_id, reminder_template)
            state.set_stage(4)
            answer_response = {
                "response": {
                    "text": f'Отлично. Сценарий под названием {reminder_template[user_id]["title"]} добавлен.'
                            f' Ваши дальнейшие действия?',
                    "tts": f'Отлично. Сценарий под названием {reminder_template[user_id]["title"]} добавлен.'
                           f' Ваши дальнейшие действия?',
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
            "response": {
                "text": "Некорректный ввод",
                "tts": "Я вас не поняла. Повторите"
            },
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
                    "text": f'Вы точно хотите удалить напоминалку "{reminder_template[user_id]["title"]}"?',
                    "tts": f'Вы точно хотите удалить напоминалку "{reminder_template[user_id]["title"]}"?',
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
                'text': 'Такой напоминалки у вас нет, повторите название или перейдите к списку ваших напоминалок',
                'tts': 'Такой напоминалки у вас нет, повторите название или перейдите к списку ваших напоминалок',
            },
            "session": session,
            "version": version
        }
        return jsonify(answer_response)

    if state.is_delete(2):
        if command == 'да' or 'да' in command and 'нет' not in command:
            answer_response = {
                "response": {
                    "text": f'Напоминалка {reminder_template[user_id]["title"]} удалена. Что вы хотите сделать теперь?',
                    "tts": f'Напоминалка {reminder_template[user_id]["title"]} удалена. Что вы хотите сделать теперь?',
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
            database.delete_reminder(user_id, reminder_template[user_id]["title"])
            state.set_zero()
            return jsonify(answer_response)

        if command == 'нет' or 'нет' in command and 'да' not in command:
            answer_response = {
                "response": {
                    "text": f'Удаление напоминалки {reminder_template[user_id]["title"]} отменено. Что вы хотите сделать теперь?',
                    "tts": f'Удаление напоминалки {reminder_template[user_id]["title"]} отменено. Что вы хотите сделать теперь?',
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
            "response": {
                'text': 'Некорректный ввод. Повторите, пожалуйста',
                'tts': 'Я вас не поняла, повторите еще раз',
            },
            "session": session,
            "version": version
        }
        return jsonify(answer_response)

    # тут обработка начального состояния, без доп. проверок.
    if state.is_using(1):
        if command in database.get_reminders_titles(user_id):
            reminder_template[user_id]["title"] = command

            # тут уже вывод всех айтемов пользователя
            items = database.get_reminder_list(reminder_template[user_id]["title"])
            answer_response = {
                "response": {
                    "text": f'Напоминалка {reminder_template[user_id]["title"]}. Незабудьте взять: {", ".join(items)}. Мне повторить?',
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

            state.set_stage(2)
            return jsonify(answer_response)

    # если пользователь решит повторить список айтемов, мб стоит сделать по-другому, не меняя стейж
    if state.is_using(2):
        if command == "да":
            items = database.get_reminder_list(reminder_template[user_id]['title'])
            answer_response = {
                "response": {
                    "text": f'Хорошо, повторяю. Незабудьте взять: {", ".join(items)}. Мне повторить?',
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

        elif command == "нет":
            answer_response = {
                "response": {
                    "text": f'Надеюсь, вы ничего не забыли. Вы хотите создать напоминалку или использовать/удалить существую?',
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


if __name__ == '__main__':
    app.run(port=6000, debug=True)
