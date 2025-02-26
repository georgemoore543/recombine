import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from tkinter import filedialog, Tk, messagebox
import tkinter as tk

class ScaleSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Set Heatmap Scale")
        self.min_value = None
        self.max_value = None
        
        # Window size and position
        window_width = 300
        window_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Instructions
        label = tk.Label(
            self.root,
            text="Enter the scale range for the heatmap:",
            pady=10
        )
        label.pack()
        
        # Min value frame
        min_frame = tk.Frame(self.root)
        min_frame.pack(pady=5)
        tk.Label(min_frame, text="Minimum value:").pack(side=tk.LEFT)
        self.min_entry = tk.Entry(min_frame, width=10)
        self.min_entry.pack(side=tk.LEFT, padx=5)
        
        # Max value frame
        max_frame = tk.Frame(self.root)
        max_frame.pack(pady=5)
        tk.Label(max_frame, text="Maximum value:").pack(side=tk.LEFT)
        self.max_entry = tk.Entry(max_frame, width=10)
        self.max_entry.pack(side=tk.LEFT, padx=5)
        
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
            command=lambda: self.finish(None, None)
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
    def validate_and_submit(self):
        try:
            min_val = float(self.min_entry.get())
            max_val = float(self.max_entry.get())
            
            if min_val >= max_val:
                tk.messagebox.showerror(
                    "Error",
                    "Maximum value must be greater than minimum value"
                )
                return
                
            self.finish(min_val, max_val)
            
        except ValueError:
            tk.messagebox.showerror(
                "Error",
                "Please enter valid numbers"
            )
            
    def finish(self, min_val, max_val):
        self.min_value = min_val
        self.max_value = max_val
        self.root.quit()
        
    def get_scale(self):
        self.root.mainloop()
        self.root.destroy()
        return self.min_value, self.max_value

class ColorSchemeSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Select Color Scheme")
        self.selected_scheme = None
        
        # Window size and position
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Instructions
        label = tk.Label(
            self.root,
            text="Select a color scheme for the heatmap:",
            pady=10
        )
        label.pack()
        
        # Color schemes with descriptions
        schemes = [
            ("RdYlBu_r", "Blue-Yellow-Red (High contrast)"),
            ("YlOrRd", "Yellow-Orange-Red (Original)"),
            ("RdPu", "White-Pink-Red (Strong emphasis on high values)"),
            ("viridis", "Purple-Green-Yellow (Perceptually uniform)"),
            ("magma", "Black-Purple-Yellow (High distinction)"),
        ]
        
        # Radio buttons for schemes
        self.var = tk.StringVar(value=schemes[0][0])  # Default to first scheme
        for scheme, desc in schemes:
            rb = tk.Radiobutton(
                self.root,
                text=desc,
                variable=self.var,
                value=scheme,
                pady=5
            )
            rb.pack(anchor=tk.W, padx=20)
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # Submit button
        submit_btn = tk.Button(
            button_frame,
            text="Submit",
            width=10,
            command=self.submit
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
        
    def submit(self):
        self.finish(self.var.get())
        
    def finish(self, scheme):
        self.selected_scheme = scheme
        self.root.quit()
        
    def get_scheme(self):
        self.root.mainloop()
        self.root.destroy()
        return self.selected_scheme

def create_heatmap():
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Prompt user to select input file
    file_path = filedialog.askopenfilename(
        title="Select Input Spreadsheet",
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
    )
    
    if not file_path:
        print("No file selected. Exiting...")
        return

    # Read the file (handles both Excel and CSV)
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Extract source IDs and split into x,y coordinates
    source_ids = df['Source IDs'].str.split(',', expand=True).astype(int)
    max_x = source_ids[0].max()
    max_y = source_ids[1].max()

    # Identify rating columns by looking for "Rating" in the column name
    rating_cols = [col for col in df.columns if 'Rating' in col]
    
    if not rating_cols:
        print("No rating columns found. Please ensure column headers contain 'Rating'")
        return

    # Calculate average ratings using only the rating columns
    avg_ratings = df[rating_cols].mean(axis=1)
    
    # Get scale range from user
    scale_selector = ScaleSelector()
    vmin, vmax = scale_selector.get_scale()
    
    if vmin is None or vmax is None:
        print("Operation cancelled. Exiting...")
        return
        
    # Get color scheme from user
    color_selector = ColorSchemeSelector()
    color_scheme = color_selector.get_scheme()
    
    if color_scheme is None:
        print("Operation cancelled. Exiting...")
        return

    # Create empty matrix filled with NaN
    heatmap_matrix = np.full((max_x, max_y), np.nan)

    # Fill matrix with average ratings
    for idx, row in source_ids.iterrows():
        x, y = row[0] - 1, row[1] - 1  # Subtract 1 for 0-based indexing
        heatmap_matrix[x, y] = avg_ratings[idx]

    # Create heatmap
    plt.figure(figsize=(10, 8))
    ax = plt.gca()
    
    # Determine whether to show annotations based on matrix size
    show_annotations = max_x <= 10 and max_y <= 10
    
    # Create heatmap with selected color scheme
    sns.heatmap(heatmap_matrix, 
                annot=heatmap_matrix if show_annotations else False,  # Pass the matrix itself for annotations
                fmt='.2f',   # Format to 2 decimal places
                cmap=color_scheme,  # Use selected color scheme
                cbar_kws={'label': 'Average Rating'},
                xticklabels=range(1, max_y + 1),
                yticklabels=range(1, max_x + 1),
                vmin=vmin,  # Set minimum value for color scale
                vmax=vmax)  # Set maximum value for color scale

    # Move x-axis to top
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')
    
    # Set labels with new descriptions
    plt.xlabel('2nd Source ID')
    plt.ylabel('1st Source ID')
    plt.title('Average Ratings Heatmap', pad=20)  # Add padding to prevent overlap with label

    # Show plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    create_heatmap()