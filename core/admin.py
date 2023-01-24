from django.contrib import admin
from csvimport.models import Csv
from journeys.models import Journey
from stations.models import Station

# Departure,Return,Departure station id,Departure station name,Return station id,Return station name,Covered distance (m),Duration (sec.)
class JourneyAdmin(admin.ModelAdmin):

    list_display = (
        'departure_time',
        'return_time',
        'departure_station',
        'departure_station_name',
        'return_station',
        'return_station_name',
        'covered_distance',
        'duration'
        )
    search_fields = ['departure_station_name', 'return_station_name', 'duration', 'covered_distance']
    fieldsets = [

    ('Departure Time',      {'fields': ['departure_time']}),
    ('Return Time',         {'fields': ['return_time']}),
    ('Departure Station',   {'fields': ['departure_station']}),
    ('Return Station',      {'fields': ['return_station']}),
    ('Covered Distance',    {'fields': ['covered_distance']}),
    ('Duration',            {'fields': ['duration']})
    ]

    list_filter = ['departure_time', 'return_time']

# FID,ID,Nimi,Namn,Name,Osoite,Adress,Kaupunki,Stad,Operaattor,Kapasiteet,x,y
class StationAdmin(admin.ModelAdmin):

    search_fields = ['name_fin', 'name_swe', 'address_fin', 'address_swe']

    list_display = (
        'station_id',
        'name_fin',
        'address_fin',
        'city_fin',
        'operator',
        'capacity',
        )

class CsvAdmin(admin.ModelAdmin):
        list_display = (
        'upload_date',
        'task_id',
        'activated',
        )

admin.site.register(Journey, JourneyAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Csv, CsvAdmin)
