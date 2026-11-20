
import pandas as pd
import streamlit as st

from pathlib import Path

DATA_PATH = Path("output/predictions_dataset.csv")

st.set_page_config(
    page_title="Industrial Motor Monitoring",
    page_icon="⚙️",
    layout="wide"
)

st.title("Industrial Equipment Condition Monitoring")
st.subheader("Motor Fault Detection Dashboard")

if st.button("Refresh Dashboard"):
    st.rerun()

if not DATA_PATH.exists():
    st.warning("No prediction data available. Run predict_recordings.py first.")
    st.stop()

data = pd.read_csv(DATA_PATH)

if data.empty:
    st.warning("No sensor readings available.")
    st.stop()

required_columns = [
    "timestamp",
    "recording",
    "reading_number",
    "vibration_rms",
    "temperature",
    "current",
    "prediction",
    "confidence"
]

if not set(required_columns).issubset(data.columns):
    st.error("Prediction dataset has an invalid format.")
    st.stop()

data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")

for column in ["vibration_rms", "temperature", "current", "confidence"]:
    data[column] = pd.to_numeric(data[column], errors="coerce")

data = data.dropna(subset=required_columns)

if data.empty:
    st.warning("No valid readings available.")
    st.stop()

latest = data.iloc[-1]

st.subheader("Latest Motor Condition")

if latest["prediction"] == "FAULTY":
    st.error("FAULT DETECTED")
else:
    st.success("MOTOR HEALTHY")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Vibration RMS",
    f"{latest['vibration_rms']:.3f} g"
)

col2.metric(
    "Temperature",
    f"{latest['temperature']:.2f} °C"
)

col3.metric(
    "Current",
    f"{latest['current']:.3f} A"
)

col4.metric(
    "Prediction Confidence",
    f"{latest['confidence']:.2f}%"
)

st.divider()

st.subheader("Sensor Monitoring")

chart_data = data.sort_values("timestamp").set_index("timestamp")

st.write("Vibration")
st.line_chart(chart_data["vibration_rms"])

st.write("Temperature")
st.line_chart(chart_data["temperature"])

st.write("Current")
st.line_chart(chart_data["current"])

st.divider()

st.subheader("Fault Detection Statistics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Readings", len(data))

col2.metric(
    "Healthy Readings",
    int((data["prediction"] == "HEALTHY").sum())
)

col3.metric(
    "Faulty Readings",
    int((data["prediction"] == "FAULTY").sum())
)

st.subheader("Prediction Distribution")

distribution = data["prediction"].value_counts()

st.bar_chart(distribution)

st.divider()

st.subheader("Recording History")

recordings = data["recording"].unique()

selected_recording = st.selectbox(
    "Select Recording",
    recordings
)

filtered_data = data[data["recording"] == selected_recording]

st.dataframe(
    filtered_data,
    use_container_width=True
)

st.subheader("Complete Prediction Dataset")

st.dataframe(
    data.sort_values("timestamp", ascending=False),
    use_container_width=True
)

csv_data = data.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Prediction Dataset",
    csv_data,
    "predictions_dataset.csv",
    "text/csv"
)
