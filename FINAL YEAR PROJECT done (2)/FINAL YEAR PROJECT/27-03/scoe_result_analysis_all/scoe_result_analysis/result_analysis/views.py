import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages  
from django.db import models
from .models import Student, Department,Subject,SubjectMark
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import F,Sum,Value as V
from django.db.models import Count, Max
from django.db.models import Count, Case, When, IntegerField
from django.db.models.functions import Coalesce
from django.template.loader import get_template
from django.db.models import Q
from xhtml2pdf import pisa
from django.db.models import Count, Case, When, IntegerField, F, ExpressionWrapper, FloatField
from .models import Department, Student, SubjectMark, Subject
import matplotlib.pyplot as plt
from io import BytesIO
from django.db.models import Avg
import matplotlib.pyplot as plt
import io
import urllib, base64


def upload_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if excel_file:
            try:
                df = pd.read_excel(excel_file)

                for _, row in df.iterrows():
                    first_name = row['Name']
                    middle_name = row['Middlename']
                    last_name = row['Surname']
                    prn = row['PRN']
                    division = row['Division']

                    prn_prefix = prn[:3]

                    try:
                        department = Department.objects.get(prn_identifier=prn_prefix)
                    except Department.DoesNotExist:
                        department = None

                    student, _ = Student.objects.get_or_create(
                        first_name=first_name,
                        middle_name=middle_name,
                        last_name=last_name,
                        prn=prn,
                        division=division,
                        department=department
                    )

                    subject_mark, _ = SubjectMark.objects.get_or_create(student=student)
                    for col, subject_name in enumerate(df.columns[4:], start=4):
                        # marks = pd.to_numeric(row[col], errors='coerce')
                        marks = row[col]

                        if not pd.isnull(marks):
                            field_mapping = {
                                5: 'first_CIA',
                                6: 'first_ESE',
                                7: 'first_T',
                                8: 'first_GP',
                                9: 'first_GR',
                                10: 'second_CIA',
                                11: 'second_ESE',
                                12: 'second_T',
                                13: 'second_GP',
                                14: 'second_GR',
                                15: 'third_CIA',
                                16: 'third_ESE',
                                17: 'third_T',
                                18: 'third_GP',
                                19: 'third_GR',
                                20: 'fourth_CIA',
                                21: 'fourth_ESE',
                                22: 'fourth_T',
                                23: 'fourth_GP',
                                24: 'fourth_GR',
                                25: 'fifth_CIA',
                                26: 'fifth_ESE',
                                27: 'fifth_T',
                                28: 'fifth_GP',
                                29: 'fifth_GR',
                            }

                            field_name = field_mapping.get(col)

                            if field_name:
                                # Check if the field name corresponds to a *_GR field
                                if field_name.endswith('_GR'):
                                    # For *_GR fields, store the value as-is
                                    setattr(subject_mark, field_name, marks)
                                else:
                                    # For other fields, set marks as a numeric value
                                    setattr(subject_mark, field_name, marks)
            
                    # Save the SubjectMark instance after setting all fields
                    subject_mark.save()

                messages.success(request, 'Data uploaded successfully!')
            except Exception as e:
                messages.error(request, f'Error uploading data: {str(e)}')
        else:
            messages.error(request, 'No file selected.')

    return render(request, 'upload_excel.html')

def get_department_name(department_id):
    try:
        department = Department.objects.get(pk=department_id)
        return department.department_name
    except Department.DoesNotExist:
        return "Unknown Department"
    
def department_analysis(request):
    # Department count
    department_counts = Student.objects.values('department_id').annotate(student_count=Count('department_id'))
    department_count_map = {}
    for department_count in department_counts:
        department_name = get_department_name(department_count['department_id'])
        department_count_map[department_name] = department_count['student_count']

    # Division-wise all-clear percentage
    all_clear_percentages_queryset = Student.objects.values('division').annotate(
        all_clear_count=Sum(
            Case(
                When(
                    Q(subjectmark__first_GR='F') |
                    Q(subjectmark__second_GR='F') |
                    Q(subjectmark__third_GR='F') |
                    Q(subjectmark__fourth_GR='F') |
                    Q(subjectmark__fifth_GR='F'),
                    then=Value(0)
                ),
                default=Value(1)
            ),
            output_field=IntegerField()  # Use IntegerField for all_clear_count
        ),
        total_count=Count('student_id'),
    ).annotate(
        all_clear_percentage=ExpressionWrapper(
            (F('all_clear_count') * 100.0) / F('total_count'),
            output_field=FloatField()  # Use FloatField for all_clear_percentage
        )
    )

    all_clear_percentages = [(item['division'], "{:.2f}".format(item['all_clear_percentage'])) for item in all_clear_percentages_queryset]

    subjects = ['first', 'second', 'third', 'fourth', 'fifth']
    subject_names = ['M-II', 'EP', 'EG', 'CFP', 'FDS']  # Desired subject names

    subject_counts = []

    for subject, subject_name in zip(subjects, subject_names):
    # Count the number of records where the grade is 'F' for each subject
        fail_count = SubjectMark.objects.filter(**{f"{subject}_GR": 'F'}).count()
    # Calculate pass count by subtracting fail count from the total number of students
        pass_count = len(SubjectMark.objects.all()) - fail_count
        subject_counts.append((subject_name, pass_count, fail_count))


    # Subject toppers
    subject_toppers = {}
    subject_fields = {
        'M-II': ['first_T', 'first_ESE', 'first_T', 'first_GP', 'first_GR'],
        'EP': ['second_T', 'second_ESE', 'second_T', 'second_GP', 'second_GR'],
        'EG': ['third_T', 'third_ESE', 'third_T', 'third_GP', 'third_GR'],
        'CFP': ['fourth_T', 'fourth_ESE', 'fourth_T', 'fourth_GP', 'fourth_GR'],
        'FDS': ['fifth_T', 'fifth_ESE', 'fifth_T', 'fifth_GP', 'fifth_GR'],
    }
    for subject, fields in subject_fields.items():
        max_marks = SubjectMark.objects.aggregate(Max(fields[2]))[f"{fields[2]}__max"]
        toppers = SubjectMark.objects.filter(**{fields[2]: max_marks}).annotate(
            student_name=Concat('student__first_name', Value(' '), 'student__last_name', output_field=CharField()),
            marks=Value(max_marks)
        ).values('student_name', 'marks')
        subject_toppers[subject] = list(toppers)

    # Failed counts by division
    division_failed_counts = {}

    # Initialize the dictionary with keys for all divisions and failure counts
    for division in Student.objects.values_list('division', flat=True).distinct():
        division_failed_counts[division] = {i: 0 for i in range(1, 6)}

    for subject_mark in SubjectMark.objects.all():
        division = subject_mark.student.division  # Retrieve division directly from Student model
        fail_count = 0
        for subject in subjects:
            # Check if the grade for the current subject is 'F' (indicating failure)
            if getattr(subject_mark, f"{subject}_GR") == 'F':
                fail_count += 1


        # Increment the count of students failed in the appropriate number of subjects
        if fail_count in division_failed_counts[division]:  # Ensure the key exists
            division_failed_counts[division][fail_count] += 1
        else:
            # Handle the case if the fail_count exceeds the expected range
            # For example, if a student fails in 6 or more subjects
            division_failed_counts[division][5] += 1
        
    # First 5 toppers
    top_5_students = SubjectMark.objects.annotate(
        total_marks=ExpressionWrapper(
            F('first_T') + F('second_T') + F('third_T') + F('fourth_T') + F('fifth_T'),
            output_field=FloatField()  # Use FloatField for total_marks
        )
    ).order_by('-total_marks')[:5]

    max_total_marks = 5 * 100
    for student in top_5_students:
        percentage = (student.total_marks / max_total_marks) * 100
        student.percentage = round(percentage, 2)
    
    context = {
        'department_counts': department_count_map,
        'all_clear_percentages': all_clear_percentages,
        'subject_counts': subject_counts,
        'subject_toppers': subject_toppers,
        'failed_counts': division_failed_counts,
        'top_5_students': top_5_students
    }

    students = Student.objects.all()
    student_averages = []

    for student in students:
        subject_marks = SubjectMark.objects.filter(student=student)
        total_marks = 0
        total_subjects = 0

        for marks in subject_marks:
            total_marks += (
                (marks.first_CIA or 0) + (marks.first_ESE or 0) + (marks.first_T or 0) + (marks.first_GP or 0) +
                (marks.second_CIA or 0) + (marks.second_ESE or 0) + (marks.second_T or 0) + (marks.second_GP or 0) +
                (marks.third_CIA or 0) + (marks.third_ESE or 0) + (marks.third_T or 0) + (marks.third_GP or 0) +
                (marks.fourth_CIA or 0) + (marks.fourth_ESE or 0) + (marks.fourth_T or 0) + (marks.fourth_GP or 0) +
                (marks.fifth_CIA or 0) + (marks.fifth_ESE or 0) + (marks.fifth_T or 0) + (marks.fifth_GP or 0)
            )
            total_subjects += 5  # Assuming 5 subjects per student

        if total_subjects > 0:
            average_marks = total_marks / total_subjects
            student_averages.append(average_marks)

    # Plot the bell curve
    plt.figure(figsize=(10, 5))
    plt.hist(student_averages, bins=10, edgecolor='black', density=True)
    plt.title('Bell Curve of Student Average Performance')
    plt.xlabel('Average Marks')
    plt.ylabel('Density')

    # Save plot to a PNG image in memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    return render(request, 'department_student_count.html', context)



def add_department(request):
    departments = Department.objects.all()  # Retrieve all departments
    
    if request.method == 'POST':
        department_name = request.POST.get('department_name')
        prn_identifier = request.POST.get('prn_identifier')

        # Create new department
        Department.objects.create(department_name=department_name, prn_identifier=prn_identifier)

        return redirect('add_department')  # Redirect to the same page after adding department
    
    return render(request, 'add_department.html', {'departments': departments})

def generate_pdf(request):
    template_path = 'department_analysis_pdf_template.html'
    context = {
        # Provide any context data needed for PDF generation
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="department_analysis.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)

    return response

from django.shortcuts import render, redirect
from django.db.models import Max, F
from .models import SubjectMark, Subject
from django.db.models.functions import Concat
from django.db.models.functions import Concat
from django.db.models import Value, CharField

def enter_subject_names(request):
    if request.method == 'POST':
        subject1 = request.POST.get('subject1')
        subject2 = request.POST.get('subject2')
        subject3 = request.POST.get('subject3')
        subject4 = request.POST.get('subject4')
        subject5 = request.POST.get('subject5')
        
        # Save subjects to the database
        Subject.objects.create(subject_name=subject1)
        Subject.objects.create(subject_name=subject2)
        Subject.objects.create(subject_name=subject3)
        Subject.objects.create(subject_name=subject4)
        Subject.objects.create(subject_name=subject5)

        # Display success message
        success_message = "Subjects added successfully!"
        return render(request, 'enter_subject_names.html', {'success_message': success_message})

    return render(request, 'enter_subject_names.html')

from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Student, SubjectMark, Subject

def delete_records(request):
    if request.method == 'POST':
        # Use transaction.atomic to ensure atomicity of the delete operation
        with transaction.atomic():
            # Delete all records from other tables
            Student.objects.all().delete()
            SubjectMark.objects.all().delete()
            Subject.objects.all().delete()

        # Redirect to some page after deletion
        messages.success(request, 'Database Deleted')
        
        return HttpResponseRedirect(reverse('upload_excel'))




