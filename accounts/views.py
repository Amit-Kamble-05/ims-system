from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
import datetime
from courses.models import Admission, Installment
from decimal import Decimal
from django.utils import timezone
from enquiry.models import Enquiry

today_followups = Enquiry.objects.filter(
    followup_date=timezone.now().date()
).exclude(status__in=["CONVERTED", "CLOSED"]).order_by('followup_time')

def home(request):
    return redirect('admin_login')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.role == 'ADMIN':
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'custom_admin/login.html')

@login_required
def admin_dashboard(request):

    today = timezone.now().date()

    # Filters from UI
    month = request.GET.get('month', today.strftime('%Y-%m'))
    day = request.GET.get('day', today.strftime('%Y-%m-%d'))

    year, month_num = map(int, month.split('-'))
    day_date = datetime.datetime.strptime(day, "%Y-%m-%d").date()

    # Month range
    month_start = datetime.date(year, month_num, 1)
    if month_num == 12:
        month_end = datetime.date(year + 1, 1, 1)
    else:
        month_end = datetime.date(year, month_num + 1, 1)

    # Day range
    day_start = day_date
    day_end = day_date + datetime.timedelta(days=1)

    # ---------- ADMISSIONS ----------
    monthly_admissions = Admission.objects.filter(
        admission_date__gte=month_start,
        admission_date__lt=month_end
    )

    daily_admissions = Admission.objects.filter(
        admission_date__gte=day_start,
        admission_date__lt=day_end
    )

    # ---------- ENQUIRIES ----------
    monthly_enquiries = Enquiry.objects.filter(
        enquiry_date__gte=month_start,
        enquiry_date__lt=month_end
    )

    daily_enquiries = Enquiry.objects.filter(
        enquiry_date__gte=day_start,
        enquiry_date__lt=day_end
    )

    # ---------- COLLECTION ----------
    monthly_collection = (
        Installment.objects
        .filter(
            status='PAID',
            pay_date__gte=month_start,
            pay_date__lt=month_end
        )
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )

    daily_collection = (
        Installment.objects
        .filter(
            status='PAID',
            pay_date__gte=day_start,
            pay_date__lt=day_end
        )
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )

    # ---------- BILLING ----------
    monthly_course_fees = (
        monthly_admissions.aggregate(total=Sum('discounted_fees'))['total']
        or Decimal('0.00')
    )

    daily_course_fees = (
        daily_admissions.aggregate(total=Sum('discounted_fees'))['total']
        or Decimal('0.00')
    )

    registration_fee = Decimal('100.00')

    monthly_billing = monthly_course_fees + (
        monthly_admissions.count() * registration_fee
    )

    daily_billing = daily_course_fees + (
        daily_admissions.count() * registration_fee
    )

    # ---------- TODAY FOLLOWUPS ----------
    today_followups = Enquiry.objects.filter(
        followup_date=today
    ).exclude(status__in=["CONVERTED", "CLOSED"]).order_by('followup_time')

    # ---------- CONTEXT ----------
    context = {

        # Monthly
        'monthly_admission_count': monthly_admissions.count(),
        'monthly_collection': monthly_collection,
        'monthly_billing': monthly_billing,
        'monthly_enquiry_count': monthly_enquiries.count(),

        # Daily
        'daily_admission_count': daily_admissions.count(),
        'daily_collection': daily_collection,
        'daily_billing': daily_billing,
        'daily_enquiry_count': daily_enquiries.count(),

        'month': month,
        'day': day,
        'today_followups': today_followups
    }

    return render(request, 'custom_admin/dashboard.html', context)

def admin_logout(request):
    logout(request)
    return redirect('admin_login')