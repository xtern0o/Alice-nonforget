from pprint import pprint

from flask import Flask, request, jsonify
import logging

import settings
from database import DataBase
from states import States

app = Flask(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)

state = States()
database = DataBase(settings.MONGO_HOST, settings.MONGO_PORT)


@app.route('/post', methods=['POST'])
def main():
    data = request.json
    session = data['session']
    version = data['version']
    logging.info(data)
    if session['new']:
        database.add_new_user(session['user']['user_id'])
        answer_response = {
            "response": {
                'text': 'Вы запустили сценарий "незабывайка".'
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
    if state.get_state() == '*':

        if request.json['request']['command'] == 'создать':
            answer_response = {
                "response": {
                    'text': 'Напишите название нового навыка',
                    'tts': 'Произнесите название для нового навыка',
                    'end_session': False
                },
                "session": session,
                "version": version
            }
            state.set_creating_state()
            return jsonify(answer_response)

        elif request.json['request']['command'] == 'использовать':
            answer_response = {
                "response": {
                    'text': 'Напишите название навыка',
                    'tts': 'Произнесите название навыка',
                    'end_session': False
                },
                "session": session,
                "version": version
            }
            state.set_using_state()
            return jsonify(answer_response)

        elif request.json['request']['command'] == 'удалить':
            answer_response = {
                "response": {
                    'text': 'Напишите название навыка для удаления',
                    'tts': 'Произнесите название навыка для удаления',
                    'end_session': False
                },
                "session": session,
                "version": version
            }
            state.set_delete_state()
            return jsonify(answer_response)

        else:
            answer_response = {
                "response": {
                    'text': 'Некрректная команда. Повторите ввод',
                    'tts': 'Я не распознала вашу команду. Повторите, пожалуйста',
                    'end_session': False
                },
                "session": session,
                "version": version
            }
            return jsonify(answer_response)

    #  Создания нового сценария
    elif state.get_state() == 'CREATING_SCENARY':
        ...

    #  Использование уже существующего сценария
    elif state.get_state() == 'USE_EXIST_SCENARY':
        ...

    #  Удаление сценария
    elif state.get_state() == 'DELETE_SCENARY':
        ...


if __name__ == '__main__':
    app.run(port=5000, debug=True)
