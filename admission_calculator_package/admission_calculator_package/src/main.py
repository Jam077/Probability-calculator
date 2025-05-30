import sys
import os
import pandas as pd
import numpy as np
from scipy.stats import norm
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Authorized user credentials
AUTHORIZED_USER = "majidov@gmail.com"
AUTHORIZED_PASSWORD = "password123"  # In a real app, this would be hashed and stored securely

# Load data at startup to avoid reloading for each request
DATA_FILE = os.path.join(os.path.dirname(__file__), "static", "merged_score_lists_final.xlsx")
try:
    df = pd.read_excel(DATA_FILE)
    print(f"Loaded {len(df)} rows from {DATA_FILE}")
    
    # Ensure score columns are numeric
    df["Passing Score"] = pd.to_numeric(df["Passing Score"], errors="coerce")
    df["Min Score Required"] = pd.to_numeric(df["Min Score Required"], errors="coerce")
    
    # Get unique groups and sectors for dropdowns
    AVAILABLE_GROUPS = sorted(df["Extracted Group"].dropna().unique().tolist())
    AVAILABLE_SECTORS = sorted(df["Sector"].dropna().unique().tolist())
    
    print(f"Available groups: {AVAILABLE_GROUPS}")
    print(f"Available sectors: {AVAILABLE_SECTORS}")
    
except Exception as e:
    print(f"Error loading data: {e}")
    df = None
    AVAILABLE_GROUPS = []
    AVAILABLE_SECTORS = []

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email == AUTHORIZED_USER and password == AUTHORIZED_PASSWORD:
            session['logged_in'] = True
            session['user_email'] = email
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_email', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Render the main page with the calculator form."""
    return render_template('index.html', 
                          groups=AVAILABLE_GROUPS,
                          sectors=AVAILABLE_SECTORS)

@app.route('/api/calculate', methods=['POST'])
@login_required
def calculate_probability():
    """API endpoint to calculate admission probabilities."""
    if df is None:
        return jsonify({"error": "Data file not loaded. Please check server logs."}), 500
    
    try:
        # Get inputs from request
        data = request.get_json()
        user_score = float(data.get('score', 0))
        selected_group = data.get('group', '')
        selected_sector = data.get('sector', '')
        top_n = int(data.get('topN', 10))
        
        # Validate inputs
        if not (0 <= user_score <= 700):
            return jsonify({"error": "Score must be between 0 and 700"}), 400
        
        if selected_group not in AVAILABLE_GROUPS:
            return jsonify({"error": f"Invalid group. Available groups: {AVAILABLE_GROUPS}"}), 400
            
        if selected_sector not in AVAILABLE_SECTORS and selected_sector != "All":
            return jsonify({"error": f"Invalid sector. Available sectors: {AVAILABLE_SECTORS}"}), 400
            
        if not (3 <= top_n <= 20):
            return jsonify({"error": "Top N must be between 3 and 20"}), 400
        
        # Filter data for the selected group and sector
        filtered_df = df[df["Extracted Group"] == selected_group].copy()
        
        if selected_sector != "All":
            filtered_df = filtered_df[filtered_df["Sector"] == selected_sector]
        
        if filtered_df.empty:
            return jsonify({
                "error": "No data found for the selected combination of group and sector",
                "availableGroups": AVAILABLE_GROUPS,
                "availableSectors": AVAILABLE_SECTORS
            }), 404
        
        # Calculate probabilities
        results = calculate_admission_probability(user_score, filtered_df)
        
        # Limit to top N results
        results = results[:top_n]
        
        return jsonify({
            "results": results,
            "metadata": {
                "score": user_score,
                "group": selected_group,
                "sector": selected_sector,
                "topN": top_n,
                "totalSpecialties": len(results)
            }
        })
        
    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        print(f"Error in calculation: {e}")
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500

def calculate_admission_probability(user_score, filtered_df):
    """Calculate admission probabilities for specialties in the filtered dataframe."""
    results = []
    unique_specialties = filtered_df["Specialty"].unique()

    for specialty in unique_specialties:
        specialty_df = filtered_df[filtered_df["Specialty"] == specialty]
        historical_scores = specialty_df["Passing Score"].dropna().tolist()
        n = len(historical_scores)

        probability_percent = None
        status = "OK"
        mean_score = None
        std_dev = None

        if n < 2:
            status = "Insufficient Data"
        else:
            mean_score = np.mean(historical_scores)
            std_dev = np.std(historical_scores, ddof=1)  # Use sample standard deviation

            if pd.isna(std_dev):
                status = "Insufficient Data (after dropna)"
            elif std_dev < 0.01:  # Handle cases with (almost) zero standard deviation
                if user_score >= mean_score:
                    probability_percent = 99.99
                else:
                    probability_percent = 0.01  # Assign a very small probability
            else:
                probability = norm.cdf(user_score, loc=mean_score, scale=std_dev)
                probability_percent = probability * 100

        # Format values for JSON response
        results.append({
            "specialty": specialty,
            "probability": None if probability_percent is None else round(probability_percent, 2),
            "status": status,
            "mean": None if mean_score is None else round(mean_score, 2),
            "stdDev": None if std_dev is None else round(std_dev, 2),
            "dataPoints": n
        })

    # Sort by probability (descending), handling None values
    results.sort(key=lambda x: -999 if x["probability"] is None else x["probability"], reverse=True)
    
    return results

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
