# Decomposition Concordance Pipeline

This tool decomposes AI answers into atomic claims and verifies them against provided evidence (answer + question) from a CSV file.

- Decomposes the 'ai_answer' column
- Verifies against 'answer' and 'question' columns
- Uses a MedScore-style pipeline

## Usage

See requirements.txt for dependencies.

## Prompt

Edit the prompt in `prompt/MedScore_prompt.txt` as needed. 