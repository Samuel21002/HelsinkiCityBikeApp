from .models import Journey
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.timezone import datetime
from stations.models import Station
import geojson
import re

# Create your views here.
def load_journeys_page(request):
    
    context = {}
    stations = Station.objects.all()

    context.update({
        'stations' : stations,
        'search_results' : Q(),
    })

    return render(request, 'journeys/journeys.html', context)

def get_journey_info(request, id): 
    """ Gets the journey info and renders it on the map as a layer
        Returns a JSON object"""
    
    journey = Journey.objects.get(pk=id)
    print(journey)
    dep_station = Station.objects.get(pk=journey.departure_station.pk)
    ret_station = Station.objects.get(pk=journey.return_station.pk)

    # geoJSON for Leaflet
    feature_collection = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {
                "stations" : f"{dep_station.name_fin} -> {ret_station.name_fin}",
                "covered_distance" : f"{float(journey.covered_distance)}",
                "duration": f"{journey.duration}",
                },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                [float(dep_station.geo_pos_x), float(dep_station.geo_pos_y)],
                [float(ret_station.geo_pos_x), float(ret_station.geo_pos_y)]
                ],
                "bounds": [
                [float(dep_station.geo_pos_y), float(dep_station.geo_pos_x)],
                [float(ret_station.geo_pos_y), float(ret_station.geo_pos_x)]
                ]
            }
        }]
    }

    return JsonResponse(geojson.dumps(feature_collection), safe=False, status=200)

def search_journey(request):
    """ The HTTPRequest from the page containing the necessary search parameters for database queries 
        Returns a pagination object along with the search results and the query parameters for rendering
        the pagination href's """
    
    if request.method == 'GET':
        context = {}
        all_results = Journey.objects.all()

        search = request.GET.get("search", '')
        journey_dep_station = request.GET.get("journey_dep_station", '')
        journey_ret_station = request.GET.get("journey_ret_station", '')
        date_matches = re.findall(r"(\d{2}/\d{2}/\d{4})", request.GET.get("daterange"))
        dates = [datetime.strptime(date_string, "%m/%d/%Y").date().strftime("%Y-%m-%d") for date_string in date_matches]
        distance = request.GET.getlist("distance")
        duration = request.GET.getlist("duration")

        distance[0] = 10 if int(distance[0]) < 10 else distance[0]  # For validating the minimum distance
        duration[0] = 10 if int(duration[0]) < 10 else duration[0]  # For validating the minimum duration
        max_distance = Journey.objects.aggregate(Max('covered_distance'))['covered_distance__max']   # Max distance found in database
        max_duration = Journey.objects.aggregate(Max('duration'))['duration__max']   # Max duration found in database

        multiple_q = Q()

        if search:
            if journey_dep_station == "departure":
                multiple_q |= Q(departure_station_name__contains=search)
            if journey_ret_station == "return":
                multiple_q |= Q(return_station_name__contains=search)
            else:
                HttpResponse("CANNOT BE EMPTY!!!")

        """ Applies the date range filtering departure and / or return station results
            If no upper bound is selected, datetime now is selected
        """
        if dates: 
            multiple_q &= Q(departure_time__date__gte=dates[0] if journey_dep_station else datetime(2020, 1, 1, 00, 00, 00, 0).date())
            multiple_q &= Q(return_time__date__lte=dates[1] if journey_ret_station else datetime.now().date())
        
        if distance:
            multiple_q &= Q(covered_distance__gte=distance[0] if journey_dep_station else 10)
            multiple_q &= Q(covered_distance__lte=distance[1] if journey_ret_station else max_distance)
            
        if duration:
            multiple_q &= Q(duration__gte=duration[0] if journey_dep_station else 10)
            multiple_q &= Q(duration__lte=duration[1] if journey_ret_station else max_duration)
    
        result = Journey.objects.filter(multiple_q).order_by('-departure_station_name').distinct()
        paginated_filtered_releases = Paginator(result, 5)
        page_number = request.GET.get('page', 1) 

        get_copy = request.GET.copy()
        query = get_copy.pop('page', True) and get_copy.urlencode()
        page_range = paginated_filtered_releases.get_elided_page_range(number=page_number)  

        try:
            page_obj = paginated_filtered_releases.page(page_number)
        except PageNotAnInteger:
            page_obj = paginated_filtered_releases.page(5)
        except EmptyPage:
            page_obj = paginated_filtered_releases.page(paginated_filtered_releases.num_pages)

        context.update({
            'search_results' : result, 
            'page_obj' : page_obj,
            'page_range': page_range,
            'search' : search,
            'query' : query,
            })
    
    else:
        result = all_results.order_by("-departure_station_name")
        context.update({'search_results' : result})

    return render(request, 'journeys/journeys.html', context)