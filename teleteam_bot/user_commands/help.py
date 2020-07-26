from telegram import ParseMode, Chat

def help(update, context):
    if update.effective_chat.type == Chat.GROUP:
        text = """\
<b>Teleteam Help</b>

<b>✴️Getting Started</b>
/start - Register the group with Teleteam.
/join - For a user to be registered as a member in a group.

<b>🏋️‍♀️Dealing with Tasks</b>
/createtask - Create a task with the later-specified details.
/tasklist - Lists the existing task in the current group.
You will receive a notification for the tasks both when creating and nearing the deadline.

<b>👨‍💻Schedule Meetings</b>
/createmeeting - Create a meeting with the later-specified details.
/createpoll - (Only in private chat) Create a poll to discuss the meetup timing.
/meetinglist - List the meetings in the current group.

<b>Feel free to use the web client, teleteam.herokuapp.com, for better navigation and visualization.</b>
    """
    else:
        text = """\
<b>Teleteam Help</b>

<b>✴️Getting Started</b>
Make sure you have /join in at least one group.

<b>🏋️‍♀️Dealing with Tasks</b>
/tasklist - Lists all of your tasks from different groups.

<b>👨‍💻Schedule Meetings</b>
/meetinglist - List the meetings in the current group.

You will receive a notification when tasks (that you are assigned to) and meetings are created or edited. (You can change this in the Settings page of the web app)
We will send a reminder when the task/meeting is near.

<b>Feel free to use the web client, teleteam.herokuapp.com, for better navigation and visualization.</b>
    """

    context.bot.sendMessage(update.message.chat_id, text=text, parse_mode=ParseMode.HTML)