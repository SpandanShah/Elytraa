from django.contrib import admin
from .models import *

@admin.register(StudentDetail)
class StudentDetailAdmin(admin.ModelAdmin):
    list_display = ('stream', 'name', 'twelfth_score', 'email', 'mobile_number', 'city')
    list_filter = ('stream',)
    search_fields = ('name', 'email', 'mobile_number', 'city')
    # readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
