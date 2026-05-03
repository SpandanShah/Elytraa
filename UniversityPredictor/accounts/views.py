"""
accounts/views.py

Auth API endpoints using Django's built-in auth + session.

POST /api/auth/register/  — create account, auto-login
POST /api/auth/login/     — login
POST /api/auth/logout/    — logout
GET  /api/auth/status/    — check if logged in
GET  /api/auth/google/login/    — initiate Google OAuth flow
GET  /api/auth/google/callback/ — handle Google OAuth callback
"""

import logging
import secrets
import traceback

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.google_oauth import (
    GoogleOAuthError,
    build_authorization_url,
    exchange_code_for_tokens,
    fetch_google_userinfo,
    find_or_create_user,
    get_google_config,
)
from accounts.models import PredictionLog

logger = logging.getLogger(__name__)


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


@api_view(["GET"])
@permission_classes([AllowAny])
def google_login(request):
    """Initiate the Google OAuth 2.0 flow.

    Generates a random state token for CSRF protection, stores it in the
    session, and redirects the user to Google's consent screen.

    Returns HTTP 503 if Google OAuth is not configured.
    """
    config = get_google_config()
    if config is None:
        return Response(
            {"error": "Google sign-in is not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state

    authorization_url = build_authorization_url(state)
    return HttpResponseRedirect(authorization_url)


@api_view(["GET"])
@permission_classes([AllowAny])
def google_callback(request):
    """Handle the Google OAuth 2.0 callback.

    GET /api/auth/google/callback/?code=...&state=...

    Validates the state parameter, exchanges the authorization code for
    tokens, fetches the user's Google profile, finds or creates the
    corresponding Django user, logs them in, and redirects to the
    frontend.

    On any error, redirects to /?google_auth_error=<message>.
    """
    try:
        # 1. Validate state parameter against session value
        session_state = request.session.get("google_oauth_state")
        request_state = request.GET.get("state")

        if not session_state or not request_state or session_state != request_state:
            return HttpResponseRedirect("/?google_auth_error=Invalid+request")

        # 2. Handle user-denied consent (Google sends ?error=access_denied)
        if request.GET.get("error"):
            return HttpResponseRedirect("/?google_auth_error=Access+denied")

        # 3. Exchange authorization code for tokens
        code = request.GET.get("code", "")
        tokens = exchange_code_for_tokens(code)

        # 4. Fetch user profile from Google
        access_token = tokens.get("access_token", "")
        userinfo = fetch_google_userinfo(access_token)

        # 5. Reject unverified email addresses
        if not userinfo.get("email_verified", False):
            return HttpResponseRedirect(
                "/?google_auth_error=Email+not+verified"
            )

        # 6. Find or create the Django user
        user = find_or_create_user(userinfo)

        # 7. Log the user in
        login(request, user)

        # 8. Redirect to frontend success URL
        return HttpResponseRedirect("/?google_auth=success")

    except GoogleOAuthError as exc:
        logger.error("Google OAuth error during callback: %s", exc)
        return HttpResponseRedirect(
            "/?google_auth_error=Authentication+failed"
        )

    except Exception:
        logger.error(
            "Unexpected error during Google OAuth callback:\n%s",
            traceback.format_exc(),
        )
        return HttpResponseRedirect(
            "/?google_auth_error=Authentication+failed"
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def access_info(request):
    """Return the current user's access tier flags and daily usage.

    GET /api/auth/access/

    Requires authentication. Returns 403 for unauthenticated requests
    (handled by the custom_exception_handler in predictor/views.py).
    """
    profile = request.user.profile
    predictions_used_today = PredictionLog.count_today(request.user)

    return Response({
        "can_access_round2": profile.can_access_round2,
        "can_access_round3": profile.can_access_round3,
        "can_access_jee": profile.can_access_jee,
        "daily_prediction_limit": profile.daily_prediction_limit,
        "predictions_used_today": predictions_used_today,
    })
