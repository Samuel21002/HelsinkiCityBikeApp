from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as user_login, logout
from django.contrib.auth.forms import AuthenticationForm
from csvimport.tasks import go_to_sleep
from helsinkiCityBikeApp.celery import app
from csvimport.models import Csv
from celery.result import AsyncResult

import json

def load_index_page(request):
    return render(request, 'core/index.html')
    

def celery_progress_terminate(request, task_id):
    """ For terminating a celery upload 
        Returns a JSON of the upload state. """
    task = AsyncResult(task_id)
    task.revoke()

    obj = Csv.objects.get(task_id=task_id)
    obj.delete()
    obj.save()
    app.control.revoke(task_id, terminate=True, signal='SIGKILL')
        
    return JsonResponse(json.dumps({'task_status': str(task.state).capitalize()}), safe=False)

def check_celery_status(request):
    """ A context processor shared across the whole project so that the ongoing upload task progress bars
        are shown in every page (as long as a user is logged in) """

    tasks = Csv.objects.filter(activated=False)
    tasks_to_template = [] 

    if tasks:
        #If there are ongoing tasks, assign them to a list
        for task in tasks:
            if (AsyncResult(task.task_id).state == 'PENDING' or AsyncResult(task.task_id).state == '-'):
                print(f"PENDING: {task}")
                tasks_to_template.append(task)
            elif (AsyncResult(task.task_id).state == 'SUCCESS'):
                task.activated=True
                task.save()      
            elif (AsyncResult(task.task_id).state == 'FAILED'):
                print(f"FAILED: {task}")

    return {'tasks': tasks_to_template}

def loader(request):
    """ Just a test, testing the loader pip-package"""

    task = go_to_sleep.delay(5)
    request.session['task_id'] = task.task_id
    return render(request, 'core/loader.html', {'task_id' : task.task_id} )

def login(request):
    """ Login form. Loads by default when trying to access any page as an unauthorized user """

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                valuenext= str(request.POST['next'])
                if valuenext:
                    user_login(request, user)
                    return redirect(valuenext)
                else:
                    return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form':form })

def logout(request):
    logout(request)
    return redirect('core:login')