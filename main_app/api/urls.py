from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    authenticate,
    UserListView,
    UserCreateView,
    UserRetrieveDestroyView,
    UserGroupListView,
    GroupDetailView,
    TaskGroupListView,
    MeetingGroupListView,
    UserSettingsRetrieveUpdateView,
    TaskViewSet,
    MeetingViewSet,
    UserTaskListView
    )

urlpatterns = [
    # Can only create users through telegram bot.
    # path('', UserListView.as_view()),

    path('authenticate', authenticate),
    
    path('create', UserCreateView.as_view()),
    # path('<pk>/delete', UserDestroyView.as_view()),

    path('group/<group_pk>', GroupDetailView.as_view()),

    path('group/<group_pk>/tasks', TaskViewSet.as_view({'get':'list'})),
    path('group/<group_pk>/tasks/create', TaskViewSet.as_view({'post':'create'})),
    path('group/<group_pk>/tasks/<pk>/update', TaskViewSet.as_view({'post':'partial_update'})),

    path('group/<group_pk>/meetings', MeetingViewSet.as_view({'get':'list'})),
    path('group/<group_pk>/meetings/create', MeetingViewSet.as_view({'post':'create'})),
    path('group/<group_pk>/meetings/<pk>/update', MeetingViewSet.as_view({'post':'partial_update'})),

    path('<pk>/settings', UserSettingsRetrieveUpdateView.as_view()),
    path('<pk>/groups', UserGroupListView.as_view()),
    path('<pk>/tasks', UserTaskListView.as_view()),
    path('<user_id>', UserRetrieveDestroyView.as_view()),
    
    # path('group/<group_pk>/meetings', MeetingGroupListView.as_view()),
]

