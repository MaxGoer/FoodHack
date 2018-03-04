import telegram as tel
from telegram.ext import (Updater,
                          ConversationHandler,
                          CommandHandler,
                          MessageHandler,
                          Filters)
import Survey
import Commands as Com
import scoring_merged as ML

config = {
    'token': '527042956:AAE_n2vDWIIcMAUexjntYUkhYy8swz1Y7Mw'
    # 'token': '521549592:AAED5PUsn3BrghF7PcfGKM7IMBpWSQgudrE'
}


def main():
    #ML.init()

    # Init Bot
    upd = Updater(token=config['token'])

    ##
    # Handlers

    upd.dispatcher.add_handler(CommandHandler('start', Com.startme))
    upd.dispatcher.add_handler(CommandHandler('help', Com.helpme))
    upd.dispatcher.add_handler(CommandHandler('day', Com.day))
    upd.dispatcher.add_handler(CommandHandler('week', Com.week))
    upd.dispatcher.add_handler(Survey.survey)

    ##
    # Run
    
    # Press ctrl + c to stop running
    upd.start_polling()
    upd.idle()


if __name__ == '__main__':
    main()
