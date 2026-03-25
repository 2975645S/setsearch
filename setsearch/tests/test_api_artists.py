from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus

from setsearch.models import Artist


class ArtistApiTest(TestCase):
    """Test cases for artist API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = get_user_model().objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='testpass123'
        )
        self.regular_user = get_user_model().objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpass123'
        )
        self.target_user = get_user_model().objects.create_user(
            username='targetuser',
            email='target@example.com',
            password='testpass123'
        )

        self.artist = Artist.objects.create(name='Test Artist')
        self.artist_with_user = Artist.objects.create(
            name='Artist With User',
            user=self.target_user
        )

    def test_artist_list(self):
        """Test getting list of all artists."""
        response = self.client.get(reverse('api_artist_list'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        # Should contain both artists
        self.assertEqual(len(data), 2)
        artist_names = [artist['name'] for artist in data]
        self.assertIn('Test Artist', artist_names)
        self.assertIn('Artist With User', artist_names)

        # Each artist should have name and slug
        for artist in data:
            self.assertIn('name', artist)
            self.assertIn('slug', artist)

