# 🎓 Academic Collaboration Compatibility Predictor

**M.Sc. AI & ML | Machine Learning Lab (19MAM46) | CAT II Project**  
**Coimbatore Institute of Technology, Coimbatore – 641014**

---

## 📌 Project Overview

This project predicts whether **two academic researchers are likely to form a compatible and productive collaboration**, based on their research profiles.

**Best Model:** Gradient Boosting Classifier  

| Metric | Score |
|------|------|
| Accuracy | 83.25% |
| F1 Score | 0.7886 |
| AUC-ROC | 0.9142 |
| Cross-Val F1 | 0.7701 ± 0.0399 |

---

## 📂 Project Structure

```
academic_collab_predictor/
│
├── data/
│   ├── generate_dataset.py
│   └── academic_collaboration_dataset.csv
│
├── notebooks/
│   └── eda_and_modeling.py
│
├── models/
│   └── best_model.pkl
│
├── flask_app/
│   ├── app.py
│   ├── templates/
│   │   ├── index.html
│   │   └── result.html
│   └── static/
│       └── style.css
│
├── gradio_app/
│   └── app.py
│
├── report_assets/
│
├── requirements.txt
└── README.md
```

---

## 📊 Dataset Features

| Feature | Description |
|---|---|
| r1_domain, r2_domain | Research domains |
| r1_h_index, r2_h_index | H-index |
| r1_publications, r2_publications | Publication count |
| r1_years_experience, r2_years_experience | Career duration |
| r1_citations, r2_citations | Citation count |
| r1_grants, r2_grants | Research grants |
| r1_institution, r2_institution | Institution type |
| r1_country, r2_country | Country |
| shared_keywords | Shared research keywords |
| h_index_diff | H-index difference |
| experience_diff | Experience difference |
| same_domain | Same research domain |
| same_country | Same country |
| total_grants | Combined grants |
| avg_publications | Average publications |
| **compatible** | Target variable |

---

## ⚙️ How to Run

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Generate dataset

```bash
cd data
python generate_dataset.py
```

### 3️⃣ Run EDA + Modeling

```bash
cd notebooks
python eda_and_modeling.py
```

### 4️⃣ Launch Flask App

```bash
cd flask_app
python app.py
```

Open in browser:

```
http://localhost:5000
```

### 5️⃣ Run Gradio App

```bash
cd gradio_app
python app.py
```

---

## 🤖 Model Comparison

| Model | Accuracy | F1 | AUC |
|---|---|---|---|
| Naive Bayes | 72% | 0.685 | 0.745 |
| Logistic Regression | 76.5% | 0.73 | 0.79 |
| SVM | 79% | 0.76 | 0.82 |
| GNN Collaboration | 82% | 0.795 | 0.855 |
| **Gradient Boosting (Ours)** | **83.25%** | **0.789** | **0.914** |

---

## 🔍 Key Findings

- **H-index difference** is the most important feature
- **Same research domain** strongly improves collaboration
- **Shared keywords** significantly increase compatibility
- Best collaborations occur when **experience gap is 2-10 years**

Cross-validation confirms robustness:

```
Mean CV F1 = 0.77 ± 0.04
```

---

## 🚀 Deployment

**Local Flask App**

```
http://localhost:5000
```

**HuggingFace Spaces**

```
https://huggingface.co/spaces/<your-username>/academic-collab-predictor
```

---

## 📚 References

1. Beaver & Rosen (1978) – Studies in Scientific Collaboration  
2. Katz & Martin (1997) – What is Research Collaboration  
3. Lin et al. (2021) – SVM-based Collaboration Prediction  
4. Wang et al. (2023) – GNN Collaboration Recommendation  
5. Pedregosa et al. (2011) – Scikit-learn
