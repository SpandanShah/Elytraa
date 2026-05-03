"""
accounts/admin.py

Registers UserProfile with the Django admin site and adds a UserProfile
inline on the User change page so administrators can manage access tiers
directly from either the UserProfile list or the User detail view.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


# ---------------------------------------------------------------------------
# Standalone UserProfile admin (list / search / filter / inline-edit)
# ---------------------------------------------------------------------------

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user_email",
        "can_access_round2",
        "can_access_round3",
        "can_access_jee",
        "daily_prediction_limit",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    list_filter = (
        "can_access_round2",
        "can_access_round3",
        "can_access_jee",
    )
    list_editable = (
        "can_access_round2",
        "can_access_round3",
        "can_access_jee",
        "daily_prediction_limit",
    )

    @admin.display(description="User Email", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email


# ---------------------------------------------------------------------------
# UserProfile inline on the User change page
# ---------------------------------------------------------------------------

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profile"
    fk_name = "user"


# ---------------------------------------------------------------------------
# Re-register User admin with the inline
# ---------------------------------------------------------------------------

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
