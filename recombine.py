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
from tkinter import Tk, filedialog, messagebox
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

class GoalSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Set Generation Goal")
        self.goal = None
        
        # Window size and position
        window_width = 500
        window_height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Label
        label = tk.Label(
            self.root,
            text="Enter the goal for combining prompts\n(What should the generated text aim to achieve?):",
            pady=10
        )
        label.pack()
        
        # Default goal text
        default_goal = "to provide a new prompt that is novel, insightful, and actionable"
        
        # Text input
        self.text_input = tk.Text(self.root, height=4, width=50)
        self.text_input.insert("1.0", default_goal)
        self.text_input.pack(pady=10, padx=20)
        
        # Character counter
        char_counter = tk.Label(self.root, text=f"{len(default_goal)}/500 characters")
        char_counter.pack()
        
        def update_counter(event=None):
            current = len(self.text_input.get("1.0", tk.END).strip())
            char_counter.config(text=f"{current}/500 characters")
            
        self.text_input.bind("<KeyRelease>", update_counter)
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # Submit button
        submit_btn = tk.Button(
            button_frame,
            text="Submit",
            width=10,
            command=self.validate_and_submit
        )
        submit_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            width=10,
            command=lambda: self.finish(None)
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
    def validate_and_submit(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if len(text) > 500:
            tk.messagebox.showerror(
                "Error",
                "Goal text must be 500 characters or less."
            )
            return
        if not text:
            tk.messagebox.showerror(
                "Error",
                "Goal text cannot be empty."
            )
            return
        self.finish(text)
        
    def finish(self, goal):
        self.goal = goal
        self.root.quit()
        
    def get_goal(self):
        self.root.mainloop()
        self.root.destroy()
        return self.goal

class ContextSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Add Context")
        self.context = None
        
        # Window size and position
        window_width = 400
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Label
        label = tk.Label(self.root, text="Would you like to add context for the LLM\nto guide the output generation?", pady=10)
        label.pack()
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # Yes/No buttons
        yes_btn = tk.Button(
            button_frame,
            text="Yes",
            width=10,
            command=self.show_context_input
        )
        yes_btn.pack(side=tk.LEFT, padx=10)
        
        no_btn = tk.Button(
            button_frame,
            text="No",
            width=10,
            command=lambda: self.finish(None)
        )
        no_btn.pack(side=tk.LEFT, padx=10)
        
    def show_context_input(self):
        # Clear current window contents
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Add new input elements
        label = tk.Label(
            self.root,
            text="Enter structure and format instructions for the LLM (max 2000 characters):",
            pady=10
        )
        label.pack()
        
        # Text input
        text_input = tk.Text(self.root, height=4, width=40)
        text_input.pack(pady=10, padx=20)
        
        # Character counter
        char_counter = tk.Label(self.root, text="0/2000 characters")
        char_counter.pack()
        
        def update_counter(event=None):
            current = len(text_input.get("1.0", tk.END).strip())
            char_counter.config(text=f"{current}/2000 characters")
            
        text_input.bind("<KeyRelease>", update_counter)
        
        # Submit button
        submit_btn = tk.Button(
            self.root,
            text="Submit",
            width=10,
            command=lambda: self.validate_and_submit(text_input.get("1.0", tk.END))
        )
        submit_btn.pack(pady=10)
        
    def validate_and_submit(self, text):
        text = text.strip()
        if len(text) > 2000:
            tk.messagebox.showerror(
                "Error",
                "Context must be 2000 characters or less."
            )
            return
        self.finish(text)
        
    def finish(self, context):
        self.context = context
        self.root.quit()
        
    def get_context(self):
        self.root.mainloop()
        self.root.destroy()
        return self.context

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

def generate_text(prompt1, prompt2, prompt_id1, prompt_id2, user_context=None, generation_goal=None, retries=3):
    """Generate new text using OpenAI API by combining two prompts."""
    goal = generation_goal or "to provide a new prompt that is novel, insightful, and actionable"
    
    base_system_prompt = f"""
    You will receive two prompts. Generate a new text that:
    - Combines themes and elements from both prompts 
    - Satisfies the following goal or goals: {goal}
    - Matches the linguistic style and structure of the inputs
    """
    
    # Add user context if provided
    system_prompt = base_system_prompt
    if user_context:
        system_prompt = f"""
        {base_system_prompt}
        
        This additional context from the User offers instructions for the structure and format of the output:
        {user_context}
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
                max_tokens=5000
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
    
    # Get generation goal
    goal_selector = GoalSelector()
    generation_goal = goal_selector.get_goal()
    if generation_goal is None:
        print("Operation cancelled. Exiting...")
        return
    
    # Get user context
    context_selector = ContextSelector()
    user_context = context_selector.get_context()
    
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
    
    # Calculate total combinations (excluding self-combinations and duplicates)
    prompts = df["Prompt"].tolist()
    n = len(prompts)
    total_combinations = (n * (n - 1)) // 2  # Formula for combinations without repetition
    
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
            # Start j from i+1 to only get each pair once
            for j in range(i + 1, len(prompts)):
                prompt2 = prompts[j]
                try:
                    result = generate_text(
                        prompt1, 
                        prompt2, 
                        i+1, 
                        j+1, 
                        user_context=user_context,
                        generation_goal=generation_goal
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
            "Prompt": [item['text'] for item in new_texts]
        })
        
        # Ensure proper column order and formatting
        output_df = output_df[[
            "#",
            "Source IDs",
            "Prompt"
        ]]
        
        # Save to Excel with adjusted column widths
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            output_df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            worksheet.column_dimensions['A'].width = 5  # #
            worksheet.column_dimensions['B'].width = 15  # Source IDs
            worksheet.column_dimensions['C'].width = 50  # Prompt
        
        print(f"\nGeneration complete! Output saved to: {output_file}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        progress_window.close()

if __name__ == "__main__":
    main() 