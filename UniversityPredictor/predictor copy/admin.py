"""
predictor/admin.py

Registers all models with the Django admin site.
"""

from django.contrib import admin

from .models import AdmissionCutoff, Course, ScoreWeight, University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = (
        "name", "state", "mode", "inst_type",
        "infra_labs_score", "infra_sports_score", "infra_premises_score",
        "extra_curricular_score", "patent_score", "alumni_score",
    )
    list_filter = ("state", "mode", "inst_type")
    search_fields = ("name", "location", "state")
    ordering = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "name", "university", "fees",
        "placement_rate", "average_package",
        "faculty_research_score", "faculty_experience_score",
        "curriculum_score", "degree_score",
    )
    list_filter = ("university",)
    search_fields = ("name", "university__name")
    ordering = ("university__name", "name")


@admin.register(AdmissionCutoff)
class AdmissionCutoffAdmin(admin.ModelAdmin):
    list_display = (
        "course", "year", "round", "category", "board",
        "opening_rank", "closing_rank",
    )
    list_filter = ("year", "round", "category", "board")
    search_fields = ("course__name", "course__university__name")
    ordering = ("course__university__name", "course__name", "round", "category")


@admin.register(ScoreWeight)
class ScoreWeightAdmin(admin.ModelAdmin):
    """
    Singleton admin — prevents adding more than one row
    and prevents deletion of the single config row.
    """

    def has_add_permission(self, request):
        # Only allow adding if no row exists yet
        return not ScoreWeight.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
