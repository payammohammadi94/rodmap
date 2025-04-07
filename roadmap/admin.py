from django.contrib import admin
from .models import Employee, Project, Task, TaskAssignment, YearTask,RoleEmployee

# نمایش کارمندان در پنل ادمین
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("user","user__first_name","user__last_name","role")
    search_fields = ("user__username","role")
    
# نمایش نقش کارمندان در پنل ادمین
@admin.register(RoleEmployee)
class RoleEmployeeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# نمایش پروژه‌ها
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

# نمایش تسک‌ها
# نمایش اختصاص تسک‌ها به کارمندان
# @admin.register(TaskAssignment)
class TaskAssignmentInlines(admin.TabularInline):
    model = TaskAssignment
    extra = 4
    # list_display = ("employee", "task",)
    # search_fields = ("employee__user__username", "task__title")
    # list_filter = ("employee_status", "task__project","task__year__year", "task__month", "task__deadline")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "year", "get_month", "deadline")
    search_fields = ("title", "project__name","year__year", "deadline","assigned_employees__user__username")
    list_filter = ("project", "deadline","year__year", "month", "deadline")
    inlines = [TaskAssignmentInlines]
    def get_month(self, obj):
        return obj.month



@admin.register(YearTask)
class YearTaskAdmin(admin.ModelAdmin):
    list_display = ("year",)
    search_fields = ("year",)
    list_filter = ("year",)