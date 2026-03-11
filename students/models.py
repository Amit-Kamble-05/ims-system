from django.db import models
from datetime import datetime

from django.db import models
from datetime import datetime


class Student(models.Model):

    # ---------------- DROPDOWN CHOICES ---------------- #

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    CITY_CHOICES = [
        ('Pune', 'Pune'),
        ('Mumbai', 'Mumbai'),
        ('Nagpur', 'Nagpur'),
        ('Kolhapur', 'Kolhapur'),
        ('Solapur', 'Solapur'),
    ]

    QUALIFICATION_CHOICES = [
        ('Below SSC', 'Below SSC'),
        ('SSC', 'SSC'),
        ('HSC', 'HSC'),
        ('Under-Graduate', 'Under-Graduate'),
        ('Graduate', 'Graduate'),
        ('Post Graduate', 'Post Graduate'),
    ]

    # ---------------- PRIMARY KEY ---------------- #

    id = models.AutoField(primary_key=True)

    # ---------------- STUDENT PHOTO ---------------- #

    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)

    # ---------------- PERSONAL DETAILS ---------------- #

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)

    dob = models.DateField(blank=True, null=True)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    email = models.EmailField(blank=True, null=True)

    phone = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    alternate_phone = models.CharField(max_length=10, blank=True)

    city = models.CharField(
        max_length=50,
        choices=CITY_CHOICES,
        blank=True,
        null=True
    )

    qualification = models.CharField(
        max_length=50,
        choices=QUALIFICATION_CHOICES,
        blank=True,
        null=True
    )

    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ---------------- ADMISSION CODE ---------------- #

    def admission_code(self):
        year = datetime.now().year
        return f"ADM-{year}-{self.id:04d}"

    # ---------------- SAVE FUNCTION ---------------- #

    def save(self, *args, **kwargs):

        # FORCE CAPITAL LETTERS
        if self.first_name:
            self.first_name = self.first_name.strip().upper()

        if self.middle_name:
            self.middle_name = self.middle_name.strip().upper()

        if self.last_name:
            self.last_name = self.last_name.strip().upper()

        super().save(*args, **kwargs)

    # ---------------- STRING ---------------- #

    def __str__(self):
        return f"{self.first_name} {self.last_name}"