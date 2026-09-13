from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from feature_engineering import load_data, clean_isp_names, group_top_n, add_interaction_feature, prepare_features
from sklearn.model_selection import train_test_split

CHOSEN_THRESHOLD = 0.3  # Deliberately below the default 0.5 — prioritizes recall
                         # over precision/accuracy, since missed threats (false 
                         # negatives) are costlier than false alarms in a security 
                         # context. See session log for full reasoning.

df = load_data()
df = clean_isp_names(df)
df = group_top_n(df, "country", n=10)
df = group_top_n(df, "isp", n=10)
df = add_interaction_feature(df)
X, y = prepare_features(df)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

y_probs = model.predict_proba(X_test)[:, 1]
y_pred = (y_probs >= CHOSEN_THRESHOLD).astype(int)

print(f"Logistic Regression — Threshold: {CHOSEN_THRESHOLD}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))