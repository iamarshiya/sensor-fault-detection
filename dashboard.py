import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
st.set_page_config(page_title="Sensor Fault Detection", layout="wide")

st.title("🔍 Sensor Fault Detection Dashboard")
st.markdown("Detect sensor anomalies using **Isolation Forest**")

uploaded_file = st.file_uploader("Upload Sensor CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📊 Preview of Uploaded Data", df.head())

    model = IsolationForest(contamination=0.05)
    df["anomaly"] = model.fit_predict(df[["sensor"]])

    st.line_chart(df["sensor"])

    # Show anomalies
    st.subheader("🚨 Detected Anomalies")
    anomalies = df[df["anomaly"] == -1]
    st.dataframe(anomalies)

    # Plot
    fig, ax = plt.subplots()
    ax.plot(df["time"], df["sensor"], label="Sensor")
    ax.scatter(anomalies["time"], anomalies["sensor"], color="red", label="Anomaly")
    ax.legend()
    st.pyplot(fig)

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/McLaren.svg/1200px-McLaren.svg.png", width=150)
    st.title("🔧 Options")
    model_option = st.radio("Select Model:", ["Isolation Forest", "LSTM Autoencoder"])
    st.markdown("---")
    st.markdown("Built by **Arshiya**")
