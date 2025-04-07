from django.db import models
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# # Create your models here.

# class profileModel(models.Model):
#     user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile",blank=True,null=True)
#     first_name = models.CharField( max_length=50,blank=True,null=True)
#     last_name = models.CharField( max_length=50,blank=True,null=True)
#     phone = models.CharField(max_length=15,blank=True,null=True)
#     photo = models.ImageField(upload_to="profile/",blank=True,null=True)
    
#     def __str__(self):
#         return "{}-{}".format(self.first_name,self.last_name)


# @receiver(post_save,sender=User)
# def create_profile(sender,instance,created,**kwargs):
#     if created:
#         profileModel.objects.create(user=instance)