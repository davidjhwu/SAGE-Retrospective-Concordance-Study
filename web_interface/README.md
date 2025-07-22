# SAGE Case Review Web Interface

A user-friendly web interface for reviewing AI concordance evaluation results.

## Features

- **Password Protection**: Secure access with password
- **Case Overview**: Dashboard showing all 10 cases with summary statistics
- **Detailed Analysis**: Click any case to see:
  - Atomic claim decompositions
  - Verification results (Supported/Not Supported/Not Addressed)
  - Reasoning for each verdict
  - Physician concordance scores

## Quick Start

1. **Install Requirements**
   ```bash
   cd web_interface
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the Interface**
   - Open browser to: http://localhost:5000
   - Password: `djhwu`

## Interface Overview

### Login Page
- Simple password protection
- Medical-themed design
- Instructions for students

### Dashboard
- Overview statistics (total cases, average support rate, concordant cases)
- Grid of case cards showing:
  - Case ID
  - Concordance status (Concordant/Discordant)
  - Claim counts (Supported/Not Supported/Not Addressed)
  - Support and not-addressed percentages
- Color-coded cards (green for concordant, red for discordant)

### Case Detail Page
- Complete breakdown of AI response into atomic claims
- Each claim shows:
  - Original claim text
  - Verification verdict with color coding
  - Detailed reasoning from the verification process
  - Evidence context snippet
- Educational notes and reflection questions
- Summary statistics for the case

## Data Sources

The interface loads data from:
- `../test_results_gpt4.1/decompositions.jsonl` - Atomic claims
- `../test_results_gpt4.1/verifications.jsonl` - Verification results  
- `../test_results_gpt4.1/final_output.jsonl` - Summary statistics

## Educational Value

This tool helps medical students:
- Understand how AI breaks down complex medical responses
- See how claims are verified against physician answers
- Learn to critically evaluate AI-generated medical content
- Identify patterns in AI reasoning accuracy
- Develop skills for using AI as a clinical decision support tool

## Security

- Session-based authentication
- Password protection for sensitive medical education content
- Local deployment only (no external hosting of medical data)

## Technical Details

- **Framework**: Flask (Python web framework)
- **Frontend**: Bootstrap 5 + Font Awesome icons
- **Data Format**: JSONL files with structured medical case data
- **Deployment**: Local development server (suitable for educational use)