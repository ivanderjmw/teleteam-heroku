"""Controls the task views"""
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import Chat

from main_app.models import Task
from main_app.helpers import edit_assigned_users_query

import dateparser

def select_task(update, context):
    is_private_chat = update.effective_chat.type == Chat.PRIVATE
    try:
        query = update.callback_query

        task = Task.objects.get(id=int(query.data[len("TASK:"):]))

        query.edit_message_text(
            text=taskview_message(task, private_chat=is_private_chat),
            parse_mode=ParseMode.HTML, 
            reply_markup=taskview_keyboard(task)
        )

        context.bot.answer_callback_query(query.id)
    except Exception as e:
        print(e)

def taskview_keyboard(task):
    back = InlineKeyboardButton(text='Back', callback_data='tasklist')
    done = InlineKeyboardButton(text='Done', callback_data='DONE:'+str(task.id))
    edit = InlineKeyboardButton(text='Edit', callback_data='EDIT:'+str(task.id))

    inline_keyboard = [[back, done, edit]]

    return InlineKeyboardMarkup(inline_keyboard)

def taskview_message(task, private_chat=False, numbering=None):
    title = task.title
    usernames = []
    for user in task.assigned_users.all():
        usernames += [user.username]
    deadline = task.deadline.strftime('%b %d %Y')

    number = "" if numbering == None else str(numbering)+'. '

    if private_chat:
        if task.done:
            return f'<b>-- Done! --</b>\n{number}{title} - {task.group.chat_title}\n👥Assigned Users - {" ".join(usernames)}\n🗓Deadline - {deadline}'
        else:
            return f'<b>{number}{title} - {task.group.chat_title}</b>\n👥Assigned Users - {" ".join(usernames)}\n🗓Deadline - {deadline}'
    else:
        if task.done:
            return f'<b>-- Done! --</b>\n<b>{number}{title}</b>\nAssigned Users 👥{" ".join(usernames)}\nDeadline 🗓{deadline}'
        else:
            return f'<b>{number}{title}</b>\n👥Assigned Users - {" ".join(usernames)}\n🗓Deadline - {deadline}'

def set_done(update, context):
    try:
        # Gets the query
        query = update.callback_query

        # Cuts off the prefix, sets the task's state to done.
        task = Task.objects.get(id=query.data[len("DONE:"):])
        task.done = True
        task.save()

        # Gets the text for the task, for further implementation where user can undo the done.
        text = taskview_message(task)

        # Edit the inline message
        query.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=taskview_keyboard(task))

        # Returns a callback to the query
        context.bot.answer_callback_query(query.id, text="Task marked as done!")
    except Exception as e:
        print(e)


"""
EDIT TASK IMPLEMENTATION
"""

EDIT_NAME, EDIT_USERS, EDIT_DUE_DATE, EDIT_DELETE = "EDIT-name:", "EDIT-users:", "EDIT-duedate:", "EDIT-replace:"

def edit_name(update, context):
    print(context.chat_data)

    # Get the user reply (new name)
    new_task_name = update.message.text

    # Retrieve the chat data and get database object
    taskid = context.chat_data['taskid']
    task = Task.objects.get(id=taskid)
    
    # Change the title and save
    task.title = new_task_name
    task.save()

    # Reply to user that process is completed
    text = "✅Task saved!"

    # Send the message
    context.bot.sendMessage(update.message.chat_id, text=text)

    return ConversationHandler.END

def edit_due_date(update, context):
    """Handles the edit due date command"""
    print(context.chat_data)

    # Get the user reply (new name)
    new_task_due_date = dateparser.parse(update.message.text)

    if new_task_due_date is None or len(update.message.text) < 4:
        # Tell the user it's an invalid date and prompt again.
        text = "Invalid Date! Reenter a correct date"
        context.bot.sendMessage(update.message.chat_id, text=text)
        return

    # Retrieve the chat data and get database object
    taskid = context.chat_data['taskid']
    task = Task.objects.get(id=taskid)
    
    # Change the deadline and save
    task.deadline = new_task_due_date
    task.save()

    # Reply to user that process is completed
    text = "✅Task saved!"

    # Send the message
    context.bot.sendMessage(update.message.chat_id, text=text)

    return ConversationHandler.END

def edit_assigned_users(update, context):
    """Handles the edit due date command"""
    print("Edit assigned Users", context.chat_data)

    # Get the user reply (new name)
    assigned_users = update.message.text

    # Retrieve the chat data and get database object
    taskid = context.chat_data['taskid']
    
    # Create user list
    assigned_users_list = assigned_users.replace('@', '').split(' ')

    # Call the helper function
    print("Calling helper function")
    edit_assigned_users_query(taskid, assigned_users_list)

    # Reply to user that process is completed
    text = "✅Task saved!"

    # Send the message
    context.bot.sendMessage(update.message.chat_id, text=text)

    return ConversationHandler.END

def edit_task(update, context):
    """Creates the edit task page"""
    try:
        # Gets the query
        query = update.callback_query

        # Cuts the prefix
        taskid = query.data[len("EDIT:"):]

        # Get task object from database
        task = Task.objects.get(id=taskid)

        # Gets the text for the task, for further implementation where user can undo the done.
        text = taskview_message(task)

        # Generate buttons and Reply Keyboard
        editname = InlineKeyboardButton(text='Edit name', callback_data=EDIT_NAME+str(taskid))
        editdeadline = InlineKeyboardButton(text='Edit deadline', callback_data=EDIT_DUE_DATE+str(taskid))
        editusers = InlineKeyboardButton(text='Edit users', callback_data=EDIT_USERS+str(taskid))
        replace = InlineKeyboardButton(text='Delete', callback_data=EDIT_DELETE+str(taskid))
        back = InlineKeyboardButton(text='Back', callback_data=str(task.id))

        inline_keyboard = [[editname, editdeadline, editusers], [replace, back]]

        print("Now editing inline message")

        # Edit the inline message
        query.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(inline_keyboard))

        print("Now returning answer to callback query")

        # Returns a callback to the query
        context.bot.answer_callback_query(query.id)

    except Exception as e:
        print(e)

    return

def edit_methods(update, context):
    print("Edit Methods")

    # Retrieve the callback query
    query = update.callback_query

    # Get the task id
    method, taskid = query.data.split(':', 1)

    method += ':'

    # Store the taskid in the chat data
    context.chat_data.clear()
    context.chat_data['taskid'] = taskid
    print(context.chat_data)

    # Hardcode the methods
    if method == EDIT_NAME:
        # Ask for name edit
        text = "Send me the new name of the task."
    elif method == EDIT_DUE_DATE:
        # Edit due date
        text = "Send me the revised due date of the task."
    elif method == EDIT_USERS:
        # Edit users
        text = "To whom is the task supposed to be assigned?"
    elif method == EDIT_DELETE:
        # Delete task
        text = "The task is deleted"

        # Delete the task
        task = Task.objects.get(id=taskid)       
        task.delete()

        query.edit_message_text(text=text)

        return ConversationHandler.END
    else:
        # Go back to prev page
        return

    # Send the message
    query.edit_message_text(text=text)

    # Returns a callback to the query
    context.bot.answer_callback_query(query.id)

    # Go to the respective bot state
    return method

def edit_task(update, context):
    """Creates the edit task page"""
    try:
        # Gets the query
        query = update.callback_query

        # Split task id
        taskid = query.data[len("EDIT:"):]

        # Gets the task item
        task = Task.objects.get(id=taskid)

        # Gets the text for the task, for further implementation where user can undo the done.
        text = taskview_message(task)

        print("callback:", EDIT_NAME+str(taskid))

        # Generate buttons and Reply Keyboard
        editname = InlineKeyboardButton(text='Edit name', callback_data=EDIT_NAME+str(taskid))
        editdeadline = InlineKeyboardButton(text='Edit deadline', callback_data=EDIT_DUE_DATE+str(taskid))
        editusers = InlineKeyboardButton(text='Edit users', callback_data=EDIT_USERS+str(taskid))
        replace = InlineKeyboardButton(text='Delete task', callback_data=EDIT_DELETE+str(taskid))
        back = InlineKeyboardButton(text='Back', callback_data="TASK:"+str(taskid))

        inline_keyboard = [[editname, editdeadline, editusers], [replace, back]]

        print("Now editing inline message")

        # Edit the inline message
        query.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(inline_keyboard))

        print("Now returning answer to callback query")

        # Returns a callback to the query
        context.bot.answer_callback_query(query.id)

    except Exception as e:
        print(e)

    return

EDIT_TASK_CONVERSATION_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_task, pattern="EDIT:"), CallbackQueryHandler(edit_methods, pattern='EDIT-')],
    states={
        EDIT_NAME:[MessageHandler(Filters.text, edit_name)],
        EDIT_DUE_DATE:[MessageHandler(Filters.text, edit_due_date)],
        EDIT_USERS:[MessageHandler(Filters.text, edit_assigned_users)],
    },
    fallbacks=[]
)