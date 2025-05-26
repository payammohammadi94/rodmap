from django.urls import path,include
from . import views


app_name = "home"

urlpatterns = [
    path("",views.home_view,name="index"),
    path("roadmap/",views.roadmap_view,name="roadmap"),
    path("employee-report/<int:id>/",views.employee_report_view,name="employee-report"),
    path("teams/",views.teams_view,name="teams"),
    path('company-statistics/', views.task_statistics, name='company_statistics'),
    path('role-statistics/', views.role_statistics, name='role_statistics'),
]