# SAGE Retrospective Concordance Study

A research project evaluating the concordance between AI-generated medical responses and physician reference answers using automated decomposition and verification techniques.

## Overview

This study implements a novel pipeline to assess medical AI accuracy by:
1. **Decomposing** AI responses into atomic claims
2. **Verifying** each claim against reference medical answers
3. **Quantifying** concordance rates and identifying discrepancies

## Key Features

- **Multi-LLM Support**: Compatible with Stanford Healthcare API, OpenAI GPT-4, Anthropic Claude, and Google Gemini
- **Atomic Claim Analysis**: Breaks down complex medical responses into verifiable components
- **Automated Verification**: Compares claims against physician-provided reference answers
- **Comprehensive Reporting**: Generates detailed concordance statistics and analysis

## Pipeline Architecture

### Core Components

1. **Decomposer** (`decomposition_concordance_pipeline/decomposer.py`)
   - Extracts atomic medical claims from AI responses
   - Uses structured prompts to ensure consistent claim formatting

2. **Verifier** (`decomposition_concordance_pipeline/verifier.py`)
   - Validates claims against reference Q&A pairs
   - Classifies each claim as "Supported", "Not Supported", or "Not Addressed"

3. **Main Pipeline** (`decomposition_concordance_pipeline/medscore.py`)
   - Orchestrates the full evaluation workflow
   - Handles data processing and result aggregation

## Getting Started

### Prerequisites

```bash
pip install -r decomposition_concordance_pipeline/requirements.txt
```

### Basic Usage

```bash
cd decomposition_concordance_pipeline
python -m medscore \
  --input_file path/to/your/medical_data.csv \
  --api_key YOUR_API_KEY \
  --output_dir ./results
```

### Input Data Format

Your CSV file should contain:
- `dav_id`: Unique case identifier
- `ai_answer`: AI-generated medical response
- `answer`: Reference physician answer
- `question`: Original medical question

### Configuration

API settings can be modified in `decomposition_concordance_pipeline/config.py`:
- Model selection
- Rate limiting
- Timeout configurations
- Custom API endpoints

## Output

The pipeline generates:
- **Decompositions**: Individual atomic claims extracted from AI responses
- **Verifications**: Claim-by-claim validation results
- **Summary Statistics**: Concordance rates and performance metrics

## Research Applications

This tool is designed for:
- Medical AI evaluation studies
- Healthcare quality assessment
- Automated clinical decision support validation
- Medical education and training evaluation

## API Support

- **Stanford Healthcare API** (default)
- **OpenAI GPT-4**
- **Anthropic Claude**
- **Google Gemini**

## Security & Privacy

- Patient data and sensitive files are excluded from version control
- API keys are handled securely through environment variables
- Local processing ensures data privacy compliance

## Contributing

This is an active research project. For questions or collaboration inquiries, please reach out to the research team.

## License

Research use only. Please contact the authors for commercial applications.