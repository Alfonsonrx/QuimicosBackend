from rest_framework.routers import DefaultRouter
from .views import AssistanceViewSet

app_name = 'assistances'

router = DefaultRouter()
router.register(r'assistances', AssistanceViewSet)

urlpatterns = router.urls
