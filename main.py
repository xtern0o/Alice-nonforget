from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route('/post', methods=['POST'])
def main():
    session = request.json['session']
    version = request.json['version']

    if session['new']:
        answer_response = {
            "response": {
                'text': 'Вы запустили сценарий "незабывайка".'
                        ' Вы хотите создать новый сценарий, запустить или удалить существующий?',
                'tts': 'Приветствую вас в сценарий "незабывайка". Хотите создать сценарий или применить существующий?',
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
        # ТЕЩУ КОМАНДЫ !!! НЕ РАБОТАЕТ(((
        if session['command'] == "запустить":
            answer_response = {
                "response": {
                    'text': 'Старт',
                    'tts': 'Старт',
                    'end_session': False,
                },
                "session": session,
                "version": version
            }

            return jsonify(answer_response)
        return jsonify(answer_response)


if __name__ == '__main__':
    app.run(debug=True)
