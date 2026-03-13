from django.urls import path
from . import views
from .views import admin_signup


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path("signup/", admin_signup, name="admin_signup"),
]
