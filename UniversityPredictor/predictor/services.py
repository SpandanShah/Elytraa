"""
predictor/services.py

Core business logic for the University Predictor.
Adapted from Analysis/predict_uni_v2.py (AdmissionPredictor class)
to use Django ORM instead of pandas DataFrames.
"""

import logging
from django.db.models import F, Q
from django.db.models.functions import Abs

from .models import University, Course, AdmissionCutoff, ScoreWeight

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Predicts eligible universities for a student based on entrance exam rank,
    category, board, and course preferences.

    Mirrors AdmissionPredictor from Analysis/predict_uni_v2.py but reads from
    PostgreSQL via Django ORM instead of an Excel DataFrame.
    """

    # Copied verbatim from predict_uni_v2.py lines 41-129
    COURSE_KEYWORDS = {
        "computer": [
            "computer", "information technology", "it", "ai",
            "artificial intelligence", "data science", "software", "cyber",
            "machine learning", "ict", "cloud", "blockchain", "big data",
            "internet of things", "iot", "computing",
            "information & communication",
            "information and communication",
            "business systems", "design",
        ],
        "aero": [
            "aero", "aeronaut", "aerospace", "aviation",
        ],
        "agriculture": [
            "agricultur", "farm", "food", "dairy",
            "biochem", "irrigation",
        ],
        "artificial intelligence": [
            "ai", "artificial intelligence", "machine learning", "ml",
            "data science", "data", "deep learning", "intelligent systems",
        ],
        "automobile": [
            "automobile", "auto", "vehicle", "mechanical", "transport",
            "mechatronics", "production",
        ],
        "biotech": [
            "biotech", "bio", "biomedic",
            "bioinformat", "biochem",
        ],
        "chemical": [
            "chemical", "petrochem", "environ", "pharmac",
            "green technology", "sustainab", "polymer", "plastic",
            "rubber", "material", "metallurg",
        ],
        "civil": [
            "civil", "construct", "infrastructure", "water management",
            "irrigation", "survey", "transport", "structural",
            "urban", "environ", "geo", "climate",
        ],
        "electrical": [
            "electrical", "power", "power electronics",
            "electronics & electrical", "energy", "renew",
            "sustainable energy",
        ],
        "electronics": [
            "electronics", "communic", "ece", "instrument",
            "control", "telecomm", "embedded", "vlsi", "signal",
            "microelectron",
        ],
        "mechanical": [
            "mechanical", "automobile", "production", "manufactur",
            "mechatron", "robot", "automat", "thermal", "design",
            "cad", "electric vehicle",
        ],
        "robotics": [
            "robot", "automat", "mechatron", "ai",
            "machine learning", "intelligent systems",
        ],
        "marine": ["marine", "ocean", "naval"],
        "metallurgy": ["metallurg", "material", "foundry"],
        "petroleum": [
            "petroleum", "petrochem", "chemical", "oil", "gas", "refinery",
        ],
        "pharmaceutical": ["pharma", "pharmac", "chemical", "biotech"],
        "food": ["food", "dairy", "processing", "agricultur"],
        "environmental": [
            "environ", "climate", "sustainab", "green", "ecology",
            "energy", "civil",
        ],
        "energy": [
            "energy", "power", "renew", "sustainab", "solar",
            "electrical", "mechanical",
        ],
        "textile": [
            "textile", "fabric", "cloth", "garment", "fiber", "processing",
        ],
        "plastic": ["plastic", "polymer", "rubber", "chemical", "material"],
        "production": [
            "production", "manufactur", "industrial", "mechanical",
        ],
        "fire": [
            "fire", "safety", "environ", "health", "hazard", "industrial",
        ],
        "mathematics": [
            "mathemat", "computing", "cs", "data science",
            "applied math",
        ],
        "mining": ["mining", "geolog", "geoscien", "earth", "metallurg"],
    }

    def __init__(self):
        config = ScoreWeight.get_instance()
        self.tolerance = config.tolerance
        self.safe_multiplier = config.safe_multiplier
        self.stretch_multiplier = config.stretch_multiplier
        self._config = config

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def predict(
        self,
        student_rank,
        category=None,
        board=None,
        course_preferences=None,
        min_results=15,
        round_num=None,
        inst_types=None,
        districts=None,
    ):
        """
        Predict eligible colleges for a student.

        Args:
            student_rank (int): Entrance exam rank. Must be > 0.
            category (str | list | None): Reservation category e.g. 'GEN' or ['GEN','TFWS'].
            board (str | None): Exam board, e.g. 'GUJCET' or 'JEE'.
            course_preferences (list[str] | None): Preferred course keywords.
            min_results (int): Minimum results to return per course preference.
            round_num (int | None): ACPC admission round (1, 2, or 3).
            inst_types (list[str] | None): Institute types to filter by (staff-only).
            districts (list[str] | None): Districts/cities to filter by (staff-only).

        Returns:
            list[dict]: Sorted results (Safe first, then Possible, then Stretch).
                Each dict:
                    inst_name, course_name, category, board,
                    opening_rank, closing_rank, chance,
                    preferred_course, university_score, round
        """
        if not isinstance(student_rank, int) or student_rank <= 0:
            raise ValueError("student_rank must be a positive integer")

        logger.info(
            "Predicting for rank=%s category=%s board=%s round=%s",
            student_rank, category, board, round_num,
        )

        # -- Step 1: Base queryset ----------------------------------------
        qs = AdmissionCutoff.objects.select_related(
            "course", "course__university"
        ).filter(closing_rank__isnull=False)

        # -- Step 1b: Filter by round -------------------------------------
        if round_num:
            qs = qs.filter(round=round_num)
            logger.info("Filtering for round %d", round_num)

        # -- Step 2: Filter by category ------------------------------------
        if category:
            if isinstance(category, str):
                category = [category]
            category = [c.strip() for c in category if c.strip()]
            if category:
                qs = qs.filter(category__in=category)
                logger.info("After category filter: %d records", qs.count())

        # -- Step 3: Filter by board ---------------------------------------
        if board and board.strip():
            qs = qs.filter(board__iexact=board.strip())
            logger.info("After board filter: %d records", qs.count())

        # -- Step 3b: Filter by institute type (staff-only) ----------------
        if inst_types:
            cleaned = [t.strip() for t in inst_types if t.strip()]
            if cleaned:
                qs = qs.filter(course__university__inst_type__in=cleaned)
                logger.info("After inst_type filter: %d records", qs.count())

        # -- Step 3c: Filter by district (staff-only) ----------------------
        # Include colleges with empty location (unknown district)
        if districts:
            cleaned = [d.strip() for d in districts if d.strip()]
            if cleaned:
                qs = qs.filter(
                    Q(course__university__location__in=cleaned)
                    | Q(course__university__location="")
                    | Q(course__university__location__isnull=True)
                )
                logger.info("After district filter: %d records", qs.count())

        # -- Step 4: Resolve course preferences ----------------------------
        if not course_preferences:
            course_preferences = list(self.COURSE_KEYWORDS.keys())
        elif "all" in [c.lower() for c in course_preferences]:
            course_preferences = list(self.COURSE_KEYWORDS.keys())

        # -- Step 5: Expand keywords ---------------------------------------
        expanded = {}
        for pref in course_preferences:
            pref_lower = pref.lower().strip()
            expanded[pref] = self.COURSE_KEYWORDS.get(pref_lower, [pref_lower])

        # -- Step 6: Process each preference -------------------------------
        results = []
        seen = set()  # (inst_name, course_name) dedup across preferences

        for pref, keywords in expanded.items():
            logger.info("Processing preference: %s", pref)

            # Build OR filter across all keywords
            course_filter = Q()
            for kw in keywords:
                course_filter |= Q(course__name__icontains=kw)

            subset = qs.filter(course_filter)
            if not subset.exists():
                logger.warning("No matches for preference: %s", pref)
                continue

            # Determine if student rank is beyond all closing ranks
            # for this subset (i.e., rank is worse than every college)
            max_closing = subset.order_by("-closing_rank").values_list(
                "closing_rank", flat=True
            ).first()
            rank_beyond_all = (
                max_closing is not None
                and student_rank > max_closing + (self.tolerance * self.stretch_multiplier)
            )

            if rank_beyond_all:
                # Approach C: rank exceeds all closing ranks — show closest
                # matches sorted by proximity to student rank
                # Cap at 3000 rank distance to avoid unrealistic results
                logger.info(
                    "Rank %d exceeds max closing %s for %s, "
                    "using proximity sort",
                    student_rank, max_closing, pref,
                )
                max_distance = 3000

                eligible = (
                    subset.annotate(
                        rank_distance=Abs(F("closing_rank") - student_rank)
                    )
                    .filter(rank_distance__lte=max_distance)
                    .order_by("rank_distance")[:min_results]
                )
            else:
                # Normal eligibility window
                eligible = subset.filter(
                    closing_rank__gte=student_rank - (self.tolerance * self.stretch_multiplier),
                ).order_by("closing_rank")

                # Fallback: if too few results, add colleges closest
                # to student rank from below (descending from student rank)
                if eligible.count() < min_results:
                    logger.info(
                        "Only %d eligible for %s, adding closest below",
                        eligible.count(), pref,
                    )
                    # Get colleges with closing_rank below eligibility window
                    # ordered by closest to student rank (descending closing)
                    fallback_ids = list(
                        subset.filter(
                            closing_rank__lt=student_rank - (self.tolerance * self.stretch_multiplier)
                        )
                        .order_by("-closing_rank")
                        .values_list("id", flat=True)[:min_results]
                    )
                    eligible_ids = list(
                        eligible.values_list("id", flat=True)
                    )
                    combined_ids = list(set(eligible_ids + fallback_ids))
                    eligible = AdmissionCutoff.objects.filter(
                        id__in=combined_ids
                    ).select_related(
                        "course", "course__university"
                    ).order_by("-closing_rank")

            count = 0
            for cutoff in eligible:
                if count >= min_results:
                    break

                key = (cutoff.course.university.name, cutoff.course.name)
                if key in seen:
                    continue
                seen.add(key)

                chance = self._categorize_chance(student_rank, cutoff.closing_rank)
                score = self._calculate_university_score(
                    cutoff.course.university, cutoff.course
                )

                results.append({
                    "inst_name": cutoff.course.university.name,
                    "course_name": cutoff.course.name,
                    "category": cutoff.category,
                    "board": cutoff.board or "",
                    "opening_rank": cutoff.opening_rank,
                    "closing_rank": cutoff.closing_rank,
                    "chance": chance,
                    "preferred_course": pref.capitalize(),
                    "university_score": score,
                    "round": cutoff.round,
                    "inst_type": cutoff.course.university.inst_type or "",
                })
                count += 1

            logger.info("Found %d colleges for %s", count, pref)

        # -- Step 7: Sort: Safe → Possible → Stretch, then closing rank ---
        chance_order = {"Safe": 0, "Possible": 1, "Stretch": 2}
        results.sort(
            key=lambda x: (chance_order.get(x["chance"], 3), x["closing_rank"])
        )

        logger.info("Total predictions: %d", len(results))
        return results

    @staticmethod
    def get_available_options():
        """
        Returns distinct categories, boards, rounds, and course keywords
        for populating frontend dropdowns.
        """
        categories = sorted(
            AdmissionCutoff.objects.values_list("category", flat=True)
            .exclude(category="").exclude(category__isnull=True)
            .distinct()
        )
        boards = sorted(
            AdmissionCutoff.objects.values_list("board", flat=True)
            .exclude(board="").exclude(board__isnull=True)
            .distinct()
        )
        rounds = sorted(
            AdmissionCutoff.objects.values_list("round", flat=True)
            .distinct()
        )
        course_keywords = [
            kw.capitalize()
            for kw in PredictionService.COURSE_KEYWORDS.keys()
        ]

        inst_types = sorted(
            University.objects.values_list("inst_type", flat=True)
            .exclude(inst_type="").exclude(inst_type__isnull=True)
            .distinct()
        )

        districts = sorted(
            University.objects.values_list("location", flat=True)
            .exclude(location="").exclude(location__isnull=True)
            .distinct()
        )

        return {
            "categories": list(categories),
            "boards": list(boards),
            "rounds": list(rounds),
            "course_keywords": course_keywords,
            "inst_types": list(inst_types),
            "districts": list(districts),
        }

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _categorize_chance(self, student_rank, closing_rank):
        """
        Mirrors AdmissionPredictor._categorize_chance (predict_uni_v2.py lines 253-275).

        Safe     — rank is well below closing (student has high chance)
        Possible — rank is within tolerance window of closing
        Stretch  — rank is above closing but within stretch window
        """
        safe_threshold = closing_rank - (self.tolerance * self.safe_multiplier)
        if student_rank < safe_threshold:
            return "Safe"
        elif student_rank <= closing_rank + self.tolerance:
            return "Possible"
        else:
            return "Stretch"

    def _calculate_university_score(self, university, course):
        """
        Weighted composite score from README.md formula:
            FinalScore = Infra*15 + Course*30 + ExtraCurricular*10
                       + Patent*10 + Fees*15 + Alumni*10 + Degree*10
        Returns normalized 0-10 float.
        """
        cfg = self._config

        infra_avg = (
            float(university.infra_labs_score)
            + float(university.infra_sports_score)
            + float(university.infra_premises_score)
        ) / 3.0

        course_avg = (
            float(course.faculty_research_score)
            + float(course.faculty_experience_score)
            + float(course.curriculum_score)
        ) / 3.0

        raw = (
            infra_avg * cfg.infra_weight
            + course_avg * cfg.course_weight
            + float(university.extra_curricular_score) * cfg.extra_curricular_weight
            + float(university.patent_score) * cfg.patent_weight
            + float(university.alumni_score) * cfg.alumni_weight
            + float(course.degree_score) * cfg.degree_weight
        )

        # Weights sum to 100 and each score is 0-10, so raw max = 1000
        # Normalize back to 0-10
        return round(raw / 100.0, 2)
