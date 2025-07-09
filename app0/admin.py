from django.contrib import admin
from .models import Registration,Course,Instructor,Enrollment

# Register your models here.

admin.site.register(Registration)
admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(Enrollment)
