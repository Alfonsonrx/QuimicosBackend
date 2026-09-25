from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AssistanceViewSet, WorkScheduleView

app_name = 'assistances'

router = DefaultRouter()
router.register(r'assistances', AssistanceViewSet)

urlpatterns = router.urls + [
    path('schedule/', WorkScheduleView.as_view(), name='schedule'),
]
