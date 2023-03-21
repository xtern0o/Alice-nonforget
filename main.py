# не попадает под условя кнопок (надо исправить)

from flask import Flask, request, jsonify
import logging

from states import States

app = Flask(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)

states = States()


@app.route('/post', methods=['POST'])
def main():
    session = request.json['session']
    version = request.json['version']
    logging.info(request.json)
    if session['new']:
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
                        "title": "Запустить",
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

    if not (states.get_delete_state() or states.get_creating_state() or states.get_using_state()):
        if request.json['request']['command'] == 'cоздать':
            answer_response = {
                "response": {
                    'text': 'Напишите название нового навыка',
                    'tts': 'Произнесите название для нового навыка',
                    'end_session': False
                },
                "session": session,
                "version": version
            }
            states.set_creating_state(1)
            return jsonify(answer_response)

        if request.json['request']['command'] == 'использовать':
            answer_response = {
                "response": {
                    'text': 'Напишите название навыка',
                    'tts': 'Произнесите название навыка',
                    'end_session': False
                },
                "session": session,
                "version": version
            }
            states.set_using_state(1)
            return jsonify(answer_response)

        if request.json['request']['command'] == 'удалить':
            answer_response = {
                "response": {
                    'text': 'Напишите название навыка для удаления',
                    'tts': 'Произнесите название навыка для удаления',
                    'end_session': False
                },
                "session": session,
                "version": version
            }
            states.set_delete_state(1)
            return jsonify(answer_response)

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


if __name__ == '__main__':
    app.run(port=6000, debug=True)
