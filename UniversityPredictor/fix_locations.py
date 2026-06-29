"""
One-time script to extract district/city from University names.
Splits by last comma — everything after is the district.

Run: python fix_locations.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UniversityPredictor.settings")
django.setup()

from predictor.models import University

updated = 0
for uni in University.objects.all():
    if "," in uni.name:
        location = uni.name.rsplit(",", 1)[1].strip()
    else:
        location = ""

    if uni.location != location:
        uni.location = location
        uni.save(update_fields=["location"])
        updated += 1

print(f"Updated {updated} universities with extracted districts.")
print(f"Total universities: {University.objects.count()}")

# Show distinct districts
districts = (
    University.objects.values_list("location", flat=True)
    .exclude(location="").exclude(location__isnull=True)
    .distinct()
)
print(f"\nDistinct districts ({len(districts)}):")
for d in sorted(districts):
    print(f"  - {d}")
