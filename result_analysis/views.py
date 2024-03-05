import pandas as pd  # Import pandas for Excel file handling
from .models import Student  # Import your models here
from django.shortcuts import render, redirect
from django.contrib import messages  # Import messages framework
import pandas as pd  # Import pandas for Excel file handling
from .models import Student 


def upload_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if excel_file:
            try:
                # Read Excel file into DataFrame
                df = pd.read_excel(excel_file)
                
                # Iterate over DataFrame rows and save data to the database
                for index, row in df.iterrows():
                    student = Student.objects.create(
                        first_name=row['Name'],
                        middle_name=row['Middlename'],
                        last_name=row['Surname'],
                        prn=row['PRN'],
                        # Add other fields from the Excel columns as needed
                    )
                    # Save the student object
                    student.save()
                
                # Display success message
                messages.success(request, 'Data uploaded successfully!')
            except Exception as e:
                # Display error message if there is any exception
                messages.error(request, f'Error uploading data: {str(e)}')
        else:
            # Display error message if no file selected
            messages.error(request, 'No file selected.')
    return render(request, 'upload_excel.html')


