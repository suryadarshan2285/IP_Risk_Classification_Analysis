import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def export_ip_data():
    connection_string = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )
    engine = create_engine(connection_string)
    df = pd.read_sql("SELECT * FROM ip_data", engine)
    df.to_csv("ip_data_export.csv", index=False)
    print(f"✅ Exported {len(df)} rows to ip_data_export.csv")

def export_model_results():
    """
    Manually structured from this session's actual model outputs —
    since these numbers only exist as printed Python output, not
    anywhere in Postgres.
    """
    results = [
        {"model": "Baseline (always malicious)", "threshold": 0.5, "recall": 1.00, "precision": 0.50, "accuracy": 0.50,
         "true_negative": 0, "false_positive": 60, "false_negative": 0, "true_positive": 60},
        {"model": "Logistic Regression", "threshold": 0.3, "recall": 0.95, "precision": 0.83, "accuracy": 0.88,
         "true_negative": 48, "false_positive": 12, "false_negative": 3, "true_positive": 57},
        {"model": "Random Forest", "threshold": 0.3, "recall": 0.97, "precision": 0.79, "accuracy": 0.86,
         "true_negative": 45, "false_positive": 15, "false_negative": 2, "true_positive": 58},
    ]
    
    df = pd.DataFrame(results)
    df.to_csv("model_results.csv", index=False)
    print(f"✅ Exported model results to model_results.csv")
    print(df)

def export_confusion_matrix_long():
    """
    A 'long format' export specifically for the confusion matrix heatmap.
    One row per (model, actual, predicted) combination — this shape lets
    Tableau build a 2x2 grid directly from real columns, avoiding the
    'Measure Names can't be used in calculated fields' limitation.
    """
    rows = [
        {"model": "Baseline (always malicious)", "actual": "Benign", "predicted": "Benign", "count": 0},
        {"model": "Baseline (always malicious)", "actual": "Benign", "predicted": "Malicious", "count": 60},
        {"model": "Baseline (always malicious)", "actual": "Malicious", "predicted": "Benign", "count": 0},
        {"model": "Baseline (always malicious)", "actual": "Malicious", "predicted": "Malicious", "count": 60},

        {"model": "Logistic Regression", "actual": "Benign", "predicted": "Benign", "count": 48},
        {"model": "Logistic Regression", "actual": "Benign", "predicted": "Malicious", "count": 12},
        {"model": "Logistic Regression", "actual": "Malicious", "predicted": "Benign", "count": 3},
        {"model": "Logistic Regression", "actual": "Malicious", "predicted": "Malicious", "count": 57},

        {"model": "Random Forest", "actual": "Benign", "predicted": "Benign", "count": 45},
        {"model": "Random Forest", "actual": "Benign", "predicted": "Malicious", "count": 15},
        {"model": "Random Forest", "actual": "Malicious", "predicted": "Benign", "count": 2},
        {"model": "Random Forest", "actual": "Malicious", "predicted": "Malicious", "count": 58},
    ]

    df = pd.DataFrame(rows)
    df.to_csv("confusion_matrix_long.csv", index=False)
    print("✅ Exported confusion_matrix_long.csv")
    print(df)

if __name__ == "__main__":
    export_ip_data()
    export_model_results()
    export_confusion_matrix_long()

    