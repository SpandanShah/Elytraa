from django.db import models

class StudentDetail(models.Model):
    stream = models.CharField(max_length=255)
    enjoyed_subjects = models.JSONField(default=list)  # store as ["Maths", "Computers"]
    excited_subjects = models.JSONField(default=list)  # same format as above
    dream_job = models.CharField(max_length=255)
    fees_budget = models.CharField(max_length=255)
    preferred_locations = models.JSONField(default=list)

    # Student Personal Info
    name = models.CharField(max_length=100) 
    twelfth_score = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    city = models.CharField(max_length=255)

    ai_response = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
