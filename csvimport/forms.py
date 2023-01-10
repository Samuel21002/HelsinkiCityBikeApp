from django import forms
from .models import Csv

# Template form for uploading a CSV file
class CsvModelForm(forms.ModelForm):
    class Meta:
        model = Csv
        fields = ('file_name',)