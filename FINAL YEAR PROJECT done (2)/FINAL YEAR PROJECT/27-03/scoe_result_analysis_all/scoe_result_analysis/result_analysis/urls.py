from django.urls import path
from . import views
from .views import department_analysis, upload_excel
from .views import generate_pdf


urlpatterns = [
    path('', upload_excel, name='upload_sheet'),  # Landing page
    path('upload/', upload_excel, name='upload_excel'),  # Upload Excel sheet
    path('delete_records/', views.delete_records, name='delete_records'),
    path('department_student_count/', views.department_analysis, name='department_student_count'),
    path('subject/', views.enter_subject_names, name='enter_subject_names'),
    path('add_department/', views.add_department, name='add_department'),
    # path('generate_pdf/', generate_pdf, name='generate_pdf'),  # Define the URL pattern for generating the PDF
    # path('subject_pass_fail_count/', subject_pass_fail_count, name='subject_pass_fail_count'),
    # path('first-5-toppers/', views.first_5_toppers, name='first_5_toppers'),
    # path('division-pass-percentage/', views.division_pass_percentage, name='division_pass_percentage'),
    # path('subject-toppers/', views.subject_toppers, name='subject_toppers'),
]

    # other URL patterns...