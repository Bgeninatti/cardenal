# -*- coding: utf-8 -*-
import datetime
import logging
from functools import wraps
from playhouse.shortcuts import model_to_dict
from telegram.ext import Updater, CommandHandler, MessageHandler, Job, Filters
from models import User, Notificacion
from zmq_server import CardenalZmqServer

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

NOTIFICATIONS_PERIOD = 10
BOT_KEY = "439216016:AAHLviPHBfgnSCdRn8iZk8XtFkH5ZzvnfTk"


def check_auth(func):
    @wraps(func)
    def wrapped(bot, update, user_data, job_queue, *args, **kwargs):
        # extract user_id from arbitrary update
        try:
            user = update.message.from_user
        except (NameError, AttributeError):
            try:
                user = update.inline_query.from_user
            except (NameError, AttributeError):
                try:
                    user = update.chosen_inline_result.from_user
                except (NameError, AttributeError):
                    try:
                        user = update.callback_query.from_user
                    except (NameError, AttributeError):
                        logger.error('No hay user_id en el mensaje.')
                        return ConversationHandler.END

        user, created = User.get_or_create(
            id=user.id,
            username=user.username,
            last_name=user.last_name,
            first_name=user.first_name,
        )
        user_data['user'] = user
        return func(bot, update, user_data, job_queue, *args, **kwargs)
    return wrapped


class Cardenal(object):

    def __init__(self, bot_key=BOT_KEY):
        self.zmq_server = CardenalZmqServer()
        self.updater = Updater(bot_key)
        self.dp = self.updater.dispatcher

        self.dp.job_queue.run_repeating(
            self.check_for_notifications,
            NOTIFICATIONS_PERIOD
        )

        self.dp.add_handler(CommandHandler(
            "start",
            self.start,
            pass_user_data=True,
            pass_job_queue=True))
        self.dp.add_handler(MessageHandler(
            Filters.text,
            self.start,
            pass_user_data=True,
            pass_job_queue=True))
        self.dp.add_error_handler(self.error)

    def check_for_notifications(self, bot, job):
        users = User.select()
        new_msgs = self.zmq_server.check_msgs()
        logger.info(new_msgs)
        for m in new_msgs:
            user = users.where((User.id == m['user_id'])).get()
            bot.sendMessage(
                user.id,
                text=m['msg']
            )

    @check_auth
    def start(self, bot, update, user_data, job_queue):
        msg = 'Bienvenido {0}... \n\n'.format(
            user_data['user'].first_name)
        msg += 'Tu información para generar notificaciones es la siguiente: \n'
        msg += ' ID: {} \n'.format(user_data['user'].id)
        msg += ' username: {} \n'.format(user_data['user'].username)
        update.message.reply_text(msg)

    def error(self, bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def run(self):
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    instance = Cardenal()
    instance.run()
