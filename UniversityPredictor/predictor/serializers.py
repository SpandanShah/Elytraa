"""
predictor/serializers.py

DRF serializers for input validation and response formatting.
"""

from rest_framework import serializers


class PredictionInputSerializer(serializers.Serializer):
    """Validates the student's prediction request body."""

    rank = serializers.IntegerField(
        min_value=1,
        error_messages={
            "min_value": "Rank must be a positive integer (at least 1).",
            "invalid": "Rank must be a whole number.",
        },
    )
    category = serializers.CharField(
        max_length=50,
        required=False,
        default=None,
        allow_null=True,
        allow_blank=True,
        help_text="Reservation category, e.g. GEN, SC, ST, OBC, TFWs",
    )
    board = serializers.CharField(
        max_length=50,
        required=False,
        default=None,
        allow_null=True,
        allow_blank=True,
        help_text="Exam board, e.g. GUJCET or JEE",
    )
    course_preferences = serializers.ListField(
        child=serializers.CharField(max_length=50, allow_blank=False),
        required=False,
        default=None,
        allow_null=True,
        help_text="List of course keywords, e.g. ['computer', 'mechanical']",
    )
    min_results = serializers.IntegerField(
        min_value=1,
        max_value=50,
        default=15,
        required=False,
        help_text="Maximum results per course preference (default: 15)",
    )
    round = serializers.IntegerField(
        min_value=1,
        max_value=3,
        required=False,
        default=None,
        allow_null=True,
        help_text="ACPC admission round (1, 2, or 3). Omit for all rounds.",
    )
    inst_types = serializers.ListField(
        child=serializers.CharField(max_length=30, allow_blank=False),
        required=False,
        default=None,
        allow_null=True,
        help_text="Institute types, e.g. ['govt_gia']. Staff-only filter.",
    )
    districts = serializers.ListField(
        child=serializers.CharField(max_length=100, allow_blank=False),
        required=False,
        default=None,
        allow_null=True,
        help_text="Districts/cities, e.g. ['Ahmedabad', 'Surat']. Staff-only.",
    )

    def validate_category(self, value):
        """Convert empty string to None."""
        if value == "":
            return None
        return value

    def validate_board(self, value):
        """Convert empty string to None."""
        if value == "":
            return None
        return value

    def validate_course_preferences(self, value):
        """Remove empty strings from list; return None if empty list."""
        if value is None:
            return None
        cleaned = [v.strip() for v in value if v.strip()]
        return cleaned if cleaned else None


class PredictionResultSerializer(serializers.Serializer):
    """Serializes a single prediction result dict from PredictionService."""

    inst_name = serializers.CharField()
    course_name = serializers.CharField()
    category = serializers.CharField()
    board = serializers.CharField(allow_blank=True, allow_null=True)
    opening_rank = serializers.FloatField(allow_null=True)
    closing_rank = serializers.FloatField()
    chance = serializers.ChoiceField(choices=["Safe", "Possible", "Stretch"])
    preferred_course = serializers.CharField()
    university_score = serializers.FloatField()
    round = serializers.IntegerField()
    inst_type = serializers.CharField(allow_blank=True)


class DropdownOptionsSerializer(serializers.Serializer):
    """Serializes the available dropdown options for the frontend."""

    categories = serializers.ListField(child=serializers.CharField())
    boards = serializers.ListField(child=serializers.CharField())
    rounds = serializers.ListField(child=serializers.IntegerField())
    course_keywords = serializers.ListField(child=serializers.CharField())
    inst_types = serializers.ListField(child=serializers.CharField())
    districts = serializers.ListField(child=serializers.CharField())
