from django.db import models
from datetime import datetime
from django.db import models
from courses.models import Course, CourseContent

class Enquiry(models.Model):

    Enq_ID = models.AutoField(primary_key=True)

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    email = models.EmailField(blank=True)
    mobile_no = models.CharField(max_length=15)

    interested_course = models.ForeignKey(Course,on_delete=models.SET_NULL,null=True,blank=True)
    course_content = models.TextField(blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    offered_fees = models.DecimalField(max_digits=10, decimal_places=2)

    # ---------------- Batch ----------------

    BATCH_TYPE_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKEND', 'Weekend'),
        ('MWF', 'Mon-Wed-Fri'),
        ('TTS', 'Tue-Thu-Sat'),
    ]

    batch_type = models.CharField(max_length=20, choices=BATCH_TYPE_CHOICES, null=True)

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
    batch_time = models.CharField(max_length=20, choices=BATCH_TIME_CHOICES, null=True)

    # ---------------- Source ----------------

    SOURCE_CHOICES = [
        ('Walk-in', 'Walk-in'),
        ('Phone', 'Phone'),
        ('Website', 'Website'),
        ('Reference', 'Reference'),
    ]

    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES
    )

    # ---------------- Enquiry Info ----------------

    enquiry_date = models.DateTimeField(auto_now_add=True)

    remarks = models.TextField(blank=True)

    followup_date = models.DateField(null=True, blank=True)
    followup_time = models.TimeField(null=True, blank=True)

    # ---------------- Status ----------------

    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('FOLLOWUP', 'Follow Up'),
        ('CONVERTED', 'Converted'),
        ('CLOSED', 'Closed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW'
    )
    
    def enquiry_code(self):
        year = datetime.now().year
        return f"ENQ-{year}-{self.Enq_ID:04d}"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mobile_no})"

class FollowUp(models.Model):

    enquiry = models.ForeignKey(
        Enquiry,
        on_delete=models.CASCADE,
        related_name="followups"
    )

    # When the followup was logged
    done_date = models.DateField(auto_now_add=True)
    done_time = models.TimeField(auto_now_add=True)

    # Next followup schedule
    next_followup_date = models.DateField()
    next_followup_time = models.TimeField()

    remark = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)