from .views import load_journeys_page
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse, resolve

# Create your tests here.
class JourneyTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(JourneyTests, cls).setUpTestData()
        cls.client = Client()
        cls.user = User.objects.create_user('testuser', 'test@gmail.com', 'testpass')

    def setUp(self):
        self.client.login(username='testuser', password='testpass')
    
    def test_journey_load_page(self):
        url = reverse('journeys:journeys')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_journeys_page)
        self.assertEqual(response.status_code, 200)
        