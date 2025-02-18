import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from tkinter import filedialog, Tk

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
    source_ids = df['Source ID'].str.split(',', expand=True).astype(int)
    max_x = source_ids[0].max()
    max_y = source_ids[1].max()

    # Calculate average ratings across all numeric columns
    # Assuming all rating columns are numeric and non-numeric columns are at the start
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    avg_ratings = df[numeric_cols].mean(axis=1)

    # Create empty matrix filled with NaN
    heatmap_matrix = np.full((max_x, max_y), np.nan)

    # Fill matrix with average ratings
    for idx, row in source_ids.iterrows():
        x, y = row[0] - 1, row[1] - 1  # Subtract 1 for 0-based indexing
        heatmap_matrix[x, y] = avg_ratings[idx]

    # Create heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_matrix, 
                annot=True,  # Show values in cells
                fmt='.2f',   # Format to 2 decimal places
                cmap='YlOrRd',  # Yellow to Orange to Red color scheme
                cbar_kws={'label': 'Average Rating'})

    # Set labels
    plt.xlabel('Source Prompt ID')
    plt.ylabel('Source Prompt ID')
    plt.title('Average Ratings Heatmap')

    # Show plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    create_heatmap()