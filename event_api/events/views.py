from django.shortcuts import render
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedOrPublic


class EventViewSet(viewsets.ModelViewSet):
    """
    Event CRUD:
    POST /events/        (auth)
    GET /events/         list public events (pagination)
    GET /events/{id}/    detail
    PUT /events/{id}/    update (organizer only)
    DELETE /events/{id}/ delete (organizer only)
    """

    queryset = Event.objects.all().select_related("organizer")
    serializer_class = EventSerializer
    filterset_fields = ["location", "is_public"]
    search_fields = ["title", "location", "organizer__username"]
    filter_backends = [filters.SearchFilter]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            # read: check public / invited in has_object_permission
            permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsInvitedOrPublic]
        else:
            permission_classes = [
                permissions.IsAuthenticated,
                IsOrganizerOrReadOnly,
                IsInvitedOrPublic,
            ]
        return [p() for p in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Only show public events OR ones organized/invited if private
        if user.is_authenticated:
            return qs.filter(
                models.Q(is_public=True)
                | models.Q(organizer=user)
                | models.Q(invited_users=user)
            ).distinct()
        return qs.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    # ---------- RSVP ACTION ----------
    @action(detail=True, methods=["post"], url_path="rsvp", url_name="rsvp")
    def rsvp(self, request, pk=None):
        """
        POST /events/{event_id}/rsvp/  (authenticated)
        """
        event = self.get_object()
        serializer = RSVPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rsvp, created = RSVP.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={"status": serializer.validated_data["status"]},
        )
        out = RSVPSerializer(rsvp)
        return Response(out.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    # ---------- REVIEWS ----------
    @action(detail=True, methods=["get", "post"], url_path="reviews", url_name="reviews")
    def reviews(self, request, pk=None):
        """
        GET  /events/{event_id}/reviews/
        POST /events/{event_id}/reviews/
        """
        event = self.get_object()

        if request.method == "GET":
            reviews = event.reviews.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)

        # POST
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review, created = Review.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={
                "rating": serializer.validated_data["rating"],
                "comment": serializer.validated_data.get("comment", ""),
            },
        )
        out = ReviewSerializer(review)
        return Response(out.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RSVPUpdateView(APIView):
    """
    PATCH /events/{event_id}/rsvp/{user_id}/
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, event_id, user_id):
        event = get_object_or_404(Event, id=event_id)
        user = get_object_or_404(User, id=user_id)
        rsvp = get_object_or_404(RSVP, event=event, user=user)

        serializer = RSVPSerializer(rsvp, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
