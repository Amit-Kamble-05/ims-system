from django import forms
from .models import Enquiry
from courses.models import Course, CourseContent


class CourseChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}| {obj.duration} | Fees: {obj.total_fees}"
    
class EnquiryForm(forms.ModelForm):

    interested_course = CourseChoiceField(
        queryset=Course.objects.all(),
        empty_label="Select Course"
    )

    class Meta:
        model = Enquiry
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'mobile_no',
            'interested_course',
            'duration',
            'total_fees',
            'offered_fees',
            'batch_type',
            'batch_time',
            'source',
            'remarks',
            'followup_date',
            'followup_time'
        ]

        widgets = {

            'followup_date': forms.DateInput(attrs={'type': 'date'}),
            'followup_time': forms.TimeInput(attrs={'type': 'time'}),

            'remarks': forms.Textarea(attrs={
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})