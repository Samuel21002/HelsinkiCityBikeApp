from .views import load_index_page
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse, resolve

# Create your tests here.
class CoreTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super(CoreTests, cls).setUpTestData()
        cls.client = Client()
        cls.user = User.objects.create_user('testuser', 'test@gmail.com', 'testpass')

    def test_login_and_index_page(self):
        """ Tests the index page, whether the correct view is returned and whether the index-page has the right content """
      
        self.client.login(username='testuser', password='testpass')
        url = reverse('core:index')
        response = self.client.get(url)
        self.assertEqual(resolve(url).func, load_index_page)
        self.assertContains(response, '<h1>Index Page</h1>')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """ Tests whether the user has access to any pages after logging out and to what page user will be redirected to """
        
        self.client.logout()
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/')
