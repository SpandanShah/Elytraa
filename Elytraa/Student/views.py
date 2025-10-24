from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import StudentDetail
from .serializers import StudentDetailSerializer
from utils.decorators import handle_exceptions, check_authentication  # your custom decorators

from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import requests
from django.conf import settings

class StudentDetailViewSet(viewsets.ViewSet):

    @handle_exceptions
    @check_authentication
    def list(self, request):
        responses = StudentDetail.objects.all().order_by('-submitted_at')
        serializer = StudentDetailSerializer(responses, many=True)
        return Response({
            "success": True,
            "user_not_logged_in": False,
            "user_unauthorized": False,
            "data": serializer.data,
            "error": None
        }, status=status.HTTP_200_OK)

    @handle_exceptions
    def create(self, request):
        serializer = StudentDetailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": None,
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            "success": True,
            "user_not_logged_in": False,
            "user_unauthorized": False,
            "data": serializer.data,
            "error": None
        }, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class ProcessStudentAPI(APIView):
    def post(self, request):
        serializer = StudentDetailSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        instance = serializer.save()
        
        # Prepare prompt for DeepSeek API
        prompt = f"""I am providing the student details:
        Student's preferred stream to study: {instance.stream}
        Student's most enjoyed subjects: {', '.join(instance.enjoyed_subjects)}
        Student finds the following subjects exciting: {', '.join(instance.exciting_subjects)}
        Student's dream job: {instance.dream_job}
        Student's Fees budget: {instance.fees_budget}
        Student's preferred College locations: {', '.join(instance.preferred_locations)}
        Student's 12th standard score: {instance.twelfth_score}%
        Student's current location: {instance.city}

        Provide a list of 10-15 suitable colleges with these details for each: 
        - College name
        - Location
        - Courses offered that match the student's interests
        - Approximate fees
        - Placement opportunities
        - Why it's a good fit for this student
        
        Format the response as a JSON object with a 'colleges' key containing an array of college objects."""
        
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
                headers=headers,
                timeout=30  # Add timeout
            )
            response.raise_for_status()
            deepseek_data = response.json()
            
            # Store the response
            instance.ai_response = deepseek_data
            instance.save()
            
            return Response({
                "success": True,
                "data": StudentDetailSerializer(instance).data,
                "error": None
            }, status=status.HTTP_201_CREATED)
            
        except requests.exceptions.RequestException as e:
            return Response({
                "success": False,
                "data": None,
                "error": str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)