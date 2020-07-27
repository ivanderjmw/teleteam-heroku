"""
Helper functions for Database Queries
"""
import os
import dateparser
from datetime import datetime, timedelta


from django.utils.timezone import now, make_aware
from django.core.files import File
from main_app.models import UserSettings, User, Group, Task, Meeting, Reminder, Poll, Choice, Vote, TASK, MEETING
from teleteam_bot.user_commands import reminders
from django.conf import settings

def start_group(group_chat, bot):

    # Check if group already exists.
    if Group.objects.filter(group_chat_id=group_chat.id).exists():
        flag = None
        new_group = Group.objects.get(group_chat_id=group_chat.id)
    else:
        flag = True
        new_group = Group(group_chat_id=group_chat.id, chat_title=group_chat.title)
    
    # Try to get the telegram chat photo
    try:
        # Get chat object from Telegram API
        chat = bot.get_chat(group_chat.id)

        # Get photo url from Telegram API
        photo_file = chat.photo.get_small_file()

        path = settings.MEDIA_ROOT+str(chat.id)+'.jpg'

        # Download to media folder
        photo_file.download(custom_path=path)

        # Open the file
        photo = open(path, 'rb')
        new_group.photo = File(photo)
        os.remove(path)

        print(f'Group Photo is retrieved for {chat.title}')
    except Exception as e:
        print(e)

    new_group.save()

    if flag is None:
        return None

    return new_group

def check_user_exist(user, createNew=False):
    """Check if a user exists. If the user doesn't exist, create a new one"""
    user_query_result = User.objects.filter(user_id=user.id)

    if not user_query_result.exists():
        if not createNew:
            return False
        user_settings = UserSettings()
        user_settings.save()
        result_user = User(user_id=user.id, username=user.username, settings=user_settings)
        result_user.save()
    else:
        result_user = user_query_result.first()
    return result_user

def join_group(group_chat, user):
    # Create user if the user is not registered.
    result_user = check_user_exist(user, createNew=True)

    group = Group.objects.get(group_chat_id = group_chat.id)

    group.members.add(result_user)

def create_task(chat_id, title, deadline, assigned_usernames):
    """Create task from several inputs, handles multiple username assignments"""

    try:
        # Get objects from other tables
        group = Group.objects.get(group_chat_id=chat_id)
        assigned_users = []
        
        for username in assigned_usernames:
            # Make sure the assigned user is registered in the group.
            user = User.objects.get(username__iexact=username)
            if not (user in group.members):
                print("/CREATETASK ERROR: User is registered, but not inside the group.")
                raise KeyError
            assigned_users.append(user)

        new_task = Task(group=group, title=title, deadline=deadline)
        new_task.save()
        
        new_task.assigned_users.add(*assigned_users)
        new_task.save()
    except KeyError:
        raise KeyError("Either group or user is not registered yet.")


def list_tasks(chat, private_chat=False):
    if private_chat:
        user = User.objects.get(username=chat.username)
        tasks = Task.objects.filter(assigned_users__in = [user]).filter(done=False)
    else:
        group = Group.objects.get(group_chat_id = chat.id)
        tasks = Task.objects.filter(group = group).filter(done=False)

    return tasks

def edit_assigned_users_query(task_id, assigned_usernames):
    
    # Preprocess the user data
    assigned_users = []
        
    for username in assigned_usernames:
        assigned_users.append(User.objects.get(username=username))

    # Retrieve the task object
    task = Task.objects.get(id=task_id)

    task.assigned_users.set(assigned_users)

    task.save()

def create_meeting_query(chat_id, title, time):
    """Create task from several inputs, handles multiple username assignments"""
    try:
        group = Group.objects.get(group_chat_id=chat_id)

        new_meeting = Meeting(group=group, title=title, time=time)
        new_meeting.save()

    except KeyError:
        raise KeyError("Either group or user is not registered yet.")

def get_meeting_query(chat, all=False):
    """
    Gets the meetings, returns a queryset object in ascending time order.
    all: False, Get upcoming meetings, else get all.
    """
    try:
        # Get objects from other tables
        if chat.type == 'private':
            user = User.objects.get(username=chat.username)
            print(user)
            groups_with_user = Group.objects.filter(members__in = [user])
            meetings = Meeting.objects.filter(group__in = groups_with_user)
        else:
            group = Group.objects.get(group_chat_id=chat.id)
            meetings = Meeting.objects.filter(group=group, time__gte=now()).order_by('time')

    except KeyError:
        raise KeyError("Either group or user is not registered yet.")
    except Exception as e:
        print("Somehow there is an exception %s" % e)

    return meetings

def delete_reminder(reminder_id):
    try:
        Reminder.objects.get(id=reminder_id).delete()
    except Exception as e:
        print(e)

def toggle_vote(user, choice):

    poll_choices = choice.poll.choice_set
    
    # Check if vote exists
    try:

        # Delete the existing vote
        Vote.objects.get(user=user, choice=choice).delete()

    except Exception as e:
        print("Exception when register vote %s" % e)

        new_vote = Vote(user=user, choice=choice)
        new_vote.save()
            
    return

def get_user_settings(chat):
    try:
        user = User.objects.get(user_id = chat.id)
    except Exception as e:
        print("Error retrieving user")

    return user.settings
