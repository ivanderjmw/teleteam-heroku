from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TASK, MEETING, Task, Meeting, Reminder
from teleteam_bot.user_commands import reminders

@receiver(post_save, sender=Task)
def post_save_task(sender, instance, created, update_fields=[], **kwargs):
    if not created:
        Reminder.objects.filter(task = instance).delete()

    recipients = instance.assigned_users.filter(settings__autoCreateTaskReminder=True).all()

    reminders.set_reminder_to_users(
        recipients=recipients,
        task=instance,
        meeting=None,
        update_fields=update_fields,
        type=TASK
    )

@receiver(post_save, sender=Meeting)
def post_save_meeting(sender, instance, created, update_fields=[], **kwargs):
    if not created:
        Reminder.objects.filter(meeting = instance).delete()

    recipients = instance.group.members.filter(settings__autoCreateMeetingReminder=True).all()
    print('a')
    reminders.set_reminder_to_users(
        recipients=recipients,
        task=None,
        meeting=instance,
        update_fields=update_fields,
        type=MEETING
    )
