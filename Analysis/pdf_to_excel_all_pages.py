import tabula
import pandas as pd
import os
import fitz  # PyMuPDF
import pdb


class PDFToExcelConverter:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.cropped_pdf_path = None

    def crop_pdf(self, crop_top_first=100, crop_top_others=103):
        """
        Crops the PDF:
        - First page cropped by 'crop_top_first' points.
        - Remaining pages cropped by 'crop_top_others' points.
        (1 pt = 1/72 inch)
        Saves the cropped PDF as a temporary file.
        """
        try:
            doc = fitz.open(self.pdf_path)
            cropped_path = os.path.splitext(self.pdf_path)[0] + "_cropped.pdf"

            for page_index, page in enumerate(doc, start=1):
                rect = page.rect

                # Choose crop amount based on page number
                if page_index == 1:
                    crop_top = crop_top_first
                else:
                    crop_top = crop_top_others

                # Define new rectangle by trimming the top
                new_rect = fitz.Rect(
                    rect.x0, rect.y0 + crop_top, rect.x1, rect.y1
                )
                page.set_cropbox(new_rect)

            doc.save(cropped_path)
            doc.close()
            self.cropped_pdf_path = cropped_path
            print(f"✂️ Cropped PDF saved at: {cropped_path}")

        except Exception as e:
            print(f"Error cropping PDF: {e}")
            self.cropped_pdf_path = None

    def crop_pdf_old(self, crop_top=100):
        """
        Crops the top part of each page of the PDF by 'crop_top' points
        (1 pt = 1/72 inch).
        Saves the cropped PDF as a temporary file.
        """
        try:
            doc = fitz.open(self.pdf_path)
            cropped_path = os.path.splitext(self.pdf_path)[0] + "_cropped.pdf"

            for page in doc:
                rect = page.rect
                # Define new rectangle by trimming the top
                new_rect = fitz.Rect(
                    rect.x0, rect.y0 + crop_top, rect.x1, rect.y1
                )
                page.set_cropbox(new_rect)

            doc.save(cropped_path)
            doc.close()
            self.cropped_pdf_path = cropped_path
            print(f"✂️ Cropped PDF saved at: {cropped_path}")

        except Exception as e:
            print(f"Error cropping PDF: {e}")
            self.cropped_pdf_path = None

    def read_all_pages(self):
        """
        Reads all pages of the cropped PDF into a single
        concatenated DataFrame.
        """
        try:
            pdf_to_read = self.cropped_pdf_path or self.pdf_path

            # Read all pages
            dfs = tabula.read_pdf(
                pdf_to_read, pages='all', multiple_tables=False
            )
            pdb.set_trace()

            if not dfs or len(dfs) == 0:
                raise ValueError("No tables found in the PDF.")

            # Concatenate all DataFrames into one
            combined_df = pd.concat(dfs, ignore_index=True)
            print(f"📄 Combined {len(dfs)} pages into one DataFrame.")

            return combined_df
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    def save_to_excel(self, df, output_path=None):
        """Saves the DataFrame to an Excel file."""
        if df is None:
            print("No data to save.")
            return

        if output_path is None:
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            output_path = f"{base_name}_all_pages_1.xlsx"

        try:
            df.to_excel(output_path, index=False)
            print(f"✅ Excel file saved as: {output_path}")
        except Exception as e:
            print(f"Error saving Excel file: {e}")


if __name__ == "__main__":
    # ##########################################
    # # Branch Wise First and Last Admitted Rank
    # pdf_path = r"C:\Users\Dell\Desktop\Elytraa\Analysis\FirstRound\"
    # "Branch_Wise_First_and_Last_Admitted_Rank(12_06_2025).pdf"

    # converter = PDFToExcelConverter(pdf_path)
    # # Crop first page by 100 pts, rest by 103 pts
    # converter.crop_pdf(crop_top_first=100, crop_top_others=103)
    # ##########################################

    # ##########################################
    # # Institute Wise Program Wise Intake Admitted
    # pdf_path = r"C:\Users\Dell\Desktop\Elytraa\Analysis\FirstRound\"
    # "Institute_Wise_Program_Wise_Intake_Admitted(12_06_2025).pdf"

    # converter = PDFToExcelConverter(pdf_path)
    # # Crop first page by 90 pts, rest by 100 pts
    # converter.crop_pdf(crop_top_first=90, crop_top_others=100)
    # ##########################################

    # ##########################################
    # pdf_path = r"C:\Users\Dell\Desktop\Elytraa\Analysis\FirstRound\"
    # "Institute_Wise_Program_Wise_Intake_and_Reported_after_completion_of_Round_1.pdf"

    # converter = PDFToExcelConverter(pdf_path)
    # # Crop first page by 90 pts, rest by 100 pts
    # converter.crop_pdf(crop_top_first=80, crop_top_others=90)
    # ##########################################

    # ##########################################
    # Branch Wise First and Last Admitted Rank Round 3
    pdf_path = r"C:/Users/Dell/Desktop/Elytraa/Analysis/ThirdRound/Round_3_Analysis_Closure_Institute_Wise_Program_Wise.pdf"

    converter = PDFToExcelConverter(pdf_path)
    # Crop first page by 100 pts, rest by 103 pts
    converter.crop_pdf(crop_top_first=80, crop_top_others=90)
    # ##########################################

    df = converter.read_all_pages()
    converter.save_to_excel(df)
