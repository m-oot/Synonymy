# -*- coding: utf-8 -*-

import json
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.response_helper import (
    get_plain_text_content, get_rich_text_content)

from ask_sdk_model.interfaces.display import (
    ImageInstance, Image, RenderTemplateDirective, ListTemplate1,
    BackButtonBehavior, ListItem, BodyTemplate2, BodyTemplate1)
from ask_sdk_model import ui, Response

from alexa import data, util


# Skill Builder object
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Request Handler classes
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        handler_input.response_builder.speak(data.WELCOME_MESSAGE).ask(
            data.HELP_MESSAGE)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for skill session end."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")
        print("Session ended with reason: {}".format(
            handler_input.request_envelope))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")
        handler_input.attributes_manager.session_attributes = {}
        # Resetting session

        handler_input.response_builder.speak(
            data.HELP_MESSAGE).ask(data.HELP_MESSAGE)
        return handler_input.response_builder.response


class ExitIntentHandler(AbstractRequestHandler):
    """Single Handler for Cancel, Stop and Pause intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExitIntentHandler")
        handler_input.response_builder.speak(
            data.EXIT_SKILL_MESSAGE).set_should_end_session(True)
        return handler_input.response_builder.response


class QuizHandler(AbstractRequestHandler):
    """Handler for starting a quiz.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("QuizIntent")(handler_input) or
                is_intent_name("AMAZON.StartOverIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In QuizHandler")
        attr = handler_input.attributes_manager.session_attributes
        attr["state"] = "QUIZ"
        attr["counter"] = 0
        attr["quiz_score"] = 0

        question = util.ask_question(handler_input)
        response_builder = handler_input.response_builder
        response_builder.speak("{} {}".format(data.START_QUIZ_MESSAGE, question))
       
        response_builder.ask(question)

        return response_builder.response


class DefinitionHandler(AbstractRequestHandler):
    """Handler for providing word definitions to the users.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("DefinitionIntent")(handler_input) and
                attr.get("state") == "QUIZ")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In DefinitionHandler")
        response_builder = handler_input.response_builder
        attr = handler_input.attributes_manager.session_attributes

        word = attr["current_word"]
        pos = attr["current_pos"]
        definition = attr["current_definition"]


        speech = util.getDefinitionSpeech(word, pos, definition)
        
        response_builder.speak(speech)
        response_builder.ask("")

        return response_builder.response


class QuizAnswerHandler(AbstractRequestHandler):
    """Handler for answering the quiz.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attr = handler_input.attributes_manager.session_attributes
        return (attr.get("state") == "QUIZ")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In QuizAnswerHandler")
        attr = handler_input.attributes_manager.session_attributes
        response_builder = handler_input.response_builder

        item = attr["current_word"]
        item_attr = attr["current_synonyms"]

        is_ans_correct = util.compare_token_or_slots(
            handler_input=handler_input,
            value=item_attr)

        if is_ans_correct:
            speech = util.get_speechcon(correct_answer=True)
            attr["quiz_score"] += 1
            handler_input.attributes_manager.session_attributes = attr
        else:
            speech = util.get_speechcon(correct_answer=False)

        speech += util.get_answer(item_attr, item)

        if attr['counter'] < data.MAX_QUESTIONS:
            # Ask another question
            speech += util.get_current_score(
                attr["quiz_score"], attr["counter"])
            question = util.ask_question(handler_input)
            speech += question
            reprompt = question

            # Update item and item_attr for next question
            item = attr["current_word"]
            item_attr = attr["current_synonyms"]

            return response_builder.speak(speech).ask(reprompt).response
        else:
            # Finished all questions.
            speech += util.get_final_score(attr["quiz_score"], attr["counter"])
            speech += data.EXIT_SKILL_MESSAGE

            response_builder.set_should_end_session(True)

            return response_builder.speak(speech).response


class RepeatHandler(AbstractRequestHandler):
    """Handler for repeating the response to the user."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In RepeatHandler")
        attr = handler_input.attributes_manager.session_attributes
        response_builder = handler_input.response_builder
        if "recent_response" in attr:
            cached_response_str = json.dumps(attr["recent_response"])
            cached_response = DefaultSerializer().deserialize(
                cached_response_str, Response)
            return cached_response
        else:
            response_builder.speak(data.FALLBACK_ANSWER).ask(data.HELP_MESSAGE)

            return response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for handling fallback intent.

     2018-May-01: AMAZON.FallackIntent is only currently available in
     en-US locale. This handler will not be triggered except in that
     locale, so it can be safely deployed for any locale."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        handler_input.response_builder.speak(
            data.FALLBACK_ANSWER).ask(data.HELP_MESSAGE)

        return handler_input.response_builder.response


# Interceptor classes
class CacheResponseForRepeatInterceptor(AbstractResponseInterceptor):
    """Cache the response sent to the user in session.

    The interceptor is used to cache the handler response that is
    being sent to the user. This can be used to repeat the response
    back to the user, in case a RepeatIntent is being used and the
    skill developer wants to repeat the same information back to
    the user.
    """
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["recent_response"] = response


# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.

    This handler catches all kinds of exceptions and prints
    the stack trace on AWS Cloudwatch with the request envelope."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


# Request and Response Loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))


# Add all request handlers to the skill.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(QuizHandler())
sb.add_request_handler(DefinitionHandler())
sb.add_request_handler(QuizAnswerHandler())
sb.add_request_handler(RepeatHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
sb.add_global_response_interceptor(CacheResponseForRepeatInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()
