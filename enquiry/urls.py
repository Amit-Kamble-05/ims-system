from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_enquiry, name='add_enquiry'),
    path('reports/', views.enquiry_reports, name='enquiry_reports'),
    path('detail/<int:id>/', views.enquiry_detail,name='enquiry_detail'),
    path("followup/add/<int:id>/", views.add_followup, name="add_followup"),
    path('convert-admission/<int:id>/', views.convert_to_admission, name='convert_to_admission'),
    path('status/<int:id>/<str:status>/', views.change_status, name='change_status'),
    path('ajax/course-contents/', views.get_course_contents, name='get_course_contents'),
    path("edit/<int:id>/", views.edit_enquiry, name="edit_enquiry"),
    path('export/enquiry/excel/', views.export_enquiry_excel, name='export_enquiry_excel'),
]