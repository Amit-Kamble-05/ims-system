from django.db import models
from students.models import Student
from django.utils import timezone


class Course(models.Model):
    name = models.CharField(max_length=150, unique=True)
    duration = models.CharField(max_length=50)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class CourseContent(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    content_name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.course.name} - {self.content_name}"


class Admission(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('COURSE', 'Course Added'),
        ('PAYMENT', 'Payment Added'),
        ('CONFIRMED', 'Confirmed'),
    ]

    BATCH_TYPE_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKEND', 'Weekend'),
         ('MWF', 'Mon-Wed-Fri'),
        ('TTS', 'Tue-Thu-Sat'),
    ]

    BATCH_TIME_CHOICES = [
        ('09-10', '09:00 AM - 10:00 AM'),
        ('10-11', '10:00 AM - 11:00 AM'),
        ('11-12', '11:00 AM - 12:00 PM'),
        ('12-13', '12:00 PM - 01:00 PM'),
        ('13-14', '01:00 PM - 02:00 PM'),
        ('14-15', '02:00 PM - 03:00 PM'),
        ('15-16', '03:00 PM - 04:00 PM'),
        ('16-17', '04:00 PM - 05:00 PM'),
        ('17-18', '05:00 PM - 06:00 PM'),
        ('18-19', '06:00 PM - 07:00 PM'),
        ('19-20', '07:00 PM - 08:00 PM'),
        ('20-21', '08:00 PM - 09:00 PM'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_content = models.ForeignKey(CourseContent, on_delete=models.CASCADE)

    batch_type = models.CharField(max_length=10, choices=BATCH_TYPE_CHOICES, null=True)
    batch_time = models.CharField(max_length=10, choices=BATCH_TIME_CHOICES, null=True)

    discounted_fees = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20)
    gst = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    admission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course} ({self.batch_type} | {self.batch_time})"

class Installment(models.Model):
    admission = models.ForeignKey(
        Admission,
        on_delete=models.CASCADE,
        related_name='installments'
    )
    installment_type = models.CharField(max_length=50)
    pay_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateField(null=True, blank=True)

    STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='UNPAID'
    )

    def __str__(self):
        return f"{self.installment_type} - {self.amount}"