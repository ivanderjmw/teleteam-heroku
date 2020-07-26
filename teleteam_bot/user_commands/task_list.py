from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Chat

from main_app import helpers
from teleteam_bot.user_commands import task_view

def tasklist(update, context):

    query = update.callback_query

    if update.effective_chat.type == Chat.PRIVATE:
        text = "Here are all of your tasks:\n\n"
        private_chat=True
    else:
        text = "Here are the group's tasks:\n\n"
        private_chat=False

    tasks = helpers.list_tasks(update.effective_chat, private_chat)

    if private_chat and (query == None or len(query.data) == len("tasklist")):
        user_settings = helpers.get_user_settings(chat=update.effective_chat)
        detailed_view = user_settings.botDetailedViewOnDefault
    else:
        detailed_view = query != None and query.data[len("tasklist"):] == ":detailedview"

    if detailed_view:
        count = 1
        for task in tasks: 
            if task.done == False:
                text += task_view.taskview_message(task, private_chat=private_chat, numbering=count) + "\n\n"
                count += 1

    reply_markup = tasklist_keyboard(tasks, private_chat, detailed_view=detailed_view)

    if(query is not None):
        query.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        context.bot.answer_callback_query(query.id)
    else:
        context.bot.sendMessage(update.message.chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

def tasklist_keyboard(tasks, private_chat, detailed_view=False):
    inline_keyboard = []

    # List down uncompleted tasks only.
    if detailed_view:
        count = 1
        for task in tasks:
            if (count-1)%5==0:
                inline_keyboard += [[InlineKeyboardButton(text=count, callback_data="TASK:"+str(task.id))]]
            else:
                inline_keyboard[-1] += [InlineKeyboardButton(text=count, callback_data="TASK:"+str(task.id))]
            count += 1
    else:
        for task in tasks:
            inline_keyboard += [[InlineKeyboardButton(text=task.title, callback_data="TASK:"+str(task.id))]]

    add_task_button = InlineKeyboardButton(text="➕ Add task", callback_data="createtask")
    if not private_chat:
        inline_keyboard += [[add_task_button]]
    else:
        text = "🕶 Hide details" if detailed_view else "👀 See details"
        callback_data = "tasklist:buttonsview" if detailed_view else "tasklist:detailedview"
        detailed_view_button = InlineKeyboardButton(text=text, callback_data=callback_data)
        inline_keyboard += [[detailed_view_button]]

    return InlineKeyboardMarkup(inline_keyboard)