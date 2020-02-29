from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import os
import requests

from bs4 import BeautifulSoup
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

HOST = 'https://dialogs.yandex.net'


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    url = "https://ru.meming.world/wiki/Special:Random"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    text = soup.find_all('h1')[0].get_text()
    images = soup.findAll('img')

    # POST / api / v1 / skills / caee0d3a - e0ff - 4720 - a4ac - e45205aee08b / images
    # Authorization: OAuth <AgAAAAAIOCSpAAT7o82ir0CsuUqWn1L6FO9DXZE>
    # {"url": "<https://ru.meming.world/"+images[0]['src']+">"}

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу",
                "Хочу",
            ]
        }

        res['response']['text'] = 'Привет, хочешь мем?'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'мемчанский',
        'мем',
        'новый мем',
        'да',
        'Хочу',
    ]:
        res['response']['text'] = text
        return

    res['response']['buttons'] = get_suggests(user_id)
    return

# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    suggests.append({
        "title": "Ссылочка",
        "url": "https://market.yandex.ru/search?text=слон",
        "hide": True
    })

    return suggests


app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
