from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/reset/<int:user_id>/', views.reset_password, name='reset_password'),
    path('departments/', views.manage_departments, name='manage_departments'),
    path('grades/', views.manage_grades, name='manage_grades'),
    path('job-titles/', views.manage_job_titles, name='manage_job_titles'),
    path('departments/edit/<int:dept_id>/', views.edit_department, name='edit_department'),
    path('grades/edit/<int:grade_id>/', views.edit_grade, name='edit_grade'),
    path('job-titles/edit/<int:job_title_id>/', views.edit_job_title, name='edit_job_title'),
    path('departments/delete/<int:dept_id>/', views.delete_department, name='delete_department'),
    path('grades/delete/<int:grade_id>/', views.delete_grade, name='delete_grade'),
    path('job-titles/delete/<int:job_title_id>/', views.delete_job_title, name='delete_job_title'),
    path('profile/', views.user_profile, name='user_profile'),
]