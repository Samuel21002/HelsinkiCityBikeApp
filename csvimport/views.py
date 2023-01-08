from django.shortcuts import render, HttpResponse

# Create your views here.
def load_csvimport_page(request):
    return HttpResponse("CSV upload page works!")