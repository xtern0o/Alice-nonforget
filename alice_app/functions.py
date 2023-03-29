from flask import jsonify


def send_help_message(text, tts, session, version):
    answer_response = {
        "response": {
            'text': text,
            'tts': tts
        },
        "session": session,
        "version": version
    }

    return jsonify(answer_response)