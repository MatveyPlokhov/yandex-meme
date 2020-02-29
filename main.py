# coding=utf-8
from __future__ import unicode_literals

import json
import logging
import os
import requests

from bs4 import BeautifulSoup
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

sessionStorage = {}

skill_id = "caee0d3a-e0ff-4720-a4ac-e45205aee08b"
token = "AgAAAAAIOCSpAAT7o82ir0CsuUqWn1L6FO9DXZE"


@app.route("/", methods=['POST'])
def main():
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


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    url = "https://ru.meming.world/wiki/Special:Random"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    mainText = soup.find_all('h1')[0].get_text()
    images = soup.findAll('img')
    mainImageUrl = "https://ru.meming.world/" + images[0]['src']

    skillsUrl = 'https://dialogs.yandex.net/api/v1/skills/' + skill_id + '/images'
    headers = {'content-type': 'application/json', 'Authorization': 'OAuth ' + token}
    r = requests.post(skillsUrl, json={"url": mainImageUrl}, headers=headers)

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Хочу",
                "Не хочу",
            ]
        }

        res['response']['text'] = 'Привет, хочешь мем?'
        res['response']['buttons'] = get_buttons(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'мемчанский',
        'мем',
        'новый мем',
        'да',
        'хочу',
    ]:
        # res['response']['card']['title'] = mainText
        # res['response']['card']['button']['text'] = 'mainText'
        # res['response']['card']['title'] = mainText
        # res['response']['text'] = get_buttons(user_id)
        res['response']['text'] = ''
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = r.json()['image']['id']
        res['response']['card']['title'] = mainText
        # res['response']['card']['image_id'] = r.json()['image']['id']
        return

    res['response']['buttons'] = get_buttons(user_id)
    return


# Функция возвращает две подсказки для ответа.
def get_buttons(user_id):
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


def get_card(imageUrl):
    skillsUrl = 'https://dialogs.yandex.net/api/v1/skills/' + skill_id + '/images'
    headers = {'content-type': 'application/json', 'Authorization': 'OAuth ' + token}
    r = requests.post(skillsUrl, json={"url": mainImageUrl}, headers=headers)
    return imageUrl


app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
