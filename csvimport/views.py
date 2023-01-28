from .forms import CsvModelForm
from .models import Csv
from celery import current_app
from csvimport.tasks import upload_csv
from django.contrib import messages
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

# Create your views here.
def load_csvimport_page(request):
    form = CsvModelForm(request.POST or None, request.FILES or None)
    upload_type = None  # Later For choosing to upload a CSV either for journey or station objects
    return render(request, 'csvimport/upload.html', {'form': form })

def upload_file(request):
    """ Checks the user upload form and whether Celery background worker is running.
        Safe create : Safe create will wait for the file to be read until adding data to the database.
        Will improve performance but does not create the objects until the whole CSV-file is read.
        Chunk create : Creates objects by querying the database little by little but is a bit slower
    """
    form = CsvModelForm(request.POST or None, request.FILES or None)
    upload_type = None
    inspect = current_app.control.inspect()
    workers = inspect.active()

    if request.method == 'POST':
        try:
            csv_data_type = request.POST.get('csv_data')
            upload_type = request.POST.get('safe_create', 'chunk_create')

            if form.is_valid():
                obj = form.save()
                form = CsvModelForm()
                if workers:
                    # Celery worker is running and processing tasks
                    print("Reading the csv")
                    result = upload_csv.delay(obj.file_name.path, csv_data_type, upload_type)
                    if result:
                        obj.task_id = result.task_id
                        obj.save()
                    messages.success(request, "Task started!")
                    return HttpResponseRedirect(reverse('core:index'))

                else:
                    # Celery worker is not running
                    print("Celery not running")
                    obj.delete()
                    messages.error(request, "Celery is not running!")
                    return render(request, 'csvimport/upload.html', {'form': form })
        except:
            messages.error(request, "Error, upload cannot be started! Check that Redis and Celery are running and functional.")
            return render(request, 'csvimport/upload.html', {'form': form })
        else:
            messages.error(request, form.errors)

    return render(request, 'csvimport/upload.html', {'form': form })
