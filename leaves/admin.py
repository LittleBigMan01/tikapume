from django.contrib import admin
from .models import LeaveType, LeaveGradeDays, LeaveBalance, LeaveApplication


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']


@admin.register(LeaveGradeDays)
class LeaveGradeDaysAdmin(admin.ModelAdmin):
    list_display = ['leave_type', 'grade', 'days']
    list_filter = ['leave_type', 'grade']


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'leave_type', 'total_days',
                    'used_days', 'remaining_days', 'year']
    list_filter = ['leave_type', 'year']


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'leave_type', 'start_date',
                    'end_date', 'total_days', 'status', 'applied_at']
    list_filter = ['status', 'leave_type']
    search_fields = ['applicant__username', 'applicant__first_name']