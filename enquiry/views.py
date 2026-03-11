from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .forms import EnquiryForm
from .models import Enquiry, FollowUp, CourseContent
from urllib.parse import urlencode
from django.utils import timezone
import pandas as pd
from django.http import HttpResponse

def get_course_contents(request):
    course_id = request.GET.get('course_id')
    contents = CourseContent.objects.filter(course_id=course_id)

    data = []

    for c in contents:
        items = [i.strip() for i in c.content_name.split(',') if i.strip()]

        for item in items:
            data.append({
                'id': c.id,
                'name': item,
                'duration': c.course.duration,
                'fees': str(c.course.total_fees)
            })

    return JsonResponse(data, safe=False)

# ---------------- ADD ENQUIRY ----------------

def add_enquiry(request):
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            contents = request.POST.getlist("course_content[]")
            if not contents:
                form.add_error(None, "Please select at least one course content")
                return render(request, "enquiry/add_enquiry.html", {"form": form})
            enquiry.course_content = ", ".join(contents)
            enquiry.save()
            # Create first follow-up history entry
            FollowUp.objects.create(
                enquiry=enquiry,
                next_followup_date=enquiry.followup_date,
                next_followup_time=enquiry.followup_time,
                remark=enquiry.remarks
            )
            return redirect('enquiry_reports')
    else:
        form = EnquiryForm()
    return render(request, "enquiry/add_enquiry.html", {"form": form})

# ---------------- ENQUIRY REPORTS ----------------
def enquiry_reports(request):
    enquiries = Enquiry.objects.all().order_by('Enq_ID')
    context = {
        "enquiries": enquiries
    }
    return render(request, "enquiry/enquiry_reports.html", context)

# ---------------- ENQUIRY DETAIL ----------------

def enquiry_detail(request, id):
    enquiry = get_object_or_404(Enquiry, Enq_ID=id)
    followups = enquiry.followups.all().order_by('-done_date', '-done_time')
    context = {
        "enquiry": enquiry,
        "followups": followups
    }
    return render(request, "enquiry/enquiry_detail.html", context)

# ---------------- ADD FOLLOWUP ----------------
def add_followup(request, id):
    enquiry = get_object_or_404(Enquiry, Enq_ID=id)
    if request.method == "POST":
        next_date = request.POST.get("followup_date")
        next_time = request.POST.get("followup_time")
        remark = request.POST.get("remark")
        action = request.POST.get("action")

        # Save followup history
        FollowUp.objects.create(
            enquiry=enquiry,
            next_followup_date=next_date,
            next_followup_time=next_time,
            remark=remark
        )

        # Update enquiry latest followup info
        enquiry.followup_date = next_date
        enquiry.followup_time = next_time
        enquiry.remarks = remark

        # Update enquiry status based on selected action
        if action:
            enquiry.status = action
        enquiry.save()

        # If user selected CONVERTED → open admission form
        if action == "CONVERTED":
            return redirect("convert_to_admission", id=enquiry.Enq_ID)
        return redirect("enquiry_detail", id=enquiry.Enq_ID)
    return render(request, "enquiry/add_followup.html", {"enquiry": enquiry})

def convert_to_admission(request, id):
    enquiry = get_object_or_404(Enquiry, Enq_ID=id)
    # mark enquiry converted
    enquiry.status = "CONVERTED"
    enquiry.save()
    params = urlencode({

        "first_name": enquiry.first_name,
        "last_name": enquiry.last_name,
        "phone": enquiry.mobile_no,
        "email": enquiry.email,

        "course": enquiry.interested_course_id,
        "course_content": enquiry.course_content,

        "duration": enquiry.duration,
        "fees": enquiry.offered_fees,

        "batch_type": enquiry.batch_type,
        "batch_time": enquiry.batch_time

    })

    return redirect(f"/students/add/?{params}")

def change_status(request, id, status):
    enquiry = get_object_or_404(Enquiry, Enq_ID=id)
    enquiry.status = status
    enquiry.save()
    return redirect('enquiry_detail', id=enquiry.Enq_ID)

def edit_enquiry(request, id):
    enquiry = get_object_or_404(Enquiry, Enq_ID=id)
    if request.method == "POST":
        form = EnquiryForm(request.POST, instance=enquiry)
        if form.is_valid():
            enquiry = form.save(commit=False)
            contents = request.POST.getlist("course_content[]")
            enquiry.course_content = ", ".join(contents)
            enquiry.save()
            return redirect("enquiry_detail", id=enquiry.Enq_ID)
    else:
        form = EnquiryForm(instance=enquiry)
    return render(request, "enquiry/add_enquiry.html", {
        "form": form,
        "edit_mode": True
    })

def export_enquiry_excel(request):

    enquiries = Enquiry.objects.all().order_by('-Enq_ID')

    data = []

    for e in enquiries:
        data.append({
            "Enquiry Code": e.enquiry_code(),
            "Date": e.enquiry_date.strftime("%d-%m-%Y"),
            "Name": f"{e.first_name} {e.last_name}",
            "Mobile": e.mobile_no,
            "Course": str(e.interested_course),
            "Status": e.get_status_display()
        })

    df = pd.DataFrame(data)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename="enquiry_report.xlsx"'

    df.to_excel(response, index=False)

    return response