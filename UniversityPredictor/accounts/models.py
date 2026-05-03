from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class GoogleOAuthLink(models.Model):
    """Links a Google identity (sub) to a Django User."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="google_link"
    )
    google_sub = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"GoogleOAuthLink(user={self.user.username}, "
            f"sub={self.google_sub})"
        )


class UserProfile(models.Model):
    """Per-user profile storing access-tier flags and rate-limit settings."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    can_access_round2 = models.BooleanField(default=False)
    can_access_round3 = models.BooleanField(default=False)
    can_access_jee = models.BooleanField(default=False)
    daily_prediction_limit = models.IntegerField(default=2)

    def __str__(self):
        return self.user.email


class PredictionLog(models.Model):
    """Records each prediction request for daily rate-limiting."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="prediction_logs"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"PredictionLog(user={self.user.username}, "
            f"at={self.created_at})"
        )

    @classmethod
    def count_today(cls, user):
        """Count the number of predictions made by the user today (UTC)."""
        today_start = timezone.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return cls.objects.filter(
            user=user, created_at__gte=today_start
        ).count()
