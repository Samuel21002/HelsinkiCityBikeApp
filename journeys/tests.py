from .models import Journey
from stations.models import Station
from .views import load_journeys_page
from csvimport.tasks import upload_csv
from django.test import TestCase, Client, LiveServerTestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test.utils import override_settings
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import os

class JourneyTests(TestCase):

    @classmethod
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def setUpTestData(cls):
        """ CELERY_TASK_ALWAYS_EAGER=True keeps the Celery processes within the test environment """

        super(JourneyTests, cls).setUpTestData()
        cls.client = Client()
        cls.user = User.objects.create_user(
            'testuser', 'test@gmail.com', 'testpass')

    def setUp(self):
        self.client.login(username='testuser', password='testpass')
    
    def test_journey_load_page(self):
        """ Testing the basics of page loading properly and that user will be redirected to 
            the login page if not logged in and trying to access any other page """
        
        url = reverse('journeys:journeys')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_journeys_page)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
class JourneyPageTests(LiveServerTestCase):
    
    @classmethod
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def setUpClass(cls):
        """ CELERY_TASK_ALWAYS_EAGER=True keeps the Celery processes within the test environment """

        super().setUpClass()
        cls.selenium = WebDriver()
        cls.user = User.objects.create_user(
        'testuser', 'test@gmail.com', 'testpass')

        dirname = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'csvimport'))
        file_station = os.path.join(
            dirname, 'CSVFiles/Station_test_csv.csv')
        file_journey = os.path.join(
            dirname, 'CSVFiles/Journey_test_csv.csv')

        cls.station_upload_csv = upload_csv.delay(
            file_station, 'station', 'safe_create').get()
        cls.journey_upload_csv = upload_csv.delay(
            file_journey, 'journey', 'safe_create').get()

        cls.selenium.implicitly_wait(5)

    def test_csv_upload(self):
        self.assertEqual(self.station_upload_csv,
                'Station upload successful!')
        self.assertEqual(len(Station.objects.all()), 10)

        self.assertEqual(self.journey_upload_csv,
                'Journey upload successful!')
        self.assertEqual(len(Journey.objects.all()), 10)