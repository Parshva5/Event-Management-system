from rest_framework import permissions
from .models import Event


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Only organizer can update or delete the event.
    """

    def has_object_permission(self, request, view, obj: Event):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user


class IsInvitedOrPublic(permissions.BasePermission):
    """
    Private events (is_public=False) visible only to organizer or invited users.
    """

    def has_object_permission(self, request, view, obj: Event):
        # safe method visibility rule
        if obj.is_public:
            return True
        if not request.user.is_authenticated:
            return False
        return (
            obj.organizer == request.user
            or request.user in obj.invited_users.all()
        )
