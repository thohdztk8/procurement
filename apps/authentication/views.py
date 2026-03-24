from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Department, Role, User
from .serializers import (
    DepartmentSerializer, RoleSerializer, UserListSerializer,
    UserCreateSerializer, UserUpdateSerializer,
    LoginSerializer, ChangePasswordSerializer,
)
from .permissions import IsAdmin


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.last_login_at = timezone.now()
        user.save(update_fields=["last_login_at"])
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserListSerializer(user).data,
            "must_change_pass": user.must_change_pass,
        })


class LogoutView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
        except Exception:
            pass
        return Response({"detail": "Đăng xuất thành công."})


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserListSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserListSerializer


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Đổi mật khẩu thành công."})


# ── Admin: User Management ──────────────────────────────────

class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    queryset = User.objects.select_related("role", "department").all()
    search_fields = ["full_name", "email"]
    filterset_fields = ["role", "department", "is_active"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserListSerializer

    def perform_create(self, serializer):
        serializer.save()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    queryset = User.objects.select_related("role", "department").all()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserListSerializer

    def destroy(self, request, *args, **kwargs):
        # Soft delete — deactivate instead
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response({"detail": "Tài khoản đã bị vô hiệu hóa."}, status=status.HTTP_200_OK)


class DepartmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class RoleListView(generics.ListAPIView):
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
