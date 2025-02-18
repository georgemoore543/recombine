"""
Clean Prefixes - Post-processing script for recombine.py output

This script removes common prefixes like "Problem Statement:", "Opportunity:", etc. 
from the generated prompts in an Excel file.
"""

import pandas as pd
from tkinter import Tk, filedialog
from pathlib import Path

def select_file(title, file_types, save=False):
    """Open a file dialog to select a file."""
    root = Tk()
    root.withdraw()  # Hide the main window
    
    try:
        if save:
            file_path = filedialog.asksaveasfilename(
                title=title,
                filetypes=file_types,
                defaultextension=".xlsx"
            )
        else:
            file_path = filedialog.askopenfilename(
                title=title,
                filetypes=file_types
            )
        
        return file_path if file_path else None
    except Exception as e:
        print(f"Error selecting file: {str(e)}")
        return None
    finally:
        root.destroy()

def clean_text(text):
    """Remove common prefixes from generated text."""
    if not isinstance(text, str):
        return text
        
    prefixes = [
        "Problem Statement:", 
        "Opportunity:", 
        "Solution:", 
        "Insight:", 
        "Problem:",
        "Observation:"
    ]
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lstrip()
    
    for prefix in prefixes:
        if text_lower.lower().startswith(prefix.lower()):
            return text[len(prefix):].lstrip()
    
    return text

def main():
    # Select input file
    input_file = select_file(
        "Select Input Excel File",
        [("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    
    if not input_file:
        print("No input file selected. Exiting...")
        return
        
    try:
        # Read the Excel file
        df = pd.read_excel(input_file)
        
        if "Prompt" not in df.columns:
            print("Error: Input file must contain a 'Prompt' column")
            return
            
        # Clean the prompts
        df["Prompt"] = df["Prompt"].apply(clean_text)
        
        # Select output file
        output_file = select_file(
            "Select Output File Location",
            [("Excel files", "*.xlsx"), ("All files", "*.*")],
            save=True
        )
        
        if not output_file:
            print("No output file selected. Exiting...")
            return
            
        # Save to Excel with adjusted column widths
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            
            # Set column widths (adjust as needed)
            worksheet.column_dimensions['A'].width = 5   # #
            worksheet.column_dimensions['B'].width = 15  # Source IDs
            worksheet.column_dimensions['C'].width = 20  # Prompt Type
            worksheet.column_dimensions['D'].width = 50  # Prompt
            
        print(f"Cleaning complete! Output saved to: {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 