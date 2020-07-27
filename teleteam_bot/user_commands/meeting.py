"""Meeting User commands"""
import dateparser
import datetime
import arrow

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
    InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent,
    Chat)

import logging

LOGGER = logging.getLogger('django')

GET_MEETING_TITLE, GET_MEETING_TIME = range(0,2)

class CreateMeeting:
    """Meeting creation functions"""

    def create_meeting(update, context):
        """Creating a meeting using a conversation interface"""
        
        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        if update.effective_message.chat.type == Chat.PRIVATE:
            context.bot.sendMessage(
                update.message.chat_id,
                text='The /createmeeting command is not available inside a private chat. Please use the command in a Teleteam registered group.')
            return ConversationHandler.END

        # Clear all related chat_data
        context.chat_data.clear()

        if not User.objects.filter(user_id=update.message.from_user.id).exists():
            context.bot.sendMessage(chat_id=chat_id, text='‼️You need to /join a valid group to be able to create a meeting.')
            return ConversationHandler.END

        if update.effective_chat.type == 'private':
            context.bot.sendMessage(chat_id=chat_id, text='‼️You can only create a meeting inside a valid telegram group.')
            return ConversationHandler.END

        print(f'Asking for meeting title in {context.chat_data}')
        # Ask for the name of the meeting.
        context.bot.sendMessage(chat_id=chat_id, text='What\'s the meeting title 📜? i.e. <i>Meetup at Starbucks for project meeting</i>', parse_mode=ParseMode.HTML)

        return GET_MEETING_TITLE

    def get_meeting_title(update, context):
        """Gets the meeting title, a MessageHandler"""

        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # Retrieve the text
        sent_title = update.message.text

        # Store it in chat_data
        context.chat_data['meeting_title'] = sent_title

        print(f'Asking for meeting time in {context.chat_data}')

        # Ask for the meeting time
        context.bot.sendMessage(chat_id=chat_id, text='What will be the meeting time ⏱? i.e.<i>Saturday 4pm</i> or <i>1 August 12pm</i>', parse_mode=ParseMode.HTML)

        return GET_MEETING_TIME

    def get_meeting_time(update, context):
        """Gets the meeting time"""

        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # User inputs the Task due date, then prompts for users
        sent_time = dateparser.parse(update.message.text)
        if sent_time is None or len(update.message.text) < 4:
            context.bot.sendMessage(update.message.chat_id, text='‼️That\'s not a proper date, please reenter a valid date.')
            return GET_MEETING_TIME

        # Store it in chat_data
        context.chat_data['meeting_time'] = make_aware(sent_time)


        print(f'Calling create meeting from {chat_data}')
        # Now call create meeting
        try:
            create_meeting_query(
                chat_id=chat_id,
                title=context.chat_data['meeting_title'],
                time=context.chat_data['meeting_time'],
            )
            print('Successfully created meeting')
        except (TelegramError, KeyError):
            # Notify user to use the group chat
            text = f"‼️Seems like you are not in a valid group group"
            context.bot.sendMessage(text=text)
            return ConversationHandler.END

        print('Sending the user back the meeting')
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

        if not User.objects.filter(user_id=update.message.from_user.id).exists():
            context.bot.sendMessage(chat_id=chat_id, text='‼️Your telegram account is not registered yet. Try to first invite and send /start to me in your telegram group, then send /join in the same group. Or, you can login to our web client teleteam.herokuapp.com.')
            return ConversationHandler.END

        # Clear all related chat_data
        context.chat_data.clear()

        

        # Make sure chat type is not a group
        if update.message.chat.type == 'group':
            context.bot.sendMessage(chat_id=chat_id, text='‼️Please create a meeting poll through private chat with @Teleteam_bot')
            return ConversationHandler.END
        
        context.bot.sendMessage(chat_id=chat_id, text='📊This is the create meeting poll feature! I will guide you to create your poll which you can share with your groups.\n\nFirst, enter the meeting Poll Title.')

        return GET_TITLE

    def get_title(update, context):
        """Get the title"""

        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        print(f"Received get_title from f{update.effective_message}")

        try:
            new_poll_title = update.message.text
            new_poll_admin = User.objects.get(user_id=update.message.from_user.id)
        except Exception as e:
            context.bot.sendMessage(chat_id=chat_id, text='‼️An error was encountered. Please reenter the previous command.')
            return ConversationHandler.END


        print(type(new_poll_admin))
        print("A NEW POLL:", new_poll_title, new_poll_admin)

        new_poll = Poll(title=new_poll_title, admin=new_poll_admin)
        new_poll.save()

        LOGGER.info("Poll is created %s" % new_poll)

        new_poll_message = context.bot.sendMessage(chat_id=chat_id, text=new_poll.message[1], parse_mode=ParseMode.HTML)
        context.bot.sendMessage(chat_id=chat_id, text=f'Now Text me some date-time choices to include in the meeting poll!')


        context.chat_data['poll_message_id'] = new_poll_message.message_id
        context.chat_data['poll_id'] = new_poll.id
        context.chat_data['poll_choice_stack'] = []

        print("Waiting for user's choices")

        return ADD_CHOICES

    def add_choices(update, context):
        """Get choices from the user"""
        
        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # Retrieve poll_id
        poll_id = context.chat_data['poll_id']
        poll_message_id = context.chat_data['poll_message_id']

        print(f"Chat data: {context.chat_data}")

        # Retrieve poll object
        poll = Poll.objects.get(id=poll_id)

        # Create a new choice based on user input
        # User inputs the Task due date, then prompts for users
        choice_time = dateparser.parse(update.message.text)
        if choice_time is None or len(update.message.text) < 4:
            context.bot.sendMessage(update.message.chat_id, text='‼️That\'s not a proper date, please reenter a valid date.')
            return ADD_CHOICES
        
        print(f'Add choice {choice_time}')
        new_choice = Choice(poll=poll, time=make_aware(choice_time))
        new_choice.save()

        # Put in a stack
        if not context.chat_data['poll_choice_stack']:
            context.chat_data['poll_choice_stack'] = [new_choice.id]
        else:
            context.chat_data['poll_choice_stack'].append(new_choice.id)

        # Edit the poll message
        text = poll.message[1]
        context.bot.editMessageText(chat_id=chat_id, message_id=poll_message_id, text=text, parse_mode=ParseMode.HTML)

        return ADD_CHOICES

    def undo_choices(update, context):

        # Retrieve chat_id
        chat_id = update.effective_message.chat.id

        # Retrieve poll_id
        poll_id = context.chat_data['poll_id']
        poll_message_id = context.chat_data['poll_message_id']

        # Retrieve poll object
        poll = Poll.objects.get(id=poll_id)

        # Pop from stack
        if not context.chat_data['poll_choice_stack']:
            text = "‼️Error encountered, choice stack is empty. Please redo the previous command."
            context.bot.sendMessage(chat_id=chat_id, text=text)
            return ConversationHandler.END

        choice_id = context.chat_data['poll_choice_stack'].pop()
        print(f'Choice id to delete is {choice_id}')

        # Delete choice object
        choice = Choice.objects.get(id=choice_id)
        # Notify the user about undo success button
        context.bot.sendMessage(chat_id, text=f'The option {arrow.get(choice.time).to("Asia/Singapore").format("HH:mm dddd, D MMM YYYY")} was deleted')
        choice.delete()


        # Edit the poll message
        text = poll.message[1]
        context.bot.editMessageText(chat_id=chat_id, message_id=poll_message_id, text=text, parse_mode=ParseMode.HTML)
        return ADD_CHOICES

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

        # Notify the user about the share button
        context.bot.sendMessage(chat_id, text='👍Poll message has been published! Scroll up and click on the share button, then pick a group you want to send to.')

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
                text_to_append += meeting.group.chat_title
            
            text_to_append += '\n' + str(meeting.time.strftime('%A, %d %b %Y at %l:%M %p')) + '\n'
            text_arr.append(text_to_append)

        text = '\n'.join(text_arr)

    LOGGER.info(f'Chat_id {chat_id}: Send meetinglist')
    context.bot.sendMessage(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)
    

def cancel(update, context):
    """Ends the conversation"""

    # Retrieve chat_id
    chat_id = update.effective_message.chat.id

    context.chat_data.clear()

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
            CommandHandler('cancel', cancel),
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