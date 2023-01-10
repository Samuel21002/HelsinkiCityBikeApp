from .views import load_csvimport_page
from django.test import TestCase, Client
from .models import Csv
from django.contrib.auth.models import User
from django.urls import reverse, resolve
import os

# Create your tests here.
class CSVImportTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super(CSVImportTests, cls).setUpTestData()
        cls.client = Client()
        cls.user = User.objects.create_user('testuser', 'test@gmail.com', 'testpass')

    def setUp(self):
        self.client.login(username='testuser', password='testpass')

    def test_csvimport_load_page(self):
        """ Tests the upload page, whether its elements render properly and whether adding a CSV-file adds it to the database """
        url = reverse('csvimport:csvimport')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_csvimport_page)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form id="upload-form" action="" method="post" class="ui form form_style" enctype="multipart/form-data">')

        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Index Page</h1>')

    def test_add_csv_db_directly(self):
        self.obj = Csv.objects.create(file_name='test.csv')
        self.assertEqual(Csv.objects.get(pk=self.obj.pk), self.obj)
        self.assertFalse(self.obj.activated, True)