"""Create task command"""
import dateparser
import datetime

from main_app.helpers import create_task 
from main_app.models import Task, TaskSession, User, Group 
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import ParseMode

import logging

LOGGER = logging.getLogger('django')

GET_TITLE, GET_USERS, GET_DUE_DATE = range(3)

def create_new_task(update, context):

    chat_id = update.effective_message.chat.id

    # Check if user has /join-ed.
    try:
        user_creating_task = User.objects.filter(user_id = update.effective_message.from_user.id)
        if not (user_creating_task in Group.objects.get(group_chat_id = chat_id).members.all()):
            raise KeyError
    except KeyError as e:
        context.bot.sendMessage(
            update.message.chat_id, 
            text='Please /join the group before starting the /createtask command.')
        return ConversationHandler.END

    LOGGER.info("User {} createtask: creates a new task in id={}".format(chat_id, chat_id))

    # Prompts the user to send the task name
    context.bot.sendMessage(chat_id, text="➡️ Let's create a new task! Now please send the name of the task.")
    
    # Queries the database
    try:
        newtask = TaskSession.objects.get(chat_id=chat_id)
        LOGGER.info("Task session already exists")
    except TaskSession.DoesNotExist:
        LOGGER.info("Creating a new task session")
        newtask = TaskSession(chat_id=chat_id)
    
    newtask.save()
    
    return GET_TITLE

def get_title(update, context):

    LOGGER.info("User {} createtask: gets title".format(update.message.from_user))

    # Gets the title, prompts for due date
    title = update.message.text

    # Queries the database
    newtask = TaskSession.objects.get(chat_id=update.effective_chat.id)
    LOGGER.info("Task: {}".format(str(newtask)))
    newtask.title = title
    newtask.save()

    text = "Task title is <b>{}</b>\nNow enter the due date. No specific format required.".format(title)
    context.bot.sendMessage(update.message.chat_id, text=text, parse_mode=ParseMode.HTML)
    
    return GET_DUE_DATE

def get_due_date(update, context):

    LOGGER.info("User {} createtask: gets due_date".format(update.effective_chat.username))

    # User inputs the Task due date, then prompts for users
    deadline = dateparser.parse(update.message.text)
    if deadline is None or len(update.message.text) < 4:
        context.bot.sendMessage(update.message.chat_id, text='‼️That\'s not a proper date, please reenter a valid date.')
        return GET_DUE_DATE
    
    # Queries the database
    newtask = TaskSession.objects.get(chat_id=update.effective_chat.id)
    newtask.deadline = deadline
    newtask.save()

    context.bot.sendMessage(update.message.chat_id, text=f'The due date of the task {newtask.title} is {deadline.strftime("%b %d %Y")},\nwho to assign this task?')
    return GET_USERS

def get_assigned_users(update, context):

    LOGGER.info("User {} createtask: gets users".format(update.effective_chat.username))

    # User inputs a list of users assigned, then confirms the task.
    assigned_users = update.message.text

    # Queries the database
    newtask = TaskSession.objects.get(chat_id=update.effective_chat.id)
    newtask.assigned_users = assigned_users
    newtask.save()

    # Create user list
    assigned_users_list = assigned_users.replace('@', '').split(' ')

    LOGGER.info("Call create_task")
    # Calls create_task
    try:
        create_task(newtask.chat_id, newtask.title, newtask.deadline, assigned_users_list)
        TaskSession.objects.filter(chat_id=update.effective_chat.id).delete()
    except Exception as e:
        LOGGER.info("{}".format(e))
        print(e)
        context.bot.sendMessage(update.message.chat_id, text="‼️Error. Either group or user is not registered yet. That user should enter the /join command and redo /createtask.")
        return ConversationHandler.END

    # Notify user the task created
    text = "📑 Tasked {} <b>{}</b> due {}".format(newtask.assigned_users, newtask.title, newtask.deadline.strftime('%b %d %Y'))
    context.bot.sendMessage(update.message.chat_id, text=text, parse_mode=ParseMode.HTML)

    # Delete the TaskSession
    newtask.delete()

    return ConversationHandler.END

def cancel_create_task(update, context):
    context.bot.sendMessage(update.message.chat_id, text="❌ Task creation cancelled.")

    try:
        TaskSession.objects.filter(chat_id=update.effective_chat.id).delete()
    except Exception:
        pass

    return ConversationHandler.END


CREATE_TASK_HANDLER = ConversationHandler(
    entry_points=[CommandHandler("createtask", create_new_task), 
                  CallbackQueryHandler(create_new_task, pattern="createtask"),
                  ],
    states={
        GET_TITLE: [CommandHandler("cancel", cancel_create_task), MessageHandler(Filters.text, get_title)],
        GET_USERS: [CommandHandler("cancel", cancel_create_task), MessageHandler(Filters.text, get_assigned_users)],
        GET_DUE_DATE: [CommandHandler("cancel", cancel_create_task), MessageHandler(Filters.text, get_due_date)],
    },
    fallbacks=[],
)

if __name__ == "__main__":
    print("Create Task Module {}".format(CREATE_TASK_HANDLER))