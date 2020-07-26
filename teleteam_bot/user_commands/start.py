"""
Starts accepting groups
"""
from main_app import helpers
from telegram import ParseMode

def start(update, context):
    try:
        print("start command is entered.")
        group = helpers.start_group(update.effective_chat, context.bot)
        if group is not None:
            text = f'👥Group <b>{group.chat_title}</b> has been created! Members can type /join to enter the group.\n\n🌐You can login to the teleteam website with your telegram account too, teleteam.herokuapp.com.\n\nSend /help for more details on the commands.'
        else:
            text = 'Looks like the group has already been initialised!'
    except Exception as e:
        print(e)

        if update.message.chat.type == 'group':
            text = '‼️Error, you are not in a valid telegram group.'
        else:
            text = '👋Hi, I am the teleteam bot. I can help with your task management! Simply invite me to your telegram group, then enter the /start command.\n\n🌐Use the online client at teleteam.herokuapp.com.\n\n☝️For any help, you can send /help both in private/group chats!'

    
    context.bot.sendMessage(update.message.chat_id, text=text, parse_mode=ParseMode.HTML)
