from rest_framework import serializers
from .models import StudentDetail

class StudentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDetail
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['twelfth_score'] = f"{data['twelfth_score']}%"
        return data
