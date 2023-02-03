from .models import Station
from .views import load_stations_page
from csvimport.tasks import upload_csv
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, LiveServerTestCase, Client
from django.test.utils import override_settings
from django.urls import reverse, resolve
from journeys.models import Journey
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.webdriver import WebDriver
import json
import os
import time

class StationsUploadTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """ CELERY_TASK_ALWAYS_EAGER=True keeps the Celery processes within the test environment """

        super(StationsUploadTests, cls).setUpTestData()
        cls.client = Client()
        dirname = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'csvimport'))
        cls.file_station = os.path.join(
            dirname, 'CSVFiles/Station_test_csv.csv')
    
    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', 'test@gmail.com', 'testpass')
        self.client.login(username='testuser', password='testpass')
            
    def test_station_load_page(self):
        """ Testing the basics of page loading properly, the correct view being rendered and that user
        will be redirected to the login page if not logged in and trying to access any other page """

        url = reverse('stations:stations')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_stations_page)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 302)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_station_geoJSON_data(self):
        """ Testing the asynchronous CSV-upload, whether it renders the proper GeoJson endpoint data,
            checks if the Leaflet map exists on the page and whether the correct data is rendered on the page.
        """
        upload_csv.delay(self.file_station, 'station', 'safe_create').get()  # type: ignore
        time.sleep(1)
        self.maxDiff = None
        json_content = self.client.get(
            reverse('stations:render_geojson')).content
        self.assertJSONEqual(str(json.loads(json_content)),
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


class StationPageTests(LiveServerTestCase):
    """ LiveServerTestCases test the interaction of the stations page by creating stations and journeys,
    searching from the stations list, clicking on the station to retrieve information, and to display
    the top departure stations by a defined month"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(5)

    def setUp(self):
        """ Creates an user and Station & Journey objects """

        self.user = User.objects.create_user(
            'testuser', 'test@gmail.com', 'testpass')

        for i in range(1, 11):
            Station.objects.create(
                station_id=i,
                fid=i,
                name_fin=f'Testiasema {i}',
                name_swe=f'Teststation {i}',
                name_eng=f'Teststation {i}',
                address_fin=f'Testikatu {i}',
                address_swe=f'Testgatan {i}',
                city_fin=f'Testikaupunki',
                city_swe=f'Teststad',
                operator=f'Testi OY',
                capacity=int(5),
                geo_pos_x=Decimal(24.8597944),
                geo_pos_y=Decimal(60.2457079)
            )

        Journey.objects.create(
            departure_time='2021-05-31T12:57:53',
            return_time='2021-05-31T12:27:25',
            departure_station=Station.objects.get(
                station_id=1),
            departure_station_name='Testiasema 1',
            return_station=Station.objects.get(
                station_id=6),
            return_station_name='Testiasema 6',
            covered_distance=Decimal(2451),
            duration=865
        )

        Journey.objects.create(
            departure_time='2021-05-31T12:35:53',
            return_time='2021-05-31T12:27:25',
            departure_station=Station.objects.get(
                station_id=5),
            departure_station_name='Testiasema 5',
            return_station=Station.objects.get(
                station_id=5),
            return_station_name='Testiasema 5',
            covered_distance=Decimal(750),
            duration=159
        )

        Journey.objects.create(
            departure_time='2021-06-02T12:57:53',
            return_time='2021-06-02T12:27:25',
            departure_station=Station.objects.get(
                station_id=5),
            departure_station_name='Testiasema 5',
            return_station=Station.objects.get(
                station_id=3),
            return_station_name='Testiasema 3',
            covered_distance=Decimal(1250),
            duration=159
        )

    def test_page(self):
        """ LiveServerTestCases test the interaction of the stations page by creating stations and journeys,
        searching from the stations list, clicking on the station to retrieve information, and to display
        the top departure stations by a defined month"""

        # Logs in the user
        self.maxDiff = None
        self.selenium.get('%s%s' % (self.live_server_url, '/stations/'))
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys('testuser')
        password_input.send_keys('testpass')
        self.selenium.find_element(By.ID, 'id_submit').click()

        # Checks if the map element is present on the page
        time.sleep(2)
        map = self.selenium.find_element(By.ID, 'id_map')
        self.assertTrue(map)

        # Makes a search of 'Testiasema 8' and asserts that it is the only element in the search div
        time.sleep(2)
        search_input = self.selenium.find_element(By.ID, "id_search")
        search_input.send_keys('Testiasema 8')
        search_innerHtml = self.selenium.find_element(
            By.XPATH, '//*[@id="id_station_list"]').get_attribute("innerHTML").strip()
        expected_text = '''<li class="pv2">
      <a onclick="get_station_info(8); autoFill('Testiasema 8')" class="link blue lh-title">
          <span class="fw7 underline-hover"><span class="hl">Testiasema 8</span>, Teststation 8</span>
          <span class="db black-60">Testikatu 8, Testgatan 8</span>
      </a>
      </li>'''
        time.sleep(1)
        self.assertEqual(search_innerHtml, expected_text)
        search_input.clear()

        # Clicks on the 'Testiasema 5' -link displaying the info in the div and asserts the innerHTML
        self.selenium.find_element(
            By.PARTIAL_LINK_TEXT, "Testiasema 5, Teststation 5").click()
        time.sleep(2)
        ul_innerHtml = self.selenium.find_element(
            By.XPATH, "//ul[@class='info_ul']").get_attribute("innerHTML").strip()
        expected_text = '''<li>Station Name:&nbsp;&nbsp;<strong>Testiasema 5 / Teststation 5 / Teststation 5</strong></li>
      <li>Station Address:&nbsp;&nbsp;<strong>Testikatu 5, Testgatan 5</strong></li>
      <li>City:&nbsp;&nbsp;<strong>Testikaupunki, Teststad</strong></li>
      <li>Operator:&nbsp;&nbsp;<strong>Testi OY</strong></li>
      <li>Departures from station:&nbsp;&nbsp;<strong>2</strong></li>
      <li>Returns to station:&nbsp;&nbsp;<strong>1</strong></li>
      <li>Average distance from the station:&nbsp;&nbsp;<strong>1000</strong></li>
      <li>Average distance to the station:&nbsp;&nbsp;<strong>750</strong></li>'''
        self.assertEqual(ul_innerHtml, expected_text)

        # Finds the list of Most popular return stations of 'Testiasema 5' and asserts the innerHTML
        station_top_list = self.selenium.find_element(
            By.ID, "id_station_dep_most_pop_ret")
        station_top_list_html = station_top_list.get_attribute(
            "innerHTML").strip()
        expected_text = '<tr><td>1, Testiasema 3</td></tr><tr><td>1, Testiasema 5</td></tr>'
        time.sleep(2)
        self.assertEqual(station_top_list_html, expected_text)

        # Filters the results by month, thus should only display one result from 'may'.
        select_element = Select(self.selenium.find_element(By.NAME, 'month'))
        select_element.select_by_value('may')
        time.sleep(1)
        station_top_list_html_2 = station_top_list.get_attribute(
            "innerHTML").strip()
        expected_text = '<tr><td>1, Testiasema 5</td></tr>'
        time.sleep(2)
        self.assertEqual(station_top_list_html_2, expected_text)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
