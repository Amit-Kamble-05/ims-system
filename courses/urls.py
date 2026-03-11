from django.urls import path
from . import views

urlpatterns = [
    path('admission/course/<int:student_id>/',views.course_admission, name='course_admission'),
    path('ajax/course-contents/', views.get_course_contents, name='get_course_contents'),
    path('admission/detail/<int:admission_id>/', views.admission_detail, name='admission_detail'),
    path('admission/receipt/<int:admission_id>/', views.admission_receipt, name='admission_receipt'),
    path('admission/edit/<int:admission_id>/', views.edit_admission, name='edit_admission'),
    path('installment/mark-paid/<int:installment_id>/', views.mark_installment_paid, name='mark_installment_paid'),
    path('verify/admission/<int:admission_id>/', views.verify_admission, name='verify_admission'),
    path('fees/receipt-list/', views.receipt_list, name='receipt_list'),
]