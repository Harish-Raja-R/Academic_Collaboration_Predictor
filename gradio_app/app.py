"""
Academic Collaboration Compatibility Predictor
Gradio App for Hugging Face Spaces Deployment
"""

import gradio as gr
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent / "models" / "best_model.pkl"

DOMAINS = [
    "Machine Learning", "Computer Vision", "NLP", "Robotics",
    "Bioinformatics", "Data Science", "Cybersecurity", "IoT",
    "Cloud Computing", "Quantum Computing"
]
INSTITUTIONS = ["IIT", "NIT", "Central University", "Private University", "Research Institute"]
COUNTRIES = ["India", "USA", "UK", "Germany", "Australia", "Canada"]

try:
    model = joblib.load(MODEL_PATH)
    MODEL_LOADED = True
except Exception as e:
    MODEL_LOADED = False
    MODEL_ERROR = str(e)


def predict_compatibility(
    r1_domain, r1_h_index, r1_publications, r1_years_exp,
    r1_citations, r1_grants, r1_institution, r1_country,
    r2_domain, r2_h_index, r2_publications, r2_years_exp,
    r2_citations, r2_grants, r2_institution, r2_country,
    shared_keywords
):
    if not MODEL_LOADED:
        return f"❌ Model not loaded: {MODEL_ERROR}", "", ""

    row = {
        'r1_domain': r1_domain, 'r2_domain': r2_domain,
        'r1_h_index': float(r1_h_index), 'r2_h_index': float(r2_h_index),
        'r1_publications': float(r1_publications), 'r2_publications': float(r2_publications),
        'r1_years_experience': float(r1_years_exp), 'r2_years_experience': float(r2_years_exp),
        'r1_institution': r1_institution, 'r2_institution': r2_institution,
        'r1_country': r1_country, 'r2_country': r2_country,
        'r1_citations': float(r1_citations), 'r2_citations': float(r2_citations),
        'r1_grants': float(r1_grants), 'r2_grants': float(r2_grants),
        'shared_keywords': float(shared_keywords),
        'same_domain': int(r1_domain == r2_domain),
        'same_institution_type': int(r1_institution == r2_institution),
        'same_country': int(r1_country == r2_country),
        'h_index_diff': abs(float(r1_h_index) - float(r2_h_index)),
        'experience_diff': abs(float(r1_years_exp) - float(r2_years_exp)),
        'total_grants': float(r1_grants) + float(r2_grants),
        'avg_publications': (float(r1_publications) + float(r2_publications)) / 2,
    }
    X = pd.DataFrame([row])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0]
    compat_prob = prob[1] * 100

    label = "✅ Compatible" if pred else "❌ Not Compatible"
    confidence = "High" if compat_prob > 75 or compat_prob < 25 else "Moderate"

    if pred:
        insight = (
            f"These researchers show strong compatibility (probability: {compat_prob:.1f}%). "
            f"Shared domain expertise and complementary profiles suggest a productive collaboration. "
            f"Confidence: {confidence}."
        )
    else:
        insight = (
            f"Low compatibility score ({compat_prob:.1f}%). "
            f"A significant mismatch in domain, h-index gap, or experience level may hinder collaboration. "
            f"Consider pairing with a researcher from a closer domain. Confidence: {confidence}."
        )

    gauge_html = f"""
    <div style='text-align:center; font-family: Arial, sans-serif;'>
      <h2 style='color:{"#27ae60" if pred else "#e74c3c"};'>{label}</h2>
      <div style='background:#eee; border-radius:20px; height:28px; overflow:hidden; margin:10px 0;'>
        <div style='width:{compat_prob:.0f}%; height:100%; border-radius:20px;
                    background:{"#27ae60" if pred else "#e74c3c"};'></div>
      </div>
      <h3>{compat_prob:.1f}% Compatibility Probability</h3>
    </div>
    """
    return label, insight, gauge_html


with gr.Blocks(title="Academic Collaboration Predictor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎓 Academic Collaboration Compatibility Predictor
    **M.Sc. AI & ML | Machine Learning Lab (19MAM46) | CAT II Project | CIT Coimbatore**

    Enter the profiles of two researchers to predict their collaboration compatibility using
    a Gradient Boosting classifier (Accuracy: 83.25%, AUC-ROC: 0.9142).
    """)

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 👨‍🔬 Researcher 1")
            r1_domain = gr.Dropdown(DOMAINS, label="Research Domain", value="Machine Learning")
            with gr.Row():
                r1_h_index = gr.Slider(1, 50, value=8, step=1, label="H-Index")
                r1_publications = gr.Slider(1, 200, value=20, step=1, label="Publications")
            with gr.Row():
                r1_years_exp = gr.Slider(1, 40, value=7, step=1, label="Years of Experience")
                r1_citations = gr.Slider(0, 5000, value=150, step=10, label="Citations")
            with gr.Row():
                r1_grants = gr.Slider(0, 20, value=3, step=1, label="Grants")
            r1_institution = gr.Dropdown(INSTITUTIONS, label="Institution Type", value="IIT")
            r1_country = gr.Dropdown(COUNTRIES, label="Country", value="India")

        with gr.Column():
            gr.Markdown("### 👩‍🔬 Researcher 2")
            r2_domain = gr.Dropdown(DOMAINS, label="Research Domain", value="Data Science")
            with gr.Row():
                r2_h_index = gr.Slider(1, 50, value=10, step=1, label="H-Index")
                r2_publications = gr.Slider(1, 200, value=25, step=1, label="Publications")
            with gr.Row():
                r2_years_exp = gr.Slider(1, 40, value=12, step=1, label="Years of Experience")
                r2_citations = gr.Slider(0, 5000, value=200, step=10, label="Citations")
            with gr.Row():
                r2_grants = gr.Slider(0, 20, value=4, step=1, label="Grants")
            r2_institution = gr.Dropdown(INSTITUTIONS, label="Institution Type", value="NIT")
            r2_country = gr.Dropdown(COUNTRIES, label="Country", value="India")

    shared_keywords = gr.Slider(0, 6, value=2, step=1, label="🔗 Shared Research Keywords (0–6)")

    predict_btn = gr.Button("🔍 Predict Compatibility", variant="primary", size="lg")

    with gr.Row():
        prediction_label = gr.Textbox(label="Prediction", interactive=False)
        insight_text = gr.Textbox(label="Interpretation", interactive=False, lines=3)
    gauge = gr.HTML(label="Compatibility Gauge")

    predict_btn.click(
        fn=predict_compatibility,
        inputs=[
            r1_domain, r1_h_index, r1_publications, r1_years_exp,
            r1_citations, r1_grants, r1_institution, r1_country,
            r2_domain, r2_h_index, r2_publications, r2_years_exp,
            r2_citations, r2_grants, r2_institution, r2_country,
            shared_keywords
        ],
        outputs=[prediction_label, insight_text, gauge]
    )

    gr.Markdown("""
    ---
    **Model:** Gradient Boosting Classifier with Scikit-Learn Pipeline
    | **Dataset:** 2000 synthetic researcher pair records
    | **Key Features:** H-index difference, shared keywords, domain match, experience gap
    """)

if __name__ == "__main__":
    demo.launch(share=True)
