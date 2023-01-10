# HelsinkiCityBikeApp
Helsinki city bike app (Dev Academy pre-assignment)

Usually runs in: http://127.0.0.1:8000/
Requires login with admin- or other high-privilege accounts

## Apps (With 'http://127.0.0.1:8000/' URL-prefix):
 - Core ('')
    - Contains the index page, core files like 'base.html', shared images, styling, scripts and other files
 - CSVImport ('csv_import/')
    - Contains the import features for importing CSVfiles and managing uploads 
 - Journeys ('journeys/')
    - Contains a map of journeys between stations
 - Stations ('stations/')
    - Contains a map of stations and information about stations

Futhermore, the 'Admin panel' option is added to the base.html partial. 
You can manage (Browse, Add, Modify, Delete...) the model objects.

## CSVImport:
Contains a form for uploading CSV data.
The app utilizes Celery to read the CSV data as a background task and Redis as its message broker (Default URL: 127.0.0.1:6379). 
You have to specify whether you are uploading CSV-data containing Journey- or Station objects. 

"Safe create" will wait for the whole file to be read before adding any data to the database. Using Django's bulk_create(), it once finished, it will add the data to the database with only one query. This is especially good if you have large files you want
to read faster but it will not add anything while the operation is going.