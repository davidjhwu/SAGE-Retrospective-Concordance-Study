# Configuration file for Concordance Checker

# API Configuration
API_CONFIG = {
    # Stanford Healthcare API
    'stanford': {
        'url': 'https://apim.stanfordhealthcare.org/openai-eastus2/deployments/gpt-4.1-mini/chat/completions?api-version=2025-01-01-preview',
        'model': 'gpt-4.1-mini',
        'max_tokens': 5000,
        'temperature': 0.1,
        'headers': {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': ''  # Will be set dynamically
        }
    },
    
    # OpenAI API
    'openai': {
        'url': 'https://api.openai.com/v1/chat/completions',
        'model': 'gpt-4',
        'max_tokens': 500,
        'temperature': 0.1,
        'headers': {
            'Content-Type': 'application/json'
        }
    },
    
    # Anthropic Claude API
    'anthropic': {
        'url': 'https://api.anthropic.com/v1/messages',
        'model': 'claude-3-sonnet-20240229',
        'max_tokens': 500,
        'temperature': 0.1,
        'headers': {
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
    },
    
    # Google Gemini API (using REST API for Python 3.8 compatibility)
    'gemini': {
        'url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent',
        'model': 'gemini-2.0-flash-exp',
        'max_tokens': 500,
        'temperature': 0.1,
        'headers': {
            'Content-Type': 'application/json'
        }
    }
}

# Default API provider
DEFAULT_API_PROVIDER = 'stanford'  # Changed to Stanford as default

# Processing Configuration
REQUEST_DELAY = 1  # seconds between API requests
TIMEOUT = 30  # seconds for API request timeout
BATCH_SIZE = 10  # number of rows to process before progress update
