from .models import Station
from datetime import datetime
from django.core.serializers import serialize
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from journeys.models import Journey
import geojson
import json

def load_stations_page(request):
    """ Loading the stations page, returning all station objects in the div """
    context = {}
    stations = Station.objects.all()

    context.update({
        'stations': stations,
        'search_results': Q(),  # Empty until a search is performed
    })

    return render(request, 'stations/stations.html', context)


def render_geojson(request):
    """ Renders all stations from the database and creates every object into a geoJSON string.
    That string is passed on and displayed on a Leaflet map in the template.
    Objects are appended to a list and added to the end of the GeoJSON after 'FeatureCollection' is declared

    Returns a JSONResponse fetched by the front end """

    stations = []   # A List consisting of string representations of the objects attributes
    for station in Station.objects.all():
        feature = {
            "type": "Feature",
            "properties": {
                "station_id": f"{station.station_id}",
                "name_fin": f"{station.name_fin}",
                "name_swe": f"{station.name_swe}",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(station.geo_pos_x), float(station.geo_pos_y)]
            }
        }
        stations.append(feature)

    feature_collection = {
        "type": "FeatureCollection",
        "features": stations
    }

    return JsonResponse(geojson.dumps(feature_collection), safe=False, status=200)

def get_station_names(request):
    """ Passes station names to the search suggestions """

    stations = Station.objects.all().values('station_id', 'name_fin', 'name_swe', 'address_fin', 'address_swe'
    ).order_by("-name_fin")
    return JsonResponse(json.dumps(list(stations)), safe=False)

def get_station_info(request, station_id, month):
    """ Takes in the selected station id and the month from a select box.
    
    Gets:
     - Basic station information,
     - Total number of journeys starting from the station,
     - Total number of journeys ending at the station,
     - The average distance of a journey starting from the station,
     - The average distance of a journey ending at the station,
     - Top 5 most popular return stations for journeys starting from the station and
     - Top 5 most popular departure stations for journeys ending at the station,

    and additionally filter them by month if a month is provided """
    
    context = {}
    station = Station.objects.get(station_id=station_id)

    if station:

        # JSON for displaying info in the frontend div
        station_json = json.loads(serialize("json", [station]))
        context.update({
            'station' : station_json[0]['fields']
            })

        if Journey.objects:
            try:

                """ Total number of journeys starting from the station
                Total number of journeys ending at the station """
                stations_dep = Journey.objects.filter(departure_station=station)
                stations_ret = Journey.objects.filter(return_station=station)

                if month != 'All':
                    month = datetime.strptime(month, '%b').month

                    stations_dep = stations_dep.filter(departure_time__month=month)
                    stations_ret = stations_ret.filter(return_time__month=month)

                """ Counting the average distance of a journey starting from the station
                and the average distance of a journey ending at the station or return 0
                if no journeys from or to that station are found """
                stations_dep_dist_avg = round(sum([obj.covered_distance for obj in stations_dep]) 
                / stations_dep.count(), 1) if stations_dep else 0
                stations_ret_dist_avg = round(sum([obj.covered_distance for obj in stations_ret]) 
                / stations_ret.count(), 1) if stations_ret else 0

                """
                Top 5 most popular return stations for journeys starting from the station
                Top 5 most popular departure stations for journeys ending at the station
                """
                stations_dep_most_pop_ret = stations_dep.values('return_station_name'
                ).annotate(station_count=Count('return_station')
                ).order_by('-station_count')[:5]
                
                stations_ret_most_pop_dep = stations_ret.values('departure_station_name'
                ).annotate(station_count=Count('departure_station')
                ).order_by('-station_count')[:5]

                context.update({
                'station_dep_amt': stations_dep.count(),
                'station_ret_amt' : stations_ret.count(),
                'station_dep_dist_avg' : float(stations_dep_dist_avg),
                'station_ret_dist_avg' : float(stations_ret_dist_avg),
                'station_dep_most_pop_ret' : list(stations_dep_most_pop_ret),
                'station_ret_most_pop_dep' : list(stations_ret_most_pop_dep)
                })

            except ZeroDivisionError:
                print("Not divisible by zero")
            
            except:
                return HttpResponse("Station or journeys not found or value-error occurred")

        # Convert each query to JSON before returning a succesful JSON
        return JsonResponse(json.dumps(context), content_type="application/json", safe=False)
        
    return HttpResponse("No stations found")
