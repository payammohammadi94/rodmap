from django.shortcuts import render,HttpResponse,redirect
from django.db.models import Q
from django.shortcuts import get_object_or_404

from roadmap.models import Project,YearTask,Task,TaskAssignment,Employee,RoleEmployee
import jdatetime
from collections import defaultdict
from django.db.models import Count
from django.contrib.auth.decorators import login_required

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
        
        # Add difficulty tracking
        difficulty_stats = {
            "hard": 0,
            "easy": 0,
            "medium": 0,
            "total": 0,
            "challenge": 0,
            "shortTime": 0,
        }

        date_time_now = jdatetime.datetime.now()
        year_date = date_time_now.year

        employee = get_object_or_404(Employee,id=id)
        years = YearTask.objects.all()
        selected_year = request.GET.get('year')
        if selected_year:
            year_filter = selected_year
        else:
            year_filter = year_date

        assignments = TaskAssignment.objects.filter(
            employee=employee,
            task__year__year=year_filter
        ).select_related('task', 'task__project').order_by('task__month')

        report_by_month = defaultdict(lambda: {
            'tasks': [],
            'hard_tasks': 0,
            'easy_tasks': 0,
            'medium_tasks': 0,
            'challenge_tasks': 0,
            'shortTime_tasks': 0,
            'total_tasks': 0
        })

        for assignment in assignments:
            month = assignment.task.month
            month_name = month_dict.get(str(month))
            
            # Add task to monthly list
            report_by_month[month_name]['tasks'].append(assignment)
            
            # Update difficulty stats
            if assignment.task_level == 3: #hard
                report_by_month[month_name]['hard_tasks'] += 1
                difficulty_stats['hard'] += 1
            elif assignment.task_level == 1:
                report_by_month[month_name]['easy_tasks'] += 1
                difficulty_stats['easy'] += 1
            elif assignment.task_level == 2: #medium
                report_by_month[month_name]['medium_tasks'] += 1
                difficulty_stats['medium'] += 1
            elif assignment.task_level == 4:
                report_by_month[month_name]['challenge_tasks'] += 1
                difficulty_stats['challenge'] += 1
            elif assignment.task_level == 5: #shortTime
                report_by_month[month_name]['shortTime_tasks'] += 1
                difficulty_stats['shortTime'] += 1
            
            report_by_month[month_name]['total_tasks'] += 1
            difficulty_stats['total'] += 1
            
            report_status[assignment.employee_status] += 1
            report_status["total"] += 1

        context = {
            "employee": employee,
            "monthly_tasks": dict(report_by_month),
            "report_status": report_status,
            "difficulty_stats": difficulty_stats,
            "years": years,
            "selected_year": selected_year
        }
        return render(request,"home/reportEmployee.html",context)

    else:
        return render(request,"home/404.html")



@login_required
def task_statistics(request):
    # Get all years
    years = YearTask.objects.all().order_by('year')
    
    # Get selected year from request
    selected_year = request.GET.get('year')
    
    # Initialize statistics dictionary
    stats = {}
    
    # If a year is selected, only show that year's data
    if selected_year:
        years = years.filter(year=selected_year)
    
    for year in years:
        year_stats = {
            'year': year.year,
            'monthly_stats': {},
            'total_stats': {
                'pending': 0,
                'complete': 0,
                'field': 0,
                'stopProject': 0
            },
            'monthly_totals': [],  # For total tasks graph
            'monthly_success': [],  # For successful tasks graph
            'monthly_failed': []    # For failed tasks graph
        }
        
        # Get tasks for this year
        tasks = Task.objects.filter(year=year)
        
        # Monthly statistics
        for month in range(1, 13):
            month_tasks = tasks.filter(month=month)
            month_stats = {
                'pending': month_tasks.filter(task_status='pending').count(),
                'complete': month_tasks.filter(task_status='complete').count(),
                'field': month_tasks.filter(task_status='field').count(),
                'stopProject': month_tasks.filter(task_status='stopProject').count(),
                'total': month_tasks.count()
            }
            
            # Update total stats
            year_stats['total_stats']['pending'] += month_stats['pending']
            year_stats['total_stats']['complete'] += month_stats['complete']
            year_stats['total_stats']['field'] += month_stats['field']
            year_stats['total_stats']['stopProject'] += month_stats['stopProject']
            
            # Add to graph data arrays
            year_stats['monthly_totals'].append(month_stats['total'])
            year_stats['monthly_success'].append(month_stats['complete'])
            year_stats['monthly_failed'].append(month_stats['field'])
            
            year_stats['monthly_stats'][month] = month_stats
        
        stats[year.year] = year_stats
    
    context = {
        'stats': stats,
        'month_names': dict(Task.MONTH_CHOICES),
        'status_choices': dict(Task.STATUS_CHOICES),
        'available_years': YearTask.objects.all().order_by('year'),
        'selected_year': selected_year
    }
    
    return render(request, 'home/task_statistics.html', context)

@login_required
def role_statistics(request):
    # Get selected year from request
    selected_year = request.GET.get('year')
    
    # Initialize monthly statistics dictionary
    monthly_stats = {}
    annual_stats = {}
    
    if selected_year:
        # Get tasks for the selected year
        tasks = Task.objects.filter(year__year=selected_year)
        
        # Get all roles
        roles = RoleEmployee.objects.all()
        
        # Initialize annual statistics for each role
        for role in roles:
            annual_stats[role.name] = {
                'pending': 0,
                'complete': 0,
                'field': 0,
                'stopProject': 0,
                'total': 0
            }
        
        # Process each month
        for month in range(1, 13):
            month_tasks = tasks.filter(month=month)
            
            # Initialize role statistics for this month
            month_role_stats = {}
            
            # Process each role
            for role in roles:
                # Get tasks assigned to employees in this role for this month
                role_tasks = month_tasks.filter(assigned_employees__role=role).distinct()
                
                month_stats = {
                    'pending': role_tasks.filter(task_status='pending').count(),
                    'complete': role_tasks.filter(task_status='complete').count(),
                    'field': role_tasks.filter(task_status='field').count(),
                    'stopProject': role_tasks.filter(task_status='stopProject').count(),
                    'total': role_tasks.count()
                }
                
                # Update annual statistics
                annual_stats[role.name]['pending'] += month_stats['pending']
                annual_stats[role.name]['complete'] += month_stats['complete']
                annual_stats[role.name]['field'] += month_stats['field']
                annual_stats[role.name]['stopProject'] += month_stats['stopProject']
                annual_stats[role.name]['total'] += month_stats['total']
                
                month_role_stats[role.name] = month_stats
            
            # Only add month to stats if there are any tasks
            if any(role_data['total'] > 0 for role_data in month_role_stats.values()):
                monthly_stats[month] = month_role_stats
    
    context = {
        'monthly_stats': monthly_stats,
        'annual_stats': annual_stats,
        'month_names': dict(Task.MONTH_CHOICES),
        'available_years': YearTask.objects.all().order_by('year'),
        'selected_year': selected_year
    }
    
    return render(request, 'home/role_statistics.html', context)
