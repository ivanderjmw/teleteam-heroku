import time, threading
import os

from timeloop import Timeloop
from datetime import datetime, timedelta

from django_telegrambot.apps import DjangoTelegramBot
from main_app.models import *
from teleteam_bot.user_commands.reminders import scan_and_send_reminders

def setup_recurring_tasks():
    try:
        scan_and_send_reminders()
        threading.Timer(5, setup_recurring_tasks).start()
    except Exception as e:
        print(e)