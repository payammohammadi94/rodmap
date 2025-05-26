from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction

class RoleEmployee(models.Model):
    name = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="roleEmployee/", blank=True, null=True)

    class Meta:
            verbose_name = 'گروه‌های کاری'
            verbose_name_plural = 'گروه‌های کاری'
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    role = models.ForeignKey(RoleEmployee,on_delete=models.CASCADE, related_name='roleEmployee',blank=True,null=True)
    photo = models.ImageField(upload_to="profile/",blank=True,null=True,default="software")
  
    class Meta:
        verbose_name = 'کارمندان'
        verbose_name_plural = 'کارمندان'
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    

    
@receiver(post_save,sender=User)
def create_employee(sender,instance, created,**kwargs):
    if created:
        Employee.objects.create(user=instance)
        
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="project/",blank=True,null=True)
    create = models.DateTimeField(auto_now_add=True)
    number_of_step_until_end = models.IntegerField(blank=True,null=True)
    doing_step_project = models.IntegerField(blank=True,null=True)
    create = models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        verbose_name = 'پروژه ها'
        verbose_name_plural = 'پروژه ها'
    
    def __str__(self):
        return self.name
    


class YearTask(models.Model):
    year = models.IntegerField(default=1404)

    class Meta:
        verbose_name = 'سال انجام پروژه'
        verbose_name_plural = 'سال انجام پروژه'

    def __str__(self):
        return str(self.year)
    


class Task(models.Model):
    MONTH_CHOICES = (
        (1,"فروردین"),
        (2,"اردیبهشت"),
        (3,"خرداد"),
        (4,"تیر"),
        (5,"مرداد"),
        (6,"شهریور"),
        (7,"مهر"),
        (8,"آبان"),
        (9,"آذر"),
        (10,"دی"),
        (11,"بهمن"),
        (12,"اسفند"),
    )

    STATUS_CHOICES = (
        ("pending","pending"),         #color normal
        ("complete","complete"),       #color green
        ("field","field"),             #color red 
        ("stopProject","stopProject"), #color gray
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_employees = models.ManyToManyField(Employee, related_name='TaskAssignment')  # ارتباط چند به چند
    numbers_employees_work = models.IntegerField() #تعداد افرادی که روی این تسک کار میکند
    isTaskMaster = models.BooleanField() #آیا تسک کار فرمایی هست یا نه؟
    year = models.ForeignKey(YearTask, on_delete=models.CASCADE, related_name='task_years', default=1404)
    month = models.IntegerField(choices=MONTH_CHOICES)
    deadline = models.IntegerField()

    task_status = models.CharField(max_length=20, choices=STATUS_CHOICES,default="pending")
    isHiden = models.BooleanField(default=False)

    create = models.DateTimeField(auto_now_add=True,db_index=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تسک‌ها'
        verbose_name_plural = 'تسک‌ها'
    
    def __str__(self):
        return f"{self.year.year}-{self.month}-{self.deadline} - {self.title}"
    
class TaskAssignment(models.Model):
    STATUS_CHOICES = (
        ("pending","pending"),         #color normal
        ("complete","complete"),       #color green
        ("field","field"),             #color red 
        ("stopProject","stopProject"), #color gray
    )
    LEVEL_CHOICES = (
        (1,"EASY"),
        (2,"MEDIUM"),
        (3,"HARD"),
        (4,"CHALLENGE"),
        (5,"SHORT TIME")
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE,related_name='taskAssignment')
    employee_status = models.CharField(max_length=20, choices=STATUS_CHOICES,default="pending")  # آیا کارمند تسک را به موقع تمام کرده؟
    description = models.TextField(blank=True,null=True)
    task_level = models.IntegerField(choices=LEVEL_CHOICES,default=1)

    create  = models.DateTimeField(auto_now_add=True,db_index=True)
    update  = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.employee.user.username} - {self.task.year.year}-{self.task.month}-{self.task.deadline} - {self.task.title}"


    class Meta:
        verbose_name = 'تعیین وضعیت کارمندان'
        verbose_name_plural = 'تعیین وضعیت کارمندان'

@receiver(post_save, sender=Task)
def create_task_assignments(sender, instance, created, **kwargs):
    if created:  # فقط زمانی که یک تسک جدید ساخته شود اجرا شود
        transaction.on_commit(lambda: assign_employees_to_task(instance))

def assign_employees_to_task(task):
    for employee in task.assigned_employees.all():
        TaskAssignment.objects.get_or_create(task=task, employee=employee)