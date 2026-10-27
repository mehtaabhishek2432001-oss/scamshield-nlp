import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

# Paths are based on this file's location, so the script works
# no matter which folder you run it from.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "cleaned_job_postings.csv"
MODEL_PATH = BASE_DIR / "models" / "scamshield_model.pkl"
METRICS_PATH = BASE_DIR / "models" / "metrics.json"


def main():
    # 1. Load data
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)
    df["combined_text"] = df["combined_text"].fillna("")

    X = df["combined_text"]
    y = df["fraudulent"]
    print(f"Total posts: {len(df)} | Fake: {y.sum()} | Real: {(y == 0).sum()}")

    # 2. Split: 80% train, 20% test, same fake/real ratio in both
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"Train: {len(X_train)} | Test: {len(X_test)}")

    # 3. Build pipeline: text -> TF-IDF numbers -> Logistic Regression
    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=30000,
            min_df=2,
            stop_words="english",
        )),
        ("clf", LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
        )),
    ])

    # 4. Train
    print("Training model... (this can take a minute)")
    model.fit(X_train, y_train)

    # 5. Evaluate on the unseen test set
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
    }

    print("\n===== RESULTS ON TEST SET =====")
    for name, value in metrics.items():
        print(f"{name:>10}: {value}")

    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion matrix:")
    print("                 Predicted REAL  Predicted FAKE")
    print(f"Actually REAL    {cm[0][0]:>14}  {cm[0][1]:>14}")
    print(f"Actually FAKE    {cm[1][0]:>14}  {cm[1][1]:>14}")

    print("\nClassification report:")
    print(classification_report(y_test, y_pred, target_names=["Real", "Fake"]))

    # 6. Save model and metrics
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")


if __name__ == "__main__":
    main()