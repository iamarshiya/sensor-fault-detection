import streamlit as st
import matplotlib.pyplot as plt
from lstm_autoencoder import detect_anomalies_lstm

from f1_data_extractor import (
    get_driver_telemetry,
    get_available_grands_prix,
    get_driver_codes
)

st.set_page_config(page_title="🏎️ F1 Telemetry Dashboard", layout="wide")
st.title("🏁 F1 Telemetry Visualizer")

# Sidebar selections
year = st.sidebar.selectbox("Select Year", [2022, 2023, 2024])
available_gps = get_available_grands_prix(year)
gp = st.sidebar.selectbox("Select Grand Prix", available_gps)

session_type = st.sidebar.selectbox("Session Type", ["FP1", "FP2", "FP3", "Q", "R"])

driver_options = []
try:
    driver_options = get_driver_codes(year, gp, session_type)
except:
    st.sidebar.warning("Load GP first to see drivers.")

comparison_mode = st.sidebar.checkbox("🔁 Enable Multi-Driver Comparison")

if comparison_mode and driver_options:
    driver1 = st.sidebar.selectbox("Select Driver 1", driver_options, key="driver1")
    driver2 = st.sidebar.selectbox("Select Driver 2", driver_options, key="driver2")
else:
    driver = st.sidebar.selectbox("Select Driver", driver_options, key="driver_single") if driver_options else None

if st.sidebar.button("Load Telemetry"):
    try:
        if comparison_mode:
            if driver1 == driver2:
                st.error("❌ Please select two different drivers for comparison.")
            else:
                df1, pos1, _ = get_driver_telemetry(year, gp, session_type, driver1)
                df2, pos2, _ = get_driver_telemetry(year, gp, session_type, driver2)

                st.success(f"✅ Data loaded for {driver1} vs {driver2} - {gp} {session_type} {year}")

                st.subheader("📊 Telemetry Comparison (Top Rows)")
                col1, col2 = st.columns(2)
                col1.write(f"**{driver1}**")
                col1.dataframe(df1.head())
                col2.write(f"**{driver2}**")
                col2.dataframe(df2.head())

                st.subheader("🗺️ Track Maps")
                fig_map, ax_map = plt.subplots()
                ax_map.plot(pos1['X'], pos1['Y'], color='blue', label=driver1)
                ax_map.plot(pos2['X'], pos2['Y'], color='red', label=driver2)
                ax_map.set_title("Track Map Comparison")
                ax_map.axis('off')
                ax_map.legend()
                st.pyplot(fig_map)

                st.subheader("📈 Full Telemetry Plot")
                fig, ax1 = plt.subplots(figsize=(14, 6))
                ax1.plot(df1['Time'], df1['Speed'], label=f'{driver1} Speed', color='blue')
                ax1.plot(df2['Time'], df2['Speed'], label=f'{driver2} Speed', color='red')

                ax2 = ax1.twinx()
                ax2.plot(df1['Time'], df1['nGear'], label=f'{driver1} Gear', linestyle='--', color='blue', alpha=0.5)
                ax2.plot(df2['Time'], df2['nGear'], label=f'{driver2} Gear', linestyle='--', color='red', alpha=0.5)

                ax1.set_xlabel("Time (s)")
                ax1.set_ylabel("Speed (km/h)")
                ax2.set_ylabel("Gear")

                ax1.set_title(f"{driver1} vs {driver2} - {gp} {session_type} {year}")
                ax1.legend(loc="upper left")
                ax2.legend(loc="upper right")
                st.pyplot(fig)

        else:
            df, pos_data, _ = get_driver_telemetry(year, gp, session_type, driver)
            st.success(f"✅ Data loaded for {driver} - {gp} {session_type} {year}")

            st.subheader("📊 Telemetry Snapshot")
            st.dataframe(df.head())

            st.subheader("🗺️ Track Map")
            fig_map, ax_map = plt.subplots()
            ax_map.plot(pos_data['X'], pos_data['Y'], color='black')
            ax_map.set_title("Track Map")
            ax_map.axis('off')
            st.pyplot(fig_map)

            st.subheader("📈 Full Telemetry Plot")
            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax1.plot(df['Time'], df['Throttle'] * 100, label='Throttle (%)', color='blue')
            ax1.plot(df['Time'], df['Brake'] * 100, label='Brake (%)', color='red')
            ax1.plot(df['Time'], df['Speed'], label='Speed (km/h)', color='green')

            ax2 = ax1.twinx()
            ax2.plot(df['Time'], df['nGear'], label='Gear', linestyle='--', color='purple')

            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Throttle / Brake / Speed")
            ax2.set_ylabel("Gear")
            ax1.set_title(f"{driver} - {gp} {session_type} {year}")
            ax1.legend(loc="upper left")
            ax2.legend(loc="upper right")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error loading telemetry: {e}")

 # LSTM Anomaly Detection
    anomaly_df, threshold = detect_anomalies_lstm(df, field='Speed')
    st.subheader("🔍 LSTM Anomaly Detection (on Speed)")
    st.dataframe(anomaly_df[['Time', 'Speed', 'anomaly_lstm']])
