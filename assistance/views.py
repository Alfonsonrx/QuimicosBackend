from datetime import date, timedelta
from typing import override

from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from accounts.models import User
from accounts.permissions import IsAdminType
from assistance.serialiser import AssistanceSerializer, TodaySummarySerializer, WorkScheduleSerializer

from .models import AssistanceRecord, ReentryPermit, WorkSchedule

class AssistanceViewSet(viewsets.ModelViewSet):
    """
    Attendance records (ingreso / salida / falta_anticipada).

    Standard CRUD plus extra actions:
    - my-records: the requesting user's own records
    - today-status: the requesting user's marks today and which mark comes next
    - allow-reentry (admin): let a user mark ingreso again after a salida
    - today-summary (admin): today's status of every employee + weekly presence rate
    - reports/late, reports/early-exits, reports/absences (admin): per-employee reports (RE-01..03)
    Marking rules live in AssistanceSerializer.create.
    """

    queryset = AssistanceRecord.objects.select_related("user")
    permission_classes = [IsAuthenticated]

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
        if self.action in ("today_summary", "allow_reentry", "report_late", "report_early_exits", "report_absences"):
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

    # --- Reports (RE-01..03). The whole history by default; ?from= / ?to= optionally narrow it. ---

    def _report_range(self, request):
        today = timezone.localdate()
        try:
            start = date.fromisoformat(request.query_params["from"]) if "from" in request.query_params else None
            end = date.fromisoformat(request.query_params["to"]) if "to" in request.query_params else today
        except ValueError:
            raise ValidationError({"detail": "from/to must be dates in YYYY-MM-DD format."})
        if start is None:
            first = AssistanceRecord.objects.order_by("date").values_list("date", flat=True).first()
            start = first or today
        end = min(end, today)
        if start > end:
            raise ValidationError({"detail": "from must not be later than to."})
        return start, end

    def _report_response(self, days_by_user, start, end):
        """days_by_user: {user: [day dicts]} -> paginated list of employees sorted by name."""
        results = sorted(
            (
                {"user": u.id, "name": u.full_name, "position": u.position, "count": len(days), "days": days}
                for u, days in days_by_user.items() if days
            ),
            key=lambda r: r["name"],
        )
        page = self.paginate_queryset(results)
        response = self.get_paginated_response(page) if page is not None else Response({"results": results})
        response.data["from"] = start
        response.data["to"] = end
        return response

    def _employee_records(self, start, end, types):
        return (AssistanceRecord.objects.select_related("user")
                .filter(user__type=User.UserType.EMPLEADO, date__range=(start, end), type__in=types)
                .order_by("user_id", "date", "time", "id"))

    @action(detail=False, methods=["get"], url_path="reports/late")
    def report_late(self, request):
        """RE-01: first ingreso of the day later than the schedule's entry time (delay flag)."""
        start, end = self._report_range(request)
        days_by_user = {}
        for r in self._employee_records(start, end, [AssistanceRecord.AssistanceType.INGRESO]).filter(delay=True):
            days_by_user.setdefault(r.user, []).append({"date": r.date, "time": r.time})
        return self._report_response(days_by_user, start, end)

    @action(detail=False, methods=["get"], url_path="reports/early-exits")
    def report_early_exits(self, request):
        """RE-02: days whose last mark is a salida before the schedule's exit time.
        A salida followed by an authorized re-entry does not count."""
        AssistanceType = AssistanceRecord.AssistanceType
        start, end = self._report_range(request)
        last_mark = {}  # (user, date) -> last ingreso/salida of that day
        for r in self._employee_records(start, end, [AssistanceType.INGRESO, AssistanceType.SALIDA]):
            last_mark[(r.user, r.date)] = r
        days_by_user = {}
        for (user, _), r in last_mark.items():
            if r.type == AssistanceType.SALIDA and r.early_exit:
                days_by_user.setdefault(user, []).append({"date": r.date, "time": r.time})
        return self._report_response(days_by_user, start, end)

    @action(detail=False, methods=["get"], url_path="reports/absences")
    def report_absences(self, request):
        """RE-03: weekdays with neither ingreso nor salida, per active employee, since they were registered.
        A day covered by a falta_anticipada is listed as justified."""
        AssistanceType = AssistanceRecord.AssistanceType
        start, end = self._report_range(request)
        employees = User.objects.filter(is_active=True, type=User.UserType.EMPLEADO)

        records = AssistanceRecord.objects.filter(user__in=employees, date__range=(start, end))
        marked = set(records.filter(type__in=[AssistanceType.INGRESO, AssistanceType.SALIDA])
                     .values_list("user_id", "date"))
        justified = set(records.filter(type=AssistanceType.FALTA_ANTICIPADA).values_list("user_id", "date"))

        days_by_user = {}
        for emp in employees:
            day = max(start, timezone.localtime(emp.date_registered).date())
            days = []
            while day <= end:
                if day.weekday() < 5 and (emp.id, day) not in marked:
                    days.append({"date": day, "justified": (emp.id, day) in justified})
                day += timedelta(days=1)
            days_by_user[emp] = days
        return self._report_response(days_by_user, start, end)

    @action(detail=False, methods=["get"], url_path="today-summary")
    def today_summary(self, request):
        """
        Admin dashboard for today. Only active users of type empleado are counted.
        - Each employee is present (has an ingreso), else anticipated_absence
          (has a falta_anticipada), else absence.
        - weekly_rate: per weekday (Mon-Fri), % of employees with an ingreso on those days,
          from the first recorded date until today. A weekday not reached yet is None.
        """
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
