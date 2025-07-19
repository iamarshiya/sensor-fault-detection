import streamlit as st
import matplotlib.pyplot as plt
from f1_data_extractor import (
    get_driver_telemetry,
    simulate_telemetry_stream,
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

driver = st.sidebar.selectbox("Select Driver", driver_options) if driver_options else None

# Load Data
if st.sidebar.button("Load Telemetry") and driver:
    try:
        df, pos_data, session = get_driver_telemetry(year, gp, session_type, driver)
        st.success(f"✅ Data loaded for {driver} - {gp} {session_type} {year}")
        
        # Telemetry Table
        st.subheader("📊 Telemetry Snapshot")
        st.dataframe(df.head())

        # Track Map
        st.subheader("🗺️ Track Map")
        fig_map, ax_map = plt.subplots()
        ax_map.plot(pos_data['X'], pos_data['Y'], color='black')
        ax_map.set_title("Track Map")
        ax_map.axis('off')
        st.pyplot(fig_map)

        # Full Plot
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

        # Simulate
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
                ax1.set_title("Live Telemetry")
                ax1.legend(loc="upper left")
                ax2.legend(loc="upper right")

                plot_placeholder.pyplot(fig_live)

    except Exception as e:
        st.error(f"❌ Error loading telemetry: {e}")
        st.stop()
        