from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from feature_engineering import load_data, clean_isp_names, group_top_n, add_interaction_feature, prepare_features
from sklearn.model_selection import train_test_split
import pandas as pd

CHOSEN_THRESHOLD = 0.3  # Same threshold as Logistic Regression, for a fair comparison

df = load_data()
df = clean_isp_names(df)
df = group_top_n(df, "country", n=10)
df = group_top_n(df, "isp", n=10)
df = add_interaction_feature(df)
X, y = prepare_features(df)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Build and train the forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict, using the same threshold as before
y_probs = model.predict_proba(X_test)[:, 1]
y_pred = (y_probs >= CHOSEN_THRESHOLD).astype(int)

print(f"Random Forest — Threshold: {CHOSEN_THRESHOLD}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Feature importance — which features did the forest rely on most?
importances = pd.Series(model.feature_importances_, index=X.columns)
importances = importances.sort_values(ascending=False)

print("\nTop 10 most important features:")
print(importances.head(10))