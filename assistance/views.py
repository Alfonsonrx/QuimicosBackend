from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from assistance.serialiser import AssistanceSerializer

from .models import AssistanceRecord

# Create your views here.

class AssistanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Appointment CRUD operations.
    Requires active subscription with appointments feature (AppointmentsFeatureAccess).

    Supports filtering by:
    - status
    - appointment_type
    - customer
    - project
    - is_virtual
    - month (start_datetime month)
    - year (start_datetime year)
    - organizer

    Supports searching by:
    - title
    - description
    - location

    Supports ordering by:
    - start_datetime
    - end_datetime
    - created_at
    - updated_at
    """

    queryset = AssistanceRecord.objects.all()
    permission_classes = [IsAuthenticated]
    # required_permissions = {
    #     "list": "appointments:view",
    #     "retrieve": "appointments:view",
    #     "create": "appointments:create",
    #     "update": "appointments:edit",
    #     "partial_update": "appointments:edit",
    #     "destroy": "appointments:delete",
    #     "calendar": "appointments:view",
    #     "my_appointments": "appointments:view",
    # }
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = AppointmentFilter
    # search_fields = ["title", "description", "location"]
    # ordering_fields = ["start_datetime", "end_datetime", "created_at", "updated_at"]
    # ordering = ["start_datetime"]

    def get_serializer_class(self):
        return AssistanceSerializer

    @action(detail=False, methods=["get"])
    def my_appointments(self, request):
        """Return appointments where user is organizer OR attendee."""
        user = request.user
        queryset = self.filter_queryset(
            self.get_queryset()
            .filter(Q(organizer=user) | Q(attendees__user=user))
            .distinct()
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
