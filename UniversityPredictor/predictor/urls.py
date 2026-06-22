"""
predictor/urls.py
"""

from django.urls import path

from . import views

app_name = "predictor"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/predict/", views.predict, name="predict"),
    path("api/export/", views.export_predictions, name="export_predictions"),
    path("api/options/", views.options, name="options"),
    path("api/upload/", views.upload_data, name="upload_data"),
]
