import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from questins.models import QuestionAnswer
from questins.serializers import QuestionAnswerSerializer

class ProcessQuestionsAPI(APIView):
    def post(self, request):
        serializer = QuestionAnswerSerializer(data=request.data)
        if serializer.is_valid():
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

                # Save DeepSeek response
                instance.deepseek_response = deepseek_data
                instance.save()

                return Response(QuestionAnswerSerializer(instance).data, status=status.HTTP_201_CREATED)

            except requests.exceptions.RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)