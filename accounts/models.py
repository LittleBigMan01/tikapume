from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Grade(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class JobTitle(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('it_admin', 'IT Administrator'),
        ('employee', 'Employee'),
        ('hr', 'Human Resource'),
        ('approver', 'Approver'),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='employee'
    )
    secondary_role = models.CharField(
        max_length=20, choices=ROLE_CHOICES,  
        blank=True, null=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    grade = models.ForeignKey(
        Grade, on_delete=models.SET_NULL, null=True, blank=True
    )
    job_title = models.ForeignKey(
        JobTitle, on_delete=models.SET_NULL, null=True, blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(
        upload_to='profiles/', blank=True, null=True
    )
    temp_password = models.CharField(max_length=100, blank=True)
    is_supervisor = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"