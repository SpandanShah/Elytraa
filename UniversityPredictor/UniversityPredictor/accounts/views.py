"""
accounts/views.py

Auth API endpoints using Django's built-in auth + session.

POST /api/auth/register/  — create account, auto-login
POST /api/auth/login/     — login
POST /api/auth/logout/    — logout
GET  /api/auth/status/    — check if logged in
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_token(request):
    """Return a CSRF token so the frontend can include it in POST requests."""
    return Response({"csrfToken": get_token(request)})


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")
    confirm = request.data.get("confirm_password", "")

    if not email or not password:
        return Response(
            {"success": False, "error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) < 8:
        return Response(
            {"success": False,
             "error": "Password must be at least 8 characters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != confirm:
        return Response(
            {"success": False, "error": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"success": False,
             "error": "An account with this email already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Use email as username (truncated to 150 chars, Django's limit)
    username = email[:150]
    user = User.objects.create_user(
        username=username, email=email, password=password
    )
    login(request, user)
    return Response(
        {"success": True, "email": user.email},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    if not email or not password:
        return Response(
            {"success": False, "error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Authenticate by username (which we set to email on register)
    user = authenticate(request, username=email[:150], password=password)
    if user is None:
        return Response(
            {"success": False, "error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    login(request, user)
    return Response({"success": True, "email": user.email})


@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_status(request):
    if request.user.is_authenticated:
        return Response({"authenticated": True, "email": request.user.email})
    return Response({"authenticated": False})
