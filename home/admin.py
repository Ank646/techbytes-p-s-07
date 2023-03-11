from django.contrib import admin
from home.models import Contact
from home.models import EventPage
from home.models import colleges
from home.models import student

# Register your models here.

admin.site.register(Contact)

admin.site.register(student)
admin.site.register(colleges)
admin.site.register(EventPage)
