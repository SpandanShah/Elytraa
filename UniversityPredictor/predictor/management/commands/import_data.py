"""
predictor/management/commands/import_data.py

Django management command to seed the database from the Excel files in
Analysis/Universities/.

Usage:
    python manage.py import_data
    python manage.py import_data --clear
    python manage.py import_data --data-dir "C:/custom/path/to/Universities"
"""

import logging
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from predictor.models import AdmissionCutoff, Course, University

logger = logging.getLogger(__name__)

# Path relative to this file: .../predictor/management/commands/import_data.py
# Go up 5 levels to reach the repo root, then Analysis/Universities/
_DEFAULT_DATA_DIR = (
    Path(__file__).resolve().parents[5] / "Analysis" / "Universities"
)


class Command(BaseCommand):
    help = "Import university cutoff, fees and placement data from Excel files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            type=str,
            default=str(_DEFAULT_DATA_DIR),
            help=(
                "Absolute path to the folder containing the Excel files. "
                f"Defaults to: {_DEFAULT_DATA_DIR}"
            ),
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete ALL existing data before importing (fresh start).",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=2025,
            help="Admission year to tag cutoff records with. Default: 2025.",
        )

    # ------------------------------------------------------------------ #
    #  Entry point                                                         #
    # ------------------------------------------------------------------ #

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])

        if not data_dir.exists():
            self.stderr.write(
                self.style.ERROR(f"Data directory not found: {data_dir}")
            )
            return

        # Optional: wipe existing data
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing all existing data…"))
            AdmissionCutoff.objects.all().delete()
            Course.objects.all().delete()
            University.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Cleared."))

        year = options["year"]

        # ── 1. Cutoff ranks (primary source) ──────────────────────────────
        cutoff_file = self._find_cutoff_file(data_dir)
        if cutoff_file:
            self._import_cutoffs(cutoff_file, year)
        else:
            self.stderr.write(
                self.style.ERROR(
                    "No cutoff Excel file found (expected 'Branch_Wise_*.xlsx')."
                )
            )
            return  # cutoff data is mandatory

        # ── 2. Fees (optional overlay) ───────────────────────────────────
        fees_file = data_dir / "Fees_Analysis_University.xlsx"
        if fees_file.exists():
            self._import_fees(fees_file)
        else:
            self.stdout.write(
                self.style.WARNING(f"Fees file not found, skipping: {fees_file}")
            )

        # ── 3. Placement (optional overlay) ──────────────────────────────
        placement_file = data_dir / "Placement_Analysis_University.xlsx"
        if placement_file.exists():
            self._import_placements(placement_file)
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Placement file not found, skipping: {placement_file}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Import complete."))

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _find_cutoff_file(self, data_dir: Path):
        """Return the first Branch_Wise_*.xlsx file found, or None."""
        matches = list(data_dir.glob("Branch_Wise_*.xlsx"))
        if matches:
            self.stdout.write(f"Using cutoff file: {matches[0]}")
            return matches[0]
        return None

    def _import_cutoffs(self, filepath: Path, year: int):
        """
        Parse the branch-wise cutoff Excel and upsert:
            University → Course → AdmissionCutoff
        """
        self.stdout.write(f"Importing cutoff data from: {filepath}")

        try:
            df = pd.read_excel(filepath, engine="openpyxl")
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Failed to read Excel: {exc}"))
            return

        # Fix known column-name typo in source data
        if "Openinig" in df.columns:
            df.rename(columns={"Openinig": "Opening"}, inplace=True)

        # Validate required columns
        required = {"Inst_Name", "Course_name", "Cat_Name", "Closing"}
        missing = required - set(df.columns)
        if missing:
            self.stderr.write(
                self.style.ERROR(f"Cutoff file missing columns: {missing}")
            )
            return

        # Strip whitespace from string columns
        for col in ["Inst_Name", "Course_name", "Cat_Name"]:
            df[col] = df[col].astype(str).str.strip()
        if "Board" in df.columns:
            df["Board"] = df["Board"].astype(str).str.strip().replace("nan", "")

        # Coerce ranks to numeric
        df["Closing"] = pd.to_numeric(df["Closing"], errors="coerce")
        if "Opening" in df.columns:
            df["Opening"] = pd.to_numeric(df["Opening"], errors="coerce")

        # Drop rows without a closing rank (mandatory)
        df = df.dropna(subset=["Closing"])

        created_unis = created_courses = created_cutoffs = updated_cutoffs = 0

        for _, row in df.iterrows():
            inst_name = row["Inst_Name"]
            course_name = row["Course_name"]
            cat_name = row["Cat_Name"]
            board = row.get("Board", "") if "Board" in df.columns else ""
            opening = row["Opening"] if "Opening" in df.columns else None
            closing = row["Closing"]

            # Skip placeholder / invalid rows
            if not inst_name or inst_name.lower() in ("nan", "none", ""):
                continue

            # University
            uni, uni_created = University.objects.get_or_create(
                name=inst_name,
                defaults={"location": inst_name},
            )
            if uni_created:
                created_unis += 1

            # Course
            course, course_created = Course.objects.get_or_create(
                university=uni,
                name=course_name,
            )
            if course_created:
                created_courses += 1

            # Handle NaN opening rank
            opening_val = None if pd.isna(opening) else float(opening)

            # AdmissionCutoff — upsert
            _, cutoff_created = AdmissionCutoff.objects.update_or_create(
                course=course,
                year=year,
                category=cat_name,
                board=board if board else "",
                defaults={
                    "opening_rank": opening_val,
                    "closing_rank": float(closing),
                },
            )
            if cutoff_created:
                created_cutoffs += 1
            else:
                updated_cutoffs += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"  Universities created : {created_unis}\n"
                f"  Courses created      : {created_courses}\n"
                f"  Cutoffs created      : {created_cutoffs}\n"
                f"  Cutoffs updated      : {updated_cutoffs}"
            )
        )

    def _import_fees(self, filepath: Path):
        """
        Update Course.fees from the fees Excel file.
        Expected columns: 'University' (or 'Inst_Name'), 'Course', 'Fees'
        """
        self.stdout.write(f"Importing fees data from: {filepath}")
        try:
            df = pd.read_excel(filepath, engine="openpyxl")
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Failed to read fees file: {exc}"))
            return

        self.stdout.write(f"  Fees file columns: {list(df.columns)}")

        # Flexible column detection
        uni_col = next(
            (c for c in df.columns if "univ" in c.lower() or "inst" in c.lower()), None
        )
        course_col = next(
            (c for c in df.columns if "course" in c.lower()), None
        )
        fees_col = next(
            (c for c in df.columns if "fee" in c.lower()), None
        )

        if not all([uni_col, course_col, fees_col]):
            self.stderr.write(
                self.style.WARNING(
                    "  Could not auto-detect needed columns in fees file. "
                    f"Available: {list(df.columns)}"
                )
            )
            return

        updated = 0
        for _, row in df.iterrows():
            uni_name = str(row[uni_col]).strip()
            course_name = str(row[course_col]).strip()
            fees_val = pd.to_numeric(row[fees_col], errors="coerce")
            if pd.isna(fees_val):
                continue
            rows = Course.objects.filter(
                university__name__icontains=uni_name,
                name__icontains=course_name,
            )
            cnt = rows.update(fees=float(fees_val))
            updated += cnt

        self.stdout.write(f"  Updated fees for {updated} course records.")

    def _import_placements(self, filepath: Path):
        """
        Update Course.placement_rate and average_package from the placement Excel.
        Expected columns include university name, course, placement %, avg package.
        """
        self.stdout.write(f"Importing placement data from: {filepath}")
        try:
            df = pd.read_excel(filepath, engine="openpyxl")
        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"Failed to read placement file: {exc}")
            )
            return

        self.stdout.write(f"  Placement file columns: {list(df.columns)}")

        # Flexible column detection
        uni_col = next(
            (c for c in df.columns if "univ" in c.lower() or "inst" in c.lower()), None
        )
        course_col = next(
            (c for c in df.columns if "course" in c.lower()), None
        )
        rate_col = next(
            (c for c in df.columns if "rate" in c.lower() or "percent" in c.lower() or "%" in c), None
        )
        pkg_col = next(
            (c for c in df.columns if "package" in c.lower() or "salary" in c.lower() or "lpa" in c.lower()), None
        )

        if not all([uni_col, course_col]):
            self.stderr.write(
                self.style.WARNING(
                    "  Could not detect university/course columns in placement file. "
                    f"Available: {list(df.columns)}"
                )
            )
            return

        updated = 0
        for _, row in df.iterrows():
            uni_name = str(row[uni_col]).strip()
            course_name = str(row[course_col]).strip()
            updates = {}
            if rate_col:
                rate_val = pd.to_numeric(row.get(rate_col), errors="coerce")
                if not pd.isna(rate_val):
                    updates["placement_rate"] = float(rate_val)
            if pkg_col:
                pkg_val = pd.to_numeric(row.get(pkg_col), errors="coerce")
                if not pd.isna(pkg_val):
                    updates["average_package"] = float(pkg_val)
            if updates:
                cnt = Course.objects.filter(
                    university__name__icontains=uni_name,
                    name__icontains=course_name,
                ).update(**updates)
                updated += cnt

        self.stdout.write(f"  Updated placement data for {updated} course records.")
