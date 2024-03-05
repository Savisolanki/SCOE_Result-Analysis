from django.db import models

# Create your models here.
# result_analysis/models.py

from django.db import models

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    prn = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year_of_study = models.CharField(max_length=2)  # Assuming 'FY', 'SY', 'TY', etc.

    # Add other relevant student information fields as needed

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100)

    def __str__(self):
        return self.subject_name

