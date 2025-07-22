import os
import fastf1
from fastf1 import plotting
import pandas as pd
import time
import numpy as np

# Enable FastF1 cache
cache_dir = './cache'
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)
plotting.setup_mpl()  # Enable team colors in plots


def get_available_grands_prix(year):
    try:
        schedule = fastf1.get_event_schedule(year)
        return schedule['EventName'].tolist()
    except Exception:
        return []


def get_driver_codes(year, gp, session_type):
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()
        return sorted(session.laps['Driver'].unique())  # Returns codes like HAM, ALO
    except Exception:
        return []


def get_driver_telemetry(year, gp, session_type, driver_code):
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()

        # Use new FastF1 API method
        driver_laps = session.laps.pick_drivers(driver_code)
        if driver_laps.empty:
            return None, None, driver_code

        # Use fastest lap or fallback to last lap
        driver_lap = driver_laps.pick_fastest()
        if driver_lap is None or driver_lap.empty:
            driver_lap = driver_laps.iloc[-1]

        # Get car telemetry
        tel = driver_lap.get_car_data().add_distance()
        pos = driver_lap.get_pos_data()

        # Build dataframe
        df = pd.DataFrame({
            'Time': tel['Time'].dt.total_seconds(),
            'Throttle': tel.get('Throttle', pd.Series([None]*len(tel))),
            'Brake': tel.get('Brake', pd.Series([None]*len(tel))),
            'Speed': tel.get('Speed', pd.Series([None]*len(tel))),
            'nGear': tel.get('nGear', pd.Series([None]*len(tel))),
            'Distance': tel.get('Distance', pd.Series([None]*len(tel)))
        })

        # Placeholder fields (for visualization)
        df['TyreSurfaceTemperature'] = 90 + 10 * np.sin(df['Time'] / 10)
        df['TyrePressure'] = 22 + 0.5 * np.cos(df['Time'] / 15)
        df['ERSDeployMode'] = 2 + 1 * np.sin(df['Time'] / 8)

        return df, pos, driver_code
    except Exception as e:
        print(f"[ERROR] get_driver_telemetry failed: {e}")
        return None, None, driver_code


def get_pit_stops(year, gp, session_type, driver_code):
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()
        laps = session.laps.pick_drivers(driver_code)
        pit_stops = laps[laps['PitInTime'].notnull() & laps['PitOutTime'].notnull()].copy()
        pit_stops['Duration'] = (pit_stops['PitOutTime'] - pit_stops['PitInTime']).dt.total_seconds()
        return pit_stops[['LapNumber', 'PitInTime', 'PitOutTime', 'Duration']]
    except Exception:
        return pd.DataFrame()


def simulate_telemetry_stream(df, chunk_size=10):
    for i in range(chunk_size, len(df) + chunk_size, chunk_size):
        yield df.iloc[:i]
        time.sleep(0.1)
