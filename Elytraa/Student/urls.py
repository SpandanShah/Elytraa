from django.urls import path
from .views import ProcessStudentAPI

urlpatterns = [
    path('process/', ProcessStudentAPI.as_view(), name='process-student'),
]