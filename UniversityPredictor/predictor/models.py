from django.db import models


class University(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Indian state, e.g. Gujarat, Maharashtra"
    )
    mode = models.CharField(
        max_length=20,
        choices=[('regular', 'Regular'), ('distance', 'Distance'), ('both', 'Both')],
        default='regular'
    )

    # Infrastructure Score Components (0-10 scale)
    infra_labs_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    infra_sports_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    infra_premises_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)

    # Generic University Scores
    extra_curricular_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    patent_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    alumni_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)

    def __str__(self):
        return self.name


class Course(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=255)

    # Course Specific Scores
    faculty_research_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    faculty_experience_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)

    placement_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Percentage
    average_package = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    curriculum_score = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    degree_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.0,
        help_text="Score for the degree level (B.Tech, M.Tech, Diploma, etc.)"
    )

    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        unique_together = ('university', 'name')

    def __str__(self):
        return f"{self.name} at {self.university.name}"


class AdmissionCutoff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cutoffs')
    year = models.IntegerField(default=2025)
    category = models.CharField(max_length=50)          # GEN, SC, ST, OBC, TFWs, etc.
    board = models.CharField(max_length=50, blank=True, null=True)  # GUJCET, JEE, etc.
    opening_rank = models.FloatField(null=True, blank=True)
    closing_rank = models.FloatField()

    class Meta:
        unique_together = ('course', 'year', 'category', 'board')

    def __str__(self):
        return f"{self.course} - {self.category} ({self.year})"


class ScoreWeight(models.Model):
    """
    Singleton model storing configurable weight percentages for the scoring
    algorithm. Only one row (pk=1) should ever exist.
    Weights should sum to 100.
    """
    # Scoring weights (percentages, must sum to 100)
    infra_weight = models.IntegerField(default=15, help_text="Weight % for infrastructure score")
    course_weight = models.IntegerField(default=30, help_text="Weight % for course score")
    extra_curricular_weight = models.IntegerField(default=10, help_text="Weight % for extra-curricular")
    patent_weight = models.IntegerField(default=10, help_text="Weight % for patent score")
    fees_weight = models.IntegerField(default=15, help_text="Weight % for fees score")
    alumni_weight = models.IntegerField(default=10, help_text="Weight % for alumni score")
    degree_weight = models.IntegerField(default=10, help_text="Weight % for degree score")

    # Prediction tuning parameters
    tolerance = models.IntegerField(
        default=50,
        help_text="Rank buffer — how close to closing rank counts as Possible"
    )
    safe_multiplier = models.IntegerField(
        default=2,
        help_text="Ranks below (closing - tolerance * safe_multiplier) are Safe"
    )
    stretch_multiplier = models.IntegerField(
        default=10,
        help_text="Ranks above (closing + tolerance * stretch_multiplier) are excluded"
    )

    class Meta:
        verbose_name = "Score Weight Configuration"
        verbose_name_plural = "Score Weight Configuration"

    def save(self, *args, **kwargs):
        # Enforce singleton: always pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Score Weight Configuration"
