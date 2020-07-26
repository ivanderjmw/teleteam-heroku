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

def set_reminder_to_users(recipients, meeting, task, update_fields=[], type=MEETING):
    """Given a list of recipient users, send a reminder for a meeting or task."""
    try:
        for recipient in recipients:
            reminder = Reminder(reminding_type=type, recipient=recipient)

            if type == MEETING:
                reminder.meeting = meeting
                reminder.time = meeting.time - recipient.settings.defaultMeetingReminderTimedelta
            else:
                reminder.task = task
                reminder.time = task.deadline - recipient.settings.defaultTaskReminderTimedelta

            reminder.save()

            # Notify the user via a private chat that a reminder has been set
            reminder_set_notification(reminder, update_fields)
        
    except Exception as e:
        print(e)

def display_reminder_text(reminder, message, new_reminder=False):
    #TODO: Clean up this mess.

    if message is not None:
        text = message + "\n\n"
    else:
        text = ""

    if reminder.reminding_type == TASK:
        text += "<b>" + reminder.task.title + "</b>"
        event_time = reminder.task.deadline
        text += "\ndue "
    else:
        text += "<b>" + reminder.meeting.title + "</b>"
        event_time = reminder.meeting.time
        text += "\n⏱: "
    
    if arrow.get(reminder.time).to("Asia/Singapore") < arrow.now().shift(hours=12):
        text += arrow.get(event_time).to("Asia/Singapore").humanize(granularity=["hour", "minute"])
        humanized_reminder_time = arrow.get(reminder.time).to("Asia/Singapore").humanize(granularity=["hour", "minute"])
    else:
        text += arrow.get(event_time).to("Asia/Singapore").format("HH:mm dddd, D MMM YYYY")
        humanized_reminder_time = arrow.get(reminder.time).to("Asia/Singapore").format("HH:mm dddd, D MMM YYYY")

    if new_reminder:
        text += "\n\nwe will remind you: " + humanized_reminder_time

    return text

def reminder_set_notification(reminder, update_fields):
    dp = DjangoTelegramBot.dispatcher

    if reminder.reminding_type == TASK:
        if (update_fields == []):
            message = "You have been assigned a task in the group \"" + reminder.task.group.chat_title + "\"\n"
        else:
            message = "Task updated in the group \"" + reminder.task.group.chat_title + "\"\n"
    else:
        if (update_fields == []):
            message = "New meeting in the group \"" + reminder.meeting.group.chat_title + "\""
        else:
            message = "Meeting updated in the group \"" + reminder.meeting.group.chat_title + "\"\n"
    text = display_reminder_text(reminder, message, new_reminder=True)

    reply_markup = display_reminder_keyboard(reminder)
    dp.bot.send_message(reminder.recipient.user_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

def display_reminder_keyboard(reminder):
    cancel_reminder = InlineKeyboardButton(text="🗑 Delete reminder", callback_data="REMINDER-DELETE:"+str(reminder.id))
    change_date = InlineKeyboardButton(text="⏱ Change time", callback_data="REMINDER-CHANGETIME:"+str(reminder.id))

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
    
    text = display_reminder_text(reminder, message="Reminder time settings changed!", new_reminder=True)
    
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
        if arrow.get(reminder.time).to('Asia/Singapore') <= arrow.now().to('Asia/Singapore'):
            dp.bot.send_message(
                reminder.recipient.user_id,
                parse_mode=ParseMode.HTML,
                text=display_reminder_text(reminder, message="Reminder:"))
            reminder.delete()
