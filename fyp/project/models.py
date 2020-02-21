from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=150)
    dataset = models.FileField(upload_to='datasets/')
    pub_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Dataset(models.Model):
    title = models.CharField(max_length=100)
    columns = models.TextField()
    size = models.CharField(max_length=100)
