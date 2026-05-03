"""
Unit tests for the accounts admin configuration.

Validates Requirements 5.1, 5.2, 5.3, 5.4, 5.5
"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from accounts.admin import UserProfileAdmin, UserProfileInline
from accounts.models import UserProfile


class UserProfileAdminListDisplayTest(TestCase):
    """Test that the UserProfile list view displays expected columns."""

    def test_list_display_contains_expected_fields(self):
        """Validates: Requirement 5.2"""
        expected = (
            "user_email",
            "can_access_round2",
            "can_access_round3",
            "can_access_jee",
            "daily_prediction_limit",
        )
        self.assertEqual(UserProfileAdmin.list_display, expected)

    def test_user_email_callable_returns_email(self):
        """The user_email column should return the related user's email."""
        user = User.objects.create_user(
            username="admintest",
            email="admin@example.com",
            password="testpass123",
        )
        profile = user.profile
        model_admin = UserProfileAdmin(UserProfile, admin.site)
        self.assertEqual(model_admin.user_email(profile), "admin@example.com")

    def test_list_editable_fields(self):
        """Validates: Requirement 5.1 — boolean fields and limit are editable."""
        expected = (
            "can_access_round2",
            "can_access_round3",
            "can_access_jee",
            "daily_prediction_limit",
        )
        self.assertEqual(UserProfileAdmin.list_editable, expected)


class UserProfileAdminSearchFilterTest(TestCase):
    """Test that search and filter work correctly on UserProfile admin."""

    def test_search_fields_include_user_email_and_username(self):
        """Validates: Requirement 5.3"""
        expected = ("user__email", "user__username")
        self.assertEqual(UserProfileAdmin.search_fields, expected)

    def test_list_filter_includes_access_booleans(self):
        """Validates: Requirement 5.4"""
        expected = (
            "can_access_round2",
            "can_access_round3",
            "can_access_jee",
        )
        self.assertEqual(UserProfileAdmin.list_filter, expected)


class UserProfileInlineOnUserTest(TestCase):
    """Test that the User change page includes the UserProfile inline."""

    def test_user_admin_has_userprofile_inline(self):
        """Validates: Requirement 5.5"""
        superuser = User.objects.create_superuser(
            username="inlineadmin",
            email="inlineadmin@example.com",
            password="testpass123",
        )
        request = RequestFactory().get("/admin/")
        request.user = superuser
        user_admin = admin.site._registry[User]
        inline_classes = [
            type(i) for i in user_admin.get_inline_instances(request)
        ]
        self.assertIn(UserProfileInline, inline_classes)

    def test_userprofile_inline_model(self):
        """The inline should be bound to the UserProfile model."""
        self.assertEqual(UserProfileInline.model, UserProfile)

    def test_userprofile_inline_cannot_delete(self):
        """Admins should not be able to delete the profile inline."""
        self.assertFalse(UserProfileInline.can_delete)


class UserProfileAdminRegistrationTest(TestCase):
    """Test that UserProfile is registered in the admin site."""

    def test_userprofile_is_registered(self):
        self.assertIn(UserProfile, admin.site._registry)

    def test_user_is_registered(self):
        self.assertIn(User, admin.site._registry)
