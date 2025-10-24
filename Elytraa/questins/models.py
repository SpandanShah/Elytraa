from django.db import models

class QuestionAnswer(models.Model):
    student_stream = models.CharField(max_length=100, null=True, blank=True)
    enjoyed_subject = models.CharField(max_length=100, null=True, blank=True)
    exciting_subject = models.CharField(max_length=100, null=True, blank=True)
    dream_job = models.CharField(max_length=100, null=True, blank=True)
    fees_budget = models.CharField(max_length=100, null=True, blank=True)
    college_location = models.CharField(max_length=100, null=True, blank=True)

    student_name = models.CharField(max_length=30, null=True, blank=True)
    student_12th_score_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    email_id = models.CharField(max_length=100, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    student_location = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response {self.id}"



