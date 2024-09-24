from django.db import models
from django.utils import timezone

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    prn_identifier = models.CharField(max_length=10,null=True)  # PRN Identifier for the department

    def __str__(self):
        return self.department_name    

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    prn = models.CharField(max_length=20, blank=True, null=True)
    division = models.CharField(max_length=10, blank=True, null=True)  # New field: Division
    gender = models.CharField(max_length=1, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    year_of_study = models.CharField(max_length=2)


    def __str__(self):  
        return f"{self.first_name} {self.last_name}"

class SubjectMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)   
    first_CIA = models.FloatField(null=True, blank=True)
    first_ESE = models.FloatField(null=True, blank=True)
    first_T = models.FloatField(null=True, blank=True)
    first_GP = models.FloatField(null=True, blank=True)
    first_GR = models.CharField(null=True,max_length=100)
    second_CIA = models.FloatField(null=True, blank=True)
    second_ESE = models.FloatField(null=True, blank=True)
    second_T = models.FloatField(null=True, blank=True)
    second_GP = models.FloatField(null=True, blank=True)
    second_GR = models.CharField(null=True,max_length=100)
    third_CIA = models.FloatField(null=True, blank=True)
    third_ESE = models.FloatField(null=True, blank=True)
    third_T = models.FloatField(null=True, blank=True)
    third_GP = models.FloatField(null=True, blank=True)
    third_GR = models.CharField(null=True,max_length=100)
    fourth_CIA = models.FloatField(null=True, blank=True)
    fourth_ESE = models.FloatField(null=True, blank=True)
    fourth_T = models.FloatField(null=True, blank=True)
    fourth_GP = models.FloatField(null=True, blank=True)
    fourth_GR = models.CharField(null=True,max_length=100)
    fifth_CIA = models.FloatField(null=True, blank=True)
    fifth_ESE = models.FloatField(null=True, blank=True)
    fifth_T = models.FloatField(null=True, blank=True)
    fifth_GP = models.FloatField(null=True, blank=True)
    fifth_GR = models.CharField(null=True,max_length=100)

    def __str__(self):
        return f"{self.student}"
        

class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject_name