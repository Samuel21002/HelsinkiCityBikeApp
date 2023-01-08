from .views import load_journeys_page
from django.test import TestCase
from django.urls import reverse, resolve

# Create your tests here.
class JourneyTests(TestCase):
    
    def test_journey_load_page(self):
        url = reverse('journeys:journeys')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_journeys_page)
        self.assertEqual(response.status_code, 200)
        