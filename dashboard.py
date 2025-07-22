import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
from PIL import Image

from lstm_autoencoder import detect_anomalies_lstm
from f1_data_extractor import (
    get_driver_telemetry,
    get_available_grands_prix,
    get_driver_codes,
    get_pit_stops,
    simulate_telemetry_stream
)

# Page Config
st.set_page_config(page_title="🏎️ F1 Telemetry Dashboard", layout="wide")
st.title("🏁 F1 Telemetry Visualizer")

# === Sidebar Inputs ===
year = st.sidebar.selectbox("Select Year", [2020, 2021, 2022, 2023, 2024, 2025])

try:
    gps = get_available_grands_prix(year)
except Exception as e:
    st.sidebar.error(f"Failed to load Grand Prix list: {e}")
    gps = []

gp = st.sidebar.selectbox("Select Grand Prix", gps)
session_type = st.sidebar.selectbox("Session Type", ["FP1", "FP2", "FP3", "Q", "R"])

# === Driver Selection ===
try:
    driver_options = get_driver_codes(year, gp, session_type)
except Exception:
    driver_options = []
    st.sidebar.warning("Load GP first to see drivers.")

comparison_mode = st.sidebar.checkbox("🔁 Enable Multi-Driver Comparison")
driver1 = driver2 = driver = None

if comparison_mode and driver_options:
    driver1 = st.sidebar.selectbox("Select Driver 1", driver_options, key="driver1")
    driver2 = st.sidebar.selectbox("Select Driver 2", driver_options, key="driver2")
elif driver_options:
    driver = st.sidebar.selectbox("Select Driver", driver_options, key="driver_single")

# === Logo Loader ===
def display_driver_logo(code):
    logo_path = os.path.join("logos", f"{code.upper()}.png")  # Not under /data
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        st.image(img, width=100)
    else:
        st.warning(f"⚠️ Logo for {code} not found.")

# === Load Telemetry Button ===
if st.sidebar.button("Load Telemetry"):
    try:
        if comparison_mode:
            if driver1 == driver2:
                st.error("❌ Select different drivers.")
            else:
                df1, pos1, code1 = get_driver_telemetry(year, gp, session_type, driver1)
                df2, pos2, code2 = get_driver_telemetry(year, gp, session_type, driver2)

                if df1 is None or df2 is None:
                    st.error("❌ No telemetry data available.")
                else:
                    st.success(f"✅ Loaded telemetry for {driver1} vs {driver2}")

                    col_logos = st.columns(2)
                    with col_logos[0]: display_driver_logo(code1)
                    with col_logos[1]: display_driver_logo(code2)

                    st.subheader("📊 Telemetry Snapshot")
                    col1, col2 = st.columns(2)
                    col1.write(f"**{driver1}**")
                    col1.dataframe(df1.head())
                    col2.write(f"**{driver2}**")
                    col2.dataframe(df2.head())

                    st.subheader("🗺️ Track Map")
                    fig_map, ax_map = plt.subplots()
                    ax_map.plot(pos1['X'], pos1['Y'], label=driver1, color='blue')
                    ax_map.plot(pos2['X'], pos2['Y'], label=driver2, color='red')
                    ax_map.set_title("Track Comparison")
                    ax_map.axis('off')
                    ax_map.legend()
                    st.pyplot(fig_map)

        elif driver:
            df, pos, code = get_driver_telemetry(year, gp, session_type, driver)

            if df is None:
                st.error("❌ No telemetry data found.")
            else:
                st.success(f"✅ Data loaded for {driver}")
                display_driver_logo(code)

                st.subheader("📊 Telemetry Snapshot")
                st.dataframe(df.head())

                st.subheader("🔍 LSTM Anomaly Detection (Speed)")
                try:
                    anomaly_df, threshold = detect_anomalies_lstm(df, field='Speed')
                    st.dataframe(anomaly_df[['Time', 'Speed', 'anomaly_lstm']])
                except Exception as e:
                    st.warning(f"Anomaly detection failed: {e}")

                st.subheader("🗺️ Track Map")
                fig_map, ax_map = plt.subplots()
                ax_map.plot(pos['X'], pos['Y'], color='black')
                ax_map.set_title("Track Map")
                ax_map.axis('off')
                st.pyplot(fig_map)

                st.subheader("📈 Full Telemetry Plot")
                fig, ax1 = plt.subplots(figsize=(14, 6))
                ax1.plot(df['Time'], df['Throttle'] * 100, label='Throttle (%)', color='green')
                ax1.plot(df['Time'], df['Brake'] * 100, label='Brake (%)', color='red')
                ax1.plot(df['Time'], df['Speed'], label='Speed (km/h)', color='blue')

                ax2 = ax1.twinx()
                ax2.plot(df['Time'], df['nGear'], label='Gear', color='purple', linestyle='--')
                ax1.set_xlabel("Time (s)")
                ax1.set_ylabel("Throttle / Brake / Speed")
                ax2.set_ylabel("Gear")
                ax1.legend(loc="upper left")
                ax2.legend(loc="upper right")
                st.pyplot(fig)

                st.subheader("🔥 Tire Temp / Pressure / ERS")
                fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

                if 'TyreSurfaceTemperature' in df.columns:
                    axs[0].plot(df['Time'], df['TyreSurfaceTemperature'], color='orange', label='Tire Temp')
                    axs[0].legend()
                else:
                    axs[0].text(0.5, 0.5, "No Tire Temp data", ha='center')

                if 'TyrePressure' in df.columns:
                    axs[1].plot(df['Time'], df['TyrePressure'], color='blue', label='Tire Pressure')
                    axs[1].legend()
                else:
                    axs[1].text(0.5, 0.5, "No Tire Pressure data", ha='center')

                if 'ERSDeployMode' in df.columns:
                    axs[2].plot(df['Time'], df['ERSDeployMode'], color='purple', label='ERS Mode')
                    axs[2].legend()
                else:
                    axs[2].text(0.5, 0.5, "No ERS data", ha='center')

                axs[0].set_ylabel("°C")
                axs[1].set_ylabel("psi")
                axs[2].set_ylabel("ERS")
                axs[2].set_xlabel("Time (s)")
                st.pyplot(fig)

                st.subheader("🛑 Pit Stop Detection")
                try:
                    pit_df = get_pit_stops(year, gp, session_type, driver)
                    if not pit_df.empty:
                        st.dataframe(pit_df)
                    else:
                        st.info("No pit stops found.")
                except Exception as e:
                    st.warning(f"Pit stop detection failed: {e}")

                if st.button("🚦 Start Live Simulation"):
                    st.subheader("📡 Live Telemetry Simulation")
                    plot_placeholder = st.empty()
                    for stream_df in simulate_telemetry_stream(df):
                        fig_live, ax1 = plt.subplots(figsize=(10, 5))
                        ax1.plot(stream_df['Time'], stream_df['Throttle'] * 100, label='Throttle (%)', color='blue')
                        ax1.plot(stream_df['Time'], stream_df['Brake'] * 100, label='Brake (%)', color='red')
                        ax1.plot(stream_df['Time'], stream_df['Speed'], label='Speed (km/h)', color='green')

                        ax2 = ax1.twinx()
                        ax2.plot(stream_df['Time'], stream_df['nGear'], label='Gear', linestyle='--', color='purple')

                        ax1.set_xlabel("Time (s)")
                        ax1.set_ylabel("Throttle / Brake / Speed")
                        ax2.set_ylabel("Gear")

                        ax1.legend(loc="upper left")
                        ax2.legend(loc="upper right")
                        plot_placeholder.pyplot(fig_live)

    except Exception as e:
        st.error(f"❌ Error loading telemetry: {e}")
