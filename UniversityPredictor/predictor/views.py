"""
predictor/views.py

API views for the University Predictor.

Endpoints:
    GET  /              → Render the main HTML page (index.html)
    POST /api/predict/  → Run prediction, return JSON results
    GET  /api/options/  → Return dropdown data (categories, boards, course keywords)
    POST /api/upload/   → (stub) Upload new Excel data file
"""

import logging

from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import (
    DropdownOptionsSerializer,
    PredictionInputSerializer,
    PredictionResultSerializer,
)
from .services import PredictionService

logger = logging.getLogger(__name__)


def index(request):
    """
    GET /
    Renders the main HTML template with the student input form.
    """
    return render(request, "predictor/index.html")


@api_view(["POST"])
def predict(request):
    """
    POST /api/predict/

    Request body (JSON):
        {
            "rank": 3000,
            "category": "GEN",
            "board": "GUJCET",
            "course_preferences": ["computer", "mechanical"],
            "min_results": 15
        }

    Response (JSON):
        {
            "success": true,
            "count": 28,
            "results": [ ... ],
            "error": null
        }
    """
    input_serializer = PredictionInputSerializer(data=request.data)

    if not input_serializer.is_valid():
        logger.warning("Invalid prediction input: %s", input_serializer.errors)
        return Response(
            {
                "success": False,
                "count": 0,
                "results": [],
                "error": input_serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = input_serializer.validated_data

    try:
        service = PredictionService()
        results = service.predict(
            student_rank=data["rank"],
            category=data.get("category"),
            board=data.get("board"),
            course_preferences=data.get("course_preferences"),
            min_results=data.get("min_results", 15),
        )
    except ValueError as exc:
        logger.error("Prediction ValueError: %s", exc)
        return Response(
            {"success": False, "count": 0, "results": [], "error": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        logger.exception("Unexpected error during prediction: %s", exc)
        return Response(
            {"success": False, "count": 0, "results": [], "error": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    result_serializer = PredictionResultSerializer(results, many=True)
    return Response(
        {
            "success": True,
            "count": len(results),
            "results": result_serializer.data,
            "error": None,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def options(request):
    """
    GET /api/options/

    Returns all dropdown options for the frontend:
        categories    — distinct reservation categories in the database
        boards        — distinct exam boards in the database
        course_keywords — all supported course preference keywords
    """
    try:
        data = PredictionService.get_available_options()
    except Exception as exc:
        logger.exception("Error fetching options: %s", exc)
        return Response(
            {"success": False, "data": None, "error": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    serializer = DropdownOptionsSerializer(data)
    return Response(
        {"success": True, "data": serializer.data, "error": None},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def upload_data(request):
    """
    POST /api/upload/

    Stub — Excel upload via API is not yet implemented.
    Use the management command instead:
        python manage.py import_data
        python manage.py import_data --clear
    """
    return Response(
        {
            "success": False,
            "error": (
                "Not implemented. Run: "
                "python manage.py import_data  (or --clear for a fresh load)"
            ),
        },
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )
