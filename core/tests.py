from .views import load_index_page
from django.test import TestCase
from django.urls import reverse, resolve

# Create your tests here.
class CoreTests(TestCase):
    
    def test_index_load_page(self):
        url = reverse('core:index')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_index_page)
        self.assertEqual(response.status_code, 200)
        