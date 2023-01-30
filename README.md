# HelsinkiCityBikeApp

![Helsinki city bikes](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Helsinki_city_bikes_station_2016_kauppatori.jpg/640px-Helsinki_city_bikes_station_2016_kauppatori.jpg)
*"Helsinki city bikes station 2016 kauppatori" by Olimar is licensed under CC BY-SA 4.0.*

Helsinki City Bike App is a pre-assignment for Solita's Dev Academy. 
The project utilizes Django / Python in the backend along with Celery and Redis for handling background tasks. The frontend utilises Bulma and Tachyons CSS-libraries and JavaScript.

Helsinki City Bike App is a web app where you can upload, search, display and modify journeys and station data. 

### Apps
The primary features consists of a CSV-upload page, Stations view page, Journeys page and the Admin panel. 

The project is divided into 'apps' and they run on the localhost (with 'http://127.0.0.1:8000/' URL-prefix):

1. Core ('')
    - Contains the index page, core files like 'base.html', shared images, styling, scripts and other files
2. CSVImport ('csv_import/')
    - Contains the import features for importing CSVfiles and managing uploads 
3. Journeys ('journeys/')
    - Contains a map of journeys between stations
4. Stations ('stations/')
    - Contains a map of stations and information about stations
5. Admin panel ('admin/')

So in this case eg. *'http://127.0.0.1:8000/stations'* would run the features / pages of the projects Station -app.

### CSVImport:
Contains a form for uploading CSV data.

The app utilizes Celery to read the CSV data as a background task and Redis as its message broker (Default URL: 127.0.0.1:6379). 
You have to specify whether you are uploading CSV-data containing Journey- or Station objects. 

"Safe create" will wait for the whole file to be read before adding any data to the database. Using Django's bulk_create(), it once finished, it will add the data to the database with only one query. This is especially good if you have large files you want to go through faster but it will not add anything to the database while the upload is ongoing.

### Journeys:
Contains the search functionality for searching journeys. The station names, timeframe, duration and distance can be specified in order to specify a search. The search matches will be displayed, are sortable and upon clicking on a journey, it will be displayed on the map above. Journey information includes:

 - Departure- and Return station
 - Departure and return time
 - Covered distance
 - Duration

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

### Admin panel

The *'Admin panel'* is added to the navigation bar in order to manage the database more proficiently.
You can conviniently manage (Browse, Add, Modify, Delete...) the created database objects, add new users or user groups, scroll for the background task results etc.


## Setup (Run locally):

___

**For the sake of convinience, it is recommended that you make all of these steps in the same directory the file *manage.py* is in to ensure everything goes right!**

Installation and management of the project happens via the Command Line / Terminal. The Django server and Celery should be run simultaneously in two separate Command Line / Terminal windows.

### Python:
Install Python 3 *'https://www.python.org/downloads/'*(https://www.python.org/downloads/) and pip *'https://pip.pypa.io/en/stable/installation/'*(https://pip.pypa.io/en/stable/installation/).

### Redis:
Install Redis on your local computer *'https://redis.io/download/'*(https://redis.io/download/). By default it should run in *http://127.0.0.1:6379/*. If you want to select another port number, you need to change the  *CELERY_BROKER_URL* in the settings.py file! You can check the functionality of Redis by running the *ping* -command in the Redis CLI. In order to run Celery tasks, Redis must be running.

### Venv:
The project lists the dependencies in the file *requirements.txt*.

In the root folder (where manage.py is located), create a new virtual environment by typing 'python3 -m venv <your virtual env name>'. 
From the same folder (where you created your venv-folder), you can activate it with the command *'source venv/bin/activate'*. To install the dependencies for the project, type: *'pip install -r requirements.txt'*.

**Remember to keep the virtual environment running while you are doing the steps below!**

### Celery:
Celery is used as the background task handler and it uses Redis as its message broker. When uploading a form, the task gets sent to Celery and you can continue scroll the application right away.

When in the virtual environment, activate Celery with the command 'celery -A helsinkiCityBikeApp worker -l info'.
However, make sure Redis is running first!

### Database:
The project uses PostgreSQL as the default database and you can get it from *'https://www.postgresql.org/download/'*(https://www.postgresql.org/download/).

It is recommended to use a Linux distribution. Due to a user permissions related bug, Mac OS X and Windows users might encounter an installation error where the database clusters are not created properly.

These threads might prove helpful:
(Windows):
*https://stackoverflow.com/questions/30689251/failed-to-load-sql-modules-into-the-database-cluster-during-postgresql-installat*(https://stackoverflow.com/questions/30689251/failed-to-load-sql-modules-into-the-database-cluster-during-postgresql-installat)

(Mac OS X):
*https://stackoverflow.com/questions/59189729/postgressql-installation-fails-database-cluster-initialisation-failed-mac-os*(https://stackoverflow.com/questions/59189729/postgressql-installation-fails-database-cluster-initialisation-failed-mac-os)

After creating the pip virtual environment, the Postgres database adapter for Python should be installed.

You can check the settings.py file for the connection settings. The development database server is set up as such:

        `
        'NAME': 'db_hcbapp',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432'
        `

Make sure you have installed PostgreSQL on your computer and have a user called *'postgres'* with the password *'postgres'*. 

Create a database associated with the user *'postgres'* called *'db_hcbapp'* by first running: *'psql -U postgres -W'*. In the database use *CREATE DATABASE db_hcbapp;*

If you want to use your own setup, you need to change the settings in the *settings.py* -file

To migrate and create a database you need to enter *'python3 manage.py makemigrations'* from the root folder, which will check for unmigrated model changes. If everything is up to date, enter *'python3 manage.py migrate'* to create or update the database tables. 
Journey search queries are stored in a temporary database cache. In order to use a database cache, you also need to run *'python3 manage.py createcachetable'*.

The Postgres database should now have all the necessary tables ready to be populated.

### Admin account / superuser:
The app uses authentication. An extended user interface will be later!

In order to scroll the app, you need to create a superuser. This can be done by running *'python3 manage.py createsuperuser'*. The prompt will ask for a username, email and a strong password. You will be able to log in to the site with these so don't forget the username and password! :)

___

## Running the project

1. Like mentioned about, running the project requires logging in with admin- or other high-privilege accounts.
Before you run the project, make sure Redis, Celery and the virtual environment are running. Also make sure the database has been migrated!

2. After that, you can run the local server by typing in *'python3 manage.py runserver'*. By default, the development version of the project runs in *'http://127.0.0.1:8000/'*(http://127.0.0.1:8000/) if nothing else has been set up in *settings.py*.

In case there is an issue with the SECRET_KEY not being found, you can generate one here *'https://djecrety.ir/*(https://djecrety.ir/). Add the generated key to the *settings.py* -file by replacing the old SECRET_KEY variable as such:

eg. `SECRET_KEY = '<Your generated key here>'`

ENJOY!
