import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
from PIL import Image
from driver_data import driver_info  # Import from your file

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
st.title("🏎️ F1 Telemetry Visualizer")

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

comparison_mode = st.sidebar.checkbox("🔀 Enable Multi-Driver Comparison")
driver1 = driver2 = driver = None

if comparison_mode and driver_options:
    driver1 = st.sidebar.selectbox("Select Driver 1", driver_options, key="driver1")
    driver2 = st.sidebar.selectbox("Select Driver 2", driver_options, key="driver2")
elif driver_options:
    driver = st.sidebar.selectbox("Select Driver", driver_options, key="driver_single")

# === Logo Loader ===
def display_driver_logo(code):
    """
    Display logo and driver full name + number using driver code from external file.
    """
    code = code.upper()
    logo_path = os.path.join("logos", f"{code}.png")
    col1, col2 = st.columns([1, 3])

    with col1:
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            st.image(img, width=100)
        else:
            st.warning(f"⚠️ Logo for '{code}' not found.")

    with col2:
        if code in driver_info:
            name = driver_info[code]["name"]
            number = driver_info[code]["number"]
            st.markdown(f"### #{number} {name}")
        else:
            st.warning(f"⚠️ Info for '{code}' not found.")

# === Load Telemetry Button ===
if st.sidebar.button("Load Telemetry"):
    try:
        # === Multi-Driver Comparison ===
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

                    # === Telemetry Snapshot ===
                    st.subheader("📊 Telemetry Snapshot")
                    col1, col2 = st.columns(2)
                    col1.write(f"**{driver1}**")
                    col1.dataframe(df1.head())
                    col2.write(f"**{driver2}**")
                    col2.dataframe(df2.head())

                    # === Track Map ===
                    st.subheader("🗺️ Track Map")
                    fig_map, ax_map = plt.subplots()
                    ax_map.plot(pos1['X'], pos1['Y'], label=driver1, color='blue')
                    ax_map.plot(pos2['X'], pos2['Y'], label=driver2, color='red')
                    ax_map.set_title("Track Comparison")
                    ax_map.axis('off')
                    ax_map.legend()
                    st.pyplot(fig_map)

                    # === Anomaly Detection (Speed) for Both Drivers ===
                    st.subheader("🔍 LSTM Anomaly Detection (Speed)")
                    try:
                        anomaly1, th1 = detect_anomalies_lstm(df1, field='Speed')
                        anomaly2, th2 = detect_anomalies_lstm(df2, field='Speed')

                        col_anom = st.columns(2)
                        with col_anom[0]:
                            st.write(f"**{driver1} Anomalies** (Threshold={th1:.2f})")
                            st.dataframe(anomaly1[['Time', 'Speed', 'anomaly_lstm']].head(20))
                        with col_anom[1]:
                            st.write(f"**{driver2} Anomalies** (Threshold={th2:.2f})")
                            st.dataframe(anomaly2[['Time', 'Speed', 'anomaly_lstm']].head(20))

                        # Plot anomalies
                        fig_anom, ax = plt.subplots(figsize=(14, 5))
                        ax.plot(anomaly1['Time'], anomaly1['Speed'], label=f'{driver1} Speed', color='blue')
                        ax.scatter(anomaly1['Time'][anomaly1['anomaly_lstm'] == 1],
                                   anomaly1['Speed'][anomaly1['anomaly_lstm'] == 1],
                                   color='red', label=f'{driver1} Anomalies', s=40)
                        ax.plot(anomaly2['Time'], anomaly2['Speed'], label=f'{driver2} Speed', color='green')
                        ax.scatter(anomaly2['Time'][anomaly2['anomaly_lstm'] == 1],
                                   anomaly2['Speed'][anomaly2['anomaly_lstm'] == 1],
                                   color='orange', label=f'{driver2} Anomalies', s=40)
                        ax.set_xlabel("Time (s)")
                        ax.set_ylabel("Speed (km/h)")
                        ax.legend()
                        st.pyplot(fig_anom)
                    except Exception as e:
                        st.warning(f"Anomaly detection failed: {e}")

                    # === Telemetry Comparison ===
                    st.subheader("📈 Speed / Throttle / Brake Comparison")
                    fig, ax1 = plt.subplots(figsize=(14, 6))
                    ax1.plot(df1['Time'], df1['Speed'], label=f'{driver1} Speed', color='blue')
                    ax1.plot(df2['Time'], df2['Speed'], label=f'{driver2} Speed', color='red')
                    ax1.set_xlabel("Time (s)")
                    ax1.set_ylabel("Speed (km/h)")
                    ax1.legend(loc="upper left")

                    ax2 = ax1.twinx()
                    ax2.plot(df1['Time'], df1['Throttle'] * 100, '--', label=f'{driver1} Throttle', color='cyan')
                    ax2.plot(df2['Time'], df2['Throttle'] * 100, '--', label=f'{driver2} Throttle', color='orange')
                    ax2.plot(df1['Time'], df1['Brake'] * 100, ':', label=f'{driver1} Brake', color='purple')
                    ax2.plot(df2['Time'], df2['Brake'] * 100, ':', label=f'{driver2} Brake', color='brown')
                    ax2.set_ylabel("Throttle / Brake (%)")
                    ax2.legend(loc="upper right")
                    st.pyplot(fig)

                    # === Gear Comparison ===
                    st.subheader("⚙️ Gear Comparison")
                    fig, ax = plt.subplots(figsize=(14, 4))
                    ax.plot(df1['Time'], df1['nGear'], label=f'{driver1} Gear', color='blue')
                    ax.plot(df2['Time'], df2['nGear'], label=f'{driver2} Gear', color='red')
                    ax.set_xlabel("Time (s)")
                    ax.set_ylabel("Gear")
                    ax.legend()
                    st.pyplot(fig)

                    # === Tire Temp / Pressure / ERS Comparison ===
                    st.subheader("🔥 Tire Temp / Pressure / ERS Comparison")
                    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
                    axs[0].plot(df1['Time'], df1['TyreSurfaceTemperature'], color='blue', label=f'{driver1} Tire Temp')
                    axs[0].plot(df2['Time'], df2['TyreSurfaceTemperature'], color='red', label=f'{driver2} Tire Temp')
                    axs[0].legend()
                    axs[1].plot(df1['Time'], df1['TyrePressure'], color='blue', label=f'{driver1} Tire Pressure')
                    axs[1].plot(df2['Time'], df2['TyrePressure'], color='red', label=f'{driver2} Tire Pressure')
                    axs[1].legend()
                    axs[2].plot(df1['Time'], df1['ERSDeployMode'], color='blue', label=f'{driver1} ERS Mode')
                    axs[2].plot(df2['Time'], df2['ERSDeployMode'], color='red', label=f'{driver2} ERS Mode')
                    axs[2].legend()
                    axs[0].set_ylabel("°C")
                    axs[1].set_ylabel("psi")
                    axs[2].set_ylabel("ERS")
                    axs[2].set_xlabel("Time (s)")
                    st.pyplot(fig)

                    # === Pit Stops for Both Drivers ===
                    st.subheader("🛑 Pit Stops Comparison")
                    try:
                        pit_df1 = get_pit_stops(year, gp, session_type, driver1)
                        pit_df2 = get_pit_stops(year, gp, session_type, driver2)

                        col_pit = st.columns(2)
                        with col_pit[0]:
                            st.write(f"**{driver1} Pit Stops**")
                            st.dataframe(pit_df1 if not pit_df1.empty else pd.DataFrame({"Info": ["No pit stops"]}))
                        with col_pit[1]:
                            st.write(f"**{driver2} Pit Stops**")
                            st.dataframe(pit_df2 if not pit_df2.empty else pd.DataFrame({"Info": ["No pit stops"]}))
                    except Exception as e:
                        st.warning(f"Pit stop comparison failed: {e}")

        # === Single Driver Mode ===
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
                axs[0].plot(df['Time'], df['TyreSurfaceTemperature'], color='orange', label='Tire Temp')
                axs[1].plot(df['Time'], df['TyrePressure'], color='blue', label='Tire Pressure')
                axs[2].plot(df['Time'], df['ERSDeployMode'], color='purple', label='ERS Mode')
                axs[0].legend(); axs[1].legend(); axs[2].legend()
                axs[0].set_ylabel("°C"); axs[1].set_ylabel("psi"); axs[2].set_ylabel("ERS")
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
