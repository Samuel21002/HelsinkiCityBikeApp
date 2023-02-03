# HelsinkiCityBikeApp
  - Samuel L-Kovanko

![Helsinki city bikes](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Helsinki_city_bikes_station_2016_kauppatori.jpg/640px-Helsinki_city_bikes_station_2016_kauppatori.jpg)

*"Helsinki city bikes station 2016 kauppatori" by Olimar is licensed under CC BY-SA 4.0.*

Helsinki City Bike App is a pre-assignment for Solita's Dev Academy. 
The project utilizes Pythons Django -framework in the back-end along with Celery and Redis for handling background tasks. The frontend utilises Bulma and Tachyons CSS-libraries and JavaScript.

Helsinki City Bike App is a web app where you can upload CSV-data along with searching, adding, displaying and modifying citybike journeys and stations.

### Apps
The primary features consists of a CSV-upload page, Stations view page, Journeys page and the Admin panel. 

The project is divided into "apps" and they run on the localhost (with an *'http://127.0.0.1:8000/'* URL-prefix):

1. Core ('')
    - Contains the index page, core template files, shared images, styling, main scripts among other files
2. CSVImport ('csv_import/')
    - Contains the import features for importing CSVfiles and managing uploads 
3. Journeys ('journeys/')
    - Contains a map of journeys between stations
4. Stations ('stations/')
    - Contains a map of stations and information about stations
5. Admin panel ('admin/')
    - The endpoint for handling users, CRUD-operations and monitoring Celery tasks. 

So in other words: eg. *'http://127.0.0.1:8000/stations'* would run the features / page belonging to the projects Station -app from its corresponding folder within the project.

### CSVImport:
Contains a form for uploading CSV data.

The app utilizes Celery to read the CSV data as a background task and Redis as its message broker (Default URL: 127.0.0.1:6379). 
You have to specify whether you are uploading CSV-data containing Journey- or Station objects. 

"Safe create" will wait for the whole file to be read before adding any data to the database. It uses Django's bulk_create() method. Once an upload finishes, it will add the data to the database with only one query. This is especially good if you have large files you want to go through faster but it will not add anything to the database while the upload is ongoing.

Upon submitting a file, celery will take care of the uploading and validating the CSV data and fields. The status of the upload can be displayed by clicking on the green button down on the right of the page. You can also cancel your upload at any time you'd like.

### Journeys:
Contains the search functionality for searching journeys. The departure and return station names, a journeys timeframe, duration and distance can be specified for a more extensive search. The search matches will be displayed, are sortable and upon clicking on a journey, it will be displayed on the map above. Journey information includes:

 - Departure- and Return station
 - Departure and return time
 - Covered distance
 - Duration

### Stations:
Contains a map of all the stations in the database.

You can narrow down the results by typing in the input box. Clicking on the stations on the list or the markers on the map, displays more information about the station, including:

 - Location on the map
 - Station name
 - Station address
 - Total number of journeys starting from the station
 - Total number of journeys ending at the station
 - The average distance of a journey starting from the station
 - The average distance of a journey ending at the station
 - Top 5 most popular return stations for journeys starting from the station
 - Top 5 most popular departure stations for journeys ending at the station
 - Filtering the calculations by month

### Admin panel

The *'Admin panel'* is added to the navigation bar in order to manage the database more proficiently.
You can conviniently manage (Browse, Add, Modify, Delete...) the created database objects, add new users or user groups, scroll for the background task results etc.

___

## Setup (Run locally):

**For the sake of convinience, it is recommended that you make all of these steps in the same directory the file *manage.py* is in to ensure everything goes right!**

Installation and management of the project happens via the Command Line / Terminal. The Django server and Celery should be run simultaneously in two separate Command Line / Terminal windows.

### Python:
Install Python 3 *'https://www.python.org/downloads/'*(https://www.python.org/downloads/) and pip *'https://pip.pypa.io/en/stable/installation/'*(https://pip.pypa.io/en/stable/installation/).

### Redis:
Install Redis on your local computer *'https://redis.io/download/'*(https://redis.io/download/). By default it should run in *http://127.0.0.1:6379/*. If you want to select another port number, you need to change the  *CELERY_BROKER_URL* in the settings.py file! You can test the functionality of Redis by running the *ping* -command in the Redis CLI. In order to run Celery tasks, Redis must be running in *http://127.0.0.1:6379/*, although you can use a different address as long as you change the corresponding settings in the projects *'settings.py'* -file.  

### Venv:
The project lists the dependencies in the file *requirements.txt*.

In the root folder (where manage.py is located), create a new virtual environment by typing 'python3 -m venv <your virtual env name>'. 
From the same folder (where you created your venv-folder), you can activate it with the command *'source <your venv name>/bin/activate'*. To install the dependencies for the project, type: *'pip install -r requirements.txt'*.

**Remember to keep the virtual environment running while you are doing the steps below!**

### Celery:
Celery is used as the background task handler and it uses Redis as its message broker. When uploading a form, the task gets sent to Celery and you can continue scroll the application right away. 

When in the virtual environment, activate Celery with the command 'celery -A helsinkiCityBikeApp worker -l info'.
However, make sure Redis is running first!
The status of an upload can be seen on the page but for more thorough details of what goes on in Celery, you can follow the console output. 

### Database:
The project uses PostgreSQL as the default database and you can get it from *'https://www.postgresql.org/download/'*(https://www.postgresql.org/download/).

It is recommended to use Linux as it has Postgres integrated on most distributions. Due to Postgres's user permissions related bug, Mac OS X and Windows users might encounter an installation error where the database clusters are not created properly.

These threads might prove helpful:
(Windows):
*https://stackoverflow.com/questions/30689251/failed-to-load-sql-modules-into-the-database-cluster-during-postgresql-installat*(https://stackoverflow.com/questions/30689251/failed-to-load-sql-modules-into-the-database-cluster-during-postgresql-installat)

(Mac OS X):
*https://stackoverflow.com/questions/59189729/postgressql-installation-fails-database-cluster-initialisation-failed-mac-os*(https://stackoverflow.com/questions/59189729/postgressql-installation-fails-database-cluster-initialisation-failed-mac-os)

After installing the required dependencies in pip virtual environment, the Postgres database adapter for Python (*'psycopg2'*) should be included.

You can check the *'settings.py'* file for the connection settings. The development database server is set up as such:

        `
        'NAME': 'db_hcbapp',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432'
        `

Make sure you have installed PostgreSQL on your computer and have a user called *'postgres'* with a password *'postgres'*. 

Create a database associated with the user *'postgres'* called *'db_hcbapp'*. In the database client, use *CREATE DATABASE db_hcbapp;*

If you want to use your own setup, you need to change the settings in the *settings.py* -file!

To migrate the database you need to enter the command *'python3 manage.py makemigrations'* from the root folder destination, which will check for unmigrated model changes. If everything is up to date, enter *'python3 manage.py migrate'* to create or update the database tables. 

The Postgres database should now have all the necessary tables ready to be populated.

### Admin account / superuser:

Helsinki Citybike App uses authentication in order for an extended user interface to be later.

In order to scroll the app, you need to create a superuser. This can easily be done by running *'python3 manage.py createsuperuser'*. The prompt will ask for a username, email and a strong password. You will be able to log in to the site with these so don't forget the username and password! :)

___

## Running the project

1. Before you run the project, make sure Redis, Celery and the virtual environment are running. Also make sure the database has been migrated! Like mentioned about, viewing the pages require logging in with admin- or other high-privilege accounts.

2. After that, you can run the local server by typing in *'python3 manage.py runserver'*. By default, the development version of the project runs in *'http://127.0.0.1:8000/'*(http://127.0.0.1:8000/) if nothing else has been set up in *settings.py*.

In case there is an issue with the SECRET_KEY not being found, you can generate one here *'https://djecrety.ir/*(https://djecrety.ir/). Add the generated key to the *settings.py* -file by replacing the old SECRET_KEY variable as such:

eg. `SECRET_KEY = '<Your generated key here>'`

## Testing 

You can run all project tests at once by typing 'python3 manage.py test' from the same folder manage.py is located in.
To run specific tests for an app, type 'python3 manage.py test (*appname*).tests.(*TestClass*).(*methodname*)' eg. *'python3 manage.py csvimport.tests.CSVImportTests.test_csvimport_load_page'*. Alternatively you can leave out the method name to run all tests within a test class.
The tests are meant to test the basic functionalities, like authentication, Django views (backend), Celery, returning JSON endpoint data, plus page interaction using Selenium.

Selenium uses '*chromedriver*' as its engine so you need Chrome installed on your local computer. Also make sure you are running tests in the Virtual Environment with Redis running. Furthermore, in *'settings.py'*, make sure Debug is set to *'True'* as it temporarily disables the CSRF middleware for testing purposes.

*Note! Although it should work, if you run all tests in one run, you might encounter some errors. This might be due to the database not being reset properly thus not returning the desired output on a template*

Tests use CSV data found in the *'csvimport/CSVFiles'* folder.

# Final thoughts

As the first beta-version of helsinkiCityBikeApp, this works pretty well, although more thorough testing will definitely be necessary! Also, page performance seems to be an issue with large amounts of data, especially when deployed to Azure. Part of it is due to lack of some database optimization. 
However i am very pleased with the overall results, hope you are too!

### *BON APETIT!*