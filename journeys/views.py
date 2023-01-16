from django.shortcuts import render
from .models import Journey
from stations.models import Station
from django.db.models import Q

# Create your views here.
def load_journeys_page(request):
    
    context = {}
    stations = Station.objects.all()

    context.update({
        'stations' : stations,
        'search_results' : Q(),
    })

    return render(request, 'journeys/journeys.html', context)