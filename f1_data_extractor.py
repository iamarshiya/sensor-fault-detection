import os
import fastf1
from fastf1 import plotting
import pandas as pd
import time

# Setup cache directory
cache_dir = './cache'
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)
plotting.setup_mpl()  # Use team colors in matplotlib plots

def get_available_grands_prix(year):
    """Return list of all races (EventName) for the given year."""
    schedule = fastf1.get_event_schedule(year)
    return schedule['EventName'].tolist()

def get_driver_codes(year, gp, session_type):
    """Return sorted list of all drivers for the given session."""
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return sorted(session.laps['Driver'].unique())

def get_driver_telemetry(year, gp, session_type, driver_code):
    """
    Get telemetry and position data for the fastest lap of a driver.
    Returns:
        df: DataFrame with Time, Throttle, Brake, Speed, Gear, Distance
        pos: Position data (X, Y)
        session: Original session object (in case more is needed)
    """
    session = fastf1.get_session(year, gp, session_type)
    session.load()

    # Pick fastest lap for selected driver
    driver_lap = session.laps.pick_driver(driver_code).pick_fastest()
    tel = driver_lap.get_car_data().add_distance()
    pos = driver_lap.get_pos_data()

    # Build DataFrame
    df = pd.DataFrame({
        'Time': tel['Time'].dt.total_seconds(),
        'Throttle': tel['Throttle'],
        'Brake': tel['Brake'],
        'Speed': tel['Speed'],
        'nGear': tel['nGear'],
        'Distance': tel['Distance']
    })

    return df, pos, session

def simulate_telemetry_stream(df, chunk_size=10):
    """
    Simulates live streaming of telemetry data by yielding chunks.
    (You’ve removed simulation from the dashboard, but kept for testing.)
    """
    for i in range(chunk_size, len(df) + chunk_size, chunk_size):
        yield df.iloc[:i]
        time.sleep(0.1)
