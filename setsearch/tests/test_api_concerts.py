from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus

from setsearch.models import Artist, Concert, Venue


class ConcertAttendApiTest(TestCase):
    """Test cases for concert attendance API."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpass123'
        )
        self.artist = Artist.objects.create(name='Test Artist')
        self.venue = Venue.objects.create(name='Test Venue', city='Test City')
        self.concert = Concert.objects.create(artist=self.artist, venue=self.venue)

    def test_concert_attend_toggle_on(self):
        self.client.login(username='regularuser', password='testpass123')

        response = self.client.post(reverse('api_concert_attend'), {'concert': self.concert.id})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()['attending'])

        from setsearch.models import Attendance
        self.assertTrue(Attendance.objects.filter(user=self.user, concert=self.concert).exists())

    def test_concert_attend_toggle_off(self):
        """Test toggling attendance off by attending twice."""
        from setsearch.models import Attendance
        self.client.login(username='regularuser', password='testpass123')

        # First attend
        response = self.client.post(reverse('api_concert_attend'), {'concert': self.concert.id})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()['attending'])
        self.assertTrue(Attendance.objects.filter(user=self.user, concert=self.concert).exists())

        # Second attend (toggle off)
        response = self.client.post(reverse('api_concert_attend'), {'concert': self.concert.id})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(response.json()['attending'])
        self.assertFalse(Attendance.objects.filter(user=self.user, concert=self.concert).exists())

    def test_concert_attend_unauthenticated(self):
        """Test unauthenticated user cannot attend."""
        response = self.client.post(reverse('api_concert_attend'), {'concert': self.concert.id})
        self.assertIn(response.status_code, [HTTPStatus.UNAUTHORIZED, HTTPStatus.FOUND])  # 401 or 302


class ConcertRateApiTest(TestCase):
    """Test cases for concert rating API."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpass123'
        )
        self.artist = Artist.objects.create(name='Test Artist')
        self.venue = Venue.objects.create(name='Test Venue', city='Test City')
        self.concert = Concert.objects.create(artist=self.artist, venue=self.venue)

    def test_concert_rate_success(self):
        from setsearch.models import Attendance
        Attendance.objects.create(user=self.user, concert=self.concert)

        self.client.login(username='regularuser', password='testpass123')
        response = self.client.post(reverse('api_concert_rate'), {'concert': self.concert.id, 'rating': 4})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        attendance = Attendance.objects.get(user=self.user, concert=self.concert)
        self.assertEqual(attendance.rating, 4)

    def test_concert_rate_invalid_value(self):
        """Test invalid rating values return error."""
        from setsearch.models import Attendance
        Attendance.objects.create(user=self.user, concert=self.concert)

        self.client.login(username='regularuser', password='testpass123')

        # Test invalid high rating
        response = self.client.post(reverse('api_concert_rate'), {'concert': self.concert.id, 'rating': 99})
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

        # Test invalid low rating
        response = self.client.post(reverse('api_concert_rate'), {'concert': self.concert.id, 'rating': -1})
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_concert_rate_without_attendance(self):
        """Test rating without attendance record is forbidden."""
        self.client.login(username='regularuser', password='testpass123')
        response = self.client.post(reverse('api_concert_rate'), {'concert': self.concert.id, 'rating': 4})
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)