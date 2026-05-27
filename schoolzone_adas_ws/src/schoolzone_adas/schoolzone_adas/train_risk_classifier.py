import argparse
from pathlib import Path

from .common import FEATURE_NAMES


def main():
    parser = argparse.ArgumentParser(description="Train the school-zone ADAS risk classifier.")
    parser.add_argument("--input", default="data/features.csv", help="CSV file with feature rows and label/risk_state.")
    parser.add_argument("--output", default="models/risk_classifier.pkl", help="Output joblib model path.")
    parser.add_argument("--trees", type=int, default=200, help="Number of Random Forest trees.")
    args = parser.parse_args()

    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report
    from sklearn.model_selection import train_test_split

    input_path = Path(args.input)
    output_path = Path(args.output)
    df = pd.read_csv(input_path)
    label_col = "label" if "label" in df.columns else "risk_state"
    missing = [name for name in FEATURE_NAMES if name not in df.columns]
    if missing:
        raise ValueError(f"missing feature columns: {missing}")
    if label_col not in df.columns:
        raise ValueError("CSV must contain either 'label' or 'risk_state'")

    x = df[list(FEATURE_NAMES)].fillna(0.0)
    y = df[label_col].astype(str)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y if y.nunique() > 1 else None
    )
    model = RandomForestClassifier(
        n_estimators=args.trees,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(x_train, y_train)
    print(classification_report(y_test, model.predict(x_test), zero_division=0))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(f"saved model: {output_path}")


if __name__ == "__main__":
    main()
