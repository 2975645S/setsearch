import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from setsearch.models import Artist, Concert, Venue


class ConcertModelTest(TestCase):
    """Test cases for the Concert model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.artist = Artist.objects.create(name='Test Artist')
        self.venue = Venue.objects.create(name='Test Venue', city='Test City', address='123 Test St')

    def test_concert_creation_basic(self):
        concert = Concert.objects.create(artist=self.artist, venue=self.venue)
        self.assertEqual(concert.name, 'Test Artist at Test Venue')

    def test_concert_date_precision_day(self):
        concert = Concert.objects.create(artist=self.artist, venue=self.venue)
        concert.set_date(year=2023, month=6, day=15)
        concert.save()

        self.assertEqual(concert.date, datetime.date(2023, 6, 15))
        self.assertEqual(concert.precision, Concert.DatePrecision.DAY)

    def test_concert_name_generation_with_date(self):
        concert = Concert(artist=self.artist, venue=self.venue)
        concert.set_date(year=2023, month=6, day=15)
        concert.save()
        self.assertEqual(concert.name, 'Test Artist at Test Venue on 15-06-2023')

    def test_concert_validation_date_required_for_precision(self):
        concert = Concert(artist=self.artist, venue=self.venue, precision=Concert.DatePrecision.YEAR)
        with self.assertRaises(ValidationError):
            concert.full_clean()