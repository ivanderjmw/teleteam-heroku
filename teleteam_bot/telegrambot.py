"""This is the main telegram bot module"""

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
    InlineQueryHandler,
)
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from django_telegrambot.apps import DjangoTelegramBot



import logging


from main_app.models import *
from .user_commands.create_task import CREATE_TASK_HANDLER
from .user_commands.help import help
from .user_commands.join import join
from .user_commands.start import start
from .user_commands.task_list import tasklist
from .user_commands.task_view import select_task, set_done, EDIT_TASK_CONVERSATION_HANDLER
from .user_commands.meeting import CREATE_MEETING_POLL_HANDLER,CREATE_MEETING_HANDLER, list_meetings, TelegramMeetingPoll
from .user_commands.reminders import delete_reminder, reminder_change_time, reminder_set_time, scan_and_send_reminders


import main_app.helpers as helpers

LOGGER = logging.getLogger('django')

def error(update, context):
    LOGGER.warn('Update "%s" caused error "%s"' % (update, context.error))

def main():
    LOGGER.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.TELEGRAM_BOT_TOKENS)
    # dp = DjangoTelegramBot.dispatcher
    dp = DjangoTelegramBot.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("join", join))
    dp.add_handler(CommandHandler("tasklist", tasklist))

    dp.add_handler(CREATE_TASK_HANDLER)
    dp.add_handler(CallbackQueryHandler(tasklist, pattern="tasklist"))
    dp.add_handler(CallbackQueryHandler(set_done, pattern="DONE:"))
    dp.add_handler(EDIT_TASK_CONVERSATION_HANDLER)
    dp.add_handler(CallbackQueryHandler(select_task, pattern="TASK:"))

    dp.add_handler(CREATE_MEETING_HANDLER)
    dp.add_handler(CREATE_MEETING_POLL_HANDLER)
    dp.add_handler(CommandHandler("meetinglist", list_meetings))

    dp.add_handler(CallbackQueryHandler(delete_reminder, pattern="REMINDER-DELETE:"))
    dp.add_handler(CallbackQueryHandler(reminder_change_time, pattern="REMINDER-CHANGETIME:"))
    dp.add_handler(CallbackQueryHandler(reminder_set_time, pattern="REMINDER-SETTIME:"))

    dp.add_handler(InlineQueryHandler(TelegramMeetingPoll.share, pattern='poll-'))
    dp.add_handler(CallbackQueryHandler(TelegramMeetingPoll.manage_vote, pattern='POLL:'))

    dp.add_error_handler(error)
