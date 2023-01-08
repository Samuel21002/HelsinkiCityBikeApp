from django.shortcuts import render, HttpResponse

# Create your views here.
def load_index_page(request):
    return HttpResponse("Index page works!")