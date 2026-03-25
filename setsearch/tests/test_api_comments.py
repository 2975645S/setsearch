from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus
import json

from setsearch.models import Artist, Concert, Venue, Comment


class CommentApiTest(TestCase):
    """Test cases for comment API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpass123'
        )
        self.other_user = get_user_model().objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.admin_user = get_user_model().objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='testpass123'
        )

        self.artist = Artist.objects.create(name='Test Artist')
        self.venue = Venue.objects.create(
            name='Test Venue',
            city='Test City'
        )
        self.concert = Concert.objects.create(
            artist=self.artist,
            venue=self.venue
        )

    def test_comment_create(self):
        self.client.login(username='regularuser', password='testpass123')

        comment_content = 'This was an amazing concert!'
        response = self.client.post(reverse('api_comment'), {'concert': self.concert.id, 'content': comment_content})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        comment = Comment.objects.get(user=self.user, concert=self.concert)
        self.assertEqual(comment.content, comment_content)

    def test_comment_create_unauthenticated(self):
        """Test unauthenticated POST returns 401."""
        comment_content = 'This was an amazing concert!'
        response = self.client.post(reverse('api_comment'), {'concert': self.concert.id, 'content': comment_content})
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_comment_delete_by_author(self):
        comment = Comment.objects.create(user=self.user, concert=self.concert, content='Test comment')
        self.client.login(username='regularuser', password='testpass123')

        response = self.client.delete(reverse('api_comment'), data=json.dumps({'id': comment.id}), content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_comment_delete_by_admin(self):
        """Test admin deleting any comment."""
        comment = Comment.objects.create(
            user=self.user,
            concert=self.concert,
            content='Test comment'
        )

        self.client.login(username='adminuser', password='testpass123')

        response = self.client.delete(
            reverse('api_comment'),
            data=json.dumps({'id': comment.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_comment_delete_by_other_user_forbidden(self):
        """Test regular user cannot delete others' comments."""
        comment = Comment.objects.create(
            user=self.user,
            concert=self.concert,
            content='Test comment'
        )

        self.client.login(username='otheruser', password='testpass123')

        response = self.client.delete(
            reverse('api_comment'),
            data=json.dumps({'id': comment.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=comment.id).exists())

    def test_comment_delete_not_logged_in(self):
        """Test deleting comment without authentication."""
        comment = Comment.objects.create(
            user=self.user,
            concert=self.concert,
            content='Test comment'
        )

        response = self.client.delete(
            reverse('api_comment'),
            data=json.dumps({'id': comment.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertTrue(Comment.objects.filter(id=comment.id).exists())

    def test_comment_invalid_method(self):
        """Test invalid HTTP method."""
        self.client.login(username='regularuser', password='testpass123')

        response = self.client.put(reverse('api_comment'))

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)