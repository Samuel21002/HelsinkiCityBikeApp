from django.shortcuts import render, HttpResponse

# Create your views here.
def load_stations_page(request):
    return HttpResponse("Stations page works!")