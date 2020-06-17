from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=150)
    pub_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Dataset(models.Model):
    dataset = models.FileField(upload_to='datasets/',default="")
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    columns = models.TextField()
    size = models.CharField(max_length=100)

    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        self.dataset.delete()
        super().delete(*args, **kwargs)

class Plot(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    columns = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)
    plottype = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title