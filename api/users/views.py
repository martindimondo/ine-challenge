"""
    Users views
"""
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .permissions import (
    IsStaff,
    StaffDeleteNoStaff,
    IsAdmin,
    PermissionsIsolatedMixin,
)
from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserDetailedSerializer,
    StaffUserUpdateSerializer,
    NonStaffUserUpdateSerializer,
)


# pylint: disable=R0901
class UserViewSet(PermissionsIsolatedMixin, viewsets.ModelViewSet):
    """
    User api viewset
    """

    queryset = User.objects

    def get_serializer_class(self):
        user = self.request.user

        if self.action == "create":
            serializer = UserCreateSerializer
        elif self.action == "retrieve":
            if user.is_staff or self.kwargs.get("pk") == str(user.id):
                serializer = UserDetailedSerializer
            else:
                serializer = UserSerializer
        elif self.action in ("partial_update", "update"):
            if user.is_staff:
                serializer = StaffUserUpdateSerializer
            else:
                serializer = NonStaffUserUpdateSerializer
        else:
            serializer = None
        return serializer

    def list(self, *args, **kwargs):
        raise Http404

    @permission_classes((StaffDeleteNoStaff | IsAdmin,))
    def destroy(self, *args, **kwargs):
        return super().destroy(*args, **kwargs)

    @permission_classes((IsAuthenticated,))
    def update(self, request, *args, **kwargs):
        return self._update_user(request, *args, **kwargs)

    @permission_classes((IsAuthenticated,))
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self._update_user(request, *args, **kwargs)

    def _update_user(self, request, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_serialized = UserDetailedSerializer(
            instance=serializer.instance
        )
        return Response(response_serialized.data, status.HTTP_200_OK)

    @permission_classes((IsStaff,))
    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_serialized = UserDetailedSerializer(
            instance=serializer.instance
        )

        return Response(response_serialized.data, status.HTTP_201_CREATED)
