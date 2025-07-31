from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Staff, CheckIn, Winner, EventSettings
from io import BytesIO
from PIL import Image
import tempfile

class LuckyDrawTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_username = 'hr_admin'
        self.admin_password = 'staff_party_2024'
        self.user = User.objects.create_user(username=self.admin_username, password=self.admin_password, is_staff=True, is_superuser=True)
        self.event_settings = EventSettings.objects.create(day1_date='2025-07-29', day2_date='2025-07-30')
        # Create staff
        self.staff1 = Staff.objects.create(name='John Doe', department='FB', day_1=1)
        self.staff2 = Staff.objects.create(name='Jane Smith', department='Front Office', day_1=1)
        self.staff3 = Staff.objects.create(name='Mike Johnson', department='Housekeeping', day_1=2)
        self.staff4 = Staff.objects.create(name='Lisa Davis', department='HR', day_1=1)
        self.staff5 = Staff.objects.create(name='Emma Thompson', department='Marketing', day_1=1)
        self.staff6 = Staff.objects.create(name='Tom Wilson', department='IT', day_1=2)

    def login(self):
        return self.client.post(reverse('login'), {'username': self.admin_username, 'password': self.admin_password})

    def test_login_logout(self):
        response = self.login()
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_access(self):
        self.login()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Download QR Codes')

    def test_upload_staff(self):
        self.login()
        csv_content = b"Name,Department,Day\nTest User,Test Dept,1\n"
        file = BytesIO(csv_content)
        file.name = 'test.csv'
        response = self.client.post(reverse('upload_staff'), {'file': file}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Staff.objects.filter(name='Test User').exists())

    def test_download_qr_with_label(self):
        self.login()
        url = reverse('download_qr_with_label', args=[self.staff1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        # FileResponse uses streaming_content, not content
        img_bytes = b''.join(response.streaming_content)
        img = Image.open(BytesIO(img_bytes))
        self.assertEqual(img.format, 'PNG')

    def test_checkin_and_draw_winner(self):
        self.login()
        # Check in 5 unique staff for day 1
        staff_for_day1 = list(Staff.objects.filter(day_1=1)[:5])
        # If less than 5, create more
        while len(staff_for_day1) < 5:
            staff_for_day1.append(Staff.objects.create(name=f'Extra Staff {len(staff_for_day1)}', department='Extra', day_1=1))
        for staff in staff_for_day1:
            CheckIn.objects.create(staff=staff, day=1)
        # Draw winners up to 5
        for i in range(5):
            response = self.client.post(reverse('draw_winner'), data='{"day":1}', content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertIn('winner_name', response.json())
        # 6th draw should fail
        response = self.client.post(reverse('draw_winner'), data='{"day":1}', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])

    def test_clear_database(self):
        self.login()
        response = self.client.post(reverse('clear_database'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Staff.objects.count(), 0)
        self.assertEqual(CheckIn.objects.count(), 0)
        self.assertEqual(Winner.objects.count(), 0)
