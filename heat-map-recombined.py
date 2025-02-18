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
    
    sns.heatmap(heatmap_matrix, 
                annot=heatmap_matrix if show_annotations else False,  # Pass the matrix itself for annotations
                fmt='.2f',   # Format to 2 decimal places
                cmap='YlOrRd',  # Yellow to Orange to Red color scheme
                cbar_kws={'label': 'Average Rating'},
                xticklabels=range(1, max_y + 1),
                yticklabels=range(1, max_x + 1))

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