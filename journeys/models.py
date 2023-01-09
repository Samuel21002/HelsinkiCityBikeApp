from django.db import models
from stations.models import Station
from django.db.models.indexes import Index
from django.utils import timezone
from django.core.validators import MinValueValidator

# Departure,Return,Departure station id,Departure station name,Return station id,Return station name,Covered distance (m),Duration (sec.)
class Journey (models.Model):

    id = models.BigAutoField(primary_key=True)
    departure_time = models.DateTimeField(auto_now = False, auto_now_add = False, default=timezone.now)
    return_time = models.DateTimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    departure_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='departure_station')
    departure_station_name = models.CharField(max_length=30, default="-")
    return_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='return_station')
    return_station_name = models.CharField(max_length=30, default="-")
    covered_distance = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(10, "Covered distance of the journey has to be bigger than 10.")])
    duration = models.PositiveIntegerField(validators=[MinValueValidator(10, "Duration of the journey has to be bigger than 10s.")])

    # Returns the duration in hour-minute-second -format to the template
    @property
    def duration_format(self):
        return timezone.timedelta(seconds=self.duration)

    # For database indexing
    class Meta:
        indexes = [
            Index(fields=['departure_station']),
            Index(fields=['return_station']),
        ]