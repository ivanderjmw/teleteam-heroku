from main_app.models import TASK, MEETING, Reminder
from django_telegrambot.apps import DjangoTelegramBot

from main_app import helpers

import re

import arrow
from datetime import datetime, timedelta

from django.utils.timezone import make_aware

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

DELETED = 1

REMINDER_SCHEDULE_OPTIONS = [
    ["5 minutes before", 5],
    ["15 minutes before", 15],
    ["1 hour before", 60],
    ["3 hours before", 180],
    ["6 hours before", 360]
]

def display_reminder_text(reminder, message, new_reminder=False):
    if message is not None:
        text = message + "\n"
    else:
        text = ""

    if reminder.reminding_type == TASK:
        text += "<b>" + reminder.task.title + "</b>"
        text += "\ndue " + arrow.get(reminder.task.deadline).format(arrow.FORMAT_COOKIE)
    else:
        text += "<b>" + reminder.meeting.title + "</b>"
        text += "\ntime: <b>" + arrow.get(reminder.meeting.time).format(arrow.FORMAT_COOKIE) + "</b>"
        if new_reminder:
            text += "\nwe will remind you at: " + arrow.get(reminder.time).format(arrow.FORMAT_COOKIE)
        else:
            text += "\n" + arrow.get(reminder.time).humanize()

    return text

def reminder_set_notification(reminder):

    dp = DjangoTelegramBot.dispatcher

    if reminder.reminding_type == TASK:
        message = "You have been assigned a task in the group \"" + reminder.task.group.chat_title + "\"\n"
    else:
        message = "New meeting in the group \"" + reminder.meeting.group.chat_title + "\""
    text = display_reminder_text(reminder, message, new_reminder=True)

    reply_markup = display_reminder_keyboard(reminder)
    dp.bot.send_message(reminder.recipient.user_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

def display_reminder_keyboard(reminder):
    cancel_reminder = InlineKeyboardButton(text="No need to remind me!", callback_data="REMINDER-DELETE:"+str(reminder.id))
    change_date = InlineKeyboardButton(text="Change time", callback_data="REMINDER-CHANGETIME:"+str(reminder.id))

    return InlineKeyboardMarkup([[cancel_reminder, change_date]])

def delete_reminder(update, context):
    query = update.callback_query

    reminder_id = int(query.data[len("REMINDER-DELETE:"):])

    reminder = Reminder.objects.get(id=reminder_id)

    query.edit_message_text(
        text=display_reminder_text(reminder, message="Reminder deleted!"), 
        parse_mode=ParseMode.HTML
    )

    reminder.delete()
    context.bot.answer_callback_query(query.id, text="Reminder deleted!")

def reminder_change_time(update, context):
    query = update.callback_query

    reminder_id = query.data[query.data.rindex(':')+1:]

    try:
        reminder = Reminder.objects.get(id=reminder_id)
    except Exception as e:
        print(e)

    query.edit_message_text(
        text=display_reminder_text(reminder, message="When do you want the reminder to be sent?"), 
        parse_mode=ParseMode.HTML, 
        reply_markup=reminder_change_time_keyboard(reminder)
    )

def reminder_change_time_keyboard(reminder):
    buttons = []
    for option in REMINDER_SCHEDULE_OPTIONS:
        buttons += [[InlineKeyboardButton(text=option[0], callback_data="REMINDER-SETTIME:"+str(reminder.id)+":"+str(option[1]))]]

    return InlineKeyboardMarkup(buttons)

def reminder_set_time(update, context):
    query = update.callback_query

    s = query.data
    reminder_id = int(s[s.find(':')+1:s.rfind(':')])
    time_option_minutes = int(query.data[query.data.rindex(':')+1:])

    try:
        reminder = Reminder.objects.get(id=reminder_id)
    except Exception as e:
        print(e)

    if reminder.reminding_type == TASK:
        reminder.time = reminder.task.deadline - timedelta(minutes=time_option_minutes)
    else:
        reminder.time = reminder.meeting.time - timedelta(minutes=time_option_minutes)
    
    text = display_reminder_text(reminder, message="Reminder time settings changed!")
    
    reminder.save()

    context.bot.answer_callback_query(query.id, text="Reminder time settings changed!")
    query.edit_message_text(
        text=text, 
        parse_mode=ParseMode.HTML,
        reply_markup=display_reminder_keyboard(reminder)
    )

def scan_and_send_reminders():
    dp = DjangoTelegramBot.dispatcher

    reminders = Reminder.objects.all()

    for reminder in reminders:
        if reminder.time <= make_aware(datetime.now()):
            dp.bot.send_message(
                reminder.recipient.user_id,
                parse_mode=ParseMode.HTML,
                text=display_reminder_text(reminder, message="Reminder:"))
            reminder.delete()
