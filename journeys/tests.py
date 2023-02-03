from .models import Journey
from .views import load_journeys_page
from csvimport.tasks import upload_csv
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TransactionTestCase, Client, LiveServerTestCase
from django.test.utils import override_settings
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from stations.models import Station
import json
import os
import re
import time


class JourneyTests(TransactionTestCase):

    reset_sequences = True

    @classmethod
    def setUpTestData(cls):

        super(JourneyTests, cls)
        cls.client = Client()

    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', 'test@gmail.com', 'testpass')
        self.client.login(username='testuser', password='testpass')

    def test_journey_load_page(self):
        """ Testing the basics of page loading properly, the correct view being rendered and that user
        will be redirected to the login page if not logged in and trying to access any other page """

        url = reverse('journeys:journeys')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_journeys_page)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get(reverse('stations:stations'))
        self.assertEqual(response.status_code, 302)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_objects_upload(self):
        """ Tests whether uploading a CSV creates the desired amount of objects
            CELERY_TASK_ALWAYS_EAGER=True keeps the Celery processes within the test environment """

        dirname = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'csvimport'))
        file_station = os.path.join(
            dirname, 'CSVFiles/Station_test_csv.csv')
        file_journey = os.path.join(
            dirname, 'CSVFiles/Journey_test_csv.csv')
        station_upload_csv = upload_csv.delay(
            file_station, 'station', 'safe_create').get()  # type: ignore
        journey_upload_csv = upload_csv.delay(
            file_journey, 'journey', 'safe_create').get()  # type: ignore

        self.assertEqual(station_upload_csv,
                         'Station upload successful!')
        self.assertEqual(len(Station.objects.all()), 10)

        self.assertEqual(journey_upload_csv,
                         'Journey upload successful!')
        self.assertEqual(len(Journey.objects.all()), 20)

    def test_get_journeys_info(self):
        """ Tests the JSONResponse to the Leaflet map by providing a journey, consisting of two stations
            and creating the proper JSON string """

        for i in range(1, 3):
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
                station_id=2),
            return_station_name='Testiasema 2',
            covered_distance=Decimal(2451),
            duration=865
        )

        json_content = self.client.get(
            reverse('journeys:get_journey_info', args=[1])).content

        self.assertJSONEqual(str(json.loads(json_content)),
                             {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {
                                 "stations": "Testiasema 1 -> Testiasema 2", "covered_distance": "2451.0",
                                 "duration": "865"}, "geometry": {
                                 "type": "LineString", "coordinates":
                                 [[24.859794, 60.245708], [
                                     24.859794, 60.245708]],
                                 "bounds": [[60.245708, 24.859794], [60.245708, 24.859794]]}}]})

    def tearDown(self):
        super().tearDown()
        Journey.objects.all().delete()
        Station.objects.all().delete()

class JourneyPageTests(LiveServerTestCase):
    """ For page interaction tests on a temporary LiveServer.
        Uploads test data, searches for journeys to display on the template, ordering, filtering
        and asserting the amount of search results after every query """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()

    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', 'test@gmail.com', 'testpass')
        dirname = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'csvimport'))
        self.file_station = os.path.join(
            dirname, 'CSVFiles/Station_test_csv.csv')
        self.file_journey = os.path.join(
            dirname, 'CSVFiles/Journey_test_csv.csv')

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_page_interactions(self):

        self.station_upload_csv = upload_csv.delay(
            self.file_station, 'station', 'safe_create').get()  # type: ignore
        self.journey_upload_csv = upload_csv.delay(
            self.file_journey, 'journey', 'safe_create').get()  # type: ignore
        self.selenium.implicitly_wait(5)

        self.maxDiff = None

        # Logs in the user
        self.selenium.get('%s%s' % (self.live_server_url, '/journeys/'))
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys('testuser')
        password_input.send_keys('testpass')
        self.selenium.find_element(By.ID, 'id_submit').click()

        self.selenium.implicitly_wait(2)
        map = self.selenium.find_element(By.ID, 'id_map')
        self.assertTrue(map)

        # Looks for Testiasema 3 by providing the digit as a value
        self.selenium.find_element(By.ID, 'id_departure').send_keys('3')
        self.selenium.find_element(By.ID, 'id_submit').click()
        search_results = WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located((By.ID, "search_matches")))
        self.assertEqual(search_results.text, "Your search matches 2 results")

        # Looks for both departure and return stations
        self.selenium.find_element(
            By.ID, 'id_departure').send_keys('Testiasema 10')
        self.selenium.find_element(
            By.ID, 'id_return').send_keys('Testiasema 4')

        time.sleep(2)
        WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located((By.ID, "id_submit"))).click()
        search_results = WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located((By.ID, "search_matches")))
        self.assertEqual(search_results.text, "Your search matches 3 results")

        # Ordering by distance and then asserting the what the first element should be
        time.sleep(2)
        self.selenium.find_element(
            By.XPATH, '//*[@id="order_by_dist"]').click()
        first_journey_el = self.selenium.find_element(
            By.NAME, 'journey').get_attribute('innerHTML').strip()
        expected_condition = '''<li class="column is-3-widescreen is-2-tablet is-mobile pr3 f6 f6-ns fw6 ">
            <i class="fa-solid fa-map"></i>&nbsp; <a href="#id_map" onclick="get_journey(20)">
            Testiasema 10 <i class="fa-solid fa-arrow-right-long w-10"></i> Testiasema 4
            </a>
        </li>
        <li class="column is-1-widescreen is-1-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="dep_time">April 27, 2021, 7:56 a.m.</li>
        <li class="column is-1-widescreen is-1-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="ret_time">April 27, 2021, 9:01 a.m.</li>
        <li class="column is-2-widescreen is-2-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="dep_stat">Testiasema 10</li>
        <li class="column is-2-widescreen is-2-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="ret_stat">Testiasema 4</li>
        <li class="column is-1-widescreen is-1-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="cov_dist">4300.00</li>
        <li class="column is-1-widescreen is-1-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="duration">1:02:42</li>'''
        self.assertEqual(first_journey_el, expected_condition)

        # Clears all fields in the search form
        form = self.selenium.find_element(By.ID, 'id_journey_form')
        for element in form.find_elements(By.XPATH, './/input'):
            element.clear()

        # Multi parameter search
        self.selenium.find_element(By.ID, 'id_calc_month').send_keys(
            '05/01/2021 - 07/01/2021')
        self.selenium.find_element(By.ID, 'id_min-distance').send_keys('1000')
        self.selenium.find_element(By.ID, 'id_max-distance').send_keys('5000')
        self.selenium.find_element(By.ID, 'id_min-duration').send_keys('500')
        self.selenium.find_element(By.ID, 'id_max-duration').send_keys('2000')

        time.sleep(2)
        self.selenium.find_element(
            By.XPATH, '/html/body/div/div[4]/button[2]').click()
        time.sleep(1)
        WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located((By.ID, "id_submit"))).click()

        search_results = WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located((By.ID, "search_matches")))
        self.assertEqual(search_results.text, "Your search matches 2 results")
        time.sleep(1)

        # Checks the search query after the multiparameter search. Regex excludes the HOST prefix.
        current_url_no_prefix = re.sub(
            r'^http://localhost:\d{1,}', '', self.selenium.current_url)
        expected_condition = '/journeys/search_journeys/?journey_dep_station=&journey_ret_station=&daterange=05%2F01%2F2021+-+07%2F01%2F2021&distance=1000&distance=5000&duration=500&duration=2000'
        self.assertEqual(current_url_no_prefix, expected_condition)

        # Checks for matches when the page is refreshed and "all" values are there
        WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located((By.ID, "id_submit"))).click()
        search_results = WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located((By.ID, "search_matches")))
        self.assertEqual(search_results.text, "Your search matches 19 results")

        # Finally orders all results by return station and asserts the first element
        self.selenium.find_element(
            By.XPATH, '//*[@id="order_by_ret_stat"]').click()
        expected_condition = '''<li class="column is-3-widescreen is-2-tablet is-mobile pr3 f6 f6-ns fw6 ">
            <i class="fa-solid fa-map"></i>&nbsp; <a href="#id_map" onclick="get_journey(2)">
            Testiasema 5 <i class="fa-solid fa-arrow-right-long w-10"></i> Testiasema 9
            </a>
        </li>
        <li class="column is-1-widescreen is-1-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="dep_time">May 31, 2021, 11:56 p.m.</li>
        <li class="column is-1-widescreen is-1-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="ret_time">June 1, 2021, 12:02 a.m.</li>
        <li class="column is-2-widescreen is-2-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="dep_stat">Testiasema 5</li>
        <li class="column is-2-widescreen is-2-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="ret_stat">Testiasema 9</li>
        <li class="column is-1-widescreen is-1-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="cov_dist">1400.00</li>
        <li class="column is-1-widescreen is-1-tablet is-mobile fw3 measure-narrow center ph1 pv1" name="duration">0:05:50</li>'''
        first_journey_el = self.selenium.find_element(
            By.NAME, 'journey').get_attribute('innerHTML').strip()
        self.assertEqual(first_journey_el, expected_condition)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
