from .forms import CsvModelForm
from .models import Csv
from .views import load_csvimport_page
from celery import current_app
from csvimport.tasks import upload_csv
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse, resolve
from stations.models import Station
from journeys.models import Journey
from unittest.mock import patch
import os
from unittest import mock
# Create your tests here.
class CSVImportTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """ Registering a user for the test cases """
        super(CSVImportTests, cls).setUpTestData()
        cls.client = Client()
        cls.user = User.objects.create_user('testuser', 'test@gmail.com', 'testpass')

    def setUp(self):
        """ Logging in a user for the test cases """
        self.client.login(username='testuser', password='testpass')

    def test_csvimport_load_page(self):
        """ Tests the upload page, whether its elements render properly and whether adding a CSV-file adds it to the database """
        url = reverse('csvimport:csvimport')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_csvimport_page)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form id="upload-form" action="/csvimport/upload/" method="post" class="ui form form_style" enctype="multipart/form-data">')

        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Index Page</h1>')

    def test_add_csv_db_directly(self):
        """ Tests adding a CSV file to the db"""
        self.obj = Csv.objects.create(file_name='test.csv')
        self.assertEqual(Csv.objects.get(pk=self.obj.pk), self.obj)
        self.assertFalse(self.obj.activated, True)
        self.assertEqual(len(Csv.objects.all()), 1)

    def test_form_upload(self):
        """ Tests the form validation """
        dirname = os.path.dirname(__file__)
        self.file = os.path.join(dirname, 'CSVFiles/Station_test_csv.csv')
        self.url = reverse('csvimport:upload_file')
        data = {'csv_data':'station', 'safe_create': 'safe_create'}

        # Complete form
        with open(self.file, 'rb') as f:
            csv_file = SimpleUploadedFile(f.name, f.read())
        files = {'file_name': csv_file}
        form = CsvModelForm(data=data, files=files)
        response = self.client.post(self.url, data=data, files=files)  
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.is_valid())

        # Lacking form
        csv_file_lacking = SimpleUploadedFile('Station_test_csv.pdfxx', b"This file is the wrong format")
        files = {'file_name': csv_file_lacking}
        form = CsvModelForm(data=data, files=files)
        response = self.client.post(self.url, data=data, files=files)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("The file must be a CSV-file!", form.errors["file_name"])


    def test_csv_upload_with_celery(self):
        """ Tests the Celery background task by providing a csv-file with both valid and invalid row data"""
        dirname = os.path.dirname(__file__)

        self.csv_data_type_journey = 'journey'
        self.csv_data_type_station = 'station'
        self.upload_type = 'safe_create'
        self.file_station = os.path.join(dirname, 'CSVFiles/Station_test_csv.csv')
        self.file_journey = os.path.join(dirname, 'CSVFiles/Journey_test_csv.csv')

        # Journey (without station objects)
        self.result_upload_csv = upload_csv(self.file_journey, self.csv_data_type_journey, self.upload_type)
        self.assertEqual(self.result_upload_csv, 'CSV upload completed')
        self.assertEqual(len(Journey.objects.all()), 0)

        # Station
        self.result_upload_csv = upload_csv(self.file_station, self.csv_data_type_station, self.upload_type)
        self.assertEqual(self.result_upload_csv, '10 stations uploaded successfully')
        self.assertEqual(len(Station.objects.all()), 10)

        # Journey (with station objects)
        self.result_upload_csv = upload_csv(self.file_journey, self.csv_data_type_journey, self.upload_type)
        self.assertEqual(self.result_upload_csv, '5 journeys uploaded successfully')
        self.assertEqual(len(Journey.objects.all()), 5)

        # Wrong datatype
        self.result_upload_csv = upload_csv(self.file_journey, self.csv_data_type_station, self.upload_type)
        self.assertTrue(len(Journey.objects.all()), 0)

            
    # Using mock ?

    # @patch('csvimport.tasks.upload_csv')
    # def test_csv_upload_with_celery(self, my_task_mock):
    #     """ Tests the Celery background task by providing a csv-file with both valid and invalid row data"""
    #     dirname = os.path.dirname(__file__)

    #     # Upload Station to Celery
    #     self.file_station = os.path.join(dirname, 'CSVFiles/Station_test_csv.csv')
    #     self.csv_data_type_station = 'station'
    #     self.upload_type = 'safe_create'

    #     my_task_mock.delay.side_effect = '9 stations uploaded successfully'
    #     self.result_mock_upload = my_task_mock.delay(self.file_station, self.csv_data_type_station, self.upload_type)
    #     my_task_mock.delay.assert_called()
    #     self.assertEqual(self.result_mock_upload, '9 stations uploaded successfully')
    #     self.assertEqual(len(Station.objects.all()), 9)

    #     # Upload Journey to Celery
    #     self.file_journey = os.path.join(dirname, 'CSVFiles/Journey_test_csv.csv')
    #     self.csv_data_type_journey = 'journey'
    #     self.upload_type = 'safe_create'

    #     my_task_mock.delay.side_effect = '7 journeys uploaded successfully'
    #     self.result_mock_upload = my_task_mock.delay(self.file_journey, self.csv_data_type_journey, self.upload_type)
    #     my_task_mock.delay.assert_called()
    #     self.assertEqual(self.result_mock_upload, '7 journeys uploaded successfully')
    #     self.assertEqual(len(Journey.objects.all()), 7)

    #     with self.assertRaises(ValueError):
    #         self.result_mock_upload = my_task_mock.delay(self.file_journey, self.csv_data_type_station, self.upload_type)
        
