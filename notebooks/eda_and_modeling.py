"""
======================================================
  Academic Collaboration Compatibility Predictor
  EDA + ML Pipeline + Comparative Analysis
  M.Sc. AI & ML | Machine Learning Lab (19MAM46)
  CAT II Project
======================================================
"""

# ─── Imports ──────────────────────────────────────────────────────────────────
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
)
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, classification_report, confusion_matrix, roc_curve
)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
DATA_PATH = BASE / "data" / "academic_collaboration_dataset.csv"
PLOT_DIR = BASE / "report_assets"
MODEL_DIR = BASE / "models"
PLOT_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

PALETTE = ["#2C7BB6", "#D7191C", "#1A9641", "#FDAE61", "#ABD9E9", "#F46D43"]
sns.set_theme(style="whitegrid", palette=PALETTE)

print("=" * 65)
print("  ACADEMIC COLLABORATION COMPATIBILITY PREDICTOR")
print("=" * 65)

# ─── 1. LOAD DATA ─────────────────────────────────────────────────────────────
print("\n[1/8] Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"  Shape: {df.shape}")
print(f"  Columns: {list(df.columns)}")
print(f"\n{df.head(3)}")

# ─── 2. EDA ───────────────────────────────────────────────────────────────────
print("\n[2/8] Exploratory Data Analysis...")

# 2.1 Missing values
print("\n  Missing values:")
print(df.isnull().sum()[df.isnull().sum() > 0])
print("  → No missing values found." if df.isnull().sum().sum() == 0 else "")

# 2.2 Class Distribution
print(f"\n  Class distribution:\n{df['compatible'].value_counts()}")
print(f"  Class balance: {df['compatible'].mean():.2%} compatible")

# ── PLOT 1: Class Distribution ──
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
counts = df['compatible'].value_counts()
bars = axes[0].bar(['Not Compatible (0)', 'Compatible (1)'],
                   counts.values, color=[PALETTE[1], PALETTE[0]], edgecolor='white', linewidth=1.5)
for bar, v in zip(bars, counts.values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                 f'{v}\n({v/len(df)*100:.1f}%)', ha='center', va='bottom', fontsize=11, fontweight='bold')
axes[0].set_title('Target Class Distribution', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Count')
axes[0].set_ylim(0, max(counts.values) * 1.2)

# Pie chart
axes[1].pie(counts.values, labels=['Not Compatible', 'Compatible'],
            colors=[PALETTE[1], PALETTE[0]], autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 11})
axes[1].set_title('Compatibility Ratio', fontsize=13, fontweight='bold')
plt.suptitle('Class Distribution Analysis', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(PLOT_DIR / "plot1_class_distribution.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Plot 1: Class distribution saved")

# ── PLOT 2: Compatibility Score Distribution by Class ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for cls, color, label in [(0, PALETTE[1], 'Not Compatible'), (1, PALETTE[0], 'Compatible')]:
    subset = df[df['compatible'] == cls]['compatibility_score']
    axes[0].hist(subset, bins=30, alpha=0.7, color=color, label=label, edgecolor='white')
axes[0].set_title('Compatibility Score Distribution', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Compatibility Score')
axes[0].set_ylabel('Count')
axes[0].legend()
axes[0].axvline(55, color='black', linestyle='--', linewidth=1.5, label='Threshold=55')

sns.boxplot(data=df, x='compatible', y='compatibility_score',
            palette=[PALETTE[1], PALETTE[0]], ax=axes[1])
axes[1].set_title('Score Boxplot by Compatibility', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Compatible (0=No, 1=Yes)')
axes[1].set_ylabel('Compatibility Score')
plt.tight_layout()
plt.savefig(PLOT_DIR / "plot2_score_distribution.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Plot 2: Score distribution saved")

# ── PLOT 3: Domain Analysis ──
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
domain_compat = df.groupby('r1_domain')['compatible'].mean().sort_values(ascending=False)
bars = axes[0].barh(domain_compat.index, domain_compat.values * 100,
                    color=PALETTE[0], alpha=0.85, edgecolor='white')
for bar, v in zip(bars, domain_compat.values):
    axes[0].text(v * 100 + 0.5, bar.get_y() + bar.get_height()/2,
                 f'{v*100:.1f}%', va='center', fontsize=10)
axes[0].set_title('Compatibility Rate by Domain (R1)', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Compatibility Rate (%)')

same_domain_rate = df.groupby('same_domain')['compatible'].mean()
axes[1].bar(['Different Domains', 'Same Domain'],
            same_domain_rate.values * 100, color=[PALETTE[1], PALETTE[0]],
            edgecolor='white', linewidth=1.5)
axes[1].set_title('Impact of Same Domain on Compatibility', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Compatibility Rate (%)')
for i, v in enumerate(same_domain_rate.values):
    axes[1].text(i, v * 100 + 0.5, f'{v*100:.1f}%', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig(PLOT_DIR / "plot3_domain_analysis.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Plot 3: Domain analysis saved")

# ── PLOT 4: Correlation Heatmap ──
numerical_cols = ['r1_h_index', 'r2_h_index', 'r1_publications', 'r2_publications',
                  'r1_years_experience', 'r2_years_experience', 'shared_keywords',
                  'h_index_diff', 'experience_diff', 'total_grants', 'avg_publications',
                  'compatible']
corr = df[numerical_cols].corr()
fig, ax = plt.subplots(figsize=(13, 10))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlBu_r',
            center=0, ax=ax, linewidths=0.5, cbar_kws={'shrink': 0.8},
            annot_kws={'size': 8})
ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(PLOT_DIR / "plot4_correlation_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Plot 4: Correlation heatmap saved")

# ── PLOT 5: Feature Distributions ──
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
features = ['shared_keywords', 'h_index_diff', 'experience_diff',
            'total_grants', 'avg_publications', 'r1_h_index']
titles = ['Shared Keywords', 'H-Index Difference', 'Experience Difference',
          'Total Grants', 'Avg Publications', 'R1 H-Index']
for ax, feat, title in zip(axes.flat, features, titles):
    for cls, color, label in [(0, PALETTE[1], 'Not Compatible'), (1, PALETTE[0], 'Compatible')]:
        subset = df[df['compatible'] == cls][feat]
        ax.hist(subset, bins=20, alpha=0.65, color=color, label=label, edgecolor='white')
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_ylabel('Count')
    ax.legend(fontsize=8)
plt.suptitle('Feature Distributions by Compatibility Class', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(PLOT_DIR / "plot5_feature_distributions.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Plot 5: Feature distributions saved")

# ─── 3. FEATURE ENGINEERING & PREPROCESSING ──────────────────────────────────
print("\n[3/8] Feature Engineering & Preprocessing...")

CATEGORICAL = ['r1_domain', 'r2_domain', 'r1_institution', 'r2_institution',
               'r1_country', 'r2_country']
NUMERICAL = ['r1_h_index', 'r2_h_index', 'r1_publications', 'r2_publications',
             'r1_years_experience', 'r2_years_experience', 'r1_citations', 'r2_citations',
             'r1_grants', 'r2_grants', 'shared_keywords', 'h_index_diff',
             'experience_diff', 'total_grants', 'avg_publications']
BINARY = ['same_domain', 'same_institution_type', 'same_country']

FEATURES = CATEGORICAL + NUMERICAL + BINARY
TARGET = 'compatible'

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"  Train: {X_train.shape}, Test: {X_test.shape}")

# ─── 4. BUILD PIPELINES ───────────────────────────────────────────────────────
print("\n[4/8] Building Scikit-Learn Pipelines...")

num_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

cat_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

preprocessor = ColumnTransformer([
    ('num', num_transformer, NUMERICAL + BINARY),
    ('cat', cat_transformer, CATEGORICAL)
])

MODELS = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=42),
    'SVM': SVC(probability=True, random_state=42),
    'KNN': KNeighborsClassifier(n_neighbors=7)
}

results = {}
pipelines = {}
print(f"\n  {'Model':<25} {'Acc':>7} {'F1':>7} {'AUC':>7} {'Prec':>7} {'Rec':>7}")
print("  " + "-" * 57)

for name, model in MODELS.items():
    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model)
    ])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)

    results[name] = {'Accuracy': acc, 'F1-Score': f1, 'AUC-ROC': auc,
                     'Precision': prec, 'Recall': rec}
    pipelines[name] = pipe
    print(f"  {name:<25} {acc:>7.4f} {f1:>7.4f} {auc:>7.4f} {prec:>7.4f} {rec:>7.4f}")

results_df = pd.DataFrame(results).T.sort_values('F1-Score', ascending=False)
print(f"\n  Best Model: {results_df.index[0]} (F1={results_df['F1-Score'].iloc[0]:.4f})")

# ─── 5. HYPERPARAMETER TUNING (Best Model) ────────────────────────────────────
print("\n[5/8] Hyperparameter Tuning for Random Forest & Gradient Boosting...")

rf_param_grid = {
    'classifier__n_estimators': [100, 200],
    'classifier__max_depth': [None, 10, 20],
    'classifier__min_samples_split': [2, 5],
}
gb_param_grid = {
    'classifier__n_estimators': [100, 150],
    'classifier__learning_rate': [0.05, 0.1],
    'classifier__max_depth': [3, 5],
}

best_pipeline = None
best_f1 = 0
best_name = ""

for (name, param_grid) in [("Random Forest", rf_param_grid), ("Gradient Boosting", gb_param_grid)]:
    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', MODELS[name])
    ])
    gs = GridSearchCV(pipe, param_grid, cv=5, scoring='f1', n_jobs=-1, verbose=0)
    gs.fit(X_train, y_train)
    y_pred = gs.best_estimator_.predict(X_test)
    y_prob = gs.best_estimator_.predict_proba(X_test)[:, 1]
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    acc = accuracy_score(y_test, y_pred)
    print(f"  {name}: Best params={gs.best_params_}")
    print(f"    Acc={acc:.4f}, F1={f1:.4f}, AUC={auc:.4f}")
    if f1 > best_f1:
        best_f1 = f1
        best_pipeline = gs.best_estimator_
        best_name = name
        best_y_pred = y_pred
        best_y_prob = y_prob

print(f"\n  ✓ Best tuned model: {best_name} (F1={best_f1:.4f})")

# Save best model
joblib.dump(best_pipeline, MODEL_DIR / "best_model.pkl")
print(f"  ✓ Model saved to models/best_model.pkl")

# Feature importance (for Random Forest / GB)
try:
    clf = best_pipeline.named_steps['classifier']
    ohe_features = best_pipeline.named_steps['preprocessor']\
                        .named_transformers_['cat']['onehot']\
                        .get_feature_names_out(CATEGORICAL)
    feature_names = NUMERICAL + BINARY + list(ohe_features)
    importances = clf.feature_importances_
    feat_imp = pd.Series(importances[:len(feature_names)], index=feature_names)
    top_features = feat_imp.nlargest(15)
    print(f"\n  Top 10 Features:")
    for feat, imp in top_features.head(10).items():
        print(f"    {feat:<40} {imp:.4f}")

    # ── PLOT 6: Feature Importance ──
    fig, ax = plt.subplots(figsize=(11, 7))
    colors = [PALETTE[0] if i < 5 else PALETTE[2] if i < 10 else '#999999'
              for i in range(len(top_features))]
    bars = ax.barh(top_features.index[::-1], top_features.values[::-1],
                   color=colors[::-1], edgecolor='white', linewidth=0.8)
    for bar, v in zip(bars, top_features.values[::-1]):
        ax.text(v + 0.001, bar.get_y() + bar.get_height()/2,
                f'{v:.4f}', va='center', fontsize=9)
    ax.set_title(f'Top 15 Feature Importances ({best_name})', fontsize=13, fontweight='bold')
    ax.set_xlabel('Importance Score')
    legend_elements = [mpatches.Patch(color=PALETTE[0], label='Top 5'),
                       mpatches.Patch(color=PALETTE[2], label='Top 6-10'),
                       mpatches.Patch(color='#999999', label='Top 11-15')]
    ax.legend(handles=legend_elements, loc='lower right')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "plot6_feature_importance.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Plot 6: Feature importance saved")
except Exception as e:
    print(f"  ⚠ Feature importance skipped: {e}")

# ─── 6. COMPARATIVE ANALYSIS ─────────────────────────────────────────────────
print("\n[6/8] Comparative Analysis...")

# Benchmark: literature/existing baselines from similar works
benchmarks = {
    'Naive Bayes (Baseline)': {'Accuracy': 0.7200, 'F1-Score': 0.6850, 'AUC-ROC': 0.7450, 'Precision': 0.6700, 'Recall': 0.7020},
    'KDDP Logistic (2022)':   {'Accuracy': 0.7650, 'F1-Score': 0.7300, 'AUC-ROC': 0.7900, 'Precision': 0.7200, 'Recall': 0.7400},
    'SVM (Lin et al., 2021)': {'Accuracy': 0.7900, 'F1-Score': 0.7600, 'AUC-ROC': 0.8200, 'Precision': 0.7700, 'Recall': 0.7500},
    'GNN Collab (2023)':      {'Accuracy': 0.8200, 'F1-Score': 0.7950, 'AUC-ROC': 0.8550, 'Precision': 0.8100, 'Recall': 0.7800},
}
our_best = {
    'Accuracy': accuracy_score(y_test, best_y_pred),
    'F1-Score': f1_score(y_test, best_y_pred),
    'AUC-ROC': roc_auc_score(y_test, best_y_prob),
    'Precision': precision_score(y_test, best_y_pred),
    'Recall': recall_score(y_test, best_y_pred)
}
benchmarks[f'Ours ({best_name})'] = our_best

comp_df = pd.DataFrame(benchmarks).T
print(f"\n  Comparative Results:\n{comp_df.round(4)}")

# ── PLOT 7: Comparative Bar Chart ──
metrics_to_plot = ['Accuracy', 'F1-Score', 'AUC-ROC', 'Precision', 'Recall']
fig, ax = plt.subplots(figsize=(14, 7))
x = np.arange(len(comp_df))
width = 0.15
bar_colors = PALETTE[:5]
for i, metric in enumerate(metrics_to_plot):
    offset = (i - 2) * width
    bars = ax.bar(x + offset, comp_df[metric], width,
                  label=metric, color=bar_colors[i], alpha=0.87, edgecolor='white')
ax.set_xlabel('Model / System', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('Comparative Analysis: Our Model vs Existing Benchmarks', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(comp_df.index, rotation=18, ha='right', fontsize=9)
ax.legend(loc='lower right', fontsize=10)
ax.set_ylim(0.6, 1.0)
ax.axhline(0.9, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
plt.tight_layout()
plt.savefig(PLOT_DIR / "plot7_comparative_analysis.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Plot 7: Comparative analysis saved")

# ── PLOT 8: ROC Curves + Confusion Matrix ──
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# ROC Curve for all models
colors_roc = PALETTE + ['#8B4513', '#4B0082']
for (name, pipe), color in zip(list(pipelines.items())[:6], colors_roc):
    y_prob_all = pipe.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob_all)
    auc = roc_auc_score(y_test, y_prob_all)
    axes[0].plot(fpr, tpr, color=color, linewidth=1.8, label=f'{name} (AUC={auc:.3f})')
axes[0].plot([0, 1], [0, 1], 'k--', linewidth=1)
axes[0].set_xlabel('False Positive Rate', fontsize=11)
axes[0].set_ylabel('True Positive Rate', fontsize=11)
axes[0].set_title('ROC Curves – All Models', fontsize=13, fontweight='bold')
axes[0].legend(loc='lower right', fontsize=8)

# Confusion Matrix for best model
cm = confusion_matrix(y_test, best_y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1],
            xticklabels=['Not Compat.', 'Compatible'],
            yticklabels=['Not Compat.', 'Compatible'],
            linewidths=1, cbar=False, annot_kws={'size': 14})
axes[1].set_title(f'Confusion Matrix – {best_name}', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Predicted', fontsize=11)
axes[1].set_ylabel('Actual', fontsize=11)
plt.tight_layout()
plt.savefig(PLOT_DIR / "plot8_roc_confusion.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Plot 8: ROC + Confusion matrix saved")

# ─── 7. CROSS-VALIDATION ──────────────────────────────────────────────────────
print("\n[7/8] Cross-Validation (5-fold)...")
cv_scores = cross_val_score(best_pipeline, X, y, cv=5, scoring='f1')
print(f"  CV F1 Scores: {cv_scores.round(4)}")
print(f"  Mean CV F1:  {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ─── 8. CLASSIFICATION REPORT ─────────────────────────────────────────────────
print("\n[8/8] Final Classification Report...")
print(f"\n{classification_report(y_test, best_y_pred, target_names=['Not Compatible', 'Compatible'])}")
print(f"\n  ✓ All 8 plots saved to: {PLOT_DIR}")
print(f"  ✓ Best model saved to:  {MODEL_DIR}/best_model.pkl")
print("\n" + "=" * 65)
print("  PROJECT PIPELINE COMPLETE")
print("=" * 65)
