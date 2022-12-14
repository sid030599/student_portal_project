from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Notes(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    def __str__ (self):
        return self.title

    class Meta:
        verbose_name = 'notes'
        verbose_name_plural = 'notes'

class Homework(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    subject = models.CharField(max_length=30)
    title = models.CharField(max_length=100)
    description = models.TextField()
    due = models.DateField()
    is_finished = models.BooleanField()

    def __str__(self):
        return self.title

class Todo(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    is_finished = models.BooleanField()


    def __str__(self):
        return self.title