from django.db.models.signals import post_save

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, DestroyAPIView, RetrieveDestroyAPIView

from main_app.models import User, Group, Task, Meeting, UserSettings
from main_app.api.serializers import UserSerializer, GroupSerializer, GroupDetailSerializer, TaskSerializer, MeetingSerializer, UserSettingsSerializer, TaskDetailedSerializer
from main_app.api.permissions import HasObjectPermission

from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound

from .helpers import verify_login_data
import logging

LOGGER = logging.getLogger('django')

@permission_classes((AllowAny))
@api_view(['POST'])
def authenticate(request):
    print(request.data)
    if verify_login_data(request.data):
        return Response({
            'user_id': request.data['id'],
            'token': User.objects.get(user_id = request.data['id']).token,
        })
    
    return Response({'detail': 'Failed to verify credentials.'})

@permission_classes((IsAuthenticated, ))
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@permission_classes((AllowAny, ))
class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        """
        perform_create(self, serializer):

        Instead of creating a new user each time, will create if a user has not registered,
        but will return the existing user's data if it exists.

        Sample return JSON:
        ```
        {
            "id": 17,
            "user_id": 131412128,
            "username": "chihiroo",
            "first_name": null,
            "last_name": null,
            "photo_url": "https://i.pinimg.com/originals/70/37/9d/70379d89b366c16e3509fe9627208a51.jpg"
        }
        ```
        """
        LOGGER.info(serializer.validated_data)
        LOGGER.info(f"REQUEST user_id {serializer.validated_data.get('user_id')}")

        user_existing = User.objects.filter(user_id=serializer.validated_data.get('user_id'))

        if user_existing:
            LOGGER.warn("user_id already exists")

            user_updated = serializer.update(user_existing.first(), serializer.validated_data)
            print(user_updated)
            return user_updated
        
        serializer.save()
        return serializer.data

@permission_classes((HasObjectPermission, ))
class UserRetrieveDestroyView(RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'user_id'

@permission_classes((HasObjectPermission, ))
class UserGroupListView(ListAPIView):
    serializer_class = GroupSerializer

    def get_queryset(self):
        try:
            user = User.objects.get(user_id=self.kwargs['pk'])
        except User.DoesNotExist:
            print("User does not exist!")

        # Check if the request is permitted to access the User object
        self.check_object_permissions(self.request, user)

        return Group.objects.filter(members__in=[user])

@permission_classes((HasObjectPermission, ))
class UserTaskListView(ListAPIView):
    serializer_class = TaskDetailedSerializer

    def get_queryset(self):
        try:
            user = User.objects.get(user_id=self.kwargs['pk'])
        except User.DoesNotExist:
            print("User does not exist!")

        # Check if the request is permitted to access the User object
        self.check_object_permissions(self.request, user)

        return Task.objects.filter(assigned_users__in=[user])

@permission_classes((HasObjectPermission, ))
class TaskGroupListView(ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        try:
            group = Group.objects.get(group_chat_id=self.kwargs['pk'])
        except Group.DoesNotExist:
            raise NotFound(detail="Error group does not exist")

        # Check if the request is permitted to access the Group object
        self.check_object_permissions(self.request, group)

        return Task.objects.filter(group=group)

@permission_classes((HasObjectPermission, ))
class MeetingGroupListView(ListAPIView):
    serializer_class = MeetingSerializer

    def get_queryset(self):
        try:
            group = Group.objects.get(group_chat_id=self.kwargs['pk'])
        except Group.DoesNotExist:
            raise NotFound(detail="Error group does not exist")

        # Check if the request is permitted to access the Group object
        self.check_object_permissions(self.request, group)
        
        return Meeting.objects.filter(group=group)

@permission_classes((HasObjectPermission, ))
class GroupDetailView(RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupDetailSerializer
    lookup_url_kwarg = 'group_pk'

@permission_classes((HasObjectPermission, ))
class UserSettingsRetrieveUpdateView(APIView):
    queryset = UserSettings.objects.all()

    def get_object(self, pk):
        try:
            settings = User.objects.get(user_id=pk).settings
            self.check_object_permissions(self.request, settings)
            return settings
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        settings = self.get_object(pk)
        print("SETTINGS: ", settings)
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        settings = self.get_object(pk)
        serializer = UserSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Error in saving", status=status.HTTP_400_BAD_REQUEST)

@permission_classes((HasObjectPermission, ))
class TaskViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for creating, viewing and editing Tasks.
    Inherited methods:
    .list(), .create(), .partial_update()
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        group_pk = self.kwargs.get('group_pk')
        tasks = Task.objects.filter(group__pk=group_pk)

        for task in tasks:
            self.check_object_permissions(self.request, task)

        return tasks

    def create(self, request, *args, **kwargs):
        group_pk = self.kwargs.get('group_pk')
        self.check_object_permissions(request, Group.objects.get(id=group_pk))

        request.data.update({'group': group_pk})
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            post_save.send(Task, instance=instance, created=True)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

@permission_classes((HasObjectPermission, ))
class MeetingViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for creating, viewing and editing Meetings.
    Inherited methods:
    .list(), .create(), .partial_update()
    """
    serializer_class = MeetingSerializer

    def get_queryset(self):
        group_pk = self.kwargs.get('group_pk')
        meetings = Meeting.objects.filter(group__pk=group_pk)

        for meeting in meetings:
            self.check_object_permissions(self.request, meeting)

        return meetings

    def create(self, request, *args, **kwargs):
        group_pk = self.kwargs.get('group_pk')
        self.check_object_permissions(request, Group.objects.get(id=group_pk))

        request.data.update({'group': group_pk})
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        