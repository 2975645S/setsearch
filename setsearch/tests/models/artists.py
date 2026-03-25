from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from setsearch.models import Artist


class ArtistModelTest(TestCase):
    """Test cases for the Artist model."""

    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_artist_creation(self):
        """Test creating an Artist instance."""
        artist = Artist.objects.create(
            name='Test Artist',
            mbid='12345678-1234-1234-1234-123456789012'
        )
        self.assertEqual(artist.name, 'Test Artist')
        self.assertEqual(artist.mbid, '12345678-1234-1234-1234-123456789012')
        self.assertIsNotNone(artist.slug)

    def test_slug_generation(self):
        """Test that slug is generated from name on save."""
        artist = Artist(name='Test Artist Name')
        artist.save()
        self.assertEqual(artist.slug, 'test-artist-name')

    def test_slug_uniqueness(self):
        """Test that slugs are made unique when duplicates exist."""
        # Create first artist
        artist1 = Artist.objects.create(name='Test Artist')
        self.assertEqual(artist1.slug, 'test-artist')

        # Create second artist with same name
        artist2 = Artist.objects.create(name='Test Artist')
        self.assertEqual(artist2.slug, 'test-artist-1')

        # Create third artist with same name
        artist3 = Artist.objects.create(name='Test Artist')
        self.assertEqual(artist3.slug, 'test-artist-2')

    def test_artist_with_user(self):
        """Test creating an Artist linked to a User."""
        artist = Artist.objects.create(
            name='User Artist',
            user=self.user
        )
        self.assertEqual(artist.name, 'User Artist')
        self.assertEqual(artist.user, self.user)

    def test_artist_mbid_unique(self):
        """Test that MBID must be unique."""
        # Create first artist with MBID
        Artist.objects.create(
            name='Artist 1',
            mbid='12345678-1234-1234-1234-123456789012'
        )
        # Attempt to create second artist with same MBID should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Artist.objects.create(
                name='Artist 2',
                mbid='12345678-1234-1234-1234-123456789012'
            )

