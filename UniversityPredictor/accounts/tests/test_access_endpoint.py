"""
Property-based test: Access endpoint reflects profile state.

Uses hypothesis to generate random UserProfile field values and random
numbers of PredictionLog entries for today, then asserts that the
GET /api/auth/access/ endpoint returns the exact profile field values
and the correct predictions_used_today count.

**Validates: Requirements 8.2, 8.4**
"""

from django.contrib.auth.models import User
from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient

from accounts.models import PredictionLog


class AccessEndpointReflectsProfileStateTest(TestCase):
    """Property 5: Access endpoint reflects profile state.

    Validates: Requirements 8.2, 8.4
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="accesstest", password="testpass123"
        )
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

    def tearDown(self):
        PredictionLog.objects.filter(user=self.user).delete()

    @given(
        can_access_round2=st.booleans(),
        can_access_round3=st.booleans(),
        can_access_jee=st.booleans(),
        daily_prediction_limit=st.integers(min_value=1, max_value=100),
        predictions_today=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=50, deadline=None)
    def test_access_endpoint_reflects_profile_state(
        self,
        can_access_round2,
        can_access_round3,
        can_access_jee,
        daily_prediction_limit,
        predictions_today,
    ):
        """Endpoint returns exact profile values and correct daily count."""
        # Set up profile with generated values
        profile = self.user.profile
        profile.can_access_round2 = can_access_round2
        profile.can_access_round3 = can_access_round3
        profile.can_access_jee = can_access_jee
        profile.daily_prediction_limit = daily_prediction_limit
        profile.save()

        # Clear existing logs and create the generated number of entries
        PredictionLog.objects.filter(user=self.user).delete()
        for _ in range(predictions_today):
            PredictionLog.objects.create(user=self.user)

        # Call the access endpoint
        response = self.api_client.get("/api/auth/access/")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["can_access_round2"], can_access_round2)
        self.assertEqual(data["can_access_round3"], can_access_round3)
        self.assertEqual(data["can_access_jee"], can_access_jee)
        self.assertEqual(
            data["daily_prediction_limit"], daily_prediction_limit
        )
        self.assertEqual(data["predictions_used_today"], predictions_today)


class AccessEndpointUnauthenticatedTest(TestCase):
    """Test that unauthenticated requests get 403."""

    def test_unauthenticated_returns_403(self):
        """Unauthenticated request should return 403 with error message."""
        client = APIClient()
        response = client.get("/api/auth/access/")
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Authentication required.")
