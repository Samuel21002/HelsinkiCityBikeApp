from __future__ import absolute_import, unicode_literals
from decimal import Decimal
from django.test import override_settings
from journeys.models import Journey
from stations.models import Station
import csv
from datetime import datetime
from celery import shared_task
from django.db import transaction
import warnings

# For ignoring timezone sensitive objects
warnings.filterwarnings("ignore", category=RuntimeWarning, module='django.db.models.fields')

@transaction.atomic
def create_station_if_not_exists(station_id):
    """ For creating a station for a journeys if a station cannot be found by id
    Takes in a station id, assigns it to the object and provides a default value
    for the other attributes """
    station, created = Station.objects.get_or_create(
        station_id=station_id,
        defaults={
            'name_fin': '-',
            'name_swe': '-',
            'name_eng': '-',
            'address_fin': '-',
            'address_swe': '-',
            'city_fin': '-',
            'city_swe': '-',
            'operator': '-',
            'capacity': '0',
            'geo_pos_x': '0.0',
            'geo_pos_y': '0.0'}
        )

    if not created:
        print(f"Station '{station}' already exists")
    return station

@shared_task
def upload_csv(file_path, csv_data_type, upload_type):
    """ An async Celery task for reading uploaded CSV files.
    Takes in:
    file_path : Path to the uploaded file
    csv_data_type : Whether the csv file is uploading journey or station data
    upload_type : the type of object creation. safe_create creates all objects after reading the whole file,
    bulk_create creates the objects in chunks of 100 after adding them to a temporary list first """

    csv_data = []
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
        
    print(f"CSV read complete with {len(csv_data)} rows. Creating objects...")

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
                                    # departure_station=create_station_if_not_exists(   
                                    #     station_id=int(row['Departure station id'])),
                                    departure_station=Station.objects.get(
                                        station_id=int(row['Departure station id'])),
                                    departure_station_name=row['Departure station name'],
                                    # return_station=create_station_if_not_exists(
                                    #     station_id=int(row['Return station id'])),
                                    return_station=Station.objects.get(
                                        station_id=int(row['Return station id'])),
                                    return_station_name=row['Return station name'],
                                    covered_distance=Decimal(row['Covered distance (m)']),
                                    duration=int(row['Duration (sec.)'])
                                )

                                # Checks whether the journey already exists
                                if Journey.objects.filter(pk=csv_data.pk).exists():
                                    print("Journey already exists")
                                    continue

                                # Add the object to the list of objects
                                object_list.append(csv_data)
                                
                                """ If the upload_type is chunk_create, check if the list contains 100 objects.
                                    If so, add them to the database and initialise the list """
                                if upload_type == 'chunk_create':
                                    if len(object_list) == 100:
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

                        else:   # If duration or distance traveled is less than 10...
                            print(f"Row {i+1} : The duration of the journey {row['Departure station name']} to {row['Return station name']} \
                                is less than 10s, the distance is less than 10m or the value is faulty. Journey will not be added!")
                else:
                    print(f"Row {i+1} : Field empty")


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

                            # Chunk create checks if there are 100 Journey-objects, if so, creates them and initializes the list
                            if upload_type == 'chunk_create':
                                if len(object_list) >= 100:
                                    Station.objects.bulk_create(object_list)
                                    object_list = []

                            print(f"Row {i+1} : Station {row['ID']}.{row['Nimi']} created!")
                        
                        except ValueError as e:
                            print(f"Row {i+1} : Value error in row {i+1}! ", e)
                        except Exception as e:
                            print(f"Row {i+1} : Exception: {e}")
                            continue
                else:
                    print(f"Row {i+1} : Field empty")

            # If there are objects in the list for bulk create or left from creating objects in chunk, add them to the db 
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
        
