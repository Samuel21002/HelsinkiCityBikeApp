from django.db import models
from django.core.validators import FileExtensionValidator

# Model for the CSV-upload form, saving any uploaded CSVs to a local folder 'csv_uploads'
class Csv(models.Model):
    file_name = models.FileField(upload_to='csv_uploads', validators=[FileExtensionValidator( ['csv'], "The file must be a CSV-file!" ) ])
    upload_date = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False)

    def __str__(self):
        return f"File id: {self.pk} - {self.file_name}"

