import pandas as pd
import regex

class AdmissionPredictor:
    def __init__(self, df, tolerance=50):
        """
        df: pandas DataFrame with columns:
            Inst_Name, Course_name, Cat_Name, Board, Inst_Type, Opening, Closing
        tolerance: int -> allowed rank difference above last year's closing rank
        """
        self.df = df.copy()
        self.tolerance = tolerance

        # Standardize column names and strip text
        self.df.columns = self.df.columns.str.strip()
        for col in ['Course_name', 'Cat_Name', 'Board']:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()

    def predict_colleges(self, student_rank, category=None, board=None, cource_preference=None):
        """
        Predict possible colleges for a given student rank, optional category & board.

        student_rank: int -> Student's rank
        category: str or list[str] -> Optional, e.g. 'GEN' or ['GEN', 'TFWs']
        board: str -> Optional, e.g. 'GUJCET' or 'JEE'

        Returns:
            Filtered and sorted DataFrame of eligible colleges.
        """

        filtered_df = self.df.copy()

        # Optional filtering by category
        if category:
            if isinstance(category, str):
                category = [category]  # make it a list for uniformity
            filtered_df = filtered_df[filtered_df['Cat_Name'].isin(category)]

        # Optional filtering by board
        if board:
            filtered_df = filtered_df[filtered_df['Board'].str.upper() == board.upper()]
            
        # Normalize columns
        filtered_df['Course_name'] = (
            filtered_df['Course_name']
            .str.replace(r'[\n\r]+', ' ', regex=True)
            .str.replace('-\s*TFWS', '', case=False, regex=True)
            .str.lower()
        )

        # Optional filtering by preferred course
        if cource_preference:
            if isinstance(cource_preference, str):
                cource_preference = [cource_preference]

            # Normalize input
            cource_preference = [c.lower().strip() for c in cource_preference]

            # Define related keywords mapping
            related_keywords = {
                "computer": [
                    "computer", "information technology", "it", "ai", "artificial intelligence", "data science",
                    "software", "cyber", "machine learning", "ict", "cloud", "blockchain", "big data",
                    "internet of things", "iot", "computing", "information & communication",
                    "information and communication", "business systems", "design"
                ],

                "aero": [
                    "aero", "aeronautical", "aerospace", "aviation"
                ],

                "agriculture": [
                    "agriculture", "agricultural", "farm", "food", "dairy", "biochemical", "irrigation"
                ],

                "artificial intelligence": [
                    "ai", "artificial intelligence", "machine learning", "ml", "data science",
                    "data", "deep learning", "intelligent systems"
                ],

                "automobile": [
                    "automobile", "auto", "vehicle", "mechanical", "transport", "mechatronics", "production"
                ],

                "biotech": [
                    "biotech", "biotechnology", "bio", "biomedical", "bioinformatics", "biochemical"
                ],

                "chemical": [
                    "chemical", "petrochemical", "environmental", "pharmaceutical", "green technology",
                    "sustainability", "polymer", "plastic", "rubber", "materials", "metallurgical"
                ],

                "civil": [
                    "civil", "construction", "infrastructure", "water management", "irrigation", "surveying",
                    "transportation", "structural", "urban", "environmental", "geo", "climate"
                ],

                "electrical": [
                    "electrical", "power", "power electronics", "electronics & electrical",
                    "energy", "renewable", "sustainable energy"
                ],

                "electronics": [
                    "electronics", "communication", "ece", "instrumentation", "control", "telecommunication",
                    "embedded", "vlsi", "signal", "microelectronics"
                ],

                "mechanical": [
                    "mechanical", "automobile", "production", "manufacturing", "mechatronics",
                    "robotics", "automation", "thermal", "design", "cad", "electric vehicle"
                ],

                "robotics": [
                    "robotics", "automation", "mechatronics", "ai", "machine learning", "intelligent systems"
                ],

                "marine": [
                    "marine", "ocean", "naval"
                ],

                "metallurgy": [
                    "metallurgy", "metallurgical", "materials", "foundry"
                ],

                "petroleum": [
                    "petroleum", "petrochemical", "chemical", "oil", "gas", "refinery"
                ],

                "pharmaceutical": [
                    "pharma", "pharmaceutical", "chemical", "biotech"
                ],

                "food": [
                    "food", "dairy", "processing", "agriculture", "agricultural"
                ],

                "environmental": [
                    "environmental", "climate", "sustainability", "green", "ecology", "energy", "civil"
                ],

                "energy": [
                    "energy", "power", "renewable", "sustainable", "solar", "electrical", "mechanical"
                ],

                "textile": [
                    "textile", "fabric", "cloth", "garment", "fiber", "processing"
                ],

                "plastic": [
                    "plastic", "polymer", "rubber", "chemical", "material"
                ],

                "production": [
                    "production", "manufacturing", "industrial", "mechanical"
                ],

                "fire": [
                    "fire", "safety", "environment", "health", "hazard", "industrial"
                ],

                "mathematics": [
                    "mathematics", "computing", "cs", "data science", "applied mathematics"
                ],

                "mining": [
                    "mining", "geology", "geoscience", "earth", "metallurgy"
                ],
            }

            # Expand preferences with related terms
            expanded_keywords = set()
            for pref in cource_preference:
                expanded_keywords.add(pref)
                for key, values in related_keywords.items():
                    if key in pref:
                        expanded_keywords.update(values)

            # Filter rows whose Course_name contains any of the expanded keywords
            filtered_df = filtered_df[
                filtered_df['Course_name'].str.lower().apply(
                    lambda x: any(term in x for term in expanded_keywords)
                )
            ]
        
        if filtered_df.empty:
            print("No matching colleges found with given filters.")
            return pd.DataFrame()


        # Ensure numeric ranks
        filtered_df['Opening'] = pd.to_numeric(filtered_df['Opening'], errors='coerce')
        filtered_df['Closing'] = pd.to_numeric(filtered_df['Closing'], errors='coerce')

        # # Apply filtering logic: include institutes where closing rank 
        # # is greater than or within tolerance of student's rank
        # eligible_df = filtered_df[
        #     (filtered_df['Closing'] + self.tolerance >= student_rank)
        #     # (filtered_df['Opening'] - self.tolerance <= student_rank)
        # ].copy()

        # # Sort by closing rank ascending
        # eligible_df = eligible_df.sort_values(by='Closing', ascending=True).reset_index(drop=True)
        # # eligible_df = eligible_df.sort_values(by='Opening', ascending=True).reset_index(drop=True)

        # Apply filtering logic: consider only colleges within extended range
        eligible_df = filtered_df[
            (student_rank >= filtered_df['Opening'] - self.tolerance) &
            (student_rank <= filtered_df['Closing'] + (self.tolerance * 10))
        ].copy()
        import pdb; pdb.set_trace()

        if eligible_df.empty:
            print("No colleges found within rank range.")
            # return pd.DataFrame()
            eligible_df = filtered_df.sort_values(by='Closing', ascending=True).head(15).copy()

        # Categorize based on proximity to closing rank
        def categorize(row):
            if student_rank < row['Closing'] - (self.tolerance * 2):
                return "Safe"
            elif row['Closing'] - (self.tolerance * 2) <= student_rank <= row['Closing'] + self.tolerance:
                return "Possible"
            else:
                return "Stretch"

        eligible_df['Chance'] = eligible_df.apply(categorize, axis=1)

        # Sort by chance type, then closing rank
        chance_order = {"Safe": 2, "Possible": 1, "Stretch": 0}
        eligible_df['ChanceOrder'] = eligible_df['Chance'].map(chance_order)
        eligible_df = eligible_df.sort_values(by=['ChanceOrder', 'Closing']).reset_index(drop=True) #.drop(columns=['ChanceOrder'])

        return eligible_df


if __name__ == "__main__":
    # === Step 1: Load data ===
    excel_path = r"C:\Users\Dell\Desktop\Elytraa\Analysis\FirstRound\Branch_Wise_First_and_Last_Admitted_Rank(12_06_2025)_all_pages_original.xlsx"

    df = pd.read_excel(excel_path)

    # Fix typo in column name if needed
    if 'Openinig' in df.columns:
        df.rename(columns={'Openinig': 'Opening'}, inplace=True)

    print(f"✅ Loaded data: {len(df)} rows")

    # === Step 2: Create predictor ===
    predictor = AdmissionPredictor(df, tolerance=50)  # You can adjust tolerance

    # === Step 3: Inputs ===
    student_rank = 30
    category = ['GEN']
    board = 'GUJCET'
    cource_preference = ['mechanical', 'computer']

    # === Step 4: Predict colleges ===
    eligible_universities = predictor.predict_colleges(
        student_rank=student_rank,
        category=category,
        board=board,
        cource_preference=cource_preference
    )

    # === Step 5: Display / Save ===
    print(f"\nFound {len(eligible_universities)} potential colleges for rank {student_rank}:")
    # print(eligible_universities[['Inst_Name', 'Course_name', 'Cat_Name', 'Board', 'Opening', 'Closing', 'ChanceOrder']])

    # Optional: Save results to Excel
    output_path = f"Predicted_Colleges_{student_rank}.xlsx"
    eligible_universities.to_excel(output_path, index=False)
    print(f"\nResults saved to: {output_path}")


    # cource_list = df['Course_name'].unique().tolist()
    
    # cource_list = ['AERO SPACE ENGINEERING', 'AERO SPACE ENGINEERING-TFWS', 'AERONAUTICAL ENGINEERING',
    #  'AERONAUTICAL ENGINEERING -\nTFWS', 'AGRICULTURAL ENGINEERING', 'AGRICULTURAL ENGINEERING -\nTFWS',
    #  'AGRICULTURAL TECHNOLOGY', 'ARTIFICIAL INTELLIGENCE AND DATA\nSCIENCE', 'ARTIFICIAL INTELLIGENCE AND DATA\nSCIENCE - TFWS',
    #  'ARTIFICIAL INTELLIGENCE(AI) AND\nMACHINE LEARNING', 'ARTIFICIAL INTELLIGENCE(AI) AND\nMACHINE LEARNING - TFW',
    #  'AUTOMOBILE ENGINEERING', 'AUTOMOBILE ENGINEERING - TFWS', 'BACHELOR OF TECHNOLOGY (HONS)\nIN CIVIL ENGINEERING (BCE)',
    #  'BACHELOR OF TECHNOLOGY (HONS)\nIN CIVIL ENGINEERING (BCE) - TFW', 'BIOINFORMATICS', 'BIOINFORMATICS - TFW',
    #  'BIOMEDICAL ENGINEERING', 'BIOMEDICAL ENGINEERING - TFWS', 'BIOTECHNOLOGY', 'BIOTECHNOLOGY - TFWS',
    #  'CHEMICAL & BIOCHEMICAL\nENGINEERING', 'CHEMICAL AND ENVIRONMENTAL\nENGINEERING', 'CHEMICAL AND ENVIRONMENTAL\nENGINEERING-TFWS',
    #  'CHEMICAL ENGINEERING', 'CHEMICAL ENGINEERING - TFWS', 'CHEMICAL ENGINEERING (GREEN\nTECHNOLOGY AND SUSTAINABILITY',
    #  'CHEMICAL TECHNOLOGY', 'CIVIL ENGINEERING', 'CIVIL ENGINEERING - TFWS', 'CIVIL ENGINEERING\n(CONSTRUCTION TECHNOLOGY)',
    #  'CIVIL ENGINEERING (SUSTAINABLE\nENERGY ENGINEERING)-TFWS', 'CIVIL IRRIGATION WATER\nMANAGEMENT', 'CLIMATE CHANGE',
    #  'CLOUD TECH &INFORMATION\nSECURITY', 'COMPUTER ENGINEERING', 'COMPUTER ENGINEERING - TFWS', 'COMPUTER ENGINEERING &\nAPPLICATION',
    #  'COMPUTER ENGINEERING\n(ARTIFICIAL INTELLIGENCE AND', 'COMPUTER ENGINEERING\n(ARTIFICIAL INTELLIGENCE AND\nMACHINE LEARNING)',
    #  'COMPUTER ENGINEERING\n(ARTIFICIAL INTELLIGENCE AND\nMACHINE LEARNING) - TFWS', 'COMPUTER ENGINEERING\n(ARTIFICIAL INTELLIGENCE)',
    #  'COMPUTER ENGINEERING\n(ARTIFICIAL INTELLIGENCE) - TFWS', 'COMPUTER ENGINEERING (CLOUD\nTECH. & INFO.SEC.)',
    #  'COMPUTER ENGINEERING (DATA\nSCIENCE)', 'COMPUTER ENGINEERING\n(SOFTWARE ENGINEERING)',
    #  'COMPUTER ENGINEERING\n(SOFTWARE ENGINEERING) - TFW', 'COMPUTER SCIENCE & BIOSCIENCES', 'COMPUTER SCIENCE & BIOSCIENCES\n- TFW',
    #  'COMPUTER SCIENCE & BUSINESS\nSYSTEMS', 'COMPUTER SCIENCE & BUSINESS\nSYSTEMS - TFW', 'COMPUTER SCIENCE & DESIGN',
    #  'COMPUTER SCIENCE & DESIGN -\nTFW', 'COMPUTER SCIENCE &\nENGINEERING', 'COMPUTER SCIENCE &\nENGINEERING - M.TECH',
    #  'COMPUTER SCIENCE &\nENGINEERING - TFWS', 'COMPUTER SCIENCE &\nENGINEERING (ARTIFICIAL',
    #  'COMPUTER SCIENCE &\nENGINEERING (ARTIFICIAL\nINTELLIGENCE AND MACHINE', 'COMPUTER SCIENCE &\nENGINEERING (ARTIFICIAL\nINTELLIGENCE)',
    #  'COMPUTER SCIENCE &\nENGINEERING (ARTIFICIAL\nINTELLIGENCE) - TFWS', 'COMPUTER SCIENCE &\nENGINEERING (BIG DATA',
    #  'COMPUTER SCIENCE &\nENGINEERING (BLOCK CHAIN', 'COMPUTER SCIENCE &\nENGINEERING (CLOUD COMPUTING)',
    #  'COMPUTER SCIENCE &\nENGINEERING (CYBER SECURITY)', 'COMPUTER SCIENCE &\nENGINEERING (CYBER SECURITY) -',
    #  'COMPUTER SCIENCE &\nENGINEERING (CYBER SECURITY) -\nTFWS', 'COMPUTER SCIENCE &\nENGINEERING (DATA SCIENCE)',
    #  'COMPUTER SCIENCE &\nENGINEERING (DATA SCIENCE) -', 'COMPUTER SCIENCE &\nENGINEERING (INTERNET OF\nTHINGS & CYBER SECURITY',
    #  'COMPUTER SCIENCE &\nENGINEERING (INTERNET OF', 'COMPUTER SCIENCE &\nINFORMATION TECHNOLOGY',
    #  'COMPUTER SCIENCE &\nINFORMATION TECHNOLOGY -', 'COMPUTER SCIENCE &\nTECHNOLOGY', 'COMPUTER SCIENCE &\nTECHNOLOGY - TFWS',
    #  'CYBER SECURITY', 'CYBER SECURITY -TFWS', 'DAIRY TECHNOLOGY', 'DAIRY TECHNOLOGY - TFWS', 'ELECTRICAL AND ELECTRONICS\nENGINEERING',
    #  'ELECTRICAL AND ELECTRONICS\nENGINEERING - TFWS', 'ELECTRICAL ENGINEERING', 'ELECTRICAL ENGINEERING - TFWS',
    #  'ELECTRICAL ENGINEERING\n(SUSTAINABLE ENERGY', 'ELECTRONICS & COMMUNICATION\n(COMMUNICATION SYSTEM ENGG.)',
    #  'ELECTRONICS & COMMUNICATION\nENGINEERING', 'ELECTRONICS & COMMUNICATION\nENGINEERING - TFWS',
    #  'ELECTRONICS & COMMUNICATION\nENGINEERING (ARTIFICIAL\nINTELLIGENCE AND MACHINE', 'ELECTRONICS & COMMUNICATION\nENGINEERING (VLSI DESIGN AND',
    #  'ELECTRONICS & INSTRUMENTATION\nENGINEERING', 'ELECTRONICS & INSTRUMENTATION\nENGINEERING - TFW', 'ELECTRONICS ENGINEERING',
    #  'ELECTRONICS ENGINEERING (VLSI\nDESIGN AND TECHNOLOGY)', 'ELECTRONICS ENGINEERING (VLSI\nDESIGN AND TECHNOLOGY) - TFW',
    #  'ELECTRONICS ENGINEERING-TFWS', 'ENERGY ENGINEERING', 'ENVIRONMENTAL ENGINEERING', 'ENVIRONMENTAL ENGINEERING -\nTFWS',
    #  'ENVIRONMENTAL SCIENCE &\nTECHNOLOGY', 'FIRE AND ENVIRONMENT, HEALTH,\nSAFETY ENGINEERING',
    #  'FIRE AND ENVIRONMENT, HEALTH,\nSAFETY ENGINEERING - TFWS', 'FOOD ENGINEERING AND\nTECHNOLOGY', 'FOOD PROCESSING TECHNOLOGY',
    #  'FOOD PROCESSING TECHNOLOGY -\nTFWS', 'FOOD TECHNOLOGY', 'FOOD TECHNOLOGY -TFW', 'HONS. IN ICT WITH MINOR IN\nCOMPUTATIONAL SCIENCE (CS)',
    #  'HONS. IN ICT WITH MINOR IN\nCOMPUTATIONAL SCIENCE (CS) -', 'INFORMATION & COMMUNICATION\nTECHNOLOGY',
    #  'INFORMATION & COMMUNICATION\nTECHNOLOGY - TFWS', 'INFORMATION TECHNOLOGY', 'INFORMATION TECHNOLOGY -\nTFWS',
    #  'INFORMATION TECHNOLOGY &\nENGINEERING', 'INSTRUMENTATION & CONTROL\nENGINEERING', 'INSTRUMENTATION & CONTROL\nENGINEERING - TFWS',
    #  'MANUFACTURING ENGINEERING', 'MARINE ENGINEERING', 'MATHEMATICS AND COMPUTING', 'MATHEMATICS AND COMPUTING -\nTFWS', 'MECHANICAL ENGINEERING',
    #  'MECHANICAL ENGINEERING - TFWS', 'MECHANICAL ENGINEERING\n(ELECTRIC VEHICLE)', 'MECHANICAL ENGINEERING\n(SUSTAINABLE ENERGY',
    #  'MECHATRONICS ENGINEERING', 'METALLURGICAL AND MATERIALS\nENGINEERING', 'METALLURGICAL AND MATERIALS\nENGINEERING - TFWS',
    #  'METALLURGICAL ENGINEERING', 'METALLURGY', 'MINING ENGINEERING', 'PETROCHEMICAL ENGINEERING', 'PETROLEUM ENGINEERING',
    #  'PETROLEUM ENGINEERING - TFWS', 'PHARMACEUTICAL ENGINEERING', 'PLASTIC AND POLYMER\nENGINEERING', 'PLASTIC ENGINEERING',
    #  'PLASTIC TECHNOLOGY', 'PLASTIC TECHNOLOGY-TFWS', 'POWER ELECTRONICS', 'POWER ELECTRONICS - TFWS', 'PRODUCTION ENGINEERING',
    #  'PRODUCTION ENGINEERING - TFWS', 'ROBOTICS & ARTIFICIAL\nINTELLIGENCE', 'ROBOTICS & ARTIFICIAL\nINTELLIGENCE - TFW',
    #  'ROBOTICS AND AUTOMATION', 'ROBOTICS AND AUTOMATION -\nTFWS', 'RUBBER TECHNOLOGY', 'RUBBER TECHNOLOGY - TFWS', 'TEXTILE ENGINEERING',
    #  'TEXTILE ENGINEERING - TFWS', 'TEXTILE PROCESSING', 'TEXTILE TECHNOLOGY', 'TEXTILE TECHNOLOGY - TFWS']