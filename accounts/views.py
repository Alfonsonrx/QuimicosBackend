from django.shortcuts import render
from jwt import decode
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
import time

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import *
from .permissions import IsAdminType
# Create your views here.

class CustomCreateView(APIView):
  permission_classes = [IsAuthenticated, IsAdminType] # Permissions needed to register a new profile, being authenticated

  def post(self, request, *args, **kwargs):
    serializer = UserCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
      user = serializer.save()
      return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
  # Creation stays in CustomCreateView (registration/)
  queryset = User.objects.all().order_by('id')
  serializer_class = UserSerializer
  permission_classes = [IsAuthenticated, IsAdminType]

  def perform_destroy(self, instance):
    # Soft delete: AssistanceRecord.user is CASCADE, a hard delete would wipe the user's history
    instance.is_active = False
    instance.save(update_fields=['is_active'])

  @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
  def me(self, request):
    return Response(SelfUserSerializer(request.user).data)
