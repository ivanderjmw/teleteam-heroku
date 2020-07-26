"""Meeting User commands"""
import dateparser
import datetime

from django.utils.timezone import make_aware

from main_app.helpers import create_meeting_query, get_meeting_query, toggle_vote

from main_app.models import Task, Meeting, Poll, User, Group, Choice, Vote
from telegram.ext import (ConversationHandler, 
                          CommandHandler, 
                          MessageHandler, 
                          CallbackQueryHandler, 
                          Filters)
from telegram import (
    ParseMode, TelegramError, InlineKeyboardButton, 
    InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
    )

import logging

LOGGER = logging.getLogger('django')

GET_MEETING_TITLE, GET_MEETING_TIME = range(0,2)

class CreateMeeting:
    """Meeting creation functions"""

    def create_meeting(update, context):
        """Creating a meeting using a conversation interface"""
        
        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # Ask for the name of the meeting.
        context.bot.sendMessage(chat_id=chat_id, text='What\'s the meeting title 📜?')

        return GET_MEETING_TITLE

    def get_meeting_title(update, context):
        """Gets the meeting title, a MessageHandler"""

        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # Retrieve the text
        sent_title = update.message.text

        # Store it in chat_data
        context.chat_data['meeting_title'] = sent_title

        # Ask for the meeting time
        context.bot.sendMessage(chat_id=chat_id, text='What will be the meeting time ⏱?')

        return GET_MEETING_TIME

    def get_meeting_time(update, context):
        """Gets the meeting time"""

        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # Retrieve the text
        sent_time = update.message.text

        # Check if it is a valid time
        if not sent_time:
            context.bot.sendMessage(chat_id=chat_id, text='Resend a valid time 😨. Try \'Tomorrow 3pm\'')
            return GET_MEETING_TIME

        # Store it in chat_data
        context.chat_data['meeting_time'] = make_aware(dateparser.parse(sent_time))

        # Now call create meeting
        try:
            create_meeting_query(
                chat_id=chat_id,
                title=context.chat_data['meeting_title'],
                time=context.chat_data['meeting_time'],
            )
        except TelegramError:
            # Notify user to use the group chat
            text = f"Seems like you are not in your group"
            context.bot.sendMessage(text=text)

        # Review the meeting details
        text = f"Created a meeting titled {context.chat_data['meeting_title']} held on {context.chat_data['meeting_time'].strftime('%A, %d %b %Y at %l:%M %p')}"
        context.bot.sendMessage(chat_id=chat_id, text=text)

        context.chat_data.clear()

        return ConversationHandler.END

GET_TITLE, ADD_CHOICES = range(0,2)

class TelegramMeetingPoll:
    """Telegram Meeting Polls"""

    def create_poll(update, context):
        """Create Meeting Poll"""

        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # Make sure chat type is not a group
        if update.message.chat.type == 'group':
            context.bot.sendMessage(chat_id=chat_id, text='Please create a meeting poll through private chat with @Teleteam_bot')
            return ConversationHandler.END
        
        context.bot.sendMessage(chat_id=chat_id, text='What is the meeting Poll Title?')

        return GET_TITLE
        # Guide meeting creation, dates and stuff


        # Might want to add a keyboard for common timings.

        # Edit message according to the poll options

        # Share button

        # Inline message in the group to refer to the poll.

        # Create percentages of polls, names too.

    def get_title(update, context):
        """Get the title"""

        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        new_poll_title = update.message.text
        new_poll_admin = User.objects.get(username=update.message.chat.username)

        print(type(new_poll_admin))
        print("A NEW POLL:", new_poll_title, new_poll_admin)

        new_poll = Poll(title=new_poll_title, admin=new_poll_admin)
        new_poll.save()

        LOGGER.info("Poll is created %s" % new_poll)

        new_poll_message = context.bot.sendMessage(chat_id=chat_id, text=new_poll.message[1], parse_mode=ParseMode.HTML)
        context.bot.sendMessage(chat_id=chat_id, text=f'Now Text me some date-time choices to include!\nPoll id: {str(new_poll.id)}')


        context.chat_data['poll_message_id'] = new_poll_message.message_id
        context.chat_data['poll_id'] = new_poll.id

        return ADD_CHOICES

    def add_choices(update, context):
        """Get choices from the user"""
        
        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # Retrieve poll_id
        poll_id = context.chat_data['poll_id']
        poll_message_id = context.chat_data['poll_message_id']

        # Retrieve poll object
        poll = Poll.objects.get(id=poll_id)

        # Create a new choice based on user input
        new_poll_choice = dateparser.parse(update.message.text)
        new_choice = Choice(poll=poll, time=new_poll_choice)
        new_choice.save()

        # Put in a stack

        # Edit the poll message
        text = poll.message[1]
        context.bot.editMessageText(chat_id=chat_id, message_id=poll_message_id, text=text, parse_mode=ParseMode.HTML)

        return ADD_CHOICES

    def undo_choices(update, context):
        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

         # Edit the poll message
        text = "This command is under construction."
        context.bot.sendMessage(chat_id=chat_id, text=text)
        pass

    def publish(update, context):
        """Allows user to publish the poll in any groups"""

        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # Retrieve poll_id
        poll_id = context.chat_data['poll_id']
        poll_message_id = context.chat_data['poll_message_id']

        # Retrieve poll object
        poll = Poll.objects.get(id=poll_id)

        LOGGER.info("Create Inline Keyboard")
        share_button = InlineKeyboardButton(text='Share', switch_inline_query='poll-'+str(poll_id))
        inline_keyboard = InlineKeyboardMarkup([[share_button]])

        LOGGER.info("Edit the poll message")
        context.bot.editMessageReplyMarkup(chat_id=chat_id, message_id=poll_message_id, reply_markup=inline_keyboard)

        LOGGER.info("Clear chat data")
        context.chat_data.clear()

        LOGGER.info("End conversation")

        return ConversationHandler.END

    def share(update, context):
        """Sends the poll based on the uuid"""

        # # Retrieve chat_id
        # chat_id = update.effective_message.chat.id
        LOGGER.info("Incoming Inline Query")

        # Retrieve the message
        poll_id = update.inline_query.query.split('poll-', 1)[1]

        LOGGER.info("Received Inline Query from Poll with uuid: %s" % poll_id)

        # Retrieve poll object
        poll = Poll.objects.get(id=poll_id)

        pollchcdict, pollmsg = poll.message

        LOGGER.info("Poll dict: %s" % pollchcdict)

        

        inlinekeyboard = TelegramMeetingPoll.inline_keyboard(pollchcdict, poll_id)

        LOGGER.info("InlineKeyboard: %s" % inlinekeyboard)

        # Create results
        results = [
            InlineQueryResultArticle(
                id=poll_id, 
                title=poll.title, 
                input_message_content=InputTextMessageContent(
                                    pollmsg,
                                    parse_mode=ParseMode.HTML
                                    ),
                reply_markup=InlineKeyboardMarkup(inlinekeyboard)
                )
        ]

        return update.inline_query.answer(results)
    
    def inline_keyboard(pollchcdict, poll_id):
        MAX_BUTTON_ROW = 5

        inlinekeyboard = []
        for key in pollchcdict:
            if not key % MAX_BUTTON_ROW:
                inlinekeyboard.append([])
            inlinekeyboard[key // MAX_BUTTON_ROW].append(
                InlineKeyboardButton(
                    text=str(key), 
                    callback_data="POLL:"+str(poll_id)+":"+str(key)
                )
            )
        return inlinekeyboard

    def manage_vote(update, context):

        # Gets the query
        query = update.callback_query

        LOGGER.info("CallbackQuery: %s" % query)

        # Split the queries
        pattern, poll_id, keychoice = query.data.split(':')

        keychoice = int(keychoice)

        LOGGER.info("Pattern: %s, uuid: %s, keychoice: %s" % (pattern, poll_id, keychoice))
        LOGGER.info("User: %s Query" % query.from_user)


        # Gets user
        user = User.objects.get(user_id=query.from_user.id)

        LOGGER.info("User: %s sent a callback Query" % user.username)

        # Retrieve poll object
        poll = Poll.objects.get(id=poll_id)

        # Retrieve poll message
        pollchcdict, pollmsg = poll.message

        LOGGER.info("Pollchcdict: %s, choice: %s" % (pollchcdict, pollchcdict[keychoice]))

        # Toggle the user's votes.
        toggle_vote(user, pollchcdict[keychoice])

        # Retrieve poll message
        pollchcdict, pollmsg = poll.message

        query.edit_message_text(
            text=pollmsg, 
            parse_mode=ParseMode.HTML, 
            reply_markup=InlineKeyboardMarkup(TelegramMeetingPoll.inline_keyboard(pollchcdict, poll_id))
            )

        # Returns a callback to the query
        context.bot.answer_callback_query(query.id)


def list_meetings(update, context):
    """List the upcoming meetings for the group"""

    # Retrieve chat_id
    chat_id = update.effective_message.chat.id

    LOGGER.info(f'Chat_id {chat_id}: Query meetings')

    # Queries for the Meeting items
    meetings = get_meeting_query(update.effective_message.chat)

    # Check if there are any meetings or not
    if not meetings:
        LOGGER.info(f'Chat_id {chat_id}: No meetings 🙈') 
        if update.effective_message.chat.type == 'private':
            text='You have no meetings in any of your groups. Enter /createmeeting in a group to create one.'
        else:
            text='There are no meetings in this group. Enter /createmeeting to create one.'
    else:
        LOGGER.info(f'Chat_id {chat_id}: Stitching meetings')
        # Use inline keyboard to show the meetings
        text_arr = ["Your upcoming meetings 💡:"]

        # Stitch the meeting info together into one message.
        for meeting in meetings:
            text_to_append = '<b>' + str(meeting.title) + '</b> - ' 

            if update.effective_message.chat.type == 'private':
                text_to_append += meeting.group.chat_title + ' '
            
            text_to_append += str(meeting.time.strftime('%A, %d %b %Y at %l:%M %p'))
            text_arr.append(text_to_append)

        text = '\n'.join(text_arr)

    LOGGER.info(f'Chat_id {chat_id}: Send meetinglist')
    context.bot.sendMessage(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)
    

def cancel(update, context):
    """Ends the conversation"""

    # Retrieve chat_id
    chat_id = update.effective_message.chat.id

    context.bot.sendMessage(chat_id=chat_id, text="Cancelled!", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

CREATE_MEETING_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('createmeeting', CreateMeeting.create_meeting)],
    states={
        GET_MEETING_TITLE:[CommandHandler('cancel', cancel), MessageHandler(Filters.text, CreateMeeting.get_meeting_title)],
        GET_MEETING_TIME:[CommandHandler('cancel', cancel), MessageHandler(Filters.text, CreateMeeting.get_meeting_time)]
    },
    fallbacks=[]
)

CREATE_MEETING_POLL_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('createpoll', TelegramMeetingPoll.create_poll)],
    states={
        GET_TITLE:[MessageHandler(Filters.text, TelegramMeetingPoll.get_title)],
        ADD_CHOICES:[
            CommandHandler('undo', TelegramMeetingPoll.undo_choices),
            CommandHandler('publish', TelegramMeetingPoll.publish),
            MessageHandler(Filters.text, TelegramMeetingPoll.add_choices)
            ]
    },
    fallbacks=[]
)

if __name__ == "manage":
    # Test create meeting poll
    LOGGER.info("Creating test Meeting Poll")

    admin = User.objects.get(username='ivanderjmw')
    group = Group.objects.filter(members__username='ivanderjmw').first()
    new_poll = Poll(title="Test Poll 0", group=group, admin=admin)
    new_poll.save()

    # Test create choice
    LOGGER.info("Create test choices")

    choice = Choice(poll=new_poll)
    choice.save()

    # Test create votes
    LOGGER.info("Before make votes")

    print(new_poll.message[1])

    LOGGER.info("After make votes")

    new_vote = Vote(choice=choice, user=admin)
    new_vote.save()

    print(new_poll.message[1])