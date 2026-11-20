
import joblib
import pandas as pd

from pathlib import Path
from datetime import datetime

MODEL_PATH = Path("model/motor_fault_model.joblib")
INPUT_DIR = Path("new_recordings")
OUTPUT_PATH = Path("output/predictions_dataset.csv")

FEATURES = [
    "vibration_rms",
    "temperature",
    "current"
]

if not MODEL_PATH.exists():
    raise FileNotFoundError("Train the model first")

model = joblib.load(MODEL_PATH)

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

recordings = sorted(INPUT_DIR.glob("*.csv"))

if not recordings:
    raise ValueError("No new recordings found")

results = []

for file in recordings:
    data = pd.read_csv(file)

    if not set(FEATURES).issubset(data.columns):
        print("Skipped:", file.name)
        continue

    X = data[FEATURES].apply(pd.to_numeric, errors="coerce")

    if X.isnull().any().any():
        print("Skipped invalid recording:", file.name)
        continue

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)

    for index, prediction in enumerate(predictions):
        confidence = probabilities[index][list(model.classes_).index(prediction)]

        results.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "recording": file.name,
            "reading_number": index + 1,
            "vibration_rms": X.iloc[index]["vibration_rms"],
            "temperature": X.iloc[index]["temperature"],
            "current": X.iloc[index]["current"],
            "prediction": "FAULTY" if prediction == 1 else "HEALTHY",
            "confidence": round(float(confidence) * 100, 2)
        })

if not results:
    raise ValueError("No valid recordings could be processed")

new_results = pd.DataFrame(results)

if OUTPUT_PATH.exists():
    new_results.to_csv(
        OUTPUT_PATH,
        mode="a",
        header=False,
        index=False
    )
else:
    new_results.to_csv(OUTPUT_PATH, index=False)

print(new_results.to_string(index=False))
print("\nPredictions saved to:", OUTPUT_PATH)
