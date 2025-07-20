import os
import fastf1
from fastf1 import plotting
import pandas as pd

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
        return sorted(session.laps['Driver'].unique())
    except Exception:
        return []

def get_driver_telemetry(year, gp, session_type, driver_code):
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()

        driver_lap = session.laps.pick_driver(driver_code).pick_fastest()
        if driver_lap is None:
            return None, None, driver_code

        tel = driver_lap.get_car_data().add_distance()
        pos = driver_lap.get_pos_data()

        df = pd.DataFrame({
            'Time': tel['Time'].dt.total_seconds(),
            'Throttle': tel['Throttle'],
            'Brake': tel['Brake'],
            'Speed': tel['Speed'],
            'nGear': tel['nGear'],
            'Distance': tel['Distance']
        })

        # Placeholder telemetry values (FastF1 doesn't always have these fields)
        df['TyreSurfaceTemperature'] = 90 + 10 * pd.np.sin(df['Time'] / 10)
        df['TyrePressure'] = 22 + 0.5 * pd.np.cos(df['Time'] / 15)
        df['ERSDeployMode'] = 2 + 1 * pd.np.sin(df['Time'] / 8)

        return df, pos, driver_code
    except Exception as e:
        return None, None, driver_code

def get_pit_stops(year, gp, session_type, driver_code):
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()
        laps = session.laps.pick_driver(driver_code)
        pit_stops = laps[laps['PitInTime'].notnull() & laps['PitOutTime'].notnull()].copy()

        pit_stops['Duration'] = (pit_stops['PitOutTime'] - pit_stops['PitInTime']).dt.total_seconds()
        return pit_stops[['LapNumber', 'PitInTime', 'PitOutTime', 'Duration']]
    except Exception:
        return pd.DataFrame()
