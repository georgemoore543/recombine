"""
Recombine - Text Generation using HIT Matrix Method

This script generates new text data by combining pairs of prompts using OpenAI's GPT-3.5-turbo model.
It reads prompts from an Excel file and generates N² new text items, where N is the number of input prompts.

Requirements:
- Python 3.8+
- OpenAI API key set in .env file
- Required packages listed in requirements.txt
"""

import os
import sys
import time
from pathlib import Path
from tkinter import Tk, filedialog
from tkinter.ttk import Progressbar
import tkinter as tk
import pandas as pd
from dotenv import load_dotenv
import openai
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

class ProgressWindow:
    def __init__(self, total_items):
        self.root = tk.Tk()
        self.root.title("Generation Progress")
        
        # Window size and position
        window_width = 400
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Progress bar
        self.progress = Progressbar(self.root, length=300, mode='determinate')
        self.progress.pack(pady=20)
        
        # Progress label
        self.label = tk.Label(self.root, text="0 / 0 items generated")
        self.label.pack(pady=10)
        
        self.total = total_items
        self.current = 0
        
    def update(self, current):
        self.current = current
        percentage = (current / self.total) * 100
        self.progress['value'] = percentage
        self.label.config(text=f"{current} / {self.total} items generated")
        self.root.update()
        
    def close(self):
        self.root.destroy()

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

def generate_text(prompt1, prompt2, retries=3):
    """Generate new text using OpenAI API by combining two prompts."""
    system_prompt = """
    Create a new, unique text that combines themes and elements from the two provided prompts.
    The result should be novel and useful while maintaining coherence with both source prompts.
    """
    
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Prompt 1: {prompt1}\nPrompt 2: {prompt2}"}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
            
        except openai.RateLimitError:
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
        except Exception as e:
            print(f"Error generating text: {str(e)}")
            if attempt < retries - 1:
                time.sleep(1)
            else:
                raise

def main():
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in .env file")
        sys.exit(1)
    
    # Select input file
    input_file = select_file(
        "Select Input Excel File",
        [("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if not input_file:
        print("No input file selected. Exiting...")
        return
    
    # Read input data
    try:
        df = pd.read_excel(input_file)
        if "Prompt" not in df.columns:
            print("Error: Input file must contain a 'Prompt' column")
            return
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return
    
    # Calculate total combinations
    prompts = df["Prompt"].tolist()
    total_combinations = len(prompts) ** 2
    
    # Select output file
    output_file = select_file(
        "Select Output File Location",
        [("Excel files", "*.xlsx"), ("All files", "*.*")],
        save=True
    )
    if not output_file:
        print("No output file selected. Exiting...")
        return
    
    # Initialize progress window
    progress_window = ProgressWindow(total_combinations)
    
    # Generate new texts
    new_texts = []
    counter = 0
    
    try:
        for i, prompt1 in enumerate(prompts):
            for j, prompt2 in enumerate(prompts):
                try:
                    new_text = generate_text(prompt1, prompt2)
                    new_texts.append(new_text)
                    counter += 1
                    progress_window.update(counter)
                except Exception as e:
                    print(f"Error generating text for prompts {i+1} and {j+1}: {str(e)}")
                    new_texts.append(f"Error: {str(e)}")
    
        # Create output dataframe
        output_df = pd.DataFrame({
            "#": range(1, len(new_texts) + 1),
            "Prompt": new_texts
        })
        
        # Save to Excel
        output_df.to_excel(output_file, index=False)
        print(f"\nGeneration complete! Output saved to: {output_file}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        progress_window.close()

if __name__ == "__main__":
    main() 