from .views import load_csvimport_page
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse, resolve

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
        url = reverse('csvimport:csvimport')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_csvimport_page)
        self.assertEqual(response.status_code, 200)
        # log in a user
        # send a GET request to the view
        response = self.client.get(reverse('core:index'))
        # check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Index Page</h1>')