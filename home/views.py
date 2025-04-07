from django.shortcuts import render,HttpResponse,redirect
from django.db.models import Q
from django.shortcuts import get_object_or_404

from roadmap.models import Project,YearTask,Task,TaskAssignment,Employee,RoleEmployee
import jdatetime
from collections import defaultdict

def home_view(request):
    employees = Employee.objects.all()
    projects = Project.objects.all()
    for i in projects:
        print(i.photo.url)
    context = {
        "employees":employees,
        "projects":projects,
    }
    return render(request,"home/index.html",context)

def roadmap_view(request):
    month_dict = {
        "1":"فروردین",
        "2":"اردیبهشت",
        "3":"خرداد",
        "4":"تیر",
        "5":"مرداد",
        "6":"شهریور",
        "7":"مهر",
        "8":"آبان",
        "9":"آذر",
        "10":"دی",
        "11":"بهمن",
        "12":"اسفند",
    }

    date_time_now = jdatetime.datetime.now()
    year_date = date_time_now.year
    month_date = date_time_now.month
    projects = Project.objects.all()
    years =  YearTask.objects.all()
        # دریافت مقادیر فیلتر از GET
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    selected_project = request.GET.get('project')
    month_show_html = month_dict.get(str(month_date))
    year_show_html = str(year_date)
    if( (selected_project and selected_project!="Project") or (selected_month and selected_month!="Month") or (selected_year and selected_year!="Year")):
        tasks = Task.objects.all().order_by('deadline')
        
        if selected_year and selected_year!="Year":
            tasks = tasks.filter(year__year=selected_year,isHiden=False)
            year_show_html = str(selected_year)
        if selected_month and selected_month!="Month":
            tasks = tasks.filter(month=selected_month,isHiden=False)
            month_show_html = month_dict.get(str(selected_month))
        if selected_project and selected_project!="Project":
            tasks = tasks.filter(project__name=selected_project,isHiden=False)
    else:
        tasks = Task.objects.filter(Q(year__year = year_date ) & Q(month=month_date) & Q(isHiden=False)).order_by('deadline')

    context = {"projects":projects,"years":years,"tasks":tasks,"month_show_html":month_show_html,"year_show_html":year_show_html}
    return render(request,"home/roadmap.html",context)

def teams_view(request):
    roles = RoleEmployee.objects.prefetch_related('roleEmployee__user')  # roleEmployee = related_name

    context = {
        "roles": roles
    }
    return render(request,"home/teams.html",context)

def employee_report_view(request,id):
    if (request.user.id == id or request.user.is_superuser):
        month_dict = {
            "1":"فروردین",
            "2":"اردیبهشت",
            "3":"خرداد",
            "4":"تیر",
            "5":"مرداد",
            "6":"شهریور",
            "7":"مهر",
            "8":"آبان",
            "9":"آذر",
            "10":"دی",
            "11":"بهمن",
            "12":"اسفند",
        }

        report_status = {
            "complete": 0,
            "field": 0,
            "pending": 0,
            "stopProject": 0,
            "total": 0
        }

        date_time_now = jdatetime.datetime.now()
        year_date = date_time_now.year
        #month_date = date_time_now.month

        employee = get_object_or_404(Employee,id=id)
        years = YearTask.objects.all()
        selected_year = request.GET.get('year')
        if selected_year:
            year_filter = selected_year
        else:
            year_filter = year_date
        # تمام تسک‌های مرتبط با این کارمند در سال ۱۴۰۴
        assignments = TaskAssignment.objects.filter(
            employee=employee,
            task__year__year=year_filter
        ).select_related('task', 'task__project').order_by('task__month')

            # دیکشنری پیش‌فرض برای نگهداری لیست‌ها به تفکیک ماه
        report_by_month = defaultdict(list)

        for assignment in assignments:
            month = assignment.task.month
            report_by_month[month_dict.get(str(month))].append(assignment)
            report_status[assignment.employee_status] += 1
            report_status["total"] += 1 

        context = {
            "employee": employee,
            "monthly_tasks": dict(report_by_month),  # تبدیل به دیکشنری معمولی برای استفاده در قالب
            "report_status":report_status,
            "years":years,
        }
        return render(request,"home/reportEmployee.html",context)

    else:
        return render(request,"home/404.html")