from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('read/<int:notification_id>/', views.mark_read, name='mark_read'),
    path('count/', views.notification_count, name='notification_count'),
]