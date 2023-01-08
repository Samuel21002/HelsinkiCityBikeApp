from django.shortcuts import render, HttpResponse

# Create your views here.
def load_journeys_page(request):
    return HttpResponse("Journeys page works!")