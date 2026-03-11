from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:id>/', views.delete_student, name='delete_student'),
    path('export/excel/', views.export_students_excel, name='export_students_excel'),
    path('export/pdf/', views.export_students_pdf, name='export_students_pdf'),
]