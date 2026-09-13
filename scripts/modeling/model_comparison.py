from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from feature_engineering import load_data, clean_isp_names, group_top_n, add_interaction_feature, prepare_features
import numpy as np

CHOSEN_THRESHOLD = 0.3

df = load_data()
df = clean_isp_names(df)
df = group_top_n(df, "country", n=10)
df = group_top_n(df, "isp", n=10)
df = add_interaction_feature(df)
X, y = prepare_features(df)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --- Baseline: always predict malicious ---
baseline = DummyClassifier(strategy="constant", constant=1)
baseline.fit(X_train, y_train)
baseline_pred = baseline.predict(X_test)

print("="*50)
print("BASELINE (always predicts malicious)")
print("="*50)
print(classification_report(y_test, baseline_pred))

# --- Cross-validation for both real models ---
log_reg = LogisticRegression(max_iter=1000)
rf = RandomForestClassifier(n_estimators=100, random_state=42)

# cv=5 means 5-fold cross-validation, scoring='recall' focuses 
# specifically on malicious-class recall, matching our project's priority
log_reg_scores = cross_val_score(log_reg, X, y, cv=5, scoring='recall')
rf_scores = cross_val_score(rf, X, y, cv=5, scoring='recall')

print("\n" + "="*50)
print("CROSS-VALIDATION (5-fold, recall scores)")
print("="*50)
print(f"Logistic Regression — scores per fold: {np.round(log_reg_scores, 3)}")
print(f"Logistic Regression — mean recall: {log_reg_scores.mean():.3f} (+/- {log_reg_scores.std():.3f})")
print(f"\nRandom Forest — scores per fold: {np.round(rf_scores, 3)}")
print(f"Random Forest — mean recall: {rf_scores.mean():.3f} (+/- {rf_scores.std():.3f})")