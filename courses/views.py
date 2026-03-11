from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, time, datetime
from decimal import Decimal
from django.db.models import Sum, Case, When, IntegerField
from django.views.decorators.http import require_POST
from django.utils import timezone
from students.models import Student
from enquiry.models import Enquiry
from .models import Course, CourseContent, Admission, Installment

from django.core.paginator import Paginator
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from django.conf import settings
import os

import qrcode
from io import BytesIO

# --------------------------------------------------
# AJAX: Load course contents
# --------------------------------------------------
def get_course_contents(request):
    course_id = request.GET.get('course_id')
    contents = CourseContent.objects.filter(course_id=course_id)

    data = []

    for c in contents:
        items = [i.strip() for i in c.content_name.split(',') if i.strip()]

        for item in items:
            data.append({
                'id': c.id,
                'name': item
            })

    return JsonResponse(data, safe=False)

# --------------------------------------------------
# STEP 2: Course Admission + Installments
# --------------------------------------------------

def course_admission(request, student_id):
    
    course_id = request.GET.get("course")
    course_content = request.GET.get("course_content")
    fees = request.GET.get("fees")
    batch_type = request.GET.get("batch_type")
    batch_time = request.GET.get("batch_time")
    student = get_object_or_404(Student, id=student_id)
    courses = Course.objects.all()

    if request.method == 'POST':
        course_id = request.POST.get('course')
        selected_contents = request.POST.getlist('course_content[]')

        if not selected_contents:
            return render(request, 'courses/admission_course.html', {
                'student': student,
                'courses': courses,
                'today': date.today().isoformat(),
                'error': 'Please select at least one course content'
            })

        content_string = ", ".join(selected_contents)


        # FIXED (no comma)
        batch_type = request.POST.get('batch_type')
        batch_time = request.POST.get('batch_time')

        discounted_fees_raw = request.POST.get('discounted_fees')
        payment_type = request.POST.get('payment_type')
        gst_value = request.POST.get('gst')

        # ---------- VALIDATION ----------
        if not all([
            course_id,
            selected_contents,
            batch_type,
            batch_time,
            discounted_fees_raw,
            payment_type
        ]):
            return render(request, 'courses/admission_course.html', {
                'student': student,
                'courses': courses,
                'today': date.today().isoformat(),
                'error': 'All fields including Batch details are required'
            })

        discounted_fees = Decimal(discounted_fees_raw.replace(',', '').strip())

        course = get_object_or_404(Course, id=course_id)
        course_content = CourseContent.objects.filter(course=course).first()

        if course_content:
            course_content.content_name = content_string
            course_content.save()
        else:
            course_content = CourseContent.objects.create(
                course=course,
                content_name=content_string
            )


        # ---------- CREATE ADMISSION (COURSE STAGE) ----------
        admission = Admission.objects.create(
            student=student,
            course=course,
            course_content=course_content,
            batch_type=batch_type,
            batch_time=batch_time,
            discounted_fees=discounted_fees,
            payment_type=payment_type,
            gst=True if gst_value == 'Yes' else False,
            status='COURSE'
        )

        enquiry = Enquiry.objects.filter(mobile_no=student.phone).first()

        if enquiry:
            enquiry.status = "CONVERTED"
            enquiry.save()

        # ---------- INSTALLMENTS ----------
        types = request.POST.getlist('installment_type[]')
        dates = request.POST.getlist('installment_date[]')
        amounts = request.POST.getlist('installment_amount[]')

        total_paid = Decimal('0.00')

        for t, d, a in zip(types, dates, amounts):
            if t and d and a:
                amt = Decimal(a.replace(',', '').strip())
                Installment.objects.create(
                    admission=admission,
                    installment_type=t,
                    pay_date=d,
                    amount=amt
                )
                total_paid += amt

        # ENSURE REGISTRATION FEE (OUTSIDE LOOP)
        Installment.objects.get_or_create(
            admission=admission,
            installment_type="Registration Fees",
            defaults={
                "pay_date": date.today(),
                "amount": Decimal("100.00"),
                "status": "UNPAID"
            }
        )


        # ---------- STATUS UPDATE ----------
        admission.status = 'INCOMPLETE'
        admission.save()


        return redirect('admission_detail', admission_id=admission.id)

    # ---------- GET ----------
    return render(request, 'courses/admission_course.html', {
    'student': student,
    'courses': courses,
    'today': date.today().isoformat(),
    'course_id': course_id,
    'fees': fees,
    'batch_type': batch_type,
    'batch_time': batch_time
})


# --------------------------------------------------
# Admission Detail Page
# --------------------------------------------------
def admission_detail(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)

    installments = admission.installments.annotate(
        priority=Case(
            When(installment_type__iexact='Registration Fees', then=0),
            default=1,
            output_field=IntegerField()
        )
    ).order_by('priority', 'pay_date')


    # ONLY PAID installments
    total_paid = (
        installments
        .filter(status='PAID')
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )

    registration_fee = Decimal('100.00')
    total_fees = admission.discounted_fees + registration_fee

    remaining_balance = total_fees - total_paid

    # Admission confirmation rule
    admission_confirmed = total_paid >= 100  # registration fee paid
    fees_details={
        'admission': admission,
        'installments': installments,
        'total_fees' : total_fees,
        'total_paid': total_paid,
        'remaining_balance': remaining_balance,
        'admission_confirmed': admission_confirmed
    }
    return render(request, 'students/student_admission_detail.html', fees_details)


def admission_receipt(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)
    student = admission.student
    installments = admission.installments.all()

    # ---- Calculations ----
    registration_fee = Decimal("100.00")

    total_paid = (
        installments.filter(status='PAID')
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )

    total_fees = admission.discounted_fees + registration_fee
    # course_paid = max(total_paid, Decimal("0.00"))
    remaining_fees = total_fees - total_paid

    receipt_no = f"REC-{datetime.now().year}-{admission.id:05d}"

    # ---- QR CODE ----
    verify_url = request.build_absolute_uri(f"/verify/admission/{admission.id}/")

    qr = qrcode.make(verify_url)
    qr_buffer = BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)


    # ---- PDF Setup ----
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="student_receipt.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # ---- COLORS ----
    primary = HexColor("#0d6efd")
    gray = HexColor("#6c757d")

    y = height - 40

    # ---- LOGO ----
    logo_path = os.path.join(settings.BASE_DIR, "static/img/logo.png")
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 40, y - 40, width=80, height=80, preserveAspectRatio=True)

    # ---- INSTITUTE NAME ----
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(primary)
    p.drawString(120, y, "A&A Tech Institute")

    p.setFont("Helvetica", 10)
    p.setFillColor(gray)
    p.drawString(120, y - 16, "Professional Computer Training Institute")

    # ---- RECEIPT INFO ----
    p.setFillColor(HexColor("#000000"))
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 40, y, f"Receipt No: {receipt_no}")
    p.drawRightString(width - 40, y - 15, f"Admission No: {admission.id}")
    p.drawRightString(width - 40, y - 30, f"Date: {admission.admission_date.strftime('%d-%m-%Y')}")

    y -= 80

    # ---- STUDENT DETAILS ----
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Student Details")
    y -= 15
    p.line(40, y, width - 40, y)

    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"Name: {student.first_name} {student.last_name}")
    p.drawString(320, y, f"Phone: {student.phone}")
    y -= 15
    p.drawString(40, y, f"Email: {student.email}")
    p.drawString(320, y, f"City: {student.city}")
    y -= 15
    p.drawString(40, y, f"Address: {student.address}")

    y -= 30

    # ---- COURSE DETAILS ----
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Course Details")
    y -= 15
    p.line(40, y, width - 40, y)

    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"Course: {admission.course.name}")
    y -= 15
    p.drawString(40, y, f"Course Content: {admission.course_content.content_name}")
    y -= 15
    p.drawString(40, y, f"Duration: {admission.course.duration}")
    y -= 15
    p.drawString(40, y, f"Batch: {admission.batch_type} ({admission.batch_time})")

    y -= 30

    # ---- FEES TABLE ----
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Fees Details")
    y -= 15
    p.line(40, y, width - 40, y)
    y -= 20

    # ---- ORDERED INSTALLMENTS ----
    installments = admission.installments.annotate(
        priority=Case(
            When(installment_type__iexact='Registration Fees', then=0),
            default=1,
            output_field=IntegerField()
        )
    ).order_by('priority', 'pay_date')

    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Date")
    p.drawString(140, y, "Installment")
    p.drawString(300, y, "Amount")
    p.drawString(400, y, "Status")
    y -= 10
    p.line(40, y, width - 40, y)
    y -= 15

    p.setFont("Helvetica", 10)
    for inst in installments:
        p.drawString(40, y, inst.pay_date.strftime('%d-%m-%Y'))
        p.drawString(140, y, inst.installment_type)
        p.drawString(300, y, f"Rs. {inst.amount}")
        p.drawString(400, y, inst.status)
        y -= 15

        if y < 120:
            p.showPage()
            y = height - 50

    y -= 20
    p.line(40, y, width - 40, y)
    y -= 20

    # ---- TOTALS ----
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(width - 40, y, f"Total Fees: Rs. {total_fees}")
    y -= 15
    p.drawRightString(width - 40, y, f"Paid Fees: Rs. {total_paid}")
    y -= 15
    p.drawRightString(width - 40, y, f"Remaining Fees: Rs. {remaining_fees}")

    verify_url = request.build_absolute_uri(
        f"/verify/admission/{admission.id}/"
    )

    qr = qrcode.make(verify_url)

    qr_buffer = BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)

    qr_image = ImageReader(qr_buffer)

    p.drawImage(
        qr_image,
        width - 140,
        60,
        width=90,
        height=90,
        mask='auto'
    )

    p.setFont("Helvetica", 8)
    p.drawRightString(
        width - 40,
        50,
        "Scan to verify receipt"
    )


    # ---- FOOTER ----
    y -= 40
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(gray)
    p.drawCentredString(
        width / 2, y,
        "This is a system generated receipt. No signature required."
    )

    p.showPage()
    p.save()

    return response


# --------------------------------------------------
# ADMIN: Edit Admission
# --------------------------------------------------
def edit_admission(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)

    student = admission.student
    courses = Course.objects.all()

    # Load related data
    course_contents = CourseContent.objects.filter(course=admission.course)
    installments = admission.installments.annotate(
        priority=Case(
            When(installment_type__iexact='Registration Fees', then=0),
            default=1,
            output_field=IntegerField()
        )
    ).order_by('priority', 'pay_date')


    if request.method == 'POST':
        # ---- UPDATE ADMISSION (NO DELETE) ----
        selected_contents = request.POST.getlist('course_content[]')
        if not selected_contents:
            return render(request, 'courses/admission_course.html', {
                'student': student,
                'courses': courses,
                'admission': admission,
                'course_contents': course_contents,
                'installments': installments,
                'edit_mode': True,
                'error': 'Please select at least one course content'
            })

        content_string = ", ".join(selected_contents)

        course_content = CourseContent.objects.filter(
            course=admission.course
        ).first()

        if course_content:
            course_content.content_name = content_string
            course_content.save()
        else:
            course_content = CourseContent.objects.create(
                course=admission.course,
                content_name=content_string
            )

        admission.course_content = course_content
        admission.course_id = request.POST.get('course')
        admission.discounted_fees = request.POST.get('discounted_fees')
        admission.payment_type = request.POST.get('payment_type')
        admission.gst = True if request.POST.get('gst') == 'Yes' else False
        admission.save()

        # ---- UPDATE / ADD INSTALLMENTS ----
        inst_ids = request.POST.getlist('installment_id[]')
        inst_types = request.POST.getlist('installment_type[]')
        inst_dates = request.POST.getlist('installment_date[]')
        inst_amounts = request.POST.getlist('installment_amount[]')

        for iid, t, d, a in zip(inst_ids, inst_types, inst_dates, inst_amounts):
            if iid:  # existing installment
                inst = Installment.objects.get(id=iid)
                inst.installment_type = t
                inst.pay_date = d
                inst.amount = a.replace(',', '')
                inst.save()
            else:
                # new installment added by user
                if t and d and a:
                    Installment.objects.create(
                        admission=admission,
                        installment_type=t,
                        pay_date=d,
                        amount=a.replace(',', '')
                    )

        return redirect('admission_detail', admission_id=admission.id)

    return render(request, 'courses/admission_course.html', {
        'student': student,
        'courses': courses,
        'admission': admission,
        'course_contents': course_contents,
        'installments': installments,
        'edit_mode': True
    })


@require_POST
def mark_installment_paid(request, installment_id):
    inst = get_object_or_404(Installment, id=installment_id)

    # Mark installment as PAID
    if inst.status != 'PAID':
        inst.status = 'PAID'
        inst.paid_at = timezone.now().date()
        inst.save()

    admission = inst.admission
    installments = admission.installments.all()

    # Confirm admission ONLY if registration fee is paid
    if installments.filter(
        installment_type__iexact='Registration Fees',
        status='PAID'
    ).exists():
        admission.status = 'CONFIRMED'
        admission.save()

    #  TOTAL PAID (ONLY PAID INSTALLMENTS)
    total_paid = (
        installments
        .filter(status='PAID')
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )

    #  REGISTRATION FEE SEPARATE
    registration_fee = Decimal('100.00')

    #  TOTAL FEES = COURSE + REGISTRATION
    total_fees = admission.discounted_fees + registration_fee

    #  REMAINING
    remaining_balance = total_fees - total_paid

    return JsonResponse({
        'success': True,
        'installment_status': inst.status,
        'admission_status': admission.status,
        'total_paid': str(total_paid),
        'remaining_balance': str(remaining_balance)
    })

def verify_admission(request, admission_id):
    admission = get_object_or_404(Admission, id=admission_id)

    return render(request, 'courses/verify_admission.html', {
        'admission': admission
    })


def receipt_list(request):
    today = timezone.now().date()

    # Base queryset (PAID installments only)
    receipts_qs = Installment.objects.filter(
        status='PAID'
    ).select_related(
        'admission__student',
        'admission__course'
    )

    # ---------------- FILTERS ----------------
    single_date = request.GET.get('date')
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')

    if single_date:
        receipts_qs = receipts_qs.filter(paid_at=single_date)

    elif from_date and to_date:
        receipts_qs = receipts_qs.filter(
            paid_at__range=[from_date, to_date]
        )

    else:
        # ✅ DEFAULT: CURRENT MONTH DATA
        receipts_qs = receipts_qs.filter(
            paid_at__year=today.year,
            paid_at__month=today.month
        )

    receipts_qs = receipts_qs.order_by('paid_at')

    # ---------------- TOTALS ----------------
    total_collection = receipts_qs.aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_receipt = receipts_qs.count()

    # ---------------- PAGINATION ----------------
    paginator = Paginator(receipts_qs, 10)
    page_number = request.GET.get('page')
    receipts = paginator.get_page(page_number)

    context = {
        'receipts': receipts,
        'total_collection': total_collection,
        'total_receipt': total_receipt,
    }

    return render(request, 'courses/receipt_list.html', context)

def student_list(request):

    admissions = Admission.objects.select_related('student', 'course')

    # ✅ DEBUG (temporary – remove later)
    print("GET PARAMS:", request.GET)

    sort_by = request.GET.get('sort_by')
    month = request.GET.get('month')
    single_date = request.GET.get('single_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    now = timezone.now()

    # ✅ FILTER LOGIC (THIS WILL WORK)
    if sort_by == 'month' and month:
        admissions = admissions.filter(
            admission_date__year=now.year,
            admission_date__month=int(month)
        )

    elif sort_by == 'single_date' and single_date:
        d = datetime.strptime(single_date, "%Y-%m-%d").date()
        admissions = admissions.filter(
            admission_date__gte=datetime.combine(d, time.min),
            admission_date__lte=datetime.combine(d, time.max)
        )

    elif sort_by == 'multi_date' and start_date and end_date:
        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
        ed = datetime.strptime(end_date, "%Y-%m-%d").date()
        admissions = admissions.filter(
            admission_date__gte=datetime.combine(sd, time.min),
            admission_date__lte=datetime.combine(ed, time.max)
        )

    admissions = admissions.order_by('-admission_date')

    # ✅ BUILD student_data (LIKE YOUR TEMPLATE EXPECTS)
    student_data = []

    for admission in admissions:
        total_paid = (
            admission.installments.filter(status='PAID')
            .aggregate(total=Sum('amount'))['total']
            or 0
        )

        total_fees = admission.discounted_fees + 100
        due_fees = total_fees - total_paid

        student_data.append({
            'student': admission.student,
            'admission': admission,
            'installment': {'total_paid': total_paid},
            'due_fees': due_fees,
            'status': admission.status,
            'admission_date': admission.admission_date,
            'teacher': None,
            'batch': admission.batch_time,
            'track': admission.batch_type,
        })

    return render(request, 'students/student_list.html', {
        'student_data': student_data
    })
