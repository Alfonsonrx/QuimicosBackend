from django.shortcuts import render
from jwt import decode
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import time

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import *
from .permissions import IsAdminType
# Create your views here.

class CustomCreateView(APIView):
  permission_classes = [IsAuthenticated, IsAdminType] # Permissions needed to register a new profile, being authenticated

  def post(self, request, *args, **kwargs):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({'message': 'Registration successful.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
