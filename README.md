# HelsinkiCityBikeApp
  - Samuel L-Kovanko

![Helsinki city bikes](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Helsinki_city_bikes_station_2016_kauppatori.jpg/640px-Helsinki_city_bikes_station_2016_kauppatori.jpg)

*"Helsinki city bikes station 2016 kauppatori" by Olimar is licensed under CC BY-SA 4.0.*

Helsinki City Bike App is a web app where you can upload CSV-data along with searching, adding, displaying and modifying citybike journeys and stations.
This project is a pre-assignment for Solita's Dev Academy. 

The project utilizes Pythons Django -framework in the back-end along with Celery and Redis for handling background tasks. The frontend utilises Bulma and Tachyons CSS-libraries and JavaScript. I choose Django because of its ability to scale for larger projects, pleasant workflow and easy maintainability.

___
###Deployed app on Azure:
[https://helsinkicitybikeapp.azurewebsites.net/](https://helsinkicitybikeapp.azurewebsites.net/)

Log In With:
Username: citybikeuser
Password: citybik3sar3aw3som3

You are able to visit the admin page to perform CRUD operations but do not obviously have superuser privileges. 

*NOTE! CSV Uploading will not work in this deployed version as i did not get the Redis / Celery to work yet.* 
___


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

![CSVUpload Form View](https://i.postimg.cc/MZgST1YX/HCBAPP-CSVUPLOAD.png)
Contains a form for uploading CSV data.

The app utilizes Celery to read the CSV data as a background task and Redis as its message broker (Default URL: 127.0.0.1:6379). 
You have to specify whether you are uploading CSV-data containing Journey- or Station objects. 

"Safe create" will wait for the whole file to be read before adding any data to the database. It uses Django's bulk_create() method. Once an upload finishes, it will add the data to the database with only one query. This is especially good if you have large files you want to go through faster but it will not add anything to the database while the upload is ongoing.

Upon submitting a file, celery will take care of the uploading and validating the CSV data and fields. The status of the upload can be displayed by clicking on the green button down on the right of the page. You can also cancel your upload at any time you'd like.

![CSVUpload Process](https://i.postimg.cc/x13DthVb/HCBAPP-CSVUPLOAD-2.png)

### Journeys:
Contains the search functionality for searching journeys. The departure and return station names, a journeys timeframe, duration and distance can be specified for a more extensive search. The search matches will be displayed in the div, are sortable and upon clicking on a journey, it will be displayed on the map above. An arrow will indicate the gap between stations. 

Single journey information includes:

 - Departure- and Return station
 - Departure and return time
 - Covered distance
 - Duration

![Journeys View](https://i.postimg.cc/pdVN7CPc/HCBAPP-JOURNEYS.png)

### Stations:
Contains a map of all the stations in the database plus a search functionality for all stations.

You can narrow down the results by typing in the input box. Clicking on the stations on the list or the markers on the map, displays more information about a single station, including:

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

![Stations / Single station view](https://i.postimg.cc/Bn0f5sk0/HCBAPP-STATIONS.png)

### Admin panel

The *'Admin panel'* is added to the navigation bar in order to manage the database more proficiently.
You can conviniently manage (Browse, Add, Modify, Delete...) the created database objects, add new users or user groups, scroll for the background task results etc.

![Admin View](https://i.postimg.cc/nVXxp3B6/HCBAPP-ADMIN-small.png)

___

## Setup (Run locally):

**For the sake of convinience, it is recommended that you make all of these steps in the same directory the file *manage.py* is in to ensure everything goes right! Also i would recommend using Linux as this proejct is easiest and fastest to set up on Ubuntu. I've tried to list the most essential installing steps as well as i could but there might always be some unexpected circumstances. I hope this will be a relatively painless process :) **

Installation and management of the project happens via the Command Line / Terminal. The Django server and Celery should be run simultaneously in two separate Command Line / Terminal windows.

### Python:
Install Python 3 *'[https://www.python.org/downloads/](https://www.python.org/downloads/)'* and pip *'[https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/)'*. In Linux you can install pip with 'sudo apt install python3-pip'. Python3 should automatically exist on newer Linux distributions but that might not always be the case.

### Redis:
Redis is the message broker for Celery background tasks.
You can find .tar installers for Redis on *'[https://redis.io/download/](https://redis.io/download/)'*. 
Unfortunately there is no direct support for *Windows* so in order to run it, you still need to have WSL (Windows Subsystem for Linux). 

Using 'sudo apt install redis' installs Redis on Linux. After the installation, typing 'sudo systemctl start redis' should start the server (if it is not already running) and typing 'sudo redis-cli' should open the server command line.

On a Mac, you can use Homebrew to install a cask-package of Redis, which is a standalone application. After installation just open the program and the server should start as a background task.
For more info, visit *'[https://redis.io/docs/getting-started/](https://redis.io/docs/getting-started/)'*.

By default, Redis should run in *http://127.0.0.1:6379/*. If you want to select another port number, you need to change the  *CELERY_BROKER_URL* in the projects *'settings.py'* file! You can test the functionality of Redis by running the *ping* -command in the Redis CLI. In order to run Celery tasks, Redis must be running in *http://127.0.0.1:6379/*, although you can use a different address as long as you change the corresponding settings in the projects *'settings.py'* -file.  

### Venv:
Venv is the virtual environment for Python. On Linux you can install venv by running 'sudo install python3-venv' or using pip you can run 'pip install virtualenv'. 

The project lists the dependencies in the file *requirements.txt*.
In the root folder (where manage.py is located), create a new virtual environment by typing 'python3 -m venv <your virtual env name>'. 
From the same folder (where you created your venv-folder), you can activate it with the command *'source <your venv name>/bin/activate'* (Mac / Linux) or '<your venv name>/scripts/activate' on Windows. To install the dependencies for the project, type: *'pip install -r requirements.txt'*.

In case the installer cannot install psycopg2, you can try installing the binary version by typing *'pip install psycopg2-binary' if it doesnt exist in your environment.
  
In case there are errors in installing the requirements succesfully, try installing the requirements one by one from the requirements.txt file by typing in *'pip3 install <appname>'*.
The most essential ones are: *django, celery, celery-progress, django-celery-results, django-querystring-tag, geojson, postgres, psycopg2 (or psycopg2-binary), redis, selenium, splinter and whitenoise*. The other dependencies usually come with the ones i just listed.
  
**Remember to keep the virtual environment running while you are doing the steps below!**

### Database:
The project uses PostgreSQL as the default database and you can get the standalone apps along with the associated tools from *'[https://www.postgresql.org/download/](https://www.postgresql.org/download/)'*.

Due to Postgres's user permissions related bug, Mac OS X and Windows users might encounter an installation error where the database clusters are not created properly.

These threads might prove helpful:
(Windows):
*'[https://stackoverflow.com/questions/30689251/failed-to-load-sql-modules-into-the-database-cluster-during-postgresql-installat](https://stackoverflow.com/questions/30689251/failed-to-load-sql-modules-into-the-database-cluster-during-postgresql-installat)'*

(Mac OS X):
*'[https://stackoverflow.com/questions/59189729/postgressql-installation-fails-database-cluster-initialisation-failed-mac-os](https://stackoverflow.com/questions/59189729/postgressql-installation-fails-database-cluster-initialisation-failed-mac-os)'*
  
On Linux, you can just copy the script from the PostgreSQLs homepage instructions here: *'[https://www.postgresql.org/download/linux/ubuntu/](https://www.postgresql.org/download/linux/ubuntu/)'*. 

After installing the required dependencies in pip virtual environment (from requirements.txt earlier), the Postgres database adapter for Python (*'psycopg2'*) should be included.

You can check the *'settings.py'* file for the connection settings. The development database server is set up as such:

        `
        'NAME': 'db_hcbapp',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432'
        `
Make sure you have installed PostgreSQL on your computer and have a user called *'postgres'* with a password *'postgres'*. 

Create a database on the local host associated with the user *'postgres'* called *'db_hcbapp'*. Either using the Postgres standalone application 'pgAdmin' or via the console (database client). Using Linux / Mac this can be done by using 'sudo su postgres' and then typing 'psql' to enter the CLI. Here you should simple be able to use *CREATE DATABASE db_hcbapp;* to create an empy database. In case you did not remember to set the password you can always come back to your db by typing *'sudo -u postgres psql db_hcbapp'*. Then you can type *'ALTER USER postgres WITH PASSWORD 'postgres'.
  
For Windows you can also use the standalone application 'pgAdmin' or via the CLI. These instructions might be helpful:
*'[https://www.microfocus.com/documentation/idol/IDOL_12_0/MediaServer/Guides/html/English/Content/Getting_Started/Configure/_TRN_Set_up_PostgreSQL.htm](https://www.microfocus.com/documentation/idol/IDOL_12_0/MediaServer/Guides/html/English/Content/Getting_Started/Configure/_TRN_Set_up_PostgreSQL.htm)'*

If you want to use your own database setup, you need to change the corresponding database settings in the *settings.py* -file!

To migrate the database you need to enter the command *'python3 manage.py makemigrations'* from the root folder destination, which will check for unmigrated model changes. If everything is up to date, enter *'python3 manage.py migrate'* to create or update the database tables. 

The Postgres database should now have all the necessary tables ready to be populated.

### Celery:
Celery is used as the background task handler and it uses Redis as its message broker. When uploading a form, the task gets sent to Celery and you can continue scroll the application right away. 

When in the virtual environment, activate Celery with the command 'celery -A helsinkiCityBikeApp worker -l info'. However, make sure Redis is running first! The status of an upload can be seen on the page but for more thorough details of what goes on in Celery, you can follow the console output or visit the admin page.
  
### Admin account / superuser:

Helsinki Citybike App uses authentication in order for an extended user interface to be later.

In order to scroll the app, you need to create a superuser. This can easily be done by running *'python3 manage.py createsuperuser'*. The prompt will ask for a username, email and a strong password. You will be able to log in to the site with these so don't forget the username and password! :)

___

## Running the project

1. Before you run the project, make sure Redis, Celery and the virtual environment are running. Also make sure the database has been migrated! Like it is mentioned above, viewing the pages require logging in with admin- or other registered user accounts.
  
2. You need to generate a SECRET_KEY as it is needed to run the project. You can generate one here *'[https://djecrety.ir/](https://djecrety.ir/)'*. Add the generated key to the *settings.py* -file by replacing the old SECRET_KEY variable as such:

eg. SECRET_KEY = 'Your Key Here'

3. Finally, you can run the local server by typing in *'python3 manage.py runserver'*. By default, the development version of the project runs in *'http://127.0.0.1:8000/'*(http://127.0.0.1:8000/) if nothing else has been set up in *settings.py*.

## Testing 

**Selenium uses '*chromedriver*' as its engine so you need Chrome installed on your local computer.** 
  
You can run all project tests at once by typing 'python3 manage.py test' from the same folder manage.py is located in.
To run specific tests for an app, type 'python3 manage.py test (*appname*).tests.(*TestClass*).(*methodname*)' eg. *'python3 manage.py csvimport.tests.CSVImportTests.test_csvimport_load_page'*. Alternatively you can leave out the method name to run all tests within a test class.
The tests are meant to test the basic functionalities, like authentication, Django views (backend), Celery, returning JSON endpoint data, plus page interaction using Selenium.

Also make sure you are running tests in the Virtual Environment with Redis running! Furthermore, check in *'settings.py'* and make sure Debug is set to *'True'* as it temporarily disables the CSRF middleware for testing purposes.

*Note! Although it should work, if you run all tests in one run, you might encounter some errors. This might be due to the database not being reset properly thus not returning the desired output on a template*.

Tests use CSV files found in the *'csvimport/CSVFiles'* folder.

# Final thoughts

As the first beta-version of helsinkiCityBikeApp, this works pretty well, although more thorough testing will definitely be necessary.
I'm aware setting up the project on a new computer would be much easier with a Docker container!
  
Also, page performance seems to be an issue with large amounts of data, especially when deployed to Azure. Part of it is due to lack of some database optimization. 
However i am very pleased with the overall results, hope you are too!

### *BON APETIT!*
