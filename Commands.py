import telegram as tel
from telegram.ext import (Updater,
                          ConversationHandler,
                          CommandHandler,
                          MessageHandler,
                          Filters)

messages = {
    'start': '/gimme - подобрать что-нибудь по вкусу\n'
             '/day - меню на день\n'
             '/week - меню на неделю\n'
             '/help - расскажу, что могу делать\n'
             'можно всегда остановиться с помощью /cancel\n',
    'help': '/gimme - подобрать что-нибудь по вкусу\n'
            '/day - меню на день\n'
            '/week - меню на неделю\n'
            '/help - расскажу, что могу делать\n'
            'можно всегда остановиться с помощью /cancel\n',
    'day': 'Не, мне лень',
    'week': 'Не, мне лень',
    'gimme': {
        'text': 'Опиши мне то, что хочешь',
        'answer': 'Я думаю, что {} подходит тебе лучше всего'
    },
    'cancel': 'Ладно, в другой раз'
}


def cancel(bot: tel.Bot, update: tel.Update):
    update.message.reply_text(messages['cancel'])
    return ConversationHandler.END


def startme(bot: tel.Bot, update: tel.Update):
    update.message.reply_text(messages['start'])


def helpme(bot: tel.Bot, update: tel.Update):
    update.message.reply_text(messages['help'])


def gimme(bot: tel.Bot, update: tel.Update, next_state: int):
    update.message.reply_text(messages['gimme']['text'])
    return next_state


def day(bot: tel.Bot, update: tel.Update):
    update.message.reply_text(messages['day'])


def week(bot: tel.Bot, update: tel.Update):
    update.message.reply_text(messages['week'])
