"""
predictor/tests.py

Unit tests for PredictionService and API endpoints.

Run with:
    python manage.py test predictor -v2
"""

import json

from django.contrib.auth.models import User
from django.test import TestCase, Client

from .models import AdmissionCutoff, Course, ScoreWeight, University
from .services import PredictionService


class PredictionServiceTest(TestCase):
    """Tests for PredictionService — mirrors predict_uni_v2.py logic."""

    def setUp(self):
        """Create minimal seed data: 2 universities, 3 courses, 4 cutoffs."""
        # University 1 — computer college
        self.uni_a = University.objects.create(name="Alpha Engineering College")
        self.course_cs = Course.objects.create(
            university=self.uni_a, name="Computer Engineering"
        )
        AdmissionCutoff.objects.create(
            course=self.course_cs,
            year=2025,
            category="GEN",
            board="GUJCET",
            opening_rank=100,
            closing_rank=5000,
        )

        # University 2 — mechanical college
        self.uni_b = University.objects.create(name="Beta Technical Institute")
        self.course_mech = Course.objects.create(
            university=self.uni_b, name="Mechanical Engineering"
        )
        AdmissionCutoff.objects.create(
            course=self.course_mech,
            year=2025,
            category="GEN",
            board="GUJCET",
            opening_rank=200,
            closing_rank=8000,
        )

        # SC category cutoff for computer
        self.course_cs2 = Course.objects.create(
            university=self.uni_b, name="Computer Engineering"
        )
        AdmissionCutoff.objects.create(
            course=self.course_cs2,
            year=2025,
            category="SC",
            board="GUJCET",
            opening_rank=1000,
            closing_rank=15000,
        )

        self.service = PredictionService()

    # ── categorize_chance ────────────────────────────────────────── #

    def test_safe_chance(self):
        """Rank well below closing should return Safe."""
        # closing=5000, tolerance=50, safe_multiplier=2 → safe_threshold=4900
        # rank=100 < 4900 → Safe
        chance = self.service._categorize_chance(100, 5000)
        self.assertEqual(chance, "Safe")

    def test_possible_chance(self):
        """Rank within tolerance window of closing should return Possible."""
        # closing=5000, safe_threshold=4900, rank=4950 → Possible
        chance = self.service._categorize_chance(4950, 5000)
        self.assertEqual(chance, "Possible")

    def test_stretch_chance(self):
        """Rank above closing+tolerance should return Stretch."""
        # closing=5000, tolerance=50, rank=5200 > 5050 → Stretch
        chance = self.service._categorize_chance(5200, 5000)
        self.assertEqual(chance, "Stretch")

    # ── predict ─────────────────────────────────────────────────── #

    def test_predict_returns_list(self):
        """predict() should return a list."""
        results = self.service.predict(student_rank=3000)
        self.assertIsInstance(results, list)

    def test_predict_safe_results(self):
        """Low rank should produce Safe results for computer courses."""
        results = self.service.predict(
            student_rank=500,
            category="GEN",
            board="GUJCET",
            course_preferences=["computer"],
        )
        self.assertTrue(len(results) > 0, "Expected at least one result")
        safe_results = [r for r in results if r["chance"] == "Safe"]
        self.assertTrue(len(safe_results) > 0, "Expected at least one Safe result")

    def test_predict_filters_by_category(self):
        """Results should only contain the requested category."""
        results = self.service.predict(
            student_rank=5000,
            category="SC",
            course_preferences=["computer"],
        )
        for r in results:
            self.assertEqual(r["category"], "SC")

    def test_predict_result_keys(self):
        """Each result dict must contain all required keys."""
        results = self.service.predict(student_rank=3000, course_preferences=["computer"])
        if results:
            required_keys = {
                "inst_name", "course_name", "category", "board",
                "opening_rank", "closing_rank", "chance",
                "preferred_course", "university_score",
            }
            self.assertTrue(required_keys.issubset(set(results[0].keys())))

    def test_predict_sorted_by_chance(self):
        """Results should be sorted Safe → Possible → Stretch."""
        results = self.service.predict(student_rank=5000, course_preferences=["computer"])
        if len(results) > 1:
            order = {"Safe": 0, "Possible": 1, "Stretch": 2}
            for i in range(len(results) - 1):
                self.assertLessEqual(
                    order[results[i]["chance"]],
                    order[results[i + 1]["chance"]],
                    "Results not sorted by chance",
                )

    def test_predict_invalid_rank_raises(self):
        """Rank <= 0 should raise ValueError."""
        with self.assertRaises(ValueError):
            self.service.predict(student_rank=-1)

    def test_predict_invalid_rank_zero_raises(self):
        with self.assertRaises(ValueError):
            self.service.predict(student_rank=0)

    def test_predict_no_matching_course(self):
        """Non-matching course preference should return empty or fallback list."""
        results = self.service.predict(
            student_rank=3000,
            category="GEN",
            course_preferences=["marine"],  # Not in test data
        )
        self.assertIsInstance(results, list)  # must not crash

    # ── get_available_options ────────────────────────────────────── #

    def test_options_returns_dict(self):
        opts = PredictionService.get_available_options()
        self.assertIn("categories", opts)
        self.assertIn("boards", opts)
        self.assertIn("course_keywords", opts)

    def test_options_contains_seeded_category(self):
        opts = PredictionService.get_available_options()
        self.assertIn("GEN", opts["categories"])

    def test_options_contains_seeded_board(self):
        opts = PredictionService.get_available_options()
        self.assertIn("GUJCET", opts["boards"])


class APIEndpointTest(TestCase):
    """Tests for REST API views."""

    def setUp(self):
        self.client = Client()

        # Create and log in a test user so the auth-gated predict endpoint works
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
        )
        self.client.force_login(self.user)

        uni = University.objects.create(name="Test University")
        course = Course.objects.create(university=uni, name="Computer Engineering")
        AdmissionCutoff.objects.create(
            course=course,
            year=2025,
            category="GEN",
            board="GUJCET",
            opening_rank=100,
            closing_rank=5000,
        )

    # ── GET / ───────────────────────────────────────────────────── #

    def test_index_page_loads(self):
        """Homepage should return 200 with HTML content."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'University Predictor')

    # ── GET /api/options/ ────────────────────────────────────────── #

    def test_options_returns_200(self):
        res = self.client.get('/api/options/')
        self.assertEqual(res.status_code, 200)

    def test_options_json_structure(self):
        res = self.client.get('/api/options/')
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("categories", data["data"])
        self.assertIn("boards", data["data"])
        self.assertIn("course_keywords", data["data"])

    # ── POST /api/predict/ ───────────────────────────────────────── #

    def test_predict_valid_input_200(self):
        payload = {"rank": 3000, "category": "GEN", "board": "GUJCET"}
        res = self.client.post(
            '/api/predict/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("results", data)
        self.assertIn("count", data)

    def test_predict_missing_rank_400(self):
        payload = {"category": "GEN"}
        res = self.client.post(
            '/api/predict/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json()["success"])

    def test_predict_negative_rank_400(self):
        payload = {"rank": -500}
        res = self.client.post(
            '/api/predict/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(res.status_code, 400)

    def test_predict_zero_rank_400(self):
        payload = {"rank": 0}
        res = self.client.post(
            '/api/predict/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(res.status_code, 400)

    def test_predict_result_has_required_fields(self):
        payload = {
            "rank": 3000,
            "category": "GEN",
            "board": "GUJCET",
            "course_preferences": ["computer"],
        }
        res = self.client.post(
            '/api/predict/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        data = res.json()
        if data.get("results"):
            result = data["results"][0]
            for key in ["inst_name", "course_name", "category", "board",
                        "opening_rank", "closing_rank", "chance",
                        "preferred_course", "university_score"]:
                self.assertIn(key, result, f"Missing key: {key}")

    def test_predict_chance_values_valid(self):
        """All returned chance values must be Safe, Possible, or Stretch."""
        payload = {"rank": 3000}
        res = self.client.post(
            '/api/predict/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        data = res.json()
        valid_chances = {"Safe", "Possible", "Stretch"}
        for result in data.get("results", []):
            self.assertIn(result["chance"], valid_chances)


class ScoreWeightSingletonTest(TestCase):
    """Test the ScoreWeight singleton model."""

    def test_get_instance_creates_row(self):
        obj = ScoreWeight.get_instance()
        self.assertEqual(obj.pk, 1)
        self.assertEqual(ScoreWeight.objects.count(), 1)

    def test_get_instance_idempotent(self):
        ScoreWeight.get_instance()
        ScoreWeight.get_instance()
        self.assertEqual(ScoreWeight.objects.count(), 1)

    def test_default_weights_sum_to_100(self):
        obj = ScoreWeight.get_instance()
        total = (
            obj.infra_weight + obj.course_weight + obj.extra_curricular_weight
            + obj.patent_weight + obj.fees_weight + obj.alumni_weight
            + obj.degree_weight
        )
        self.assertEqual(total, 100, f"Weights sum to {total}, expected 100")
