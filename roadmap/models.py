from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

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

    # New fields for tracking date changes
    previous_year = models.ForeignKey(YearTask, on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_tasks')
    previous_month = models.IntegerField(null=True, blank=True)
    previous_deadline = models.IntegerField(null=True, blank=True)
    date_change_count = models.IntegerField(default=0)
    date_change_history = models.JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):
        # Check if this is a new instance
        if not self.pk:
            super().save(*args, **kwargs)
            return

        # Get the old instance from database
        old_instance = Task.objects.get(pk=self.pk)
        
        # Check if any date fields have changed
        date_changed = (
            old_instance.year != self.year or
            old_instance.month != self.month or
            old_instance.deadline != self.deadline
        )

        if date_changed:
            # Store previous values
            self.previous_year = old_instance.year
            self.previous_month = old_instance.month
            self.previous_deadline = old_instance.deadline
            
            # Increment change counter
            self.date_change_count += 1
            
            # Add to change history
            change_record = {
                'timestamp': timezone.now().isoformat(),
                'previous_year': old_instance.year.year if old_instance.year else None,
                'previous_month': old_instance.month,
                'previous_deadline': old_instance.deadline,
                'new_year': self.year.year,
                'new_month': self.month,
                'new_deadline': self.deadline
            }
            
            if not self.date_change_history:
                self.date_change_history = []
            self.date_change_history.append(change_record)

        super().save(*args, **kwargs)

    def get_date_change_history(self):
        """Return formatted date change history"""
        return self.date_change_history

    def get_date_change_count(self):
        """Return the number of times the date has been changed"""
        return self.date_change_count

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