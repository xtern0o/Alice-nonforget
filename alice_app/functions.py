from flask import jsonify


def send_help_message(session, version):
    answer_response = {
        "response": {
            "text": "Список всех команд:\nСоздать - Создать новую напоминалку\nИспользовать - Использовать уже существующую напоминалку\nУдалить - Удалить напоминалку\nЕсть идеи по улучшению навыка?\nпиши на почту: dialogroup@rambler.ru",
            "card": {
                "type": "ItemsList",
                "header": {
                    "text": "Список команд:",
                },
                "items": [
                    {
                        "title": "Создать",
                        "description": "Создать новую напоминалку",
                        "button": {
                            "text": "Создать",
                        }
                    },
                    {
                        "title": "Использовать",
                        "description": "Использовать существующую напоминалку",
                        "button": {
                            "text": "Использовать",
                        }
                    },
                    {
                        "title": "Удалить",
                        "description": "Удалить напоминалку",
                        "button": {
                            "text": "Удалить",
                        }
                    },
                    {
                        "title": "Есть идеи по улучшению навыка?",
                        "description": "Пиши нам на почту: dialogroup@rambler.ru",
                        "button": {
                            "url": "https://dialogroup@rambler.ru"
                        }
                    }
                ],
            }
        },
        "session": session,
        "version": version
    }

    return jsonify(answer_response)


def create_buttons(*args, **kwargs):
    for i in args:
        kwargs['response']['buttons'].append(i)
    return kwargs
