from flask import Flask, request, jsonify

import settings
# from database import DataBase
from states import States

app = Flask(__name__)

state = States()
# database = DataBase(settings.MONGO_HOST, settings.MONGO_PORT)

scenary_template = {'title': '', 'todo': [], 'user_id': ''}


def zero_all():
    global scenary_template
    scenary_template['title'] = ''
    scenary_template['todo'] = []
    scenary_template['user_id'] = ''
    state.set_zero()


@app.route('/post', methods=['POST'])
def main():
    global scenary_template

    data = request.json
    session = data['session']
    version = data['version']
    if session['new']:
        # database.add_new_user(session['user']['user_id'])
        scenary_template['title'] = ''
        scenary_template['todo'] = []
        scenary_template['user_id'] = session['user']['user_id']
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
        if data['request']['command'] == 'создать':
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

        if data['request']['command'] == 'использовать':
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

        if data['request']['command'] == 'удалить':
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
        if data['request']['command']:
            scenary_template['title'] = request.json['request']['command']
            answer_response = {
                "response": {
                    "text": f'Название сценария "{scenary_template["title"]}"',
                    "tts": f'Я вас правильно поняла? Название нового сценария "{scenary_template["title"]}"',
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

        answer_respone = {
            "response": {
                'text': 'Некорректный ввод. Повторите, пожалуйста',
                'tts': 'Я вас не поняла, повторите еще раз',
            },
            "session": session,
            "version": version
        }
        return jsonify(answer_respone)

    if state.is_creating(2):
        if data['request']['command'] == 'да' or \
                'да' in request.json['request']['command'] and 'нет' not in request.json['request']['command']:
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
        if data['request']['command'] == 'нет' or \
                'нет' in request.json['request']['command'] and 'да' not in request.json['request']['command']:
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
        if data['request']['command']:
            if data['request']['command'] != 'всё':
                item = data['request']['command']
                # some validation of item at this step
                scenary_template["todo"].append(item)
                answer_response = {
                    "response": {
                        "text": "Дальше",
                        "tts": "Записала"
                    },
                    "session": session,
                    "version": version
                }
                return jsonify(answer_response)

            # добавление полноценного сценария в базу данных
            state.set_stage(4)
            answer_response = {
                "response": {
                    "text": f'Отлично. Сценарий под названием {scenary_template["title"]} добавлен.'
                            f' Ваши дальнейшие действия?',
                    "tts": f'Отлично. Сценарий под названием {scenary_template["title"]} добавлен.'
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


if __name__ == '__main__':
    app.run(port=6000, debug=True)
