from django.urls import path

from .views import *

urlpatterns = [
    path('registration/', CustomCreateView.as_view(), name='register'),
]
