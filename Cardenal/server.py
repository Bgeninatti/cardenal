# -*- coding: utf-8 -*-
import logging
from functools import wraps
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Job, Filters
from telegram.error import TimedOut
from .models import User, Generator, Suscriptions, init_db
from .zmq_server import CardenalZmqServer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def check_auth(func):
    @wraps(func)
    def wrapped(self, bot, update, user_data, *args, **kwargs):
        # extract user_id from arbitrary update
        try:
            user = update.message.from_user
        except (NameError, AttributeError):
            self.logger.error('No hay user_id en el mensaje.')
            return ConversationHandler.END
        user, created = User.get_or_create(
            id=user.id,
            last_name=user.last_name,
            first_name=user.first_name,
        )
        if created:
            generators = Generator.select()
            for g in generators:
                Suscriptions.create(user=user.id, generator=g.id)

            self.logger.info(
                "Usuario {0} creado y suscripto a {1} generadores".format(
                    user.id, generators.count()))

        user_data['user'] = user
        return func(self, bot, update, user_data, *args, **kwargs)
    return wrapped


class Cardenal(object):

    def __init__(self,
                 bot_key,
                 db_path,
                 notification_period=1,
                 command_port=6666,
                 command_poller_timeout=5,
                 log_lvl='INFO'):
        self.logger = logging.getLogger('Cardenal.server')
        self.logger.setLevel(log_lvl)

        init_db(db_path)

        self._zmq_server = CardenalZmqServer(
            command_port=command_port,
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
            self._start,
            pass_user_data=True))
        self._dp.add_handler(MessageHandler(
            Filters.text,
            self._start,
            pass_user_data=True))
        self._dp.add_error_handler(self._error)

    def get_generator(self, generator_name):
        generator, created = Generator.get_or_create(
            name=generator_name,
        )

        if created:
            self.logger.info("Nuevo Generator creado: {0}".format(generator_name))

        return generator

    def get_users_subscribed(self, generator_id):
        """Find users susbcribed to the Generator ``generator_id``"""

        query = Suscriptions.select(Suscriptions.user).where(
            (Suscriptions.generator == generator_id)
        )

        if query.exists():
            return [susbcription.user for susbcription in query]

    def check_for_notifications(self, bot, job):
        while not self._zmq_server.msgs_queue.empty():
            msg = self._zmq_server.msgs_queue.get()
            generator = self.get_generator(msg["generator"])
            users = self.get_users_subscribed(generator.id)
            if users:
                for user in users:
                    try:
                        self.logger.info("Enviando mensaje a {0}.".format(user.id))
                        bot.sendMessage(
                            user.id,
                            text=msg['msg']
                        )
                    except TimedOut:
                        self.logger.error('Timeout enviando el mensaje {0}'.format(msg))
                        #self._zmq_server.msgs_queue.put(msg)
            else:
                error = 'El Generador {} no tiene Usuarios suscriptos'.format(msg['generator'])
                self.logger.error(error)

    @check_auth
    def _start(self, bot, update, user_data):
        msg = 'Bienvenido {0}... \n\n'.format(
            user_data['user'].first_name)
        msg += 'Tu información para generar notificaciones es la siguiente: \n'
        msg += ' ID: {} \n'.format(user_data['user'].id)
        update.message.reply_text(msg)

    def _error(self, bot, update, error):
        self.logger.warn('Update "%s" caused error "%s"' % (update, error))

    def run(self):
        self.logger.info("Iniciando servidor")
        self._zmq_server.start()
        self._updater.start_polling()
        self._updater.idle()
