from rest_framework import permissions
from rest_framework.authentication import BasicAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import FieldDoesNotExist
from config import settings
from .custom_jwt import jwt_decode_handler
from member.models import Member


class IsOwnerOrReadOnly(permissions.BasePermission):
  """
  Object-level permission to only allow owners of an object to edit it.
  Assumes the model instance has an `owner` attribute.
  """

  def has_object_permission(self, request, view, obj):
    return obj.owner == request.member



class AllowAny(permissions.BasePermission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(self, request, view):
        return True


class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated members.
    """

    def has_permission(self, request, view):
        member = request.user
        print(f"has_permission2 {member}")
        
        if bool(member and member.is_authenticated):
            return True
        return False


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin members.
    """

    def has_permission(self, request, view):
        if request.user is None:
            return False

        try:
            exist_is_superuser = request.user._meta.get_field('is_superuser')
            if exist_is_superuser:
              return True
        except FieldDoesNotExist:
            return False

        return False
