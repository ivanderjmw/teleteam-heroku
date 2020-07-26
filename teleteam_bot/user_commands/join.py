"""
Handles users to join the group 
"""

from main_app import helpers
from telegram import ParseMode

def join(update, context):
    helpers.join_group(update.effective_chat, update.message.from_user)

    text = f'Ok, @{update.message.from_user.username} is now registered in the group.'
    context.bot.sendMessage(update.message.chat_id, text=text, parse_mode=ParseMode.HTML)