# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import os
import sys
import logging
import gettext
import boto3
from typing import Union, List

sys.path.append(os.path.join(os.path.dirname(__file__), './vendor'))

from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractRequestInterceptor, AbstractExceptionHandler, AbstractResponseInterceptor)
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.request_envelope import RequestEnvelope
from ask_sdk_model.session import Session
from ask_sdk_core.attributes_manager import (
    AttributesManager, AttributesManagerException)
from ask_sdk_model.services.monetization import (
    EntitledState, PurchasableState, InSkillProductsResponse, Error,
    InSkillProduct)
from ask_sdk_model.interfaces.monetization.v1 import PurchaseResult
from ask_sdk_model.interfaces.connections import SendRequestDirective
from alexa import data
from boto3.dynamodb.conditions import Key
from ask_sdk_dynamodb.adapter import DynamoDbAdapter, user_id_partition_keygen

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

adapter = DynamoDbAdapter(table_name="wishboard_session", partition_key_name="id",
    attribute_name="attributes", create_table=True,
    partition_keygen=user_id_partition_keygen,
    dynamodb_resource=boto3.resource("dynamodb")
)

'''
Launch
IF パーソナライズ有効
    通常
ELSE
    有効にしてくださいで終了
IF 初回起動
    「子供として登録しますか？大人として登録しますか？」
IF 親
   「願い事が登録されています。「願い事を聞く」といってください」
ELSE
    「願い事を登録しますか？「願い事を登録する」といってください」
初回起動：
'''
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        request_envelope = handler_input.request_envelope;
        attributes_manager = AttributesManager(
            request_envelope=request_envelope,
            persistence_adapter=adapter
        )

        logger.info(request_envelope.context, exc_info=True);
        logger.info(request_envelope.context.system, exc_info=True);
        logger.info(request_envelope.context.system.person, exc_info=True);
        #DynamoDbをTest
        persistence_attr = attributes_manager.persistent_attributes

        speak_output = ''
        person_id = ''
        # test用 'person_id': 'amzn1.ask.person.AHCN7IHVHTQBKRDNNDBYSWZRJISPUHOJEEZZW6MML255REWY2YOQFETSBE7STDPDAXOJUWBPIL5ZV6WZ5555HMZVI6YPKIVDWGOEL7KB'}
        if request_envelope.context.system.person is None:
            # パーソナライズ無効
            speak_output = _(data.LAUNCH_NOT_PERSONALIZE)
            return (
                handler_input.response_builder
                .speak(speak_output)
                .response
            )
        else:
            person_id = request_envelope.context.system.person.person_id;

        if person_id not in persistence_attr:
            persistence_attr[person_id] = {}
        if 'personClass' not in persistence_attr[person_id]:
            speak_output = _(data.LAUNCH_NOT_CLASS)
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
        personClass = persistence_attr[person_id]['personClass']

        if personClass == 'parent':
            speak_output = _(data.LAUNCH_IS_PARENT).format(person_id)
        else:
            speak_output = _(data.LAUNCH_IS_CHILD).format(person_id)

        attributes_manager.save_persistent_attributes()
        logger.info(persistence_attr, exc_info=True);
        logger.info(speak_output, exc_info=True);
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

class WishAddIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("WishAddIntent")(handler_input)

    def handle(self, handler_input):
        _ = handler_input.attributes_manager.request_attributes["_"]
        request_envelope = handler_input.request_envelope;
        logger.info(request_envelope.request, exc_info=True);
        speak_output = _(data.WISH_ADD_MSG)

        attributes_manager = AttributesManager(
            request_envelope=request_envelope,
            persistence_adapter=adapter
        )
        persistence_attr = attributes_manager.persistent_attributes
        person_id = ''
        if request_envelope.context.system.person is None:
            # パーソナライズ無効
            speak_output = _(data.WISH_ADD_NOT_PERSONALIZE)
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
        else:
            person_id = request_envelope.context.system.person.person_id;

        # 親か子か
        personClass = ''
        if 'personClass' in persistence_attr[person_id]:
            personClass = persistence_attr[person_id]['personClass']
        else:
            return AnswerClassIntentHandler(AbstractRequestHandler).handle(handler_input)

        query = get_resolved_query(
            handler_input.request_envelope.request, "query")
        if (query is not None and personClass == 'child'):
            # Dialogを用いてるので原則として値は入ってくる
            persistence_attr[person_id]['wish'] = [query]
            speak_output = _(data.WISH_ADD_MSG).format(query)
        elif (query is not None and personClass == 'parent'):
            persistence_attr[person_id]['wish'] = [query]
            speak_output = _(data.WISH_ADD_PARENT_MSG).format(query)
        else :
            speak_output = _(data.WISH_ADD_MSG).format('聞き取れませんでした')

        attributes_manager.save_persistent_attributes()
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

class WishListIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("WishListIntent")(handler_input)

    def handle(self, handler_input):
        _ = handler_input.attributes_manager.request_attributes["_"]
        request_envelope = handler_input.request_envelope;
        logger.info(request_envelope.request, exc_info=True);
        speak_output = ''

        attributes_manager = AttributesManager(
            request_envelope=request_envelope,
            persistence_adapter=adapter
        )
        persistence_attr = attributes_manager.persistent_attributes
        person_id = ''
        if request_envelope.context.system.person is None:
            # パーソナライズ無効
            speak_output = _(data.WISH_LIST_NOT_PERSONALIZE)
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
        else:
            person_id = request_envelope.context.system.person.person_id;

        # パパかどうか
        personClass = ''
        if 'personClass' in persistence_attr[person_id]:
            personClass = persistence_attr[person_id]['personClass']
        else:
            return AnswerClassIntentHandler(AbstractRequestHandler).handle(handler_input)

        reprompt = True
        if 'wish' in persistence_attr[person_id] and personClass == 'child':
            speak_output = _(data.WISH_LIST_CHILD_MSG).format(persistence_attr[person_id]['wish'][0])
        elif 'wish' not in persistence_attr[person_id] and personClass == 'child':
            speak_output = _(data.WISH_LIST_NONE_CHILD_MSG)
        elif personClass == 'parent':
            speak_output = ''
            for child_id in persistence_attr:
                if 'wish' in persistence_attr[child_id]:
                    speak_output += _(data.WISH_LIST_PARENT_MSG).format(
                        child_id, persistence_attr[child_id]['wish'][0])
            if speak_output != '':
                speak_output += '伝言は以上です。さてどうしましょうか。もう一度聞く場合には「伝言を聞く」と言ってください'
            else:
                speak_output = _(data.WISH_LIST_NONE_PARENT_MSG).format(persistence_attr[person_id])
                reprompt = False

        logger.info(speak_output, exc_info=True);
        logger.info(persistence_attr, exc_info=True);
        if reprompt == True:
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
        else:
            return (
                handler_input.response_builder
                .speak(speak_output)
                .response
            )

class WishDeleteIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("WishDeleteIntent")(handler_input)

    def handle(self, handler_input):
        _ = handler_input.attributes_manager.request_attributes["_"]
        request_envelope = handler_input.request_envelope;
        logger.info(request_envelope.request, exc_info=True);
        speak_output = ''

        attributes_manager = AttributesManager(
            request_envelope=request_envelope,
            persistence_adapter=adapter
        )
        persistence_attr = attributes_manager.persistent_attributes
        person_id = ''
        logger.info(request_envelope.context.system, exc_info=True);
        if request_envelope.context.system.person is None:
            # パーソナライズ無効
            speak_output = _(data.WISH_DELETE_NOT_PERSONALIZE)
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
        else:
            person_id = request_envelope.context.system.person.person_id;

        # 親か子か
        personClass = ''
        if 'personClass' in persistence_attr[person_id]:
            personClass = persistence_attr[person_id]['personClass']
        else:
            return AnswerClassIntentHandler(AbstractRequestHandler).handle(handler_input)
        
        confirm = '消しません'
        resolved_value = get_resolved_value(
            handler_input.request_envelope.request, "confirm")
        resolved_id = get_resolved_id(
            handler_input.request_envelope.request, "confirm")
        if (resolved_value is not None):
            # Dialogを用いてるので原則として値は入ってくる
            confirm = resolved_value

        if confirm == '消します' and 'wish' in persistence_attr[person_id]:
            del(persistence_attr[person_id]['wish'])
            speak_output = _(data.WISH_DELETE_YES_MSG).format(persistence_attr[person_id])
        elif confirm == '消します':
            speak_output = _(data.WISH_DELETE_NON_MSG).format(persistence_attr[person_id])
        else:
            speak_output = _(data.WISH_DELETE_NO_MSG).format(persistence_attr[person_id])

        attributes_manager.save_persistent_attributes()
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

class AnswerClassIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AnswerClassIntent")(handler_input)

    def handle(self, handler_input):
        _ = handler_input.attributes_manager.request_attributes["_"]
        request_envelope = handler_input.request_envelope;
        logger.info(request_envelope.context.system, exc_info=True);
        attributes_manager = AttributesManager(
            request_envelope=request_envelope,
            persistence_adapter=adapter
        )

        persistence_attr = attributes_manager.persistent_attributes

        speak_output = _(data.WELCOME_MESSAGE)
        person_id = ''
        if request_envelope.context.system.person is None:
            # パーソナライズ無効
            speak_output = _(data.ANSWER_CLASS_NOT_PERSONALIZE)
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
        else:
            person_id = request_envelope.context.system.person.person_id;

        if person_id not in persistence_attr:
            persistence_attr[person_id] = {}
        if 'personClass' in persistence_attr[person_id]:
            #登録済
            pass

        personCount = get_count_person(persistence_attr)
        resolved_value = get_resolved_value(
            handler_input.request_envelope.request, "class")
        subscription = is_skill_product(handler_input)
        if (resolved_value is not None and
                resolved_value == "パパ"):
            if personCount[0] < 1 or subscription == True:
                persistence_attr[person_id]['personClass'] = 'parent'
                speak_output = _(data.ANSWER_CLASS_IS_PARENT).format(person_id,person_id)
            else:
                speak_output = _(data.ANSWER_CLASS_LIMIT_MSG)
        else :
            if personCount[1] < 2 or subscription == True:
                persistence_attr[person_id]['personClass']= 'child'
                speak_output = _(data.ANSWER_CLASS_IS_CHILD).format(person_id)
            else:
                speak_output = _(data.ANSWER_CLASS_LIMIT_MSG)

        attributes_manager.save_persistent_attributes()
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class PremiumInfoIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PremiumInfoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.PREMIUM_INFO_MSG)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.HELP_MSG)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.GOODBYE_MSG)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = _(data.REFLECTOR_MSG).format(intent_name)

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.ERROR)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        i18n = gettext.translation(
            'data', localedir='locales', languages=[locale], fallback=True)
        handler_input.attributes_manager.request_attributes["_"] = i18n.gettext

class PremiumInfoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PremiumInfoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput, Exception) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]

        speak_output = _(data.PREMIUM_INFO_MSG)
        reprompt = speak_output 
        return handler_input.response_builder.speak(speak_output).ask(
            reprompt).response

class ShoppingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ShoppingIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput, Exception) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        logger.info("In ShoppingHandler")

        if is_skill_product(handler_input):
            speak_output = _(data.SHOPPING_T_MSG)
        else:
            speak_output = _(data.SHOPPING_F_MSG)
        reprompt = speak_output 
        return handler_input.response_builder.speak(speak_output).ask(
            reprompt).response

class BuyIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BuyIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        logger.info("In BuyHandler")

        # Inform the user about what products are available for purchase
        in_skill_response = in_skill_product_response(handler_input)
        if in_skill_response:
            product_name = get_resolved_value(
                handler_input.request_envelope.request, "productName")

            # No entity resolution match
            if product_name is None:
                product_name = "パパの目安箱のプレミアム機能"
            else:
                product_name = "パパの目安箱のプレミアム機能"

            product = [l for l in in_skill_response.in_skill_products
                       if l.reference_name == product_name]
            return handler_input.response_builder.add_directive(
                SendRequestDirective(
                    name="Buy",
                    payload={
                        "InSkillProduct": {
                            "productId": product[0].product_id
                        }
                    },
                    token="correlationToken")
            ).response

class CancelSubscriptionIntentHandler(AbstractRequestHandler):
    """
    Following handler demonstrates how Skills would receive Cancel requests
    from customers and then trigger a cancel request to Alexa
    User says: Alexa, ask premium facts to cancel <product name>
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CancelSubscriptionIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        logger.info("In CancelSubscriptionHandler")

        in_skill_response = in_skill_product_response(handler_input)
        if in_skill_response:
            product_name = get_resolved_value(
                handler_input.request_envelope.request, "productName")

            # No entity resolution match
            if product_name is None:
                product_name = "パパの目安箱のプレミアム機能"
            else:
                product_name = "パパの目安箱のプレミアム機能"

            product = [l for l in in_skill_response.in_skill_products
                       if l.reference_name == product_name]
            return handler_input.response_builder.add_directive(
                SendRequestDirective(
                    name="Cancel",
                    payload={
                        "InSkillProduct": {
                            "productId": product[0].product_id
                        }
                    },
                    token="correlationToken")
            ).response

class CancelResponseHandler(AbstractRequestHandler): 
    """This handles the Connections.Response event after a cancel occurs.""" 
    def can_handle(self, handler_input): 
        # type: (HandlerInput) -> bool 
        return (ask_utils.is_request_type("Connections.Response")(handler_input) and 
                handler_input.request_envelope.request.name == "Cancel") 
 
    def handle(self, handler_input): 
        # type: (HandlerInput) -> Response 
        logger.info("In CancelResponseHandler") 
        in_skill_response = in_skill_product_response(handler_input) 
        product_id = handler_input.request_envelope.request.payload.get( 
            "productId") 
 
        if in_skill_response: 
            product = [l for l in in_skill_response.in_skill_products 
                       if l.product_id == product_id] 
            logger.info("Product = {}".format(str(product))) 
            if handler_input.request_envelope.request.status.code == "200": 
                speech = "まだ機能が有効になっていません。次は何をなさいますか？"
                reprompt = speech 
                purchase_result = handler_input.request_envelope.request.payload.get( 
                        "purchaseResult") 
                purchasable = product[0].purchasable 
                if purchase_result == PurchaseResult.ACCEPTED.value: 
                    speech = ("キャンセルが完了しました。次は何をなさいますか？") 
                    reprompt = speech 
 
                if purchase_result == PurchaseResult.DECLINED.value: 
                    if purchasable == PurchasableState.PURCHASABLE: 
                        speech = "まだ機能が有効になっていません。次は何をなさいますか？"
                    else: 
                        speech = "次は何をなさいますか？"
                    reprompt = speech 
 
                return handler_input.response_builder.speak(speech).ask( 
                    reprompt).response 
            else: 
                logger.log("Connections.Response indicated failure. " 
                           "Error: {}".format( 
                    handler_input.request_envelope.request.status.message)) 
 
                return handler_input.response_builder.speak( 
                        "There was an error handling your cancellation " 
                        "request. Please try again or contact us for " 
                        "help").response 

class BuyResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after a buy occurs."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Buy")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In BuyResponseHandler")
        in_skill_response = in_skill_product_response(handler_input)
        product_id = handler_input.request_envelope.request.payload.get(
            "productId")

        if in_skill_response:
            product = [l for l in in_skill_response.in_skill_products
                       if l.product_id == product_id]
            logger.info("Product = {}".format(str(product)))
            if handler_input.request_envelope.request.status.code == "200":
                speech = None
                reprompt = None
                purchase_result = handler_input.request_envelope.request.payload.get(
                    "purchaseResult")
                if purchase_result == PurchaseResult.ACCEPTED.value:
                    speech = "{} が有効になっています。次は何をしますか？".format(product[0].name)
                    reprompt = speech
                elif purchase_result in (
                        PurchaseResult.DECLINED.value,
                        PurchaseResult.ERROR.value,
                        PurchaseResult.NOT_ENTITLED.value):
                    speech = "{} は有効になりませんでした。次は何をしますか？".format(product[0].name)
                    reprompt = "使い方を知りたい方は「ヘルプ」と言ってください。"
                elif purchase_result == PurchaseResult.ALREADY_PURCHASED.value:
                    logger.info("Already purchased product")
                    speech = "機能はすでに有効になっています。次は何をしますか？"
                    reprompt = "使い方を知りたい方は「ヘルプ」と言ってください。"
                else:
                    # Invalid purchase result value
                    logger.info("Purchase result: {}".format(purchase_result))
                    return CatchAllExceptionHandler().handle(handler_input)

                return handler_input.response_builder.speak(speech).ask(
                    reprompt).response
            else:
                logger.log("Connections.Response indicated failure. "
                           "Error: {}".format(
                    handler_input.request_envelope.request.status.message))

                return handler_input.response_builder.speak(
                    "There was an error handling your purchase request. "
                    "Please try again or contact us for help").response

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
#
def is_skill_product(handler_input):
        # Inform the user about what products are available for purchase
        in_skill_response = in_skill_product_response(handler_input)
        if in_skill_response:
            logger.info("in_skill_products: {}".format(in_skill_response.in_skill_products))
            purchasable = [l for l in in_skill_response.in_skill_products
                           if l.entitled == EntitledState.ENTITLED]
            logger.info("Purchase: {}".format(purchasable))

            if len(purchasable) > 0:
                return True
            else:
                return False

def in_skill_product_response(handler_input):
    """Get the In-skill product response from monetization service."""
    # type: (HandlerInput) -> Union[InSkillProductsResponse, Error]
    locale = handler_input.request_envelope.request.locale
    ms = handler_input.service_client_factory.get_monetization_service()
    return ms.get_in_skill_products(locale)

# Utility functions
def get_resolved_value(request, slot_name):
    """Resolve the slot name from the request using resolutions."""
    # type: (IntentRequest, str) -> Union[str, None]
    try:
        logger.info("resolve_value {} for request: {}".format(slot_name, request))
        return (request.intent.slots[slot_name].resolutions.
                resolutions_per_authority[0].values[0].value.name)
    except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
        logger.info("Couldn't resolve {} for request: {}".format(slot_name, request))
        logger.info(str(e))
        return None

def get_resolved_id(request, slot_name):
    """Resolve the slot name from the request using resolutions."""
    # type: (IntentRequest, str) -> Union[str, None]
    try:
        logger.info("resolve_id {} for request: {}".format(slot_name, request))
        return (request.intent.slots[slot_name].resolutions.
                resolutions_per_authority[0].values[0].value.id)
    except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
        logger.info("Couldn't resolve {} for request: {}".format(slot_name, request))
        logger.info(str(e))
        return None

def get_resolved_query(request, slot_name):
    """Resolve the slot name from the request using resolutions."""
    # type: (IntentRequest, str) -> Union[str, None]
    try:
        return (request.intent.slots[slot_name].value)
    except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
        logger.info("Couldn't resolve {} for request: {}".format(slot_name, request))
        logger.info(str(e))
        return None
    
def get_count_person(persistence_attr):
    personClass = [0,0]
    for person_id in persistence_attr:
        if 'personClass' not in persistence_attr[person_id]:
            pass
        elif 'parent' == persistence_attr[person_id]['personClass']:
            personClass[0] += 1
        elif 'child' == persistence_attr[person_id]['personClass']:
            personClass[1] += 1
    return personClass

sb = StandardSkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(WishAddIntentHandler())
sb.add_request_handler(WishListIntentHandler())
sb.add_request_handler(WishDeleteIntentHandler())
sb.add_request_handler(AnswerClassIntentHandler())
sb.add_request_handler(PremiumInfoIntentHandler())
sb.add_request_handler(ShoppingIntentHandler())
sb.add_request_handler(BuyIntentHandler())
sb.add_request_handler(CancelSubscriptionIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(BuyResponseHandler())
sb.add_request_handler(CancelResponseHandler())
# make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
sb.add_request_handler(IntentReflectorHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
