# -*- coding: utf-8 -*-
import logging
from functools import wraps
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Job, Filters
from telegram.error import TimedOut
from models import User
from zmq_server import CardenalZmqServer
from utils import logger

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def check_auth(func):
    @wraps(func)
    def wrapped(self, bot, update, user_data, *args, **kwargs):
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
        return func(self, bot, update, user_data, *args, **kwargs)
    return wrapped


class Cardenal(object):

    def __init__(self,
                 bot_key,
                 notification_period=1,
                 command_port=6666,
                 command_poller_timeout=5,
                 log_lvl='INFO'):
        self.logger = logging.getLogger('Cardenal.server')
        self.logger.setLevel(log_lvl)
        self._zmq_server = CardenalZmqServer(
            command_port=command_port
            command_poller_timeout=command_poller_timeout,
            log_lvl=log_lvl)
        self._updater = Updater(bot_key)
        self._dp = self._updater.dispatcher

        self._dp.job_queue.run_repeating(
            self.check_for_notifications,
            notification_period
        )

        self._dp.add_handler(CommandHandler(
            "start",
            self.start,
            pass_user_data=True))
        self._dp.add_handler(MessageHandler(
            Filters.text,
            self.start,
            pass_user_data=True))
        self._dp.add_error_handler(self.error)

    def check_for_notifications(self, bot, job):
        users = User.select()
        while not self._zmq_server.msgs_queue.empty():
            msg = self._zmq_server.msgs_queue.get()
            user = users.where((User.id == msg['user_id']) | (User.username == msg['username'])).get()
            try:
                bot.sendMessage(
                    user.id,
                    text=msg['msg']
                )
            except TimedOut:
                logger.error('TimedOut error en mensaje {}'.format(msg))
                self._zmq_server.msgs_queue.put(msg)

    @check_auth
    def start(self, bot, update, user_data):
        msg = 'Bienvenido {0}... \n\n'.format(
            user_data['user'].first_name)
        msg += 'Tu información para generar notificaciones es la siguiente: \n'
        msg += ' ID: {} \n'.format(user_data['user'].id)
        msg += ' username: {} \n'.format(user_data['user'].username)
        update.message.reply_text(msg)

    def error(self, bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def run(self):
        self._zmq_server.start()
        self._updater.start_polling()
        self._updater.idle()
