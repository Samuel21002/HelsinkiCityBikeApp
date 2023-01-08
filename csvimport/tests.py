from .views import load_csvimport_page
from django.test import TestCase
from django.urls import reverse, resolve

# Create your tests here.
class CSVImportTests(TestCase):
    
    def test_csvimport_load_page(self):
        url = reverse('csvimport:csvimport')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_csvimport_page)
        self.assertEqual(response.status_code, 200)
        