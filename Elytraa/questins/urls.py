from django.urls import path
from .views import ProcessQuestionsAPI

urlpatterns = [
    path('process-questions/', ProcessQuestionsAPI.as_view(), name='process-questions'),
]