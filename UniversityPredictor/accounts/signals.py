from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, **kwargs):
    """Ensure every User has a UserProfile.

    Runs on every User save (not just creation) so that existing users
    who were created before the UserProfile model was added also get
    a profile the next time their User record is saved (e.g., login,
    admin edit, password change).
    """
    from accounts.models import UserProfile

    UserProfile.objects.get_or_create(user=instance)
