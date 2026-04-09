import tabula
import pandas as pd
import os
import fitz  # PyMuPDF
import pdb

class PDFToExcelConverter:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.cropped_pdf_path = None

    def crop_pdf(self, crop_top=100):
        """
        Crops the top part of each page of the PDF by 'crop_top' points (1 pt = 1/72 inch).
        Saves the cropped PDF as a temporary file.
        """
        try:
            doc = fitz.open(self.pdf_path)
            cropped_path = os.path.splitext(self.pdf_path)[0] + "_cropped.pdf"
            
            for page in doc:
                rect = page.rect
                # Define new rectangle by trimming the top
                new_rect = fitz.Rect(rect.x0, rect.y0 + crop_top, rect.x1, rect.y1)
                page.set_cropbox(new_rect)
            
            doc.save(cropped_path)
            doc.close()
            self.cropped_pdf_path = cropped_path
            print(f"✂️ Cropped PDF saved at: {cropped_path}")
        
        except Exception as e:
            print(f"Error cropping PDF: {e}")
            self.cropped_pdf_path = None

    def read_first_page(self):
        """Reads the first page of the cropped PDF into a pandas DataFrame."""
        try:
            pdf_to_read = self.cropped_pdf_path or self.pdf_path
            
            dfs = tabula.read_pdf(pdf_to_read, pages=1, multiple_tables=False)
            pdb.set_trace()
            
            if not dfs or len(dfs) == 0:
                raise ValueError("No tables found on the first page of the PDF.")
            
            return dfs[0]
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
            output_path = f"{base_name}_page1.xlsx"
        
        try:
            df.to_excel(output_path, index=False)
            print(f"✅ Excel file saved as: {output_path}")
        except Exception as e:
            print(f"Error saving Excel file: {e}")

if __name__ == "__main__":
    pdf_path = r"C:\Users\Dell\Desktop\Elytraa\Analysis\FirstRound\Branch_Wise_First_and_Last_Admitted_Rank(12_06_2025).pdf"
    
    converter = PDFToExcelConverter(pdf_path)
    converter.crop_pdf(crop_top=100)  # Crop top 100 points (~1.4 inches)
    df = converter.read_first_page()
    converter.save_to_excel(df)
