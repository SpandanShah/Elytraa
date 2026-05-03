"""
Property-based tests for access-tier enforcement and rate limiting
on the predict endpoint (POST /api/predict/).

Uses hypothesis to generate random combinations of user profile flags
and request parameters, verifying that the backend correctly enforces
round access, board access, daily rate limits, and check ordering.
"""

from django.contrib.auth.models import User
from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import TestCase
from rest_framework.test import APIClient

from accounts.models import PredictionLog


class RoundAccessPropertyTest(TestCase):
    """Property 1: Round access enforcement.

    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="roundtest", password="testpass123"
        )
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

    def tearDown(self):
        PredictionLog.objects.filter(user=self.user).delete()

    @given(
        can_access_round2=st.booleans(),
        can_access_round3=st.booleans(),
        requested_round=st.sampled_from([1, 2, 3]),
    )
    @settings(max_examples=50, deadline=None)
    def test_round_access_enforcement(
        self, can_access_round2, can_access_round3, requested_round
    ):
        """Round access denied (403) iff user lacks requested round."""
        profile = self.user.profile
        profile.can_access_round2 = can_access_round2
        profile.can_access_round3 = can_access_round3
        profile.daily_prediction_limit = 9999
        profile.save()

        PredictionLog.objects.filter(user=self.user).delete()

        payload = {
            "rank": 1000,
            "category": "GEN",
            "board": "GUJCET",
            "round": requested_round,
            "min_results": 15,
        }
        response = self.api_client.post(
            "/api/predict/", data=payload, format="json"
        )

        should_deny = (
            (requested_round == 2 and not can_access_round2)
            or (requested_round == 3 and not can_access_round3)
        )

        if should_deny:
            self.assertEqual(response.status_code, 403)
        else:
            self.assertNotEqual(response.status_code, 403)


class BoardAccessPropertyTest(TestCase):
    """Property 2: Board access enforcement.

    Validates: Requirements 3.1, 3.2, 3.3
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="boardtest", password="testpass123"
        )
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

    def tearDown(self):
        PredictionLog.objects.filter(user=self.user).delete()

    @given(
        can_access_jee=st.booleans(),
        board=st.sampled_from(["JEE", "GUJCET", "", None]),
    )
    @settings(max_examples=50, deadline=None)
    def test_board_access_enforcement(self, can_access_jee, board):
        """Board access denied (403) iff board is JEE and no access."""
        profile = self.user.profile
        profile.can_access_jee = can_access_jee
        profile.can_access_round2 = True
        profile.can_access_round3 = True
        profile.daily_prediction_limit = 9999
        profile.save()

        PredictionLog.objects.filter(user=self.user).delete()

        payload = {
            "rank": 1000,
            "category": "GEN",
            "round": 1,
            "min_results": 15,
        }
        if board is not None:
            payload["board"] = board

        response = self.api_client.post(
            "/api/predict/", data=payload, format="json"
        )

        is_jee = board is not None and board.upper() == "JEE"
        should_deny = is_jee and not can_access_jee

        if should_deny:
            self.assertEqual(response.status_code, 403)
        else:
            self.assertNotEqual(response.status_code, 403)


class RateLimitPropertyTest(TestCase):
    """Property 3: Rate limit enforcement.

    Validates: Requirements 4.2, 4.3, 4.4
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="ratetest", password="testpass123"
        )
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

    def tearDown(self):
        PredictionLog.objects.filter(user=self.user).delete()

    @given(
        daily_limit=st.integers(min_value=1, max_value=10),
        predictions_already_made=st.integers(min_value=0, max_value=15),
    )
    @settings(max_examples=50, deadline=None)
    def test_rate_limit_enforcement(
        self, daily_limit, predictions_already_made
    ):
        """Rate limit returns 429 iff used >= limit."""
        profile = self.user.profile
        profile.daily_prediction_limit = daily_limit
        profile.can_access_round2 = True
        profile.can_access_round3 = True
        profile.can_access_jee = True
        profile.save()

        PredictionLog.objects.filter(user=self.user).delete()
        for _ in range(predictions_already_made):
            PredictionLog.objects.create(user=self.user)

        payload = {
            "rank": 1000,
            "category": "GEN",
            "board": "GUJCET",
            "round": 1,
            "min_results": 15,
        }
        response = self.api_client.post(
            "/api/predict/", data=payload, format="json"
        )

        should_rate_limit = predictions_already_made >= daily_limit

        if should_rate_limit:
            self.assertEqual(response.status_code, 429)
        else:
            self.assertNotEqual(response.status_code, 429)


class AccessBeforeRateLimitPropertyTest(TestCase):
    """Property 4: Access tier checks precede rate limiting.

    Validates: Requirements 4.6
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="ordertest", password="testpass123"
        )
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

    def tearDown(self):
        PredictionLog.objects.filter(user=self.user).delete()

    @given(
        scenario=st.sampled_from([
            {"round": 2, "board": "GUJCET",
             "can_r2": False, "can_r3": True, "can_jee": True},
            {"round": 3, "board": "GUJCET",
             "can_r2": True, "can_r3": False, "can_jee": True},
            {"round": 1, "board": "JEE",
             "can_r2": True, "can_r3": True, "can_jee": False},
            {"round": 2, "board": "JEE",
             "can_r2": False, "can_r3": True, "can_jee": False},
            {"round": 3, "board": "JEE",
             "can_r2": True, "can_r3": False, "can_jee": False},
        ]),
        excess_predictions=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=50, deadline=None)
    def test_access_denied_before_rate_limit(
        self, scenario, excess_predictions
    ):
        """When access denied AND rate exceeded, response is 403."""
        profile = self.user.profile
        profile.can_access_round2 = scenario["can_r2"]
        profile.can_access_round3 = scenario["can_r3"]
        profile.can_access_jee = scenario["can_jee"]
        profile.daily_prediction_limit = 1
        profile.save()

        PredictionLog.objects.filter(user=self.user).delete()
        for _ in range(1 + excess_predictions):
            PredictionLog.objects.create(user=self.user)

        payload = {
            "rank": 1000,
            "category": "GEN",
            "board": scenario["board"],
            "round": scenario["round"],
            "min_results": 15,
        }
        response = self.api_client.post(
            "/api/predict/", data=payload, format="json"
        )

        # Access check should fire first -> 403, not 429
        self.assertEqual(response.status_code, 403)
