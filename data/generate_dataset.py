"""
Academic Collaboration Compatibility Dataset Generator
Generates a realistic synthetic dataset of researcher pairs with compatibility labels.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import random

random.seed(42)
np.random.seed(42)

DOMAINS = [
    "Machine Learning", "Computer Vision", "NLP", "Robotics",
    "Bioinformatics", "Data Science", "Cybersecurity", "IoT",
    "Cloud Computing", "Quantum Computing"
]

INSTITUTIONS = ["IIT", "NIT", "Central University", "Private University", "Research Institute"]

COUNTRIES = ["India", "USA", "UK", "Germany", "Australia", "Canada"]

KEYWORDS = {
    "Machine Learning": ["deep learning", "neural networks", "optimization", "reinforcement learning"],
    "Computer Vision": ["image processing", "object detection", "CNN", "segmentation"],
    "NLP": ["transformers", "text classification", "sentiment analysis", "LLM"],
    "Robotics": ["path planning", "control systems", "SLAM", "actuators"],
    "Bioinformatics": ["genomics", "protein folding", "sequence analysis", "drug discovery"],
    "Data Science": ["statistics", "visualization", "big data", "feature engineering"],
    "Cybersecurity": ["network security", "cryptography", "threat detection", "privacy"],
    "IoT": ["edge computing", "sensor networks", "embedded systems", "protocols"],
    "Cloud Computing": ["distributed systems", "containerization", "microservices", "scalability"],
    "Quantum Computing": ["quantum algorithms", "qubits", "superposition", "entanglement"]
}

def get_shared_keywords(domain1, domain2):
    kw1 = set(KEYWORDS[domain1])
    kw2 = set(KEYWORDS[domain2])
    base_shared = len(kw1 & kw2)
    if domain1 == domain2:
        base_shared += np.random.randint(2, 5)
    else:
        base_shared += np.random.randint(0, 2)
    return min(base_shared, 6)

def generate_researcher():
    domain = random.choice(DOMAINS)
    h_index = int(np.random.gamma(3, 3) + 1)
    publications = int(np.random.gamma(5, 4) + h_index)
    years_exp = np.random.randint(1, 30)
    institution = random.choice(INSTITUTIONS)
    country = random.choice(COUNTRIES)
    citations = publications * np.random.randint(5, 25)
    grant_count = np.random.randint(0, 10)
    return {
        "domain": domain,
        "h_index": h_index,
        "publications": publications,
        "years_experience": years_exp,
        "institution_type": institution,
        "country": country,
        "citations": citations,
        "grant_count": grant_count
    }

def compute_compatibility(r1, r2):
    score = 0

    # Domain match
    if r1["domain"] == r2["domain"]:
        score += 30
    else:
        # adjacent domains get partial score
        related_pairs = [
            ("Machine Learning", "Data Science"), ("Machine Learning", "Computer Vision"),
            ("NLP", "Machine Learning"), ("IoT", "Robotics"), ("Cloud Computing", "IoT"),
            ("Bioinformatics", "Data Science"), ("Cybersecurity", "Cloud Computing")
        ]
        for d1, d2 in related_pairs:
            if (r1["domain"] in [d1, d2]) and (r2["domain"] in [d1, d2]):
                score += 15
                break

    # h-index complementarity (not too far apart)
    h_diff = abs(r1["h_index"] - r2["h_index"])
    if h_diff <= 3:
        score += 20
    elif h_diff <= 7:
        score += 10
    else:
        score += 2

    # Experience balance (senior+junior works well)
    exp_diff = abs(r1["years_experience"] - r2["years_experience"])
    if 2 <= exp_diff <= 10:
        score += 15
    elif exp_diff < 2:
        score += 10
    else:
        score += 5

    # Institution diversity bonus
    if r1["institution_type"] != r2["institution_type"]:
        score += 5

    # Grant availability
    total_grants = r1["grant_count"] + r2["grant_count"]
    if total_grants >= 5:
        score += 10
    elif total_grants >= 2:
        score += 5

    # Geographic proximity
    if r1["country"] == r2["country"]:
        score += 10
    elif r1["country"] in ["USA", "UK", "Canada", "Australia"] and r2["country"] in ["USA", "UK", "Canada", "Australia"]:
        score += 5

    # Publication productivity
    avg_pubs = (r1["publications"] + r2["publications"]) / 2
    if avg_pubs > 20:
        score += 10
    elif avg_pubs > 10:
        score += 5

    # Add noise
    score += np.random.randint(-10, 10)
    score = max(0, min(100, score))
    return score

def generate_dataset(n=2000):
    records = []
    for _ in range(n):
        r1 = generate_researcher()
        r2 = generate_researcher()
        shared_kw = get_shared_keywords(r1["domain"], r2["domain"])
        compat_score = compute_compatibility(r1, r2)
        compatible = 1 if compat_score >= 55 else 0

        record = {
            "r1_domain": r1["domain"],
            "r2_domain": r2["domain"],
            "r1_h_index": r1["h_index"],
            "r2_h_index": r2["h_index"],
            "r1_publications": r1["publications"],
            "r2_publications": r2["publications"],
            "r1_years_experience": r1["years_experience"],
            "r2_years_experience": r2["years_experience"],
            "r1_institution": r1["institution_type"],
            "r2_institution": r2["institution_type"],
            "r1_country": r1["country"],
            "r2_country": r2["country"],
            "r1_citations": r1["citations"],
            "r2_citations": r2["citations"],
            "r1_grants": r1["grant_count"],
            "r2_grants": r2["grant_count"],
            "shared_keywords": shared_kw,
            "same_domain": int(r1["domain"] == r2["domain"]),
            "same_institution_type": int(r1["institution_type"] == r2["institution_type"]),
            "same_country": int(r1["country"] == r2["country"]),
            "h_index_diff": abs(r1["h_index"] - r2["h_index"]),
            "experience_diff": abs(r1["years_experience"] - r2["years_experience"]),
            "total_grants": r1["grant_count"] + r2["grant_count"],
            "avg_publications": (r1["publications"] + r2["publications"]) / 2,
            "compatibility_score": compat_score,
            "compatible": compatible
        }
        records.append(record)

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = generate_dataset(2000)
    df.to_csv("academic_collaboration_dataset.csv", index=False)
    print(f"Dataset generated: {df.shape}")
    print(f"Class distribution:\n{df['compatible'].value_counts()}")
    print(f"\nFeature summary:\n{df.describe()}")
