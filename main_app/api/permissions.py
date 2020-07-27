from rest_framework import permissions

from main_app.models import UserSettings, User, Group, Task, Meeting

class HasObjectPermission(permissions.BasePermission):
    """
    Only allow users that is associated with an object 
    to access it.
    """

    def has_object_permission(self, request, view, obj):
        object_type = type(obj)

        if object_type == User:
            return obj.token.hex == request.user.token.hex
        elif object_type == UserSettings:
            return obj == request.user.settings
        elif object_type == Group:
            return request.user in obj.members.all()
        elif object_type == Task:
            return request.user in obj.group.members.all()
        elif object_type == Meeting:
            return request.user in obj.group.members.all()

        return obj.user == request.user
