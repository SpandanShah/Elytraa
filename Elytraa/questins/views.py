from rest_framework import viewsets, status
from rest_framework.response import Response
import requests
from django.conf import settings
from questins.models import QuestionAnswer
from questins.serializers import QuestionAnswerSerializer


class ProcessQuestionsViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = QuestionAnswerSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": None,
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()

        # Prepare prompt for DeepSeek API
        prompt = f"""I am providing the student details:
        Student's preferred stream to study: {instance.student_stream}
        Student's most enjoyed subject: {instance.enjoyed_subject}
        Student finds the following subject most exciting: {instance.exciting_subject}
        Student's dream job: {instance.dream_job}
        Student's Fees budget: {instance.fees_budget}
        Student's preferred College location: {instance.college_location}
        Student's 12th standard score in percentage: {instance.student_12th_score_percentage}
        Student's current location: {instance.student_location}

        give me only list of dictionary with 'college name', 'college location', 'note' if any. and not anything else"""

        # Call DeepSeek API
        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            deepseek_data = response.json()
            instance.deepseek_response = deepseek_data
            instance.save()

            return Response({
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": QuestionAnswerSerializer(instance).data,
                "error": None
            }, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response({
                "success": True,
                "user_not_logged_in": False,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": None,
                "error": str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)