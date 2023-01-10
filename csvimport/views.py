from django.shortcuts import render
from django.urls import reverse
from .forms import CsvModelForm

# Create your views here.
def load_csvimport_page(request):
    form = CsvModelForm(request.POST or None, request.FILES or None)
    upload_type = None  # Later For choosing to upload a CSV either for journey or station objects
    return render(request, 'csvimport/upload.html', {'form': form })

def upload_file(request):
    
    """ Safe create : Safe create will wait for the file to be read until adding data to the database.
        Will improve performance but does not create the objects until the whole CSV-file is read.
        Chunk create : Creates objects by querying the database little by little but is a bit slower
    """

    if request.method == 'POST':
        csv_data_type = request.POST.get('csv_data')
        upload_type = request.POST.get('safe_create', 'chunk_create')
        print(f"CSV data type: {csv_data_type}")
        print(f"Upload type: {upload_type}")
        if form.is_valid():
            obj = form.save()
            form = CsvModelForm()
            # READ THE CSV USING CELERY AND REDIS AS BACKGROUND TASK HANDLERS... 
            obj.activated = True    # After upload is succesful
            obj.save()  # Saves 
            return render(request, 'core/index.html')
        else:
            return render(request, 'csvimport/upload.html', {'form': form })
