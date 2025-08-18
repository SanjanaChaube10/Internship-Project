# accounts/urls.py
from django.urls import path
from . import views
from .views import dashboard_view, profile_edit_view

urlpatterns = [
    # User auth
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    # Admin auth
    path('admin-register/', views.admin_register, name='admin_register'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),


    path("dashboard/", dashboard_view, name="dashboard"),
    path("profile/edit/", profile_edit_view, name="profile_edit"),
] 