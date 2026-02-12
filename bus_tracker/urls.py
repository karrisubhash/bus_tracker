from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import render

def home(request):
    return render(request, "admin_login.html")

urlpatterns = [
    # Django admin
    path("",home),
    path('admin/', admin.site.urls),

    # API routes
    path('api/', include('core.urls')),

    # Student pages
    path('student-login/', TemplateView.as_view(template_name="student_login.html")),
    path('student-live/', TemplateView.as_view(template_name="student_live.html")),
    

    # Admin panel pages (ONLY entry points)
    path('admin-panel/login/', TemplateView.as_view(template_name="admin_login.html")),
    path('admin-panel/live/', TemplateView.as_view(template_name="admin_live.html")),
    path('admin-panel/table/', TemplateView.as_view(template_name="admin_table.html")),
    path('admin-panel/dashboard/', TemplateView.as_view(template_name="admin_dashboard.html")),

]
