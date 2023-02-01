from django.core.validators import FileExtensionValidator
from django.db import models

# Model for the CSV-upload form
class Csv(models.Model):
    file_name = models.FileField(upload_to='csv_uploads', validators=[FileExtensionValidator( ['csv'], "The file must be a CSV-file!" ) ])
    upload_date = models.DateTimeField(auto_now_add=True)
    task_id = models.CharField(max_length=60, default="0")
    activated = models.BooleanField(default=False)

    def __str__(self):
        return f"File id: {self.pk} - {self.file_name}"

