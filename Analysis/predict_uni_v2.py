"""
University Admission Predictor - Version 2.0

This module predicts eligible universities/colleges for students based on their
entrance exam rank, category, board, and course preferences.

Improvements over v1:
- PEP 8 compliant code
- Better error handling and input validation
- Improved algorithm efficiency
- Configurable parameters
- Type hints and comprehensive documentation
- Logging support
"""

import logging
from pathlib import Path
from typing import List, Optional, Union, Dict
import pandas as pd


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdmissionPredictor:
    """
    Predicts eligible universities for students based on admission criteria.

    Attributes:
        df (pd.DataFrame): Admission data with institute and course info
        tolerance (int): Rank buffer for eligibility calculations
        COURSE_KEYWORDS (dict): Mapping of course categories to related terms
    """

    # Class-level constant for course keyword mappings
    COURSE_KEYWORDS = {
        "computer": [
            "computer", "information technology", "it", "ai",
            "artificial intelligence", "data science", "software", "cyber",
            "machine learning", "ict", "cloud", "blockchain", "big data",
            "internet of things", "iot", "computing",
            "information & communication",
            "information and communication",
            "business systems", "design"
        ],
        "aero": [
            "aero", "aeronautical", "aerospace", "aviation"
        ],
        "agriculture": [
            "agriculture", "agricultural", "farm", "food", "dairy",
            "biochemical", "irrigation"
        ],
        "artificial intelligence": [
            "ai", "artificial intelligence", "machine learning", "ml",
            "data science", "data", "deep learning", "intelligent systems"
        ],
        "automobile": [
            "automobile", "auto", "vehicle", "mechanical", "transport",
            "mechatronics", "production"
        ],
        "biotech": [
            "biotech", "biotechnology", "bio", "biomedical",
            "bioinformatics", "biochemical"
        ],
        "chemical": [
            "chemical", "petrochemical", "environmental", "pharmaceutical",
            "green technology", "sustainability", "polymer", "plastic",
            "rubber", "materials", "metallurgical"
        ],
        "civil": [
            "civil", "construction", "infrastructure", "water management",
            "irrigation", "surveying", "transportation", "structural",
            "urban", "environmental", "geo", "climate"
        ],
        "electrical": [
            "electrical", "power", "power electronics",
            "electronics & electrical", "energy", "renewable",
            "sustainable energy"
        ],
        "electronics": [
            "electronics", "communication", "ece", "instrumentation",
            "control", "telecommunication", "embedded", "vlsi", "signal",
            "microelectronics"
        ],
        "mechanical": [
            "mechanical", "automobile", "production", "manufacturing",
            "mechatronics", "robotics", "automation", "thermal", "design",
            "cad", "electric vehicle"
        ],
        "robotics": [
            "robotics", "automation", "mechatronics", "ai",
            "machine learning", "intelligent systems"
        ],
        "marine": ["marine", "ocean", "naval"],
        "metallurgy": ["metallurgy", "metallurgical", "materials", "foundry"],
        "petroleum": [
            "petroleum", "petrochemical", "chemical", "oil", "gas", "refinery"
        ],
        "pharmaceutical": ["pharma", "pharmaceutical", "chemical", "biotech"],
        "food": ["food", "dairy", "processing", "agriculture", "agricultural"],
        "environmental": [
            "environmental", "climate", "sustainability", "green", "ecology",
            "energy", "civil"
        ],
        "energy": [
            "energy", "power", "renewable", "sustainable", "solar",
            "electrical", "mechanical"
        ],
        "textile": [
            "textile", "fabric", "cloth", "garment", "fiber", "processing"
        ],
        "plastic": ["plastic", "polymer", "rubber", "chemical", "material"],
        "production": [
            "production", "manufacturing", "industrial", "mechanical"
        ],
        "fire": [
            "fire", "safety", "environment", "health", "hazard", "industrial"
        ],
        "mathematics": [
            "mathematics", "computing", "cs", "data science",
            "applied mathematics"
        ],
        "mining": ["mining", "geology", "geoscience", "earth", "metallurgy"],
    }

    # Configuration constants
    SAFE_MULTIPLIER = 2
    STRETCH_MULTIPLIER = 10
    REQUIRED_COLUMNS = [
        'Inst_Name', 'Course_name', 'Cat_Name',
        'Board', 'Opening', 'Closing'
    ]

    def __init__(self, df: pd.DataFrame, tolerance: int = 50):
        """
        Initialize the AdmissionPredictor.

        Args:
            df: DataFrame with columns: Inst_Name, Course_name, Cat_Name,
                Board, Inst_Type, Opening, Closing
            tolerance: Rank buffer for eligibility (default: 50)

        Raises:
            ValueError: If required columns are missing
            TypeError: If df is not a DataFrame
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")

        if df.empty:
            raise ValueError("DataFrame cannot be empty")

        # Validate required columns
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}"
            )

        self.df = df.copy()
        self.tolerance = tolerance

        # Standardize column names and strip text
        self.df.columns = self.df.columns.str.strip()
        for col in ['Course_name', 'Cat_Name', 'Board']:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()

        # Ensure numeric ranks
        self.df['Opening'] = pd.to_numeric(
            self.df['Opening'], errors='coerce'
        )
        self.df['Closing'] = pd.to_numeric(
            self.df['Closing'], errors='coerce'
        )

        # Remove rows with invalid ranks
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=['Opening', 'Closing'])
        removed = initial_count - len(self.df)
        if removed > 0:
            logger.warning(
                f"Removed {removed} rows with invalid rank data"
            )

        logger.info(f"Initialized predictor with {len(self.df)} records")

    def _normalize_course_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize course names for consistent matching.

        Args:
            df: DataFrame with Course_name column

        Returns:
            DataFrame with normalized Course_name
        """
        df = df.copy()
        df['Course_name'] = (
            df['Course_name']
            .str.replace(r'[\n\r]+', ' ', regex=True)
            .str.replace(r'-\s*TFWS', '', case=False, regex=True)
            .str.lower()
        )
        return df

    def _expand_course_keywords(
        self,
        preferences: List[str]
    ) -> Dict[str, List[str]]:
        """
        Expand course preferences to include related keywords.

        Args:
            preferences: List of course preference strings

        Returns:
            Dictionary mapping each preference to its expanded keywords
        """
        expanded = {}
        for pref in preferences:
            pref_lower = pref.lower().strip()
            # Get related keywords or use the preference itself
            keywords = self.COURSE_KEYWORDS.get(pref_lower, [pref_lower])
            expanded[pref] = keywords
        return expanded

    def _filter_by_course(
        self,
        df: pd.DataFrame,
        keywords: List[str]
    ) -> pd.DataFrame:
        """
        Filter DataFrame by course keywords.

        Args:
            df: DataFrame to filter
            keywords: List of keywords to match

        Returns:
            Filtered DataFrame
        """
        mask = df['Course_name'].apply(
            lambda x: any(term in x for term in keywords)
        )
        return df[mask]

    def _categorize_chance(
        self,
        student_rank: int,
        closing_rank: float
    ) -> str:
        """
        Categorize admission chance based on rank proximity.

        Args:
            student_rank: Student's entrance exam rank
            closing_rank: College's closing rank

        Returns:
            Chance category: "Safe", "Possible", or "Stretch"
        """
        safe_threshold = closing_rank - (self.tolerance * self.SAFE_MULTIPLIER)

        if student_rank < safe_threshold:
            return "Safe"
        elif student_rank <= closing_rank + self.tolerance:
            return "Possible"
        else:
            return "Stretch"

    def predict_colleges(
        self,
        student_rank: int,
        category: Optional[Union[str, List[str]]] = None,
        board: Optional[str] = None,
        course_preference: Optional[List[str]] = None,
        min_results: int = 15
    ) -> pd.DataFrame:
        """
        Predict eligible colleges for a student.

        Args:
            student_rank: Student's entrance exam rank
            category: Reservation category (e.g., 'GEN', ['GEN', 'TFWs'])
            board: Exam board ('GUJCET' or 'JEE')
            course_preference: List of preferred courses
                              (e.g., ['computer', 'mechanical'])
            min_results: Minimum results per course preference

        Returns:
            DataFrame with eligible colleges, sorted by chance and rank

        Raises:
            ValueError: If student_rank is invalid
        """
        # Input validation
        if not isinstance(student_rank, int) or student_rank <= 0:
            raise ValueError("student_rank must be a positive integer")

        if min_results <= 0:
            raise ValueError("min_results must be positive")

        logger.info(
            f"Predicting colleges for rank {student_rank}, "
            f"category={category}, board={board}"
        )

        # Start with full dataset
        filtered_df = self.df.copy()

        # Filter by category
        if category:
            if isinstance(category, str):
                category = [category]
            filtered_df = filtered_df[
                filtered_df['Cat_Name'].isin(category)
            ]
            logger.info(
                f"After category filter: {len(filtered_df)} records"
            )

        # Filter by board
        if board:
            filtered_df = filtered_df[
                filtered_df['Board'].str.upper() == board.upper()
            ]
            logger.info(f"After board filter: {len(filtered_df)} records")

        if filtered_df.empty:
            logger.warning("No colleges found after filtering")
            return pd.DataFrame()

        # Normalize course names
        filtered_df = self._normalize_course_names(filtered_df)

        # Handle course preferences
        if not course_preference:
            course_preference = list(self.COURSE_KEYWORDS.keys())
            logger.info("No preferences specified, using all courses")
        elif 'all' in [c.lower() for c in course_preference]:
            course_preference = list(self.COURSE_KEYWORDS.keys())
            logger.info("'all' specified, using all courses")

        # Expand keywords for each preference
        expanded_keywords = self._expand_course_keywords(course_preference)

        results = []

        # Process each course preference
        for pref, keywords in expanded_keywords.items():
            logger.info(f"Processing preference: {pref}")

            # Filter by course
            subset_df = self._filter_by_course(filtered_df, keywords)

            if subset_df.empty:
                logger.warning(f"No matches for preference: {pref}")
                continue

            # Filter by rank eligibility
            eligible_df = subset_df[
                (student_rank >= subset_df['Opening'] - self.tolerance) &
                (student_rank <= subset_df['Closing'] +
                 (self.tolerance * self.STRETCH_MULTIPLIER))
            ].copy()

            # If insufficient results, add top colleges by closing rank
            if len(eligible_df) < min_results:
                logger.info(
                    f"Only {len(eligible_df)} eligible for {pref}, "
                    f"adding top colleges"
                )
                top_colleges = subset_df.nsmallest(min_results, 'Closing')
                eligible_df = pd.concat(
                    [eligible_df, top_colleges]
                ).drop_duplicates(subset=['Inst_Name', 'Course_name'])

            # Limit to min_results
            eligible_df = eligible_df.head(min_results)

            # Categorize chances
            eligible_df['Chance'] = eligible_df['Closing'].apply(
                lambda x: self._categorize_chance(student_rank, x)
            )
            eligible_df['Preferred_Course'] = pref.capitalize()

            # Sort by chance and closing rank
            chance_order = {"Safe": 2, "Possible": 1, "Stretch": 0}
            eligible_df['ChanceOrder'] = eligible_df['Chance'].map(
                chance_order
            )
            eligible_df = eligible_df.sort_values(
                by=['ChanceOrder', 'Closing']
            )

            results.append(eligible_df)
            logger.info(f"Found {len(eligible_df)} colleges for {pref}")

        # Combine all results
        if results:
            final_df = pd.concat(results, ignore_index=True)
            logger.info(
                f"Total predictions: {len(final_df)} colleges"
            )
            return final_df
        else:
            logger.warning("No matching colleges found for any preference")
            return pd.DataFrame()

    def save_results(
        self,
        results: pd.DataFrame,
        output_path: Union[str, Path],
        separate_sheets: bool = True
    ) -> None:
        """
        Save prediction results to Excel file.

        Args:
            results: DataFrame with prediction results
            output_path: Path to save Excel file
            separate_sheets: If True, create separate sheets per course

        Raises:
            ValueError: If results DataFrame is empty
        """
        if results.empty:
            raise ValueError("Cannot save empty results")

        output_path = Path(output_path)

        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                if separate_sheets and 'Preferred_Course' in results.columns:
                    # Create sheet per course
                    for course, group in results.groupby('Preferred_Course'):
                        sheet_name = str(course)[:31]  # Excel limit
                        group.to_excel(
                            writer, sheet_name=sheet_name, index=False
                        )

                # Always include combined results
                results.to_excel(writer, sheet_name='All_Results', index=False)

            logger.info(f"Results saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise


def main():
    """Example usage of AdmissionPredictor."""
    # Configuration
    data_path = Path(__file__).parent / "FirstRound" / \
        "Branch_Wise_First_and_Last_Admitted_Rank(12_06_2025)" \
        "_all_pages_original.xlsx"

    # Load data
    try:
        df = pd.read_excel(data_path)
        logger.info(f"Loaded data: {len(df)} rows")
    except FileNotFoundError:
        logger.error(f"Data file not found: {data_path}")
        return
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return

    # Fix typo in column name if needed
    if 'Openinig' in df.columns:
        df.rename(columns={'Openinig': 'Opening'}, inplace=True)

    # Create predictor
    try:
        predictor = AdmissionPredictor(df, tolerance=50)
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to create predictor: {e}")
        return

    # Student inputs
    student_rank = 3000
    category = ['GEN']
    board = 'GUJCET'
    course_preference = ['mechanical', 'computer']

    # Predict colleges
    try:
        results = predictor.predict_colleges(
            student_rank=student_rank,
            category=category,
            board=board,
            course_preference=course_preference,
            min_results=15
        )
    except ValueError as e:
        logger.error(f"Prediction failed: {e}")
        return

    # Display results
    if not results.empty:
        print(f"\nFound {len(results)} potential colleges "
              f"for rank {student_rank}:")
        print(results[[
            'Inst_Name', 'Course_name', 'Cat_Name',
            'Board', 'Opening', 'Closing', 'Chance'
        ]].to_string())

        # Save results
        output_path = Path(f"Predicted_Colleges_{student_rank}_v2.xlsx")
        try:
            predictor.save_results(results, output_path)
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    else:
        print("No colleges found matching criteria")


if __name__ == "__main__":
    main()
