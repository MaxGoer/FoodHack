import telegram as tel
from telegram.ext import (Updater,
                          ConversationHandler,
                          CommandHandler,
                          MessageHandler,
                          Filters)
import Commands as Com
import DayCalc
import one_day as OD

users = {}

messages = {
    'gender': {
        'text': 'Твой пол?',
        'kb': [['Мужской', 'Женский']]
    },
    'age': {
        'text': 'Возраст?',
        'kb': [
            ['18-29'],
            ['30-39'],
            ['>40']
        ]
    },
    'activity': {
        'text': 'Занимаешься ли спортом?',
        'kb': [
            ['Практически нет'],
            ['Периодически'],
            ['Часто и много']
        ]
    },
    'cal_tracking': {
        'text': 'Следишь за потребляемыми калориями?',
        'kb': [['Да', 'Нет']],
        'nodes': (5, 6)
    },
    'track_target': {
        'text': 'С какой целью?',
        'kb': [['Хочу похудеть'],
               ['Хочу поддерживать текущий вес'],
               ['Хочу набрать массу']]
    }

}

MALE, FEMALE = 0, 1


# 1
def proc_gender(bot: tel.Bot, update: tel.Update, next_state: int):
    global users

    ##
    # Process answer
    answer = update.message.text

    if answer == messages['gender']['kb'][0][0]:
        users[update.message.chat_id]['gender'] = DayCalc.MALE
    elif answer == messages['gender']['kb'][0][1]:
        users[update.message.chat_id]['gender'] = DayCalc.FEMALE

    ##
    # Ask next
    bot.send_message(chat_id=update.message.chat_id,
                     text=messages['age']['text'],
                     reply_markup=tel.ReplyKeyboardMarkup(messages['age']['kb'],
                                                          one_time_keyboard=True))

    return next_state


# 2
def proc_age(bot: tel.Bot, update: tel.Update, next_state: int):
    global users

    ##
    # Process answer
    answer = update.message.text

    if answer == messages['age']['kb'][0][0]:
        users[update.message.chat_id]['age'] = 0
    elif answer == messages['age']['kb'][1][0]:
        users[update.message.chat_id]['age'] = 1
    elif answer == messages['age']['kb'][2][0]:
        users[update.message.chat_id]['age'] = 2

    ##
    # Ask next
    bot.send_message(chat_id=update.message.chat_id,
                     text=messages['activity']['text'],
                     reply_markup=tel.ReplyKeyboardMarkup(messages['activity']['kb'],
                                                          one_time_keyboard=True))

    return next_state


# 3
def proc_activity(bot: tel.Bot, update: tel.Update, next_state: int):
    global users

    ##
    # Process answer
    answer = update.message.text

    if answer == messages['activity']['kb'][0][0]:
        users[update.message.chat_id]['activity'] = DayCalc.NON_ACTIVE
    elif answer == messages['activity']['kb'][1][0]:
        users[update.message.chat_id]['activity'] = DayCalc.ACTIVE
    elif answer == messages['activity']['kb'][2][0]:
        users[update.message.chat_id]['activity'] = DayCalc.VERY_ACTIVE

    ##
    # Ask next
    bot.send_message(chat_id=update.message.chat_id,
                     text=messages['cal_tracking']['text'],
                     reply_markup=tel.ReplyKeyboardMarkup(messages['cal_tracking']['kb'],
                                                          one_time_keyboard=True))

    return next_state


# 4 or END
def proc_cal_tracking(bot: tel.Bot, update: tel.Update, next_state: int):
    global users

    ##
    # Process answer
    answer = update.message.text
    users[update.message.chat_id]['delta'] = DayCalc.DELTA_CAL if answer == messages['cal_tracking']['kb'][0][0] else 0

    ##
    # Do smth
    if answer == messages['cal_tracking']['kb'][0][0]:
        # A person tracks calories

        ##
        # Ask next
        bot.send_message(chat_id=update.message.chat_id,
                         text=messages['track_target']['text'],
                         reply_markup=tel.ReplyKeyboardMarkup(messages['track_target']['kb'],
                                                              one_time_keyboard=True))
        next_state = messages['cal_tracking']['nodes'][0]
    else:
        ##
        # End conversation
        print(DayCalc.get_nutrition(users[update.message.chat_id]))
        print(update.message.chat_id, ':', users[update.message.chat_id])


        next_state = messages['cal_tracking']['nodes'][1]
        get_breakfast(bot, update, next_state)

    return next_state


# 5
def proc_track_target(bot: tel.Bot, update: tel.Update, next_state: int):
    global users

    ##
    # Process answer
    answer = update.message.text
    # users[update.message.chat_id]['delta'] *= -1 if answer == messages['track_target']['kb'][0][0] else 1

    if answer == messages['track_target']['kb'][0][0]:
        users[update.message.chat_id]['delta'] *= -1

    elif answer == messages['track_target']['kb'][1][0]:
        users[update.message.chat_id]['delta'] *= 0

    elif answer == messages['track_target']['kb'][2][0]:
        users[update.message.chat_id]['delta'] *= 1

    print(update.message.chat_id, ':', users[update.message.chat_id])
    print(DayCalc.get_nutrition(users[update.message.chat_id]))
    get_breakfast(bot, update, next_state)
    return next_state


def cancel(bot: tel.Bot, update: tel.Update):
    update.message.reply_text(Com.messages['cancel'])
    return ConversationHandler.END


##
# Tastes

def get_tastes(bot: tel.Bot,
               update: tel.Update,
               next_state: int,
               query_key: str,
               next_msg: str=None,
               post_proc=None):
    global users
    users[update.message.chat_id][query_key] = update.message.text

    if next_state != ConversationHandler.END and next_msg is not None:
        ##
        # Ask next question

        update.message.reply_text(text=next_msg)

    print(update.message.chat_id, ':', users[update.message.chat_id])
    print(DayCalc.get_nutrition(users[update.message.chat_id]))

    if post_proc is not None:
        post_proc(bot, update)

    return next_state


def get_breakfast(bot: tel.Bot, update: tel.Update, next_state: int):
    update.message.reply_text(text='Напиши свои предпочтения на завтрак')
    return next_state


##
# Merge here with one_day.py
# and give results

def give_menu(bot: tel.Bot, update: tel.Update):

    nut = DayCalc.get_nutrition(users[update.message.chat_id])
    res = OD.menu(nut[DayCalc.CAL],
                  nut[DayCalc.PROT],
                  nut[DayCalc.FAT],
                  nut[DayCalc.HYD],
                  users[update.message.chat_id]['breakfast'],
                  users[update.message.chat_id]['dinner'],
                  users[update.message.chat_id]['supper'],
                  )

    template = '<a href="{}">{}</a>'
    links = []
    types = ('Завтрак', 'Обед', 'Ужин')
    cur = 0

    for rec in res:
        links.clear()
        links.append('<b>{}</b>'.format(types[cur]))

        if type(rec) is tuple or type(rec) is list:

            for r in rec:
                links.append(template.format('http://tvoirecepty.ru' + r[1], r[0]))

        else:
            links.append(template.format('http://tvoirecepty.ru' + rec[1], res[0]))

        msg = '<br>'.join(links)
        cur += 1

        update.message.reply_text(msg, parse_mode=tel.ParseMode.HTML)




    # res = 'RESULTS'
    # update.message.reply_text(res)


survey = ConversationHandler(
    entry_points=[CommandHandler('day', lambda bot, update: Com.day(bot, update, 1))],
    states={
        1: [
            MessageHandler(Filters.text,
                           callback=lambda bot, update: proc_gender(bot,
                                                                    update,
                                                                    2))
        ],
        2: [
            MessageHandler(Filters.text,
                           callback=lambda bot, update: proc_age(bot,
                                                                 update,
                                                                 3))
        ],
        3: [
            MessageHandler(Filters.text,
                           callback=lambda bot, update: proc_activity(bot,
                                                                      update,
                                                                      4))
        ],
        4: [
            MessageHandler(Filters.text,
                           callback=lambda bot, update: proc_cal_tracking(bot,
                                                                          update,
                                                                          5))
        ],
        5: [
            MessageHandler(Filters.text,
                           callback=lambda bot, update: proc_track_target(bot,
                                                                          update,
                                                                          6)),
        ],
        6: [
            MessageHandler(Filters.text,
                           callback=lambda bot, update: get_tastes(bot,
                                                                   update,
                                                                   7,
                                                                   'breakfast',
                                                                   'Напиши свои предпочтения на обед'))
        ],
        7: [
            MessageHandler(Filters.text,
                           callback=lambda bot, update: get_tastes(bot,
                                                                   update,
                                                                   8,
                                                                   'dinner',
                                                                   'Напиши свои предпочтения на ужин'))
        ],
        8: [
            MessageHandler(Filters.text,
                           callback=lambda bot, update: get_tastes(bot,
                                                                   update,
                                                                   ConversationHandler.END,
                                                                   'supper',
                                                                   post_proc=give_menu))
        ]
    },
    fallbacks=[
        CommandHandler('cancel', cancel)
    ]
)
