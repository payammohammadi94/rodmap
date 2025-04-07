from roadmap.models import Employee,Project,Task,YearTask,TaskAssignment
from rest_framework import serializers
from django.contrib.auth.models import User


# ✅ سریالایزر برای User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']  # هر فیلدی که نیاز داری اضافه کن

# ✅ سریالایزر برای Employee (اضافه کردن اطلاعات User)
class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # اطلاعات User را به JSON اضافه می‌کند

    class Meta:
        model = Employee
        fields = '__all__'

class YearTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearTask
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)  # نمایش اطلاعات پروژه
    assigned_employees = EmployeeSerializer(many=True, read_only=True)  # نمایش اطلاعات کارمندان
    year = YearTaskSerializer(read_only=True)
    class Meta:
        model = Task
        fields = '__all__'

class TaskAssignmentSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskAssignment
        fields = '__all__'

