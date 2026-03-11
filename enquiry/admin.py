from django.contrib import admin
from .models import Enquiry, FollowUp

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = (
        'Enq_ID',
        'first_name',
        'mobile_no',
        'interested_course',
        'batch_type',
        'batch_time',
        'offered_fees',
        'followup_date',
        'followup_time',
        'status'
    )

    list_filter = ('batch_type', 'status', 'interested_course')
    search_fields = ('first_name', 'mobile_no', 'email')

admin.site.register(FollowUp)