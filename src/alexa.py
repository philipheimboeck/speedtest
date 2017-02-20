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

from TwitterAPI import TwitterAPI

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

## Globals
TYPE_KEY = "Type"
RESULT_KEY = "Result"

CONFIG = config.load_config()
api = TwitterAPI(CONFIG['twitter_consumer_key'], CONFIG['twitter_consumer_secret'], CONFIG['twitter_access_token_key'], CONFIG['twitter_access_token_secret'])

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
            print response
            if (type == "download" or type == "upload"):
                session.attributes[RESULT_KEY] = int(response[0] / 1048567)
                result = str(session.attributes[RESULT_KEY]) + " Mbit/Sekunde"
            else:
                session.attributes[RESULT_KEY] = int(response[0])
                result = str(session.attributes[RESULT_KEY])

            speed_text = render_template(
                'known_type',
                currentSpeed=result,
                type=type,
                measure_date=response[1].strftime('%Y%m%d'),
                measure_time=response[1].strftime('%H:%M')
            ).encode('utf8')
            speed_reprompt = render_template('known_type_repromt', type=type).encode('utf8')

            return question('<speak>{}</speak>'.format(speed_text)).reprompt(speed_reprompt).simple_card(card_title, speed_text)
    else:
        question_text = render_template('unknown_type').encode('utf8')
        reprompt_text = render_template('unknown_type_reprompt').encode('utf8')
        return question(question_text).reprompt(reprompt_text).simple_card(card_title, question_text)

@ask.intent('TweetCurrentSpeed', mapping={'answer': 'Answer'})
def tweetCurrentSpeed(answer):
    card_title = render_template('card_title')
    type = session.attributes.get(TYPE_KEY)
    result = session.attributes.get(RESULT_KEY)

    if (answer == "ja" and result > 0):
        result_text = {
        'download': str(result) + " Mbit/Sekunde",
        'upload': str(result) + " Mbit/Sekunde",
        'ping': str(result),
        }[type]
        tweet_text = render_template('tweet_text', currentSpeed=result_text, type=type).encode('utf8')
        r = api.request('statuses/update', {'status':tweet_text})
        if (r.status_code == 200):
            statement_text = render_template('tweet_success').encode('utf8')
            return statement(statement_text).simple_card(card_title, statement_text)
        else:
            statement_text = render_template('tweet_error').encode('utf8')
            reprompt_text = render_template('error_reprompt').encode('utf8')
            return question(statement_text).reprompt(reprompt_text)

    elif (answer == "nein" or result > 0):
        statement_text = render_template('exit').encode('utf8')
        return statement(statement_text)

    elif (result <= 0):
        statement_text = render_template('tweet_noResult').encode('utf8')
        repromt_text = render_template('unknown_type_reprompt').encode('utf8')
        return question(statement_text).reprompt(repromt_text)

    else:
        statement_text = render_template('error').encode('utf8')
        reprompt_text = render_template('error_reprompt').encode('utf8')
        return question(statement_text).reprompt(reprompt_text).simple_card(card_title, error_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    statement_text = render_template('stop').encode('utf8')
    return statement(statement_text)

@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)
