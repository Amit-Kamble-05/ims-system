from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from decimal import Decimal
from courses.models import Admission, Installment
from .models import Student
from enquiry.models import Enquiry


@login_required
def student_list(request):

    search = request.GET.get('search')
    status_filter = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    admissions = Admission.objects.select_related(
        'student', 'course'
    ).order_by('-id')   

    student_data = []

    for admission in admissions:

        s = admission.student

        # SEARCH
        if search:
            if not (
                search.lower() in s.first_name.lower() or
                search.lower() in s.last_name.lower() or
                (s.phone and search in s.phone)
            ):
                continue

        # TOTAL PAID
        total_paid = Installment.objects.filter(
            admission=admission,
            status='PAID'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # FEES
        registration_fee = Decimal('100.00')
        total_fees = admission.discounted_fees + registration_fee
        due_fees = total_fees - total_paid

        # DATE FILTER
        admission_date = admission.admission_date.date()

        if start_date and end_date:
            if not (start_date <= str(admission_date) <= end_date):
                continue

        # STATUS FILTER
        if status_filter and admission.status != status_filter:
            continue

        student_data.append({
            'student': s,
            'admission': admission,
            'installment': {'total_paid': total_paid},
            'due_fees': due_fees,
            'status': admission.status,
            'batch': admission.batch_time if admission.batch_time else "—",
            'track': admission.batch_type,
            'teacher': None,
            'admission_date': admission.admission_date
        })

    return render(request, 'students/student_list.html', {
        'student_data': student_data
    })

@login_required
def add_student(request):

    enquiry_id = request.GET.get("enquiry_id")
    enquiry = None

    if enquiry_id:
        enquiry = get_object_or_404(Enquiry, Enq_ID=enquiry_id)

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        city = request.POST.get('city')

        student = Student.objects.filter(phone=phone).first()
        if not student:
            student = Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                city=city
            )

        # redirect to course admission
        if enquiry:
            return redirect(
                f"/admission/course/{student.id}/"
                f"?course={enquiry.interested_course.id}"
                f"&fees={enquiry.offered_fees}"
                f"&batch_type={enquiry.batch_type}"
                f"&batch_time={enquiry.batch_time}"
                f"&course_content={enquiry.course_content}"
            )
        else:
            return redirect(f"/admission/course/{student.id}/")

    return render(request, 'students/add_student.html', {
        'first_name': enquiry.first_name if enquiry else '',
        'middle_name': enquiry.middle_name if enquiry else '',
        'last_name': enquiry.last_name if enquiry else '',
        'email': enquiry.email if enquiry else '',
        'phone': enquiry.mobile_no if enquiry else '',
        'city': '',
        'enquiry': enquiry
    })

@login_required
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect('student_list')


@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        student.email = request.POST.get('email')
        student.phone = request.POST.get('phone')
        student.city = request.POST.get('city')
        student.save()

        admission = Admission.objects.filter(student=student).first()

        if admission:
            return redirect('edit_admission', admission_id=admission.id)
        else:
            return redirect('course_admission', student_id=student.id)

    return render(request, 'students/edit_student.html', {'student': student})


def export_students_excel(request):
    pass

def export_students_pdf(request):
    pass
