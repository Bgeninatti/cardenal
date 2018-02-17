# -*- coding: utf-8 -*-
import datetime
import logging
from functools import wraps
from playhouse.shortcuts import model_to_dict
from telegram.ext import Updater, CommandHandler, MessageHandler, Job, Filters
from models import User, Notificacion

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

NOTIFICATIONS_PERIOD = 10


def check_for_notifications(bot, job):
    user = User.get(User.id == job.context['id'])
    for s in user.notificaciones:
        if not s.notified:
            bot.sendMessage(
                user.id,
                text=s.msg
            )
            s.notified = True
            s.notified_timestamp = datetime.datetime.now()
            s.save()


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
        if created:
            dp.job_queue.run_repeating(
                check_for_notifications,
                NOTIFICATIONS_PERIOD,
                context=model_to_dict(user_data['user'])
            )
        return func(bot, update, user_data, job_queue, *args, **kwargs)
    return wrapped


@check_auth
def start(bot, update, user_data, job_queue):
    msg = 'Bienvenido {0}... \n\n'.format(
        user_data['user'].first_name)
    msg += 'Tu información para generar notificaciones es la siguiente: \n'
    msg += ' ID: {} \n'.format(user_data['user'].id)
    msg += ' username: {} \n'.format(user_data['user'].username)
    update.message.reply_text(msg)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("439216016:AAHLviPHBfgnSCdRn8iZk8XtFkH5ZzvnfTk")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    for p in User.select():
        dp.job_queue.run_repeating(
            check_for_notifications,
            NOTIFICATIONS_PERIOD,
            context=model_to_dict(p)
        )

    dp.add_handler(CommandHandler(
        "start",
        start,
        pass_user_data=True,
        pass_job_queue=True))
    dp.add_handler(MessageHandler(
        Filters.text,
        start,
        pass_user_data=True,
        pass_job_queue=True))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
