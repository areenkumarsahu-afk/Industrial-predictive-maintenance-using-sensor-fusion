
import joblib
import pandas as pd

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

TRAINING_DIR = Path("training_recordings")
MODEL_PATH = Path("model/motor_fault_model.joblib")

FEATURES = [
    "vibration_rms",
    "temperature",
    "current"
]

recordings = list(TRAINING_DIR.glob("*.csv"))

if len(recordings) != 4:
    raise ValueError("Provide exactly four training recordings")

datasets = []

for file in recordings:
    filename = file.stem.lower()

    if filename.startswith("healthy_"):
        label = 0
    elif filename.startswith("faulty_"):
        label = 1
    else:
        raise ValueError(f"Invalid recording filename: {file.name}")

    data = pd.read_csv(file)

    if not set(FEATURES).issubset(data.columns):
        raise ValueError(f"Missing sensor columns in {file.name}")

    data = data[FEATURES].apply(pd.to_numeric, errors="coerce")

    if data.isnull().any().any():
        raise ValueError(f"Invalid sensor readings in {file.name}")

    if not data.map(lambda x: pd.notna(x) and abs(x) != float("inf")).all().all():
        raise ValueError(f"Non-finite sensor readings in {file.name}")

    data["label"] = label
    datasets.append(data)

dataset = pd.concat(datasets, ignore_index=True)

if set(dataset["label"].unique()) != {0, 1}:
    raise ValueError("Training data must contain healthy and faulty recordings")

X = dataset[FEATURES]
y = dataset["label"]

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(model, MODEL_PATH)

print("Training completed")
print("Training recordings:", len(recordings))
print("Training readings:", len(dataset))
print("Healthy readings:", int((y == 0).sum()))
print("Faulty readings:", int((y == 1).sum()))
print("Model saved:", MODEL_PATH)
