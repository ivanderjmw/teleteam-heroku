from rest_framework import serializers
from main_app.models import User, Group, Task, Meeting, UserSettings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_id', 'username', 'first_name', 'last_name', 'photo_url']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'group', 'title', 'done', 'assigned_users', 'deadline']

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'group', 'title', 'time']

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = [
            'pushNotifications',
            'autoCreateMeetingReminder',
            'defaultMeetingReminderTimedelta',
            'autoCreateTaskReminder',
            'defaultTaskReminderTimedelta',
            'botDetailedViewOnDefault'
        ]

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group

        fields = ['id', 'group_chat_id', 'chat_title', 'photo_url', 'closest_deadline']

class GroupDetailSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True)
    tasks = TaskSerializer(many=True)
    meetings = MeetingSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'group_chat_id', 'chat_title', 'members', 'tasks', 'meetings']

class TaskDetailedSerializer(serializers.ModelSerializer):
    group = GroupSerializer(many=False, read_only=True)
    assigned_users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        
        fields = ['id', 'group', 'title', 'done', 'assigned_users', 'deadline']