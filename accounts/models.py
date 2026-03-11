from django.contrib.auth.models import AbstractUser
from django.db import models

class Institute(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='institute_logo/', null=True, blank=True)

    def __str__(self):
        return self.name
        
class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('FACULTY', 'Faculty'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='ADMIN')

class Student(models.Model):
    name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    batch = models.CharField(max_length=50)

class Bank(models.Model):
    bank_name = models.CharField(max_length=100, unique=True)
    account_no = models.CharField(max_length=30, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.bank_name
