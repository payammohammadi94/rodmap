from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, ProjectViewSet, TaskViewSet, TaskAssignmentViewSet

app_name = 'api'
# ایجاد Router برای مدیریت API
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'task-assignments', TaskAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),  # همه API ها از طریق این روت در دسترس خواهند بود
]