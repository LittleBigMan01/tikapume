from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Grade, JobTitle


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role',
                    'department', 'grade', 'job_title', 'is_active']
    list_filter = ['role', 'department', 'grade', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Legal Aid Bureau Info', {
            'fields': ('role', 'department', 'grade', 'job_title',
                      'phone', 'profile_photo', 'temp_password',
                      'is_first_login')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Legal Aid Bureau Info', {
            'fields': ('role', 'department', 'grade', 'job_title',
                      'phone', 'email')
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department)
admin.site.register(Grade)
admin.site.register(JobTitle)