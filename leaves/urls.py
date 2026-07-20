from django.urls import path
from . import views

urlpatterns = [
    path('leave-types/', views.manage_leave_types, name='manage_leave_types'),
    path('public-holidays/', views.manage_public_holidays, name='manage_public_holidays'),
    path('public-holidays/delete/<int:holiday_id>/', views.delete_public_holiday, name='delete_public_holiday'),
    path('balances/', views.manage_balances, name='manage_balances'),
    path('apply/', views.apply_leave, name='apply_leave'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('all-applications/', views.all_applications, name='all_applications'),
    path('hr/pending/', views.hr_pending_requests, name='hr_pending_requests'),
    path('hr/forward/<int:application_id>/', views.hr_forward_to_approver, name='hr_forward_to_approver'),
    path('supervisor/pending/', views.supervisor_pending_requests, name='supervisor_pending_requests'),
    path('supervisor/action/<int:application_id>/', views.supervisor_action, name='supervisor_action'),
    path('approver/pending/', views.approver_pending_requests, name='approver_pending_requests'),
    path('approver/action/<int:application_id>/', views.approve_decline_leave, name='approve_decline_leave'),
]