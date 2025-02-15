# Recombine - Text Generation Tool

This tool generates new text data using the HIT Matrix method and OpenAI's GPT-3.5-turbo model.

## Setup

1. Clone this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file

## Usage

1. Prepare your input Excel file:
   - Must contain a column titled "Prompt"
   - Each row should contain one text prompt

2. Run the script:
   ```bash
   python recombine.py
   ```

3. Follow the GUI prompts:
   - Select your input Excel file
   - Choose where to save the output file
   - Watch the progress bar as new text is generated

4. The output Excel file will contain:
   - A "#" column with item numbers
   - A "Prompt" column with generated text

## Error Handling

The script includes handling for:
- API rate limits (with exponential backoff)
- Token limits
- Failed API calls
- File selection errors
- Input file format errors

Error messages will be displayed in the console for debugging.

## Requirements

- Python 3.8+
- OpenAI API key
- Required packages (see requirements.txt) 