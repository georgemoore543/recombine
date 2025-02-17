# Recombine - Text Generation using HIT Matrix Method

This script generates new text data by combining pairs of prompts using OpenAI's GPT-3.5-turbo model. It reads prompts from an Excel file and generates N² new text items, where N is the number of input prompts.

## Requirements

- Python 3.8+
- OpenAI API key
- Required packages (see requirements.txt)

## Installation

1. Clone this repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Prepare an Excel file with a column named "Prompt" containing your input prompts
2. Run the script:
   ```bash
   python recombine.py
   ```
3. Follow the GUI prompts to:
   - Select the prompt type
   - Choose your input Excel file
   - Specify the output file location

## Output

The script will generate a new Excel file containing:
- Generated prompts
- Source IDs (showing which input prompts were combined)
- Prompt type
- Progress bar showing generation status

## License

[Choose an appropriate license and add it here] 