from rest_framework.permissions import BasePermission
from accounts.models import User


def is_admin_type(user):
  return bool(user and user.is_authenticated and getattr(user, "type", None) == User.UserType.ADMIN)


class IsAdminType(BasePermission):
  message = "Only administrador-type users may access this resource."

  def has_permission(self, request, view):
    return is_admin_type(request.user)