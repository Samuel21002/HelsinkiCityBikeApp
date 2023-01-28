from .models import Station
from .views import load_stations_page
from csvimport.tasks import upload_csv
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse, resolve
from splinter import Browser
import os
import json

# Create your tests here.
class StationsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(StationsTests, cls).setUpTestData()
        cls.client = Client()
        dirname = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'csvimport'))

        cls.user = User.objects.create_user('testuser', 'test@gmail.com', 'testpass')
        cls.csv_data_type_station = 'station'
        cls.upload_type = 'safe_create'
        cls.file_station = os.path.join(dirname, 'CSVFiles/Station_test_csv.csv')
        cls.result_upload_csv = upload_csv(cls.file_station, cls.csv_data_type_station, cls.upload_type)
        cls.browser = Browser('django', wait_time=3)
        
    def setUp(self):
        """ Logs in the testuser using the webdrivers browser in order to run JS-code """
        self.browser.visit(reverse('stations:stations'))
        self.browser.find_by_id('id_username').fill('testuser')
        self.browser.find_by_id('id_password').fill('testpass')
        self.browser.find_by_id('id_submit').click()
        self.client.login(username='testuser', password='testpass')
    
    def test_stations_load_page(self):
        """ Testing that the page loads """
        url = reverse('stations:stations')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_stations_page)
        self.assertEqual(response.status_code, 200)
    
    def test_station_geoJSON_data(self):
        """ Testing the render_geojson endpoint and whether the correct data is rendered to the template """

        self.assertEqual(self.result_upload_csv, '10 stations uploaded successfully')
        self.assertEqual(len(Station.objects.all()), 10)

        json_url = self.client.get(reverse('stations:render_geojson'))
        self.assertJSONEqual(str(json.loads(json_url.content)), 
        {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {
            "station_id": "1", "name_fin": "Testiasema 1", "name_swe": "Teststation 1"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}, {
            "type": "Feature", "properties": {"station_id": "2", "name_fin": "Testiasema 2", "name_swe": "Teststation 2"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}, {
            "type": "Feature", "properties": {"station_id": "3", "name_fin": "Testiasema 3", "name_swe": "Teststation 3"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}, {
            "type": "Feature", "properties": {"station_id": "4", "name_fin": "Testiasema 4", "name_swe": "Teststation 4"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}, {
            "type": "Feature", "properties": {"station_id": "5", "name_fin": "Testiasema 5", "name_swe": "Teststation 5"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}, {
            "type": "Feature", "properties": {"station_id": "6", "name_fin": "Testiasema 6", "name_swe": "Teststation 6"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}, {
            "type": "Feature", "properties": {"station_id": "7", "name_fin": "Testiasema 7", "name_swe": "Teststation 7"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}, {
            "type": "Feature", "properties": {"station_id": "8", "name_fin": "Testiasema 8", "name_swe": "Teststation 8"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}, {
            "type": "Feature", "properties": {"station_id": "9", "name_fin": "Testiasema 9", "name_swe": "Teststation 9"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}, {
            "type": "Feature", "properties": {"station_id": "10", "name_fin": "Testiasema 10", "name_swe": "Teststation 10"
        }, "geometry": {"type": "Point", "coordinates": [24.840319, 60.16582]}}]})
     
    def test_station_leaflet_loaded(self):
        """ Tests whether the map element exists and whether the stations render to the search bar 
            (LATER) tests that all station marker have been rendered from the geoJSON to the map """

        self.browser.visit(reverse('stations:stations'))
        self.assertTrue(self.browser.is_element_present_by_id('id_map'))
        self.assertTrue(self.browser.is_element_present_by_text('Testiasema 1, Teststation 1'))
        self.assertTrue(self.browser.is_element_present_by_text('Most popular departure stations to this point:'))
        self.assertTrue(self.browser.is_element_present_by_text('Most popular return stations from this point:'))

    def tearDown(self):
        self.browser.quit()