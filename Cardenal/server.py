# -*- coding: utf-8 -*-
import logging
from functools import wraps
from telegram import ReplyKeyboardMarkup
from telegram.ext import (BaseFilter,
                          Updater,
                          CommandHandler,
                          MessageHandler,
                          ConversationHandler,
                          RegexHandler,
                          Filters)
from telegram.error import TimedOut
from peewee import DoesNotExist
from .models import User, Generator, Subscriptions, init_db
from .zmq_server import CardenalZmqServer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
MAIN_MENU, SUBSCRIBE, UNSUBSCRIBE = range(3)


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
                Subscriptions.create(user=user.id, generator=g.id)

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

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start',
                                         self.start,
                                         pass_user_data=True)],
            states={
                MAIN_MENU: [RegexHandler('^(Subscribe|Unsubscribe|Get\ me\ out\ from\ here)$',
                                         self.main_menu,
                                         pass_user_data=True)],
                SUBSCRIBE: [MessageHandler(Filters.text,
                                           self.subscribe,
                                           pass_user_data=True),
                            CommandHandler('skip', self.skip)],
                UNSUBSCRIBE: [MessageHandler(Filters.text,
                                             self.unsubscribe,
                                             pass_user_data=True),
                              CommandHandler('skip', self.skip)],
            },
            fallbacks=[CommandHandler('cancel', self.error)]
        )

        self._dp.add_handler(conv_handler)

    def get_generator(self, generator_name):
        generator, created = Generator.get_or_create(
            name=generator_name,
        )

        if created:
            self.logger.info("Nuevo Generator creado: {0}".format(generator_name))

        return generator

    def get_all_generators(self):
        """Get all generators created"""
        query = Generator.select()

        if query.exists():
            return [u for u in query]

    def get_generators_subscribed(self, user_id):
        """Find generators which ``user_id`` is subscribed"""

        query = Subscriptions.select(Subscriptions.generator).where(
            (Subscriptions.user == user_id)
        )

        if query.exists():
            return [subscription.generator for subscription in query]

    def get_users_subscribed(self, generator_id):
        """Find users susbcribed to the Generator ``generator_id``"""

        query = Subscriptions.select(Subscriptions.user).where(
            (Subscriptions.generator == generator_id)
        )

        if query.exists():
            return [subscription.user for subscription in query]

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
    def start(self, bot, update, user_data):
        msg = 'Welcome {0}... Thanks for using Cardenal. \n\n'.format(
            user_data['user'].first_name)
        generators_subscribed = self.get_generators_subscribed(user_data['user'].id)
        if generators_subscribed:
            msg = 'Now you are subscribed to {0} generators:\n{1}\n\n'.format(
                len(generators_subscribed),
                '\n'.join([g.name for g in generators_subscribed]))
        else:
            msg += 'You are not subscribed to any generator.\n'
        msg += '¿What do you want to do?'
        keyboard = [['Subscribe'], ['Unsubscribe'], ['Get me out from here']]
        bot.sendMessage(chat_id=update.message.chat.id,
                        text=msg,
                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return MAIN_MENU

    def main_menu(self, bot, update, user_data):
        if update.message.text == 'Subscribe':
            keyboard = [[g.name] for g in self.get_all_generators()] + [['\skip']]
            msg = 'Please select the generators you want to SUBSCRIBE.'
            rta = SUBSCRIBE
            update.message.reply_text(msg,
                                      reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        elif update.message.text == 'Unsubscribe':
            keyboard = [[g.name] for g in self.get_generators_subscribed(user_data['user'].id)] + [['\skip']]
            msg = 'Please select the generators you want to UNSUBSCRIBE.'
            rta = UNSUBSCRIBE
            update.message.reply_text(msg,
                                      reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        elif update.message.text == 'Get me out from here.':
            update.message.reply_text('OK. Bye!')
            rta = ConversationHandler.END
        return rta

    def skip(self, bot, update):
        msg = '¿What do you want to do?'
        keyboard = [['Subscribe'], ['Unsubscribe'], ['Get me out from here.']]
        bot.sendMessage(chat_id=update.message.chat.id,
                        text=msg,
                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return MAIN_MENU

    def subscribe(self, bot, update, user_data):
        try:
            generator = Generator.get(Generator.name == update.message.text)
            subscription, created = Subscriptions.get_or_create(
                user=user_data['user'].id,
                generator=generator.id,
            )
            if created:
                generators_subscribed = self.get_generators_subscribed(user_data['user'].id)
                if generators_subscribed:
                    msg = 'Now you are subscribed to {0} generators:\n{1}\n\n'.format(
                        len(generators_subscribed),
                        '\n'.join([g.name for g in generators_subscribed]))
                else:
                    msg = 'Now you are not subscribed to any generator.\n'
            else:
                msg = "Mmmm... You already subscribed to generator {}".format(generator.name)
        except DoesNotExist:
            msg = "UPS!... I have no generators with the name {}".format(generator.name)

        msg += '\n\n¿What else do you want to do?'
        keyboard = [['Subscribe'], ['Unsubscribe'], ['Get me out from here.']]
        bot.sendMessage(chat_id=update.message.chat.id,
                        text=msg,
                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return MAIN_MENU

    def unsubscribe(self, bot, update, user_data):
        try:
            generator = Generator.get(Generator.name == update.message.text)
        except DoesNotExist:
            msg = "UPS!... I have no generators with the name {}".format(generator.name)

        try:
            subscription = Subscriptions.get(
                user=user_data['user'].id,
                generator=generator.id,
            )
            subscription.delete_instance()
            generators_subscribed = self.get_generators_subscribed(user_data['user'].id)
            if generators_subscribed:
                msg = 'Now you are subscribed to {0} generators:\n{1}\n\n'.format(
                    len(generators_subscribed),
                    '\n'.join([g.name for g in generators_subscribed]))
            else:
                msg = 'Now you are not subscribed to any generator.\n'
        except DoesNotExist:
            msg = "Mmmm... You are not subscribed to generator {}".format(generator.name)

        msg += '\n\n¿What else do you want to do?'
        keyboard = [['Subscribe'], ['Unsubscribe'], ['Get me out from here.']]
        bot.sendMessage(chat_id=update.message.chat.id,
                        text=msg,
                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return MAIN_MENU

    def error(self, bot, update, error):
        self.logger.warn('Update "%s" caused error "%s"' % (update, error))

    def run(self):
        self.logger.info("Iniciando servidor")
        self._zmq_server.start()
        self._updater.start_polling()
        self._updater.idle()
