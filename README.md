# HelsinkiCityBikeApp

Helsinki city bike app (Dev Academy pre-assignment)

### Apps
The project is divided into 'apps' and they run on the localhost (With 'http://127.0.0.1:8000/' URL-prefix):

1. Core ('')
    - Contains the index page, core files like 'base.html', shared images, styling, scripts and other files
2. CSVImport ('csv_import/')
    - Contains the import features for importing CSVfiles and managing uploads 
3. Journeys ('journeys/')
    - Contains a map of journeys between stations
4. Stations ('stations/')
    - Contains a map of stations and information about stations

So in this case eg. *'http://127.0.0.1:8000/stations'* would run the features / pages of the projects Station -app.

Futhermore, the *'Admin panel'* option is added to the base.html partial. 
You can manage (Browse, Add, Modify, Delete...) the model objects.

### CSVImport:
Contains a form for uploading CSV data.
The app utilizes Celery to read the CSV data as a background task and Redis as its message broker (Default URL: 127.0.0.1:6379). 
You have to specify whether you are uploading CSV-data containing Journey- or Station objects. 

"Safe create" will wait for the whole file to be read before adding any data to the database. Using Django's bulk_create(), it once finished, it will add the data to the database with only one query. This is especially good if you have large files you want
to read faster but it will not add anything while the operation is going.

### Stations:
Contains a map of all the stations in the database.
You can narrow down the results by typing in the input box. Clicking on the results or the markers on the map, displays more information about the station, including:

 - Station name
 - Station address
 - Total number of journeys starting from the station
 - Total number of journeys ending at the station
 - The average distance of a journey starting from the station
 - The average distance of a journey ending at the station

 - Top 5 most popular return stations for journeys starting from the station
 - Top 5 most popular departure stations for journeys ending at the station


## Setup:

### Python:
Install Python 3 'https://www.python.org/downloads/' and pip 'https://pip.pypa.io/en/stable/installation/'

### Redis:
Install Redis on your local computer. By default it should run in http://127.0.0.1:6379/. If you want to select another port number, you need to change this in the settings.py file!

### Celery:
When in the virtual environment, activate Celery with the command 'celery -A helsinkiCityBikeApp worker -l info'.

### Venv:
In the root folder (where manage.py is located), create a new virtual environment by typing 'python3 -m venv'. You may also add a custom path to the venv if you wish by adding it to the end of the command. 
You can activate it with the command 'source venv/bin/activate'. To install the dependencies for the project, type: 'pip install -r requirements.txt'.

### Database
To migrate and create a database you need to enter 'python3 manage.py makemigrations' from the root folder, which will create a migration.
If everything seems to be in order, enter 'python3 manage.py migrate' to create or update the database.

### Admin account
In order to scroll the app, manage or add users and have convinient access to the database via the admin panel, you need to create a superuser. This can be done from the project folder by running 'python3 manage.py createsuperuser'. The prompt will ask for a username, email and a strong password. 

___

## Running the project

1. Like mentioned about, running the project requires logging in with admin- or other high-privilege accounts.
Before you run the project, make sure Redis, Celery and the virtual environment are running. Also make sure the database has been migrated! From the project folder type 'source venv/bin/activate'. 

2. After that, you can run the local server by typing in 'python3 manage.py runserver'. By default, project runs in 'http://127.0.0.1:8000/' if nothing else has been set up in settings.py.

### Tests:
Running tests require step one to be initialized.
You can run all project tests at once by typing 'python3 manage.py test' in the same folder manage.py is located in. To run a specific test for an app or a specific function within a TestCase -call, type in 'python3 manage.py test #(appname)# #(test function)#' eg. 'python3 managy.py csvimport test_csvimport_load_page'

