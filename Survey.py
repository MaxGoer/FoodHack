import telegram as tel
from telegram.ext import (Updater,
                          ConversationHandler,
                          CommandHandler,
                          MessageHandler,
                          Filters)
import Commands as Com
import scoring_merged as ML

user_data = {}


##
# Input data processing

# gimme processing
def proc_gimme(bot: tel.Bot, update: tel.Update, next_state: int):
    query = update.message.text

    ###
    # Process

    res = ML.get_recipe(query)
    r_name = res[0]
    r_url = res[1]
    link = '<a href="{}">{}</a>'.format('http://tvoirecepty.ru' + res[1], res[0])

    ##
    # Answer
    update.message.reply_text(Com.messages['gimme']['answer'].format(link), parse_mode=tel.ParseMode.HTML)
    return next_state


##
# Survey

survey = ConversationHandler(
    entry_points=[CommandHandler('gimme', lambda bot, update: Com.gimme(bot, update, 1))],
    states={
        1: [
            MessageHandler(Filters.text,
                           callback=lambda bot, update: proc_gimme(bot,
                                                                   update,
                                                                   ConversationHandler.END))
        ]
    },
    fallbacks=[
        CommandHandler('cancel', Com.cancel)
    ]
)
