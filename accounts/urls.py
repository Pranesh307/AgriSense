from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',auth_views.LoginView.as_view(template_name='login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('dashboard/',views.dashboard_view,name='dashboard'),
    path('signup/',views.signup_view,name='register'),
]