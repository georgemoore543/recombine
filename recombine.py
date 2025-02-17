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

class PromptTypeSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Select Prompt Type")
        self.selected_type = None
        
        # Window size and position
        window_width = 300
        window_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Label
        label = tk.Label(self.root, text="Select the type of prompts:", pady=10)
        label.pack()
        
        # Buttons
        options = [
            "Auto-detect",
            "Insights/Observations",
            "Problem Statements",
            "Solution Proposals"
        ]
        
        for option in options:
            btn = tk.Button(
                self.root,
                text=option,
                width=20,
                command=lambda o=option: self.select_type(o)
            )
            btn.pack(pady=5)
        
        # Cancel button
        cancel_btn = tk.Button(
            self.root,
            text="Cancel",
            width=20,
            command=lambda: self.select_type(None)
        )
        cancel_btn.pack(pady=10)
        
    def select_type(self, type_value):
        self.selected_type = type_value
        self.root.quit()
        
    def get_selection(self):
        self.root.mainloop()
        self.root.destroy()
        return self.selected_type

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

def generate_text(prompt1, prompt2, prompt_id1, prompt_id2, forced_type=None, retries=3):
    """Generate new text using OpenAI API by combining two prompts."""
    system_prompt = """
    You will receive two prompts. First, analyze if these prompts are:
    1. Insights/Observations
    2. Problem Statements
    3. Solution Proposals

    Then, generate a new text that:
    - Maintains the same type/framing as the first prompt
    - Combines themes and elements from both prompts
    - Matches the linguistic style and structure of the inputs
    - Do NOT include prefixes like "Problem Statement:", "Insight:", or "Solution:"
    - Returns ONLY the new generated text without any analysis or explanation
    """
    
    if forced_type:
        system_prompt = f"""
        You will receive two prompts. The user has specified these are {forced_type.lower()}.
        Generate a new text that:
        - MUST be framed strictly as a {forced_type.lower()} like the input prompts
        - Combines themes and elements from both prompts
        - Matches the linguistic style and structure of the inputs
        - Do NOT include prefixes like "Problem Statement:", "Insight:", or "Solution:"
        - If these are Problem Statements, do NOT include solutions
        - If these are Insights, focus on observations without solutions
        - If these are Solution Proposals, focus on actionable solutions
        - Returns ONLY the new generated text without any analysis or explanation
        """
    
    client = openai.OpenAI()
    
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Prompt 1: {prompt1}\nPrompt 2: {prompt2}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return {
                'text': response.choices[0].message.content.strip(),
                'source_ids': f"{prompt_id1},{prompt_id2}"
            }
            
        except openai.RateLimitError:
            if attempt < retries - 1:
                wait_time = 2 ** attempt
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
    
    # Get prompt type selection
    selector = PromptTypeSelector()
    prompt_type = selector.get_selection()
    if prompt_type is None:
        print("Operation cancelled. Exiting...")
        return
    
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
    
    # Calculate total combinations (excluding self-combinations)
    prompts = df["Prompt"].tolist()
    total_combinations = len(prompts) * (len(prompts) - 1)
    
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
                # Skip if prompts are identical (same index)
                if i == j:
                    continue
                    
                try:
                    result = generate_text(
                        prompt1, 
                        prompt2, 
                        i+1, 
                        j+1, 
                        forced_type=None if prompt_type == "Auto-detect" else prompt_type
                    )
                    new_texts.append(result)
                    counter += 1
                    progress_window.update(counter)
                except Exception as e:
                    print(f"Error generating text for prompts {i+1} and {j+1}: {str(e)}")
                    new_texts.append({
                        'text': f"Error: {str(e)}",
                        'source_ids': f"{i+1},{j+1}"
                    })
    
        # Create output dataframe
        output_df = pd.DataFrame({
            "#": range(1, len(new_texts) + 1),
            "Source IDs": [item['source_ids'] for item in new_texts],
            "Prompt Type": prompt_type if prompt_type != "Auto-detect" else "Multiple",
            "Prompt": [item['text'] for item in new_texts]
        })
        
        # Ensure proper column order and formatting
        output_df = output_df[[
            "#",
            "Source IDs",
            "Prompt Type",
            "Prompt"
        ]]
        
        # Save to Excel with adjusted column widths
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            output_df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            worksheet.column_dimensions['A'].width = 5  # #
            worksheet.column_dimensions['B'].width = 15  # Source IDs
            worksheet.column_dimensions['C'].width = 20  # Prompt Type
            worksheet.column_dimensions['D'].width = 50  # Prompt
        
        print(f"\nGeneration complete! Output saved to: {output_file}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        progress_window.close()

if __name__ == "__main__":
    main() 