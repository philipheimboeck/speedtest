#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Executable that handles the Alexa requests
"""

import logging

from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement

from persistence import LogPersistence
import config

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

TYPE_KEY = "Type"

CONFIG = config.load_config()

@ask.launch
def launch():
    card_title = render_template('card_title').encode('utf8')
    question_text = render_template('welcome').encode('utf8')
    reprompt_text = render_template('welcome_reprompt').encode('utf8')
    return question(question_text).reprompt(reprompt_text).simple_card(card_title, question_text)

@ask.intent('CurrentSpeedIntent', mapping={'type': 'Type'})
def my_type_is(type):
    card_title = render_template('card_title')
    if type is not None:
        session.attributes[TYPE_KEY] = type
        with LogPersistence(CONFIG['database']) as persistence:
            response = persistence.fetch_last(type)
            if (type == "download" or type == "upload"):
                result = str(int(response[0] / 1048567)) + " Mbits/Sekunde"
            else:
                result = str(int(response[0]))
            speed_text = render_template('known_type', currentSpeed=result, type=type).encode('utf8')
            return statement(speed_text).simple_card(card_title, speed_text)
    else:
        question_text = render_template('unknown_type').encode('utf8')
        reprompt_text = render_template('unknown_type_reprompt').encode('utf8')
        return statement(question_text).reprompt(reprompt_text).simple_card(card_title, question_text)

@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)
