# -*- coding: utf-8 -*-

"""Utility module to generate text for commonly used responses."""

import random
import six
import pickle

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type

from . import data


def get_random_word():
    """Returns a random word and a list of synonyms for that word."""
    word = []
    with open('word_set', 'rb') as f:
        my_list = pickle.load(f)
        word = random.choice(my_list)

    return word

def get_bad_answer(item):
    """Return response text for incorrect answer."""
    return "{} {}".format(data.BAD_ANSWER.format(item), data.HELP_MESSAGE)


def get_current_score(score, counter):
    """Return the response text for current quiz score of the user."""
    return data.SCORE.format("current", score, counter)


def get_final_score(score, counter):
    """Return the response text for final quiz score of the user."""
    return data.SCORE.format("final", score, counter)


def get_ordinal_indicator(counter):
    """Return st, nd, rd, th ordinal indicators according to counter."""
    if counter == 1:
        return "1st"
    elif counter == 2:
        return "2nd"
    elif counter == 3:
        return "3rd"
    else:
        return "{}th".format(str(counter))


def get_question(counter, item):
    """Return response text for nth question to the user."""
    return (
        "Here is your {} word. Your word is " + item).format(
        get_ordinal_indicator(counter))


def get_answer(attr, item):
    """Return response text for correct answer to the user."""
    return "Accepted synonyms of {} are {}. ".format(item, ','.join(str(s) for s in attr).replace("_", " "))


def ask_question(handler_input):
    # (HandlerInput) -> None
    """Get a random word and synonyms, return question about it."""
    random_word_synonyms = get_random_word()

    random_word = random_word_synonyms[0]
    synonyms = list(random_word_synonyms[1])

    attr = handler_input.attributes_manager.session_attributes

    attr["quiz_item"] = random_word
    attr["quiz_attr"] = synonyms
    attr["counter"] += 1

    handler_input.attributes_manager.session_attributes = attr

    return get_question(attr["counter"], random_word)


def get_speechcon(correct_answer):
    """Return speechcon corresponding to the boolean answer correctness."""
    text = ("<say-as interpret-as='interjection'>{} !"
            "</say-as><break strength='strong'/>")
    if correct_answer:
        return text.format(random.choice(data.CORRECT_SPEECHCONS))
    else:
        return text.format(random.choice(data.WRONG_SPEECHCONS))


def compare_token_or_slots(handler_input, value):
    """Compare value with slots, voice response for quiz answer."""
    return compare_slots(
        handler_input.request_envelope.request.intent.slots, value)


def compare_slots(slots, value):
    """Compare slot value to the value provided."""
    for _, slot in six.iteritems(slots):
        if slot.value is not None:
            return slot.value.lower() in value
    else:
        return False

