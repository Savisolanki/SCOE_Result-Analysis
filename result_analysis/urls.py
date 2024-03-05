from django.urls import path
from .views import upload_excel


urlpatterns = [
    path('', upload_excel, name='upload_sheet'),  # Landing page
    path('upload/', upload_excel, name='upload_excel'),  # Upload Excel sheet
]