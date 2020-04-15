import telegram
from telegram.ext import (Updater, MessageHandler,
                          CommandHandler, ConversationHandler, Filters)
import logging

import core
from supported_networks import SupportedNetworks
from config import telegram_token

updater = Updater(
    token=telegram_token,
    use_context=True,
)
dispatcher = updater.dispatcher
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

token_types = [network.name for network in SupportedNetworks]


def set_token(update, context):
    tokens_keyboard = [[token_type] for token_type in token_types]
    tokens_markup = telegram.ReplyKeyboardMarkup(
        tokens_keyboard,
        one_time_keyboard=True
    )
    update.message.reply_text(
        "Choose social network",
        reply_markup=tokens_markup
    )
    return "TOKEN_TYPE"


def token_type(update, context):
    token_type = update.message.text
    if token_type in token_types:
        context.user_data["token_type"] = SupportedNetworks[token_type]
        update.message.reply_text(
            "Enter API key: ",
            reply_markup=telegram.ReplyKeyboardRemove()
        )
        return "TOKEN_VALUE"
    else:
        context.message.reply_text("Unknown network")
        return ConversationHandler.END


def token_value(update, context):
    core.add_token(
        update.effective_chat.id,
        context.user_data["token_type"],
        update.message.text
    )
    update.message.reply_text("Token set successfully!")
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("Cancelled")
    return ConversationHandler.END


token_handler = ConversationHandler(
    entry_points=[CommandHandler('set_token', set_token)],
    states={
        "TOKEN_TYPE":
            [MessageHandler(
                Filters.regex('^({})$'.format("|".join(token_types))),
                token_type
            )],
        "TOKEN_VALUE":
            [MessageHandler(Filters.text, token_value)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
dispatcher.add_handler(token_handler)


def post(update, context):
    update.message.reply_text("Enter post text (or /cancel)")
    return "POST_TEXT"


def post_text(update, context):
    core.send_task(update.effective_chat.id, update.message.text)
    update.message.reply_text("Post sent")
    return ConversationHandler.END


post_handler = ConversationHandler(
    entry_points=[CommandHandler('send', post)],
    states={
        "POST_TEXT":
            [MessageHandler(Filters.text, post_text)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
dispatcher.add_handler(post_handler)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


dispatcher.add_error_handler(error)


def route(path):
    def route_decorator(function):
        def handler_function(update, context):
            chat_id = update.effective_chat.id
            response = function(chat_id, update.message.text)
            if response:
                context.bot.send_message(chat_id, response)

        dispatcher.add_handler(CommandHandler(path, handler_function))

    return route_decorator


@route("start")
def start(user_id, message):
    core.add_user(user_id)
    return ("Hi! Use this bot to send posts to multiple"
            " social networks. Use /help to see list of commands.")


@route("help")
def help(user_id, message):
    return (
        "/set_token add tokens\n"
        "/tokens view available tokens\n"
        "/send send post\n"
        "/history see post history"
    )


@route("tokens")
def get_tokens(user_id, message):
    def token_to_string(token):
        return "{}: {}...".format(
            SupportedNetworks(token.target).name,
            token.value[:3]
        )

    tokens = core.get_tokens(user_id)
    if tokens:
        return "\n".join(map(token_to_string, tokens))
    else:
        return "No tokens set. Use /set_token to add some"
