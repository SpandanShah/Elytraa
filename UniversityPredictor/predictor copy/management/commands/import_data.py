"""
predictor/management/commands/import_data.py

Django management command to seed the database from the ACPC admission
Excel files (Round 1, 2, or 3).

Usage:
    python manage.py import_data --round 1 --data-dir "../Analysis/FirstRound"
    python manage.py import_data --round 2 --data-dir "../Analysis/SecondRound"
    python manage.py import_data --round 3 --data-dir "../Analysis"
    python manage.py import_data --round 1 --clear --data-dir "../Analysis/FirstRound"
"""

import logging
import re
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand, CommandError

from predictor.models import AdmissionCutoff, Course, University

logger = logging.getLogger(__name__)


# ── Column name normalization map ─────────────────────────────────────
# Maps known column variants (lowercased) to canonical names.
_COLUMN_MAP = {
    "inst_name": "inst_name",
    "course_name": "course_name",
    "cat_name": "cat_name",
    "board": "board",
    # Opening rank variants
    "openinig": "opening",
    "opening": "opening",
    "open rank": "opening",
    # Closing rank variants
    "closing": "closing",
    "closing rank": "closing",
    # Inst type variants
    "inst_type": "inst_type",
    "type of\ninstitute": "inst_type",
    "type of institute": "inst_type",
}

# ── Board normalization ───────────────────────────────────────────────
_BOARD_MAP = {
    "gujcet": "GUJCET",
    "gujcet based": "GUJCET",
    "gujcet\nbased": "GUJCET",
    "jee": "JEE",
    "jee based": "JEE",
    "jee\nbased": "JEE",
}

# ── Category normalization ────────────────────────────────────────────
_CATEGORY_MAP = {
    "tfws": "TFWS",
    "gen": "GEN",
    "gen-ph": "GEN-PH",
    "sc": "SC",
    "st": "ST",
    "sebc": "SEBC",
    "sebc-ph": "SEBC-PH",
    "ews": "EWS",
    "ews-ph": "EWS-PH",
    "esm": "ESM",
}

# ── Institute type normalization ──────────────────────────────────────
_INST_TYPE_MAP = {
    "govt": "govt",
    "govt/gia": "gia",
    "gia": "gia",
    "government": "govt",
    "self-finance": "self_finance",
    "self-fin": "self_finance",
    "self finance": "self_finance",
    "pvt": "private",
    "private": "private",
    "a": "",  # unknown value in Round 1
}


class Command(BaseCommand):
    help = (
        "Import ACPC admission cutoff data from Excel files. "
        "Requires --round to specify which admission round (1, 2, or 3)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--round",
            type=int,
            required=True,
            choices=[1, 2, 3],
            help="Admission round number (1, 2, or 3).",
        )
        parser.add_argument(
            "--data-dir",
            type=str,
            required=True,
            help="Path to the folder containing the Excel file(s).",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=2025,
            help="Admission year to tag records with. Default: 2025.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete ALL existing data before importing.",
        )

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])
        round_num = options["round"]
        year = options["year"]

        if not data_dir.exists():
            raise CommandError(f"Data directory not found: {data_dir}")

        if options["clear"]:
            self.stdout.write(self.style.WARNING(
                "Clearing all existing data..."
            ))
            AdmissionCutoff.objects.all().delete()
            Course.objects.all().delete()
            University.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Cleared."))

        # Find the Excel file
        xlsx_files = list(data_dir.glob("*.xlsx"))
        if not xlsx_files:
            raise CommandError(
                f"No .xlsx files found in {data_dir}"
            )

        # Pick the first xlsx (or the one matching known patterns)
        filepath = xlsx_files[0]
        for f in xlsx_files:
            if "branch_wise" in f.name.lower() or "closure" in f.name.lower():
                filepath = f
                break

        self.stdout.write(
            f"Importing Round {round_num} data from: {filepath}"
        )

        self._import_cutoffs(filepath, round_num, year)
        self.stdout.write(self.style.SUCCESS("Import complete."))

    # ────────────────────────────────────────────────────────────────────
    #  Core import logic
    # ────────────────────────────────────────────────────────────────────

    def _import_cutoffs(self, filepath: Path, round_num: int, year: int):
        try:
            df = pd.read_excel(filepath, engine="openpyxl")
        except Exception as exc:
            raise CommandError(f"Failed to read Excel: {exc}")

        # ── Step 1: Normalize column names ────────────────────────────
        df.columns = [
            _COLUMN_MAP.get(c.strip().lower(), c.strip().lower())
            for c in df.columns
        ]

        # Validate required columns
        required = {"inst_name", "course_name", "cat_name", "closing"}
        missing = required - set(df.columns)
        if missing:
            raise CommandError(
                f"Missing required columns: {missing}. "
                f"Available: {list(df.columns)}"
            )

        # ── Step 2: Clean string columns ──────────────────────────────
        for col in ["inst_name", "course_name", "cat_name"]:
            df[col] = (
                df[col].astype(str).str.strip()
                .str.replace(r"[\n\r]+", " ", regex=True)
            )

        # ── Step 3: Normalize board ───────────────────────────────────
        if "board" in df.columns:
            df["board"] = (
                df["board"].astype(str).str.strip()
                .str.replace(r"[\n\r]+", " ", regex=True)
                .str.lower()
                .map(_BOARD_MAP)
                .fillna("")
            )
        else:
            df["board"] = ""

        # ── Step 4: Normalize category ────────────────────────────────
        df["cat_name"] = (
            df["cat_name"].str.lower()
            .map(_CATEGORY_MAP)
            .fillna(df["cat_name"].str.upper())
        )

        # ── Step 5: Normalize inst_type ───────────────────────────────
        if "inst_type" in df.columns:
            df["inst_type"] = (
                df["inst_type"].astype(str).str.strip()
                .str.replace(r"[\n\r]+", " ", regex=True)
                .str.lower()
                .map(_INST_TYPE_MAP)
                .fillna("")
            )
        else:
            df["inst_type"] = ""

        # ── Step 6: Coerce ranks to numeric ───────────────────────────
        df["closing"] = pd.to_numeric(df["closing"], errors="coerce")
        if "opening" in df.columns:
            df["opening"] = pd.to_numeric(df["opening"], errors="coerce")
        else:
            df["opening"] = None

        # Drop rows without a closing rank
        df = df.dropna(subset=["closing"])

        self.stdout.write(
            f"  Rows to process: {len(df)}"
        )

        # ── Step 7: Upsert into DB ───────────────────────────────────
        stats = {
            "unis_created": 0,
            "courses_created": 0,
            "cutoffs_created": 0,
            "cutoffs_updated": 0,
        }

        for _, row in df.iterrows():
            inst_name = row["inst_name"]
            course_name = row["course_name"]
            cat_name = row["cat_name"]
            board = row.get("board", "")
            inst_type = row.get("inst_type", "")
            opening = row.get("opening")
            closing = row["closing"]

            # Skip invalid rows
            if not inst_name or inst_name.lower() in ("nan", "none", ""):
                continue

            # University — get or create
            uni, created = University.objects.get_or_create(
                name=inst_name,
                defaults={
                    "location": inst_name,
                    "inst_type": inst_type,
                },
            )
            if created:
                stats["unis_created"] += 1
            elif inst_type and not uni.inst_type:
                # Update inst_type if it was empty
                uni.inst_type = inst_type
                uni.save(update_fields=["inst_type"])

            # Course — get or create
            course, created = Course.objects.get_or_create(
                university=uni,
                name=course_name,
            )
            if created:
                stats["courses_created"] += 1

            # Opening rank — handle NaN
            opening_val = (
                None if opening is None or pd.isna(opening)
                else float(opening)
            )

            # AdmissionCutoff — upsert
            _, created = AdmissionCutoff.objects.update_or_create(
                course=course,
                year=year,
                round=round_num,
                category=cat_name,
                board=board or "",
                defaults={
                    "opening_rank": opening_val,
                    "closing_rank": float(closing),
                },
            )
            if created:
                stats["cutoffs_created"] += 1
            else:
                stats["cutoffs_updated"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"  Universities created : {stats['unis_created']}\n"
            f"  Courses created      : {stats['courses_created']}\n"
            f"  Cutoffs created      : {stats['cutoffs_created']}\n"
            f"  Cutoffs updated      : {stats['cutoffs_updated']}"
        ))
