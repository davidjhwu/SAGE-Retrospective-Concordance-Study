import pandas as pd
import requests
import json
import time
from typing import Dict, Any
import os
from config import API_CONFIG, DEFAULT_API_PROVIDER, INPUT_FILE, OUTPUT_FILE, REQUEST_DELAY, TIMEOUT, BATCH_SIZE
from concordance_prompt import make_concordance_prompt  # <-- Import the new prompt function

# Remove the old PROMPT_TEMPLATE from this file

class ConcordanceChecker:
    def __init__(self, api_key: str = None, api_provider: str = None):
        """
        Initialize the concordance checker with API credentials.
        
        Args:
            api_key: API key for the service (can be set via environment variable)
            api_provider: API provider name (stanford, openai, anthropic, gemini)
        """
        self.api_key = api_key or os.getenv('STANFORD_API_KEY') or os.getenv('API_KEY') or os.getenv('GEMINI_API_KEY')
        self.api_provider = api_provider or os.getenv('API_PROVIDER', DEFAULT_API_PROVIDER)
        
        if not self.api_key:
            raise ValueError("API key is required. Set STANFORD_API_KEY, API_KEY, or GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        if self.api_provider not in API_CONFIG:
            raise ValueError(f"Unsupported API provider: {self.api_provider}. Supported providers: {list(API_CONFIG.keys())}")
        
        self.api_config = API_CONFIG[self.api_provider]
    
    def create_concordance_prompt(self, question: str, answer: str, ai_output: str) -> str:
        """
        Create the prompt for checking concordance between answer and ai_output.
        
        Args:
            question: The original question
            answer: The human answer
            ai_output: The AI-generated output
            
        Returns:
            Formatted prompt string
        """
        # Use the new prompt function from concordance_prompt.py
        return make_concordance_prompt(question, answer, ai_output)

    def query_api(self, prompt: str) -> Dict[str, Any]:
        """
        Query the API with the given prompt.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            API response as a dictionary
        """
        headers = self.api_config['headers'].copy()
        
        # Add authorization header based on provider
        if self.api_provider == 'stanford':
            headers['Ocp-Apim-Subscription-Key'] = self.api_key
        elif self.api_provider == 'openai':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.api_provider == 'anthropic':
            headers['x-api-key'] = self.api_key
        elif self.api_provider == 'gemini':
            # For Gemini, API key is part of the URL
            pass
        
        # Prepare payload based on provider
        if self.api_provider in ['stanford', 'openai']:
            payload = {
                'model': self.api_config['model'],
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': self.api_config['max_tokens'],
                'temperature': self.api_config['temperature']
            }
        elif self.api_provider == 'anthropic':
            payload = {
                'model': self.api_config['model'],
                'max_tokens': self.api_config['max_tokens'],
                'temperature': self.api_config['temperature'],
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
        elif self.api_provider == 'gemini':
            payload = {
                'contents': [
                    {
                        'parts': [
                            {
                                'text': prompt
                            }
                        ]
                    }
                ],
                'generationConfig': {
                    'maxOutputTokens': self.api_config['max_tokens'],
                    'temperature': self.api_config['temperature']
                }
            }
        
        # Prepare URL
        url = self.api_config['url']
        if self.api_provider == 'gemini':
            url = f"{url}?key={self.api_key}"
        
        try:
            # Use json parameter for automatic JSON serialization
            response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {'error': str(e)}

    def extract_concordance_result(self, api_response: Dict[str, Any]) -> str:
        """
        Extract the concordance result from the API response.
        
        Args:
            api_response: The response from the API
            
        Returns:
            The extracted concordance result
        """
        if 'error' in api_response:
            return f"ERROR: {api_response['error']}"
        
        try:
            if self.api_provider in ['stanford', 'openai']:
                if 'choices' in api_response and len(api_response['choices']) > 0:
                    content = api_response['choices'][0]['message']['content']
                    return content.strip()
            elif self.api_provider == 'anthropic':
                if 'content' in api_response and len(api_response['content']) > 0:
                    content = api_response['content'][0]['text']
                    return content.strip()
            elif self.api_provider == 'gemini':
                if 'candidates' in api_response and len(api_response['candidates']) > 0:
                    content = api_response['candidates'][0]['content']['parts'][0]['text']
                    return content.strip()
            
            return "ERROR: Unexpected API response format"
        except (KeyError, IndexError) as e:
            return f"ERROR: Failed to parse API response: {e}"

    def process_csv(self, input_file: str = INPUT_FILE, output_file: str = OUTPUT_FILE):
        """
        Process the CSV file and add concordance results.
        
        Args:
            input_file: Path to the input CSV file
            output_file: Path to the output CSV file
        """
        print(f"Reading CSV file: {input_file}")
        print(f"Using API provider: {self.api_provider}")
        
        try:
            # Read the CSV file
            df = pd.read_csv(input_file)
            print(f"Found {len(df)} rows to process")
            print("Columns in DataFrame:", df.columns.tolist())  # Debug print
            
            # Add new columns for concordance results
            df['concordant'] = ''
            df['helpfulness'] = ''  # Add helpfulness column
            df['explanation'] = ''
            
            # Process each row
            for index, row in df.iterrows():
                print(f"Processing row {index + 1}/{len(df)} (ID: {row['dav_id']})")
                
                # Create the prompt
                prompt = self.create_concordance_prompt(
                    question=row['question'],
                    answer=row['answer'],
                    ai_output=row['ai_answer']
                )
                
                # Query the API
                api_response = self.query_api(prompt)
                
                # Extract the result
                concordance_result = self.extract_concordance_result(api_response)
                
                # Store the result
                try:
                    start = concordance_result.find('{')
                    end = concordance_result.rfind('}') + 1
                    json_str = concordance_result[start:end]
                    parsed = json.loads(json_str)
                    df.at[index, 'concordant'] = parsed.get('concordant', '')
                    df.at[index, 'helpfulness'] = parsed.get('helpfulness', '')  # Extract helpfulness
                    df.at[index, 'explanation'] = parsed.get('explanation', '')
                except Exception as e:
                    df.at[index, 'concordant'] = ''
                    df.at[index, 'helpfulness'] = ''
                    df.at[index, 'explanation'] = f'ERROR: Could not parse JSON: {e}\nRaw: {concordance_result}'
                
                # Add a small delay to avoid rate limiting
                time.sleep(REQUEST_DELAY)
                
                # Print progress
                if (index + 1) % BATCH_SIZE == 0:
                    print(f"Completed {index + 1}/{len(df)} rows")
            
            # Save the results
            print(f"Saving results to: {output_file}")
            df.to_csv(output_file, index=False)
            print("Processing completed successfully!")
            
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
        except Exception as e:
            print(f"Error processing CSV: {e}")

def main():
    """
    Main function to run the concordance checker.
    """
    print("Concordance Checker (GPT-4.1, JSON output)")
    print("==================")
    
    # Check if environment variables are set
    api_key = os.getenv('STANFORD_API_KEY') or os.getenv('API_KEY') or os.getenv('GEMINI_API_KEY')
    api_provider = os.getenv('API_PROVIDER', DEFAULT_API_PROVIDER)
    
    if not api_key:
        print("Warning: STANFORD_API_KEY, API_KEY, or GEMINI_API_KEY environment variable not set.")
        api_key = input("Please enter your API key: ").strip()
    
    print(f"Available API providers: {list(API_CONFIG.keys())}")
    if api_provider not in API_CONFIG:
        print(f"Warning: API_PROVIDER '{api_provider}' not found in configuration.")
        api_provider = input(f"Please select API provider {list(API_CONFIG.keys())}: ").strip()
    
    try:
        # Initialize the checker
        checker = ConcordanceChecker(api_key=api_key, api_provider=api_provider)
        
        # Process the CSV file
        checker.process_csv()
        
    except ValueError as e:
        print(f"Configuration error: {e}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 