from __future__ import absolute_import, unicode_literals
from decimal import Decimal
from journeys.models import Journey
from stations.models import Station
import csv
from datetime import datetime
from celery import shared_task
from celery_progress.backend import ProgressRecorder
import warnings
from time import sleep

# For ignoring timezone sensitive objects
warnings.filterwarnings("ignore", category=RuntimeWarning, module='django.db.models.fields')

@shared_task(bind=True)
def go_to_sleep(self, duration):
    """ Just a test, testing the progress bar pip-package """

    progress_recorder = ProgressRecorder(self)
    for i in range(5):
        sleep(duration)
        progress_recorder.set_progress(i + 1, 5, f'On iteration {i}')
    return 'Done'

@shared_task(bind=True)
def upload_csv(self, file_path, csv_data_type, upload_type):
    """ An async Celery task for reading uploaded CSV files.

    Takes in:
    file_path : Path to the uploaded file
    csv_data_type : Whether the csv file is uploading journey or station data
    upload_type : the type of object creation. safe_create creates all objects after reading the whole file,
    bulk_create creates the objects in chunks of 100 after adding them to a temporary list first 
    
    Returns a message from the celery task object telling whether the upload succeeded or failed """

    progress_recorder = ProgressRecorder(self)
    csv_data = []   # Temporary list for storing the CSV-rows

    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)

        if csv_data_type == 'journey':
            # Fields in the csv: [0]Departure,[1]Return,[2]Departure station id,[3]Departure station name,[4]Return station id,[5]Return station name,[6]Covered distance (m),[7]Duration (sec.)
            reader.fieldnames = ['Departure','Return','Departure station id','Departure station name','Return station id','Return station name','Covered distance (m)','Duration (sec.)']
        
        elif csv_data_type == 'station':
            # Fields in the csv: [0]FID,[1]ID,[2]Nimi,[3]Namn,[4]Name,[5]Osoite,[6]Address,[7]Kaupunki,[8]Stad,[9]Operaattor,[10]Kapasiteet,[11]x,[12]y
            reader.fieldnames = ['FID','ID','Nimi','Namn','Name','Osoite','Adress','Kaupunki','Stad','Operaattor','Kapasiteet','x','y']
        
        print("Reading the csv")
        for row in reader:
            csv_data.append(row)
        file.seek(0)
        
    rowcount = len(csv_data)    # Row count
    print(f"CSV read complete with {rowcount} rows. Creating objects...")

    try:
        object_list = []    # Temporary list for the objects about to be created in bulk

        if csv_data_type == 'journey':

            print("Uploading a Journey")
            for i, row in enumerate(csv_data):
                # Nullchecks every row
                if any(value for value in row.values()):

                        """
                        - Don't import journeys that lasted for less than ten seconds
                        - Don't import journeys that covered distances shorter than 10 meters
                        """
                        if (int(row['Duration (sec.)']) >= 10) if row['Duration (sec.)'].isdigit() else False & \
                        (float(row['Covered distance (m)']) > 10.0 if row['Covered distance (m)'].isdigit() else False):
                            
                            try:                                
                                csv_data = Journey(
                                    departure_time=datetime.strptime(
                                        (row['Departure']), '%Y-%m-%dT%H:%M:%S'),
                                    return_time=datetime.strptime(
                                        row['Return'], '%Y-%m-%dT%H:%M:%S'),
                                    departure_station=Station.objects.get(
                                        station_id=int(row['Departure station id'])),
                                    departure_station_name=row['Departure station name'],
                                    return_station=Station.objects.get(
                                        station_id=int(row['Return station id'])),
                                    return_station_name=row['Return station name'],
                                    covered_distance=Decimal(row['Covered distance (m)']),
                                    duration=int(row['Duration (sec.)'])
                                )

                                # Checks whether the journey already exists
                                if Journey.objects.filter(id=csv_data.id).exists():
                                    print("Journey already exists")
                                    continue

                                # Add the object to the temporary list of objects
                                object_list.append(csv_data)
                                
                                """ If the upload_type is chunk_create, check if the list contains 100 objects.
                                    If so, add them to the database and clear the temporary list """
                                if upload_type == 'chunk_create':
                                    if len(object_list) >= 100:
                                        Journey.objects.bulk_create(object_list)
                                        # Clear the list
                                        object_list = []

                                print(f"Row {i+1} : Journey {row['Departure station id']}.{row['Departure station name']} - {row['Return station id']}.{row['Return station name']} created!")

                            except Station.DoesNotExist:
                                print(f"Row {i+1} : Station id included in the data does not exist, journey will not be created!")
                                continue

                            except ValueError as e:
                                print(f"Row {i+1} : Value error! ", e)
                                continue

                            except Exception as e:
                                print(f"Row {i+1} : Exception: {e}")
                                continue

                        else:  
                            # If duration or distance traveled is less than 10...
                            print(f"Row {i+1} : The duration of the journey {row['Departure station name']} to {row['Return station name']} \
                                is less than 10s, the distance is less than 10m or the value is faulty. Journey will not be added!")
                else:
                    # If the row from the csv contains no data
                    print(f"Row {i+1} : Field empty")

                # Updates the progress after every iteration and passes the current state (in percentages) to the front end
                progress_recorder.set_progress(i + 1, rowcount, f'{round(((i+1) / rowcount) * 100),2}%')

            # Before task completion, checks if there are objects left in the object list, add them to the db and return a success message 
            if object_list:
                Journey.objects.bulk_create(object_list)
                return f"{len(Journey.objects.all())} journeys uploaded successfully"


        elif csv_data_type == 'station':

            print("Uploading a Station")
            for i, row in enumerate(csv_data):

                # Check empty rows
                if any(value for value in row.values()):
                        try:
                            csv_data = Station(
                                station_id=row['ID'],
                                fid=row['FID'],
                                name_fin=row['Nimi'],
                                name_swe=row['Namn'],
                                name_eng=row['Name'],
                                address_fin=row['Osoite'],
                                address_swe=row['Adress'],
                                city_fin=row['Kaupunki'],
                                city_swe=row['Stad'],
                                operator=row['Operaattor'],
                                capacity=int(row['Kapasiteet']),
                                geo_pos_x=Decimal(row['x']),
                                geo_pos_y=Decimal(row['y'])
                            )

                            # If station is found in the db, skip to the next iteration
                            if Station.objects.filter(station_id=csv_data.station_id).exists():
                                print("Station already exists")
                                continue

                            # Add the object to the list
                            object_list.append(csv_data)

                            # Chunk create checks if there are 100 Journey-objects, if so, creates them and clears the temporary list
                            if upload_type == 'chunk_create':
                                if len(object_list) >= 100:
                                    Station.objects.bulk_create(object_list)
                                    # Clear the list
                                    object_list = []

                            print(f"Row {i+1} : Station {row['ID']}.{row['Nimi']} created!")
                        
                        except ValueError as e:
                            print(f"Row {i+1} : Value error in row {i+1}! ", e)

                        except Exception as e:
                            print(f"Row {i+1} : Exception: {e}")
                            continue
                else:
                    # In case a csv-row is empty
                    print(f"Row {i+1} : Field empty")

            # If there are leftover objects in the list after bulk_create or safe_create has finished creating all objects, add them to the db.
            if object_list:
                Station.objects.bulk_create(object_list)
                return f"{len(Station.objects.all())} stations uploaded successfully"

        # Just in case neither Journey or Station upload_type is chosen
        else:
            print("Select a CSV containing proper values of either Stations or Journeys")

        # Completion message
        return "CSV upload completed"

    except Exception as e:
        print(f"Exception, something went wrong: {e}")
        return "Something went wrong"
        
