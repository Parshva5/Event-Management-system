from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EventViewSet, RSVPUpdateView

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")

urlpatterns = [
    # Event CRUD + nested /events/{id}/rsvp/ & /events/{id}/reviews/
    path("", include(router.urls)),

    # PATCH /events/{event_id}/rsvp/{user_id}/
    path(
        "events/<int:event_id>/rsvp/<int:user_id>/",
        RSVPUpdateView.as_view(),
        name="rsvp-update",
    ),
]
