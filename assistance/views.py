from datetime import timedelta
from typing import override

from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from accounts.models import User
from accounts.permissions import IsAdminType
from assistance.serialiser import AssistanceSerializer, TodaySummarySerializer, WorkScheduleSerializer

from .models import AssistanceRecord, ReentryPermit, WorkSchedule

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

    queryset = AssistanceRecord.objects.select_related("user")
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
        if self.action in ("today_summary", "allow_reentry"):
            return [IsAuthenticated(), IsAdminType()]
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=["get"], url_path="today-status")
    def today_status(self, request):
        """Requesting user's marks for today and which mark comes next (null = done for the day)."""
        AssistanceType = AssistanceRecord.AssistanceType
        today = timezone.localdate()
        records = list(self.get_queryset().filter(user=request.user, date=today).order_by("time", "id"))
        marks = [r for r in records if r.type != AssistanceType.FALTA_ANTICIPADA]
        ingresos = [r.time for r in marks if r.type == AssistanceType.INGRESO]
        salidas = [r.time for r in marks if r.type == AssistanceType.SALIDA]

        last_type = marks[-1].type if marks else None
        if last_type is None:
            next_mark = AssistanceType.INGRESO
        elif last_type == AssistanceType.INGRESO:
            next_mark = AssistanceType.SALIDA
        elif ReentryPermit.objects.filter(user=request.user, date=today, used=False).exists():
            next_mark = AssistanceType.INGRESO
        else:
            next_mark = None

        return Response({
            "ingreso": ingresos[0] if ingresos else None,
            "salida": salidas[-1] if salidas else None,
            "next": next_mark,
            "records": self.get_serializer(records, many=True).data,
        })

    @action(detail=False, methods=["post"], url_path="allow-reentry")
    def allow_reentry(self, request):
        """Admin authorizes one extra ingreso today for a user whose last mark today is a salida."""
        AssistanceType = AssistanceRecord.AssistanceType
        user = get_object_or_404(User, pk=request.data.get("user"))
        today = timezone.localdate()
        last = (AssistanceRecord.objects.filter(user=user, date=today)
                .exclude(type=AssistanceType.FALTA_ANTICIPADA).order_by("time", "id").last())
        if last is None or last.type != AssistanceType.SALIDA:
            return Response({"user": ["User has no salida today to re-enter from."]}, status=status.HTTP_400_BAD_REQUEST)

        permit, created = ReentryPermit.objects.get_or_create(
            user=user, date=today, used=False, defaults={"granted_by": request.user}
        )
        return Response(
            {"id": permit.id, "user": user.id, "date": permit.date, "used": permit.used},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

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

            today_list.append({
                "name": emp.full_name,
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


class WorkScheduleView(APIView):
    """Company schedule: any authenticated user can read it, only administradores can change it."""

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminType()]

    def get(self, request):
        return Response(WorkScheduleSerializer(WorkSchedule.get()).data)

    def patch(self, request):
        serializer = WorkScheduleSerializer(WorkSchedule.get(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
