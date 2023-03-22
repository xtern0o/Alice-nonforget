from flask import Flask, request, jsonify

import settings
# from database import DataBase
from states import States

app = Flask(__name__)

state = States()
# database = DataBase(settings.MONGO_HOST, settings.MONGO_PORT)

scenary_template = {'title': '', 'todo': [], 'user_id': ''}


@app.route('/post', methods=['POST'])
def main():
    global scenary_template

    data = request.json
    session = data['session']
    version = data['version']
    if session['new']:
        # database.add_new_user(session['user']['user_id'])
        print('2')
        scenary_template['title'] = ''
        scenary_template['todo'] = []
        scenary_template['user_id'] = session['user']['user_id']

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
                'end_session': False,
            },
            "session": session,
            "version": version
        }
        return jsonify(answer_response)

    #  Начальное состояние Алисы
    if not (state.DELETE_SCENARY or state.CREATING_SCENARY or state.USE_EXIST_SCENARY):

        if request.json['request']['command'] == 'создать':
            answer_response = {
                "response": {
                    'text': 'Напишите название нового навыка',
                    'tts': 'Произнесите название для нового навыка',
                },
                "session": session,
                "version": version
            }
            state.CREATING_SCENARY = 1
            return jsonify(answer_response)

        if request.json['request']['command'] == 'использовать':
            answer_response = {
                "response": {
                    'text': 'Напишите название навыка',
                    'tts': 'Произнесите название навыка',
                },
                "session": session,
                "version": version
            }
            state.USE_EXIST_SCENARY = 1
            return jsonify(answer_response)

        if request.json['request']['command'] == 'удалить':
            answer_response = {
                "response": {
                    'text': 'Напишите название навыка для удаления',
                    'tts': 'Произнесите название навыка для удаления',
                },
                "session": session,
                "version": version
            }
            state.DELETE_SCENARY = 1
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
    if state.CREATING_SCENARY == 1:

        if request.json['request']['command']:
            scenary_template['title'] = request.json['request']['command']
            state.CREATING_SCENARY = 2
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

    if state.CREATING_SCENARY == 2:

        if request.json['request']['command'] == 'да' or \
            'да' in request.json['request']['command'] and 'нет' not in request.json['request']['command']:
            state.CREATING_SCENARY = 3
            answer_response = {
                "response": {
                    "text": 'Отлично',
                    "tts": 'иди нахуй'
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)
        if request.json['request']['command'] == 'нет' or \
            'нет' in request.json['request']['command'] and 'да' not in request.json['request']['command']:
            answer_response = {
                "response": {
                    "text": 'Хорошо',
                    "tts": 'Хорошо'
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)


if __name__ == '__main__':
    app.run(port=6000, debug=True)
