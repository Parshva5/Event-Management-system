from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Event
from django.utils import timezone
from datetime import timedelta


class EventAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        # get JWT token
        resp = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        self.token = resp.data["access"]
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    def test_create_event(self):
        url = reverse("event-list")
        data = {
            "title": "Interview Demo Event",
            "description": "Test description",
            "location": "Online",
            "start_time": timezone.now(),
            "end_time": timezone.now() + timedelta(hours=1),
            "is_public": True,
        }
        resp = self.client.post(url, data, format="json", **self.auth_headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().organizer, self.user)

    def test_list_public_events_without_auth(self):
        Event.objects.create(
            organizer=self.user,
            title="Public",
            description="",
            location="X",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            is_public=True,
        )
        url = reverse("event-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)
