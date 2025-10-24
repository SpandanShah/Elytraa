from rest_framework import serializers
from questins.models import QuestionAnswer

class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = [
            'id', 'student_stream', 'enjoyed_subject', 'exciting_subject',
            'dream_job', 'fees_budget', 'college_location', 'student_name',
            'student_12th_score_percentage', 'email_id', 'contact_number',
            'student_location', 'deepseek_response', 'created_at'
        ]
        read_only_fields = ['id', 'deepseek_response', 'created_at']