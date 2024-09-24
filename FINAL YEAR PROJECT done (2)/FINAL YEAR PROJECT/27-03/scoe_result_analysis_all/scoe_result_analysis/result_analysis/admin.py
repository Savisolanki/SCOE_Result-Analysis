from django.contrib import admin

# Register your models here.
# result_analysis/admin.py

from django.contrib import admin
from .models import SubjectMark
from .models import Student, Department, Subject

admin.site.register(Student)
admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(SubjectMark)
