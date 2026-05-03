"""
accounts/google_oauth.py

Google OAuth 2.0 configuration helpers and URL construction.

Provides:
- GoogleOAuthError: custom exception for OAuth flow failures
- get_google_config(): reads Google credentials from Django settings
- build_authorization_url(state): constructs the Google consent URL
- exchange_code_for_tokens(code): exchanges auth code for tokens
- fetch_google_userinfo(access_token): fetches user profile from Google
- find_or_create_user(google_userinfo): resolves or creates a Django User
  from Google identity
"""

import logging
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth.models import User

from accounts.models import GoogleOAuthLink

logger = logging.getLogger(__name__)

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_SCOPES = "openid email profile"


class GoogleOAuthError(Exception):
    """Raised when any step of the Google OAuth flow fails."""
    pass


def get_google_config() -> dict | None:
    """
    Returns Google OAuth config dict or None if credentials are missing.

    Reads GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI
    from Django settings. If client_id or client_secret is empty, logs a
    warning and returns None.

    Returns:
        dict with keys: client_id, client_secret, redirect_uri
        None if credentials are not configured
    """
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
    redirect_uri = getattr(
        settings,
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/api/auth/google/callback/",
    )

    if not client_id or not client_secret:
        logger.warning(
            "Google OAuth credentials are missing. "
            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file "
            "to enable Google sign-in."
        )
        return None

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }


def build_authorization_url(state: str) -> str:
    """
    Builds the Google OAuth consent URL with required parameters.

    Args:
        state: Random string for CSRF protection, stored in the session.

    Returns:
        Full Google authorization URL with query parameters.

    Raises:
        GoogleOAuthError: If Google OAuth is not configured.
    """
    config = get_google_config()
    if config is None:
        raise GoogleOAuthError("Google OAuth is not configured.")

    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": GOOGLE_SCOPES,
        "state": state,
    }

    return f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"


def exchange_code_for_tokens(code: str) -> dict:
    """
    Exchanges an authorization code for tokens via Google's token endpoint.

    Posts the authorization code along with client credentials to Google's
    token endpoint and returns the parsed JSON response containing
    access_token, id_token, etc.

    Args:
        code: The authorization code received from Google's callback.

    Returns:
        dict with keys like access_token, id_token, token_type, expires_in.

    Raises:
        GoogleOAuthError: If the config is missing, the request fails,
            or Google returns a non-200 response.
    """
    config = get_google_config()
    if config is None:
        raise GoogleOAuthError("Google OAuth is not configured.")

    payload = {
        "code": code,
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "redirect_uri": config["redirect_uri"],
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(
            GOOGLE_TOKEN_ENDPOINT, data=payload, timeout=10
        )
    except requests.RequestException as exc:
        logger.error("Token exchange request failed: %s", exc)
        raise GoogleOAuthError(
            "Failed to connect to Google token endpoint."
        ) from exc

    if response.status_code != 200:
        logger.error(
            "Token exchange returned %s: %s",
            response.status_code,
            response.text,
        )
        raise GoogleOAuthError("Token exchange failed.")

    return response.json()


def fetch_google_userinfo(access_token: str) -> dict:
    """
    Fetches the authenticated user's profile from Google's userinfo endpoint.

    Args:
        access_token: A valid Google OAuth 2.0 access token.

    Returns:
        dict with keys like sub, email, name, picture, email_verified.

    Raises:
        GoogleOAuthError: If the request fails or Google returns a
            non-200 response.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(
            GOOGLE_USERINFO_ENDPOINT, headers=headers, timeout=10
        )
    except requests.RequestException as exc:
        logger.error("Userinfo request failed: %s", exc)
        raise GoogleOAuthError(
            "Failed to connect to Google userinfo endpoint."
        ) from exc

    if response.status_code != 200:
        logger.error(
            "Userinfo request returned %s: %s",
            response.status_code,
            response.text,
        )
        raise GoogleOAuthError("Failed to fetch Google user info.")

    return response.json()


def find_or_create_user(google_userinfo: dict) -> User:
    """
    Resolves or creates a Django User from Google identity information.

    Given Google userinfo (sub, email, name):
    1. If a GoogleOAuthLink exists for this sub → return the linked user
    2. If a User with this email exists → create a GoogleOAuthLink and
       return the user
    3. Otherwise → create a new User (unusable password) +
       GoogleOAuthLink and return the user

    Args:
        google_userinfo: dict with keys 'sub', 'email', 'name' from Google's
            userinfo endpoint.

    Returns:
        The Django User instance associated with this Google identity.
    """
    sub = google_userinfo["sub"]
    email = google_userinfo["email"]
    name = google_userinfo.get("name", "")

    # Case 1: GoogleOAuthLink already exists for this Google sub
    try:
        link = GoogleOAuthLink.objects.get(google_sub=sub)
        return link.user
    except GoogleOAuthLink.DoesNotExist:
        pass

    # Case 2: A User with this email already exists — link them
    try:
        user = User.objects.get(email=email)
        GoogleOAuthLink.objects.create(user=user, google_sub=sub)
        return user
    except User.DoesNotExist:
        pass

    # Case 3: Create a new User + GoogleOAuthLink
    username = email[:150]
    user = User.objects.create_user(username=username, email=email)
    user.set_unusable_password()
    if name:
        parts = name.split(" ", 1)
        user.first_name = parts[0][:150]
        user.last_name = parts[1][:150] if len(parts) > 1 else ""
    user.save()

    GoogleOAuthLink.objects.create(user=user, google_sub=sub)
    return user
