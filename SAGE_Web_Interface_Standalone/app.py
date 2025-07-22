#!/usr/bin/env python3
"""
SAGE Case Review Web Interface
Medical student-friendly interface for reviewing AI concordance evaluation results
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import random
import pandas as pd
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sage_medical_concordance_study_2025')

# Password for access
REVIEW_PASSWORD = os.environ.get('REVIEW_PASSWORD', "djhwu")

# Data directories
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CSV_DATA_DIR = os.path.join(os.path.dirname(__file__), 'original_data')

def load_jsonl(filepath):
    """Load data from JSONL file"""
    data = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
    return data

def load_original_data():
    """Load original CSV data with questions, answers, and AI responses"""
    csv_file = os.path.join(CSV_DATA_DIR, 'GPT-4.1_Concordance_Eval_Saloni.csv')
    try:
        df = pd.read_csv(csv_file, encoding='latin1')
        # Convert to dict with dav_id as key
        data_dict = {}
        for _, row in df.iterrows():
            data_dict[str(row['dav_id'])] = {
                'question': row['question'],
                'answer': row['answer'],  # Human physician answer
                'ai_answer': row['ai_answer'],
                'concordance': row.get('Concordance', 0)
            }
        return data_dict
    except FileNotFoundError:
        print(f"Warning: CSV file not found: {csv_file}")
        return {}

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == REVIEW_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@require_auth
def dashboard():
    """Main dashboard with case overview"""
    # Load final output data for case statistics
    final_output = load_jsonl(os.path.join(DATA_DIR, 'final_output.jsonl'))
    
    # Get first 10 cases for review
    cases = final_output[:10]
    
    # Calculate overall statistics
    total_cases = len(cases)
    avg_support = sum(float(case['support_percentage'].rstrip('%')) for case in cases) / total_cases if cases else 0
    concordant_cases = sum(1 for case in cases if case.get('Concordance', 0) == 1.0)
    
    return render_template('dashboard.html', 
                         cases=cases,
                         total_cases=total_cases,
                         avg_support=avg_support,
                         concordant_cases=concordant_cases)

@app.route('/case/<case_id>')
@require_auth
def case_detail(case_id):
    """Detailed view of a specific case"""
    # Load all data files
    decompositions = load_jsonl(os.path.join(DATA_DIR, 'decompositions.jsonl'))
    verifications = load_jsonl(os.path.join(DATA_DIR, 'verifications.jsonl'))
    final_output = load_jsonl(os.path.join(DATA_DIR, 'final_output.jsonl'))
    original_data = load_original_data()
    
    # Filter data for specific case
    case_decomps = [d for d in decompositions if d['dav_id'] == case_id]
    case_verifs = [v for v in verifications if v['dav_id'] == case_id]
    case_summary = next((c for c in final_output if c['dav_id'] == case_id), None)
    case_original = original_data.get(case_id, {})
    
    if not case_summary:
        flash(f'Case {case_id} not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Combine decomposition and verification data
    case_claims = []
    for decomp in case_decomps:
        # Find matching verification
        verif = next((v for v in case_verifs if v['id'] == decomp['id']), None)
        
        claim_data = {
            'claim_id': decomp['claim_id'],
            'claim': decomp['claim'],
            'verdict': verif['score'] if verif else 'Unknown',
            'reason': verif['reason'] if verif else 'No verification data',
            'evidence': verif.get('evidence', 'N/A')[:100] + '...' if verif and verif.get('evidence') else 'N/A'
        }
        case_claims.append(claim_data)
    
    # Sort by claim_id
    case_claims.sort(key=lambda x: x['claim_id'])
    
    return render_template('case_detail.html',
                         case_id=case_id,
                         case_summary=case_summary,
                         claims=case_claims,
                         case_original=case_original)

@app.route('/api/cases')
@require_auth
def api_cases():
    """API endpoint for case data"""
    final_output = load_jsonl(os.path.join(DATA_DIR, 'final_output.jsonl'))
    return {'cases': final_output[:10]}

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("Starting SAGE Case Review Web Interface...")
    print("Access the interface at: http://localhost:5001")
    print(f"Password: {REVIEW_PASSWORD}")
    
    # Use environment variables for production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5001))
    host = '0.0.0.0' if os.environ.get('FLASK_ENV') == 'production' else '127.0.0.1'
    
    app.run(debug=False, host=host, port=port)