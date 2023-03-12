from django.db import models
from datetime import date
import uuid
from django.contrib.auth import get_user_model
# Create your models here

User = get_user_model()


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    desc = models.TextField()

    def __str__(self):
        return self.name


class EventPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=100)
    college = models.CharField(max_length=100)
    header = models.CharField(max_length=100)
    desc = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.TextField(default='')
    tag = models.CharField(max_length=100, default='')
    eventdate = models.IntegerField(default=1)
    eventday = models.TextField(default="")
    eventmonth = models.TextField(default="")
    eventyear = models.IntegerField(default=2022)
    organizer = models.CharField(max_length=100, default='')
    participants = models.IntegerField(max_length=100, default=0)

    def __str__(self):
        return self.title


class colleges(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    uniqid = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.name


class student(models.Model):

    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    country = models.CharField(max_length=100)
