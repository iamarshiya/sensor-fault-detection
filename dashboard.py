import streamlit as st
import matplotlib.pyplot as plt
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

# Driver selection
driver_options = []
try:
    driver_options = get_driver_codes(year, gp, session_type)
except:
    st.sidebar.warning("Load GP first to see drivers.")

multi_driver_mode = st.sidebar.checkbox("Enable Multi-Driver Comparison")
selected_drivers = st.sidebar.multiselect("Select Drivers", driver_options) if multi_driver_mode else [st.sidebar.selectbox("Select Driver", driver_options) if driver_options else None]

# Load Telemetry
if st.sidebar.button("Load Telemetry") and all(selected_drivers):
    all_dfs = {}
    try:
        for driver in selected_drivers:
            df, pos_data, session = get_driver_telemetry(year, gp, session_type, driver)
            all_dfs[driver] = df

        st.success("✅ Data loaded")
        
         # Telemetry Table for first selected driver
        st.subheader(f"📊 Telemetry Snapshot for {selected_drivers[0]}")
        st.dataframe(all_dfs[selected_drivers[0]].head())

        # Track Map (from first driver)
        st.subheader("🗺️ Track Map")
        fig_map, ax_map = plt.subplots()
        ax_map.plot(pos_data['X'], pos_data['Y'], color='black')
        ax_map.set_title("Track Map")
        ax_map.axis('off')
        st.pyplot(fig_map)

        # Comparison Plot
        st.subheader("📈 Telemetry Comparison")
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()

        for driver, df in all_dfs.items():
            ax1.plot(df['Time'], df['Speed'], label=f'{driver} - Speed', linewidth=2)
            ax2.plot(df['Time'], df['nGear'], label=f'{driver} - Gear', linestyle='--')

        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Speed (km/h)")
        ax2.set_ylabel("Gear")
        ax1.set_title(f"{gp} {session_type} {year} - Driver Comparison")
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error loading telemetry: {e}")
