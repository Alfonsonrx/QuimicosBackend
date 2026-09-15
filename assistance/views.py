from datetime import timedelta
from typing import override

from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsAdminType
from assistance.serialiser import AssistanceSerializer, TodaySummarySerializer

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

    @action(detail=False, methods=["get"], url_path="my-records")
    def my_records(self, request):
        """Return assistance records belonging to the requesting user."""
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action == "today_summary":
            return [IsAuthenticated(), IsAdminType()]
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=["get"], url_path="today-summary")
    def today_summary(self, request):
        AssistanceType = AssistanceRecord.AssistanceType
        today = timezone.localdate()

        employees = User.objects.filter(is_active=True, type=User.UserType.EMPLEADO)
        employee_ids = set(employees.values_list("id", flat=True))

        # --- Today's classification ---
        today_types_by_user = {}
        for uid, t in AssistanceRecord.objects.filter(
            date=today, user_id__in=employee_ids
        ).values_list("user_id", "type"):
            today_types_by_user.setdefault(uid, set()).add(t)

        counts = {"present": 0, "absence": 0, "anticipated_absence": 0}
        today_list = []
        for emp in employees:
            types = today_types_by_user.get(emp.id, set())
            if AssistanceType.INGRESO in types:
                record_type = "present"
            elif AssistanceType.FALTA_ANTICIPADA in types:
                record_type = "anticipated_absence"
            else:
                record_type = "absence"
            counts[record_type] += 1

            name_parts = [emp.name, emp.first_lastname]
            if emp.second_lastname:
                name_parts.append(emp.second_lastname)
            today_list.append({
                "name": " ".join(name_parts),
                "position": emp.position,
                "record_type": record_type,
            })

        # --- Historical weekly rate (presence %) ---
        history = AssistanceRecord.objects.filter(user_id__in=employee_ids, type__in=[AssistanceType.INGRESO, AssistanceType.FALTA_ANTICIPADA], ).values_list("user_id", "date", "type").distinct()

        ingreso_pairs = set()
        candidate_dates = []
        for uid, day, t in history:
            candidate_dates.append(day)
            if t == AssistanceType.INGRESO:
                ingreso_pairs.add((uid, day))
        earliest = min(candidate_dates) if candidate_dates else None

        weekday_names = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        totals = {name: 0 for name in weekday_names}
        present = {name: 0 for name in weekday_names}

        if earliest is not None:
            current = earliest
            while current <= today:
                if current.weekday() < 5:  # skip Sat/Sun
                    day_name = weekday_names[current.weekday()]
                    for uid in employee_ids:
                        totals[day_name] += 1
                        if (uid, current) in ingreso_pairs:
                            present[day_name] += 1
                current += timedelta(days=1)

        weekly_rate = {
            name: round((present[name] / totals[name]) * 100, 2) if totals[name] > 0 else None
            for name in weekday_names
        }

        serializer = TodaySummarySerializer({
            "todays_records": counts,
            "today_list": today_list,
            "weekly_rate": weekly_rate,
        })
        return Response(serializer.data)
