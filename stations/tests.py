from .views import load_stations_page
from django.test import TestCase
from django.urls import reverse, resolve

# Create your tests here.
class StationsTests(TestCase):
    
    def test_stations_load_page(self):
        url = reverse('stations:stations')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_stations_page)
        self.assertEqual(response.status_code, 200)
        