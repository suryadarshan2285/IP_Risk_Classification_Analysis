import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

load_dotenv()

def load_data():
    connection_string = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )
    engine = create_engine(connection_string)
    df = pd.read_sql("SELECT * FROM ip_data", engine)
    return df

def clean_isp_names(df):
    """
    Fixes known inconsistent ISP naming before grouping.
    """
    df["isp"] = df["isp"].replace({"BHARTI": "Bharti Airtel"})
    return df

def group_top_n(df, column, n=10):
    """
    Keeps the top N most frequent values in a column as-is,
    replaces everything else with 'Other'.
    """
    top_values = df[column].value_counts().nlargest(n).index
    df[column + "_grouped"] = df[column].where(df[column].isin(top_values), "Other")
    return df

if __name__ == "__main__":
    df = load_data()
    print(f"Loaded {len(df)} rows")
    print(df.head())
    
    df = clean_isp_names(df)
    
    df = group_top_n(df, "country", n=10)
    df = group_top_n(df, "isp", n=10)
    
    print("\nCountry grouping result:")
    print(df["country_grouped"].value_counts())
    
    print("\nISP grouping result:")
    print(df["isp_grouped"].value_counts())


def add_interaction_feature(df):
    """
    Creates a new feature: True only when BOTH hosting AND proxy are True.
    Directly justified by Phase 2 Question 10's finding (97.4% malicious 
    rate for this combination vs ~47% and ~36% for either alone).
    """
    df["hosting_and_proxy"] = df["hosting"] & df["proxy"]
    return df

def prepare_features(df):
    """
    Selects final feature columns and one-hot encodes the categorical ones.
    """
    feature_columns = [
        "country_grouped", "isp_grouped", 
        "mobile", "proxy", "hosting", "hosting_and_proxy"
    ]
    
    X = df[feature_columns]
    y = df["label"]
    
    # One-hot encode the two text-based categorical columns
    X = pd.get_dummies(X, columns=["country_grouped", "isp_grouped"], drop_first=True)
    
    return X, y

if __name__ == "__main__":
    df = load_data()
    df = clean_isp_names(df)
    df = group_top_n(df, "country", n=10)
    df = group_top_n(df, "isp", n=10)
    df = add_interaction_feature(df)
    
    X, y = prepare_features(df)
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Feature columns: {list(X.columns)}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {X_train.shape[0]} rows")
    print(f"Test set: {X_test.shape[0]} rows")
    print(f"\nTraining label balance:\n{y_train.value_counts()}")
    print(f"\nTest label balance:\n{y_test.value_counts()}")