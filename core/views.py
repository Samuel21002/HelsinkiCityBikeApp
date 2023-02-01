from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as user_login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from helsinkiCityBikeApp.celery import app
from csvimport.models import Csv
from celery.result import AsyncResult

import json

def load_index_page(request):
    """ Opening the main index page """
    return render(request, 'core/index.html')

def celery_progress_terminate(request, task_id):
    """ For terminating a celery upload 
        Returns a JSON of the upload state. """
    task = AsyncResult(task_id)
    csv_obj = Csv.objects.get(task_id=task.task_id)

    if csv_obj:
        task.revoke()
        app.control.revoke(task.task_id, terminate=True, signal='SIGKILL')
        csv_obj.delete()
        
    return JsonResponse(json.dumps({'task_status': "Upload has been cancelled!"}), safe=False)

def check_celery_status(request):
    """ A context processor shared across the whole project so the ongoing uploads
        are shown on every page as progress bars (as long as a user is logged in)
        Returns only the 'PENDING' tasks to the template and ignores the rest 
        Saves the csv-file to the database if the upload is succesfully completed """
    
    tasks = Csv.objects.filter(activated=False)

    if tasks:
        #If there are ongoing tasks, assign them to a list
        for task in tasks:
            obj = AsyncResult(task.task_id)
            if obj.state == 'SUCCESS':
                print(f"SUCCESS: {task}")
                task.activated=True
                task.save()      
                tasks.exclude(task_id=obj.task_id)
            if bool(obj.state != '-') | bool(obj.state != 'PENDING'):
                tasks.exclude(task_id=obj.task_id)

    return {'tasks': tasks}

def login(request):
    """ Login form. Loads by default when trying to access any page as an unauthorized user """

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                valuenext= str(request.POST['next'])    # Redirects to the page user initially tried to access
                if valuenext:
                    user_login(request, user)
                    return redirect(valuenext)
                else:
                    return redirect('/')
        else:
            messages.error(request, "Login failed, verify your username and password.")
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form':form })

def logout(request):
    logout(request)
    return redirect('core:login')