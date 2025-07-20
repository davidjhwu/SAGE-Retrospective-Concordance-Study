import requests
from .config import API_CONFIG, TIMEOUT

def query_stanford_api(messages, api_key, model=None, max_tokens=None, temperature=None):
    config = API_CONFIG['stanford']
    url = config['url']
    headers = config['headers'].copy()
    headers['Ocp-Apim-Subscription-Key'] = api_key
    payload = {
        'model': model or config['model'],
        'messages': messages,
        'max_tokens': max_tokens if max_tokens is not None else config['max_tokens'],
        'temperature': temperature if temperature is not None else config['temperature'],
    }
    response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json() 