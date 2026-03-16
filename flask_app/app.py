"""
Academic Collaboration Compatibility Predictor
Flask Web Application
"""

from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import os

app = Flask(__name__)

MODEL_PATH = Path(__file__).parent.parent / "models" / "best_model.pkl"
model = None

DOMAINS = [
    "Machine Learning", "Computer Vision", "NLP", "Robotics",
    "Bioinformatics", "Data Science", "Cybersecurity", "IoT",
    "Cloud Computing", "Quantum Computing"
]
INSTITUTIONS = ["IIT", "NIT", "Central University", "Private University", "Research Institute"]
COUNTRIES = ["India", "USA", "UK", "Germany", "Australia", "Canada"]


def load_model():
    global model
    if model is None:
        model = joblib.load(MODEL_PATH)
    return model


def build_features(form_data):
    r1_domain = form_data.get('r1_domain')
    r2_domain = form_data.get('r2_domain')
    r1_h = float(form_data.get('r1_h_index', 5))
    r2_h = float(form_data.get('r2_h_index', 5))
    r1_pub = float(form_data.get('r1_publications', 10))
    r2_pub = float(form_data.get('r2_publications', 10))
    r1_exp = float(form_data.get('r1_years_experience', 5))
    r2_exp = float(form_data.get('r2_years_experience', 5))
    r1_inst = form_data.get('r1_institution')
    r2_inst = form_data.get('r2_institution')
    r1_country = form_data.get('r1_country')
    r2_country = form_data.get('r2_country')
    r1_citations = float(form_data.get('r1_citations', 50))
    r2_citations = float(form_data.get('r2_citations', 50))
    r1_grants = float(form_data.get('r1_grants', 2))
    r2_grants = float(form_data.get('r2_grants', 2))
    shared_kw = float(form_data.get('shared_keywords', 2))

    row = {
        'r1_domain': r1_domain,
        'r2_domain': r2_domain,
        'r1_h_index': r1_h,
        'r2_h_index': r2_h,
        'r1_publications': r1_pub,
        'r2_publications': r2_pub,
        'r1_years_experience': r1_exp,
        'r2_years_experience': r2_exp,
        'r1_institution': r1_inst,
        'r2_institution': r2_inst,
        'r1_country': r1_country,
        'r2_country': r2_country,
        'r1_citations': r1_citations,
        'r2_citations': r2_citations,
        'r1_grants': r1_grants,
        'r2_grants': r2_grants,
        'shared_keywords': shared_kw,
        'same_domain': int(r1_domain == r2_domain),
        'same_institution_type': int(r1_inst == r2_inst),
        'same_country': int(r1_country == r2_country),
        'h_index_diff': abs(r1_h - r2_h),
        'experience_diff': abs(r1_exp - r2_exp),
        'total_grants': r1_grants + r2_grants,
        'avg_publications': (r1_pub + r2_pub) / 2,
    }
    return pd.DataFrame([row])


@app.route('/')
def index():
    return render_template('index.html',
                           domains=DOMAINS,
                           institutions=INSTITUTIONS,
                           countries=COUNTRIES)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        clf = load_model()
        X = build_features(request.form)
        prediction = clf.predict(X)[0]
        probability = clf.predict_proba(X)[0]
        compat_prob = float(probability[1]) * 100

        result = {
            'compatible': bool(prediction),
            'probability': round(compat_prob, 1),
            'label': 'Compatible ✅' if prediction else 'Not Compatible ❌',
            'confidence': 'High' if compat_prob > 75 or compat_prob < 25 else 'Moderate',
            'r1_domain': request.form.get('r1_domain'),
            'r2_domain': request.form.get('r2_domain'),
        }
        return render_template('result.html', result=result)
    except Exception as e:
        return render_template('result.html', error=str(e))


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """JSON API endpoint for programmatic access."""
    try:
        clf = load_model()
        X = build_features(request.json)
        prediction = clf.predict(X)[0]
        probability = clf.predict_proba(X)[0]
        return jsonify({
            'compatible': int(prediction),
            'compatibility_probability': round(float(probability[1]), 4),
            'label': 'Compatible' if prediction else 'Not Compatible'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
