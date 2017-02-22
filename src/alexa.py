#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Executable that handles the Alexa requests
"""

import logging

from flask import Flask, render_template
from flask_ask import Ask, question, session, statement
from TwitterAPI import TwitterAPI

import config
from persistence import LogPersistence
import measure

APP = Flask(__name__)
ask = Ask(APP, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# Globals
TYPE_KEY = "Type"
RESULT_KEY = "Result"
BIT_DIVIDER = 1048567
SPEED_TYPE = " Mbit/Sekunde"

CONFIG = config.load_config()
TWITTER_API = TwitterAPI(
    CONFIG['twitter_consumer_key'],
    CONFIG['twitter_consumer_secret'],
    CONFIG['twitter_access_token_key'],
    CONFIG['twitter_access_token_secret']
)

@ask.launch
def launch():
    """
    Speedtest started
    """
    card_title = render_template('card_title').encode('utf8')
    question_text = render_template('welcome').encode('utf8')
    reprompt_text = render_template('welcome_reprompt').encode('utf8')
    return question(question_text).reprompt(reprompt_text).simple_card(card_title, question_text)


@ask.intent('CurrentSpeedIntent', mapping={'type': 'Type'})
def my_type_is(type):
    """
    Get the last speedtest result
    """
    card_title = render_template('card_title')
    if type is not None:
        session.attributes[TYPE_KEY] = type
        with LogPersistence(CONFIG['database']) as persistence:
            response = persistence.fetch_last(type)
            print response
            if type == "download" or type == "upload":
                session.attributes[RESULT_KEY] = int(response[0] / BIT_DIVIDER)
                result = str(session.attributes[RESULT_KEY]) + SPEED_TYPE
            else:
                session.attributes[RESULT_KEY] = int(response[0])
                result = str(session.attributes[RESULT_KEY])

            twitter_enabled = CONFIG['twitter_enabled'] is not None and CONFIG['twitter_enabled']

            # Choose the template
            template = 'known_type_tweet' if twitter_enabled else 'known_type'
            speed_text = render_template(
                template,
                currentSpeed=result,
                type=type,
                measure_date=response[1].strftime('%Y%m%d'),
                measure_time=response[1].strftime('%H:%M')
            ).encode('utf8')

            if twitter_enabled:
                # If twitter is enabled, we ask a question instead of stating something
                speed_reprompt = render_template('known_type_repromt', type=type).encode('utf8')
                return question('<speak>{}</speak>'.format(speed_text)) \
                    .reprompt(speed_reprompt).simple_card(card_title, speed_text)

            return statement('<speak>{}</speak>'.format(speed_text)) \
                .simple_card(card_title, speed_text)
    else:
        question_text = render_template('unknown_type').encode('utf8')
        reprompt_text = render_template('unknown_type_reprompt').encode('utf8')
        return question(question_text).reprompt(reprompt_text)\
            .simple_card(card_title, question_text)


@ask.intent('TweetCurrentSpeed', mapping={'answer': 'Answer'})
def tweetCurrentSpeed(answer):
    """
    Use twitterAPI to send out the last result
    """
    card_title = render_template('card_title')
    type = session.attributes.get(TYPE_KEY)
    result = session.attributes.get(RESULT_KEY)

    if answer == "ja" and result > 0:
        result_text = {
            'download': str(result) + " Mbit/Sekunde",
            'upload': str(result) + " Mbit/Sekunde",
            'ping': str(result),
        }[type]
        tweet_text = render_template('tweet_text', currentSpeed=result_text, type=type)\
            .encode('utf8')
        response = TWITTER_API.request('statuses/update', {'status':tweet_text})
        if response.status_code == 200:
            statement_text = render_template('tweet_success').encode('utf8')
            return statement(statement_text).simple_card(card_title, statement_text)
        else:
            statement_text = render_template('tweet_error').encode('utf8')
            reprompt_text = render_template('error_reprompt').encode('utf8')
            return question(statement_text).reprompt(reprompt_text)

    elif answer == "nein" or result > 0:
        statement_text = render_template('exit').encode('utf8')
        return statement(statement_text)

    elif result <= 0:
        statement_text = render_template('tweet_noResult').encode('utf8')
        repromt_text = render_template('unknown_type_reprompt').encode('utf8')
        return question(statement_text).reprompt(repromt_text)

    else:
        statement_text = render_template('error').encode('utf8')
        reprompt_text = render_template('error_reprompt').encode('utf8')
        return question(statement_text).reprompt(reprompt_text)\
            .simple_card(card_title, statement_text)


@ask.intent('MeasureSpeedIntent')
def start_measurement():
    """
    Start a measurement
    """
    measure.start_speedtest(config=CONFIG)
    statement_text = render_template('measure').encode('utf8')
    return statement(statement_text)


@ask.intent('StatsOfToday', mapping={'type': 'Type'})
def get_stats(type):
    """
    Get the Max, Min, Avg and Count of the given type of todays results
    """
    card_title = render_template('card_title')
    if type is not None:
        session.attributes[TYPE_KEY] = type
        print type
        with LogPersistence(CONFIG['database']) as persistence:
            response = persistence.fetch_stats(type)
            print response
            if type == "download" or type == "upload":
                speed_max = str(int(response[0] / BIT_DIVIDER)) + SPEED_TYPE
                speed_min = str(int(response[1] / BIT_DIVIDER)) + SPEED_TYPE
                speed_avg = str(int(response[2] / BIT_DIVIDER)) + SPEED_TYPE
                speed_count = response[3]
            else:
                speed_max = response[0]
                speed_min = response[1]
                speed_avg = response[2]
                speed_count = response[3]

            # Choose the template
            template = 'stats_text' if (type == 'download' or type == 'upload')\
                else 'stats_text_ping'
            speed_text = render_template(
                template,
                max=speed_max,
                min=speed_min,
                avg=speed_avg,
                count=speed_count,
                type=type
            ).encode('utf8')

            return statement('<speak>{}</speak>'.format(speed_text)) \
                .simple_card(card_title, speed_text)
    else:
        question_text = render_template('unknown_type').encode('utf8')
        reprompt_text = render_template('unknown_type_reprompt').encode('utf8')
        return question(question_text).reprompt(reprompt_text)\
            .simple_card(card_title, question_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    """
    Alexa Stop Intent
    """
    statement_text = render_template('stop').encode('utf8')
    return statement(statement_text)


@ask.session_ended
def session_ended():
    """
    Will be called when session is ended
    """
    return "", 200


if __name__ == '__main__':
    APP.run(debug=True)
