# dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import numpy as np
from lstm_autoencoder import detect_anomalies_lstm

st.set_page_config(page_title="Sensor Fault Detection Dashboard", layout="wide")

st.title("📊 Sensor Fault Detection Dashboard")

# Sidebar with visual section
def sidebar_options():
    with st.sidebar:
        st.title("🔧 Options")
        model = st.radio("Select Anomaly Detection Model:", ("Isolation Forest", "LSTM Autoencoder"))
        st.markdown("---")
        st.markdown("Created by Arshiya")
    return model

model_option = sidebar_options()

# Load or simulate sensor data
def load_sensor_data():
    np.random.seed(42)
    time = np.arange(0, 1000)
    sensor = 25 + np.random.normal(0, 0.5, 1000)
    sensor[700:] += np.linspace(0, 5, 300)
    df = pd.DataFrame({"time": time, "sensor": sensor})
    return df

df = load_sensor_data()

if model_option == "Isolation Forest":
    st.subheader("🔍 Anomaly Detection using Isolation Forest")
    model = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly'] = model.fit_predict(df[['sensor']])
    df['anomaly'] = df['anomaly'].apply(lambda x: 1 if x == -1 else 0)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df['time'], df['sensor'], label='Sensor Data')
    ax.scatter(df[df['anomaly'] == 1]['time'], df[df['anomaly'] == 1]['sensor'], color='red', label='Anomalies')
    ax.set_title('Sensor Data with Detected Anomalies (Isolation Forest)')
    ax.set_xlabel('Time')
    ax.set_ylabel('Sensor Reading')
    ax.legend()
    st.pyplot(fig)

elif model_option == "LSTM Autoencoder":
    st.subheader("🤖 Anomaly Detection using LSTM Autoencoder")
    df_lstm, threshold = detect_anomalies_lstm()

    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.plot(df_lstm['time'], df_lstm['sensor'], label='Sensor Data')
    ax2.scatter(df_lstm[df_lstm['anomaly_lstm'] == 1]['time'],
                df_lstm[df_lstm['anomaly_lstm'] == 1]['sensor'],
                color='red', label='Anomalies')
    ax2.set_title(f'Sensor Data with Detected Anomalies (LSTM Autoencoder)\nThreshold = {threshold:.4f}')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Sensor Reading')
    ax2.legend()
    st.pyplot(fig2)

st.markdown("---")
st.dataframe(df.head(20))
