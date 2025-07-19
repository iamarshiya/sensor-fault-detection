import os
import fastf1
from fastf1 import plotting
import pandas as pd
import time

# Setup cache
cache_dir = './cache'
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

def get_available_grands_prix(year):
    schedule = fastf1.get_event_schedule(year)
    return schedule['EventName'].tolist()

def get_driver_codes(year, gp, session_type):
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return sorted(session.laps['Driver'].unique())

def get_driver_telemetry(year, gp, session_type, driver_code):
    session = fastf1.get_session(year, gp, session_type)
    session.load()

    driver_lap = session.laps.pick_driver(driver_code).pick_fastest()
    tel = driver_lap.get_car_data().add_distance()

    df = pd.DataFrame({
        'Time': tel['Time'].dt.total_seconds(),
        'Throttle': tel['Throttle'],
        'Brake': tel['Brake'],
        'Speed': tel['Speed'],
        'nGear': tel['nGear'],
        'Distance': tel['Distance']
    })

    return df, driver_lap.get_pos_data(), session

def simulate_telemetry_stream(df, chunk_size=10):
    for i in range(chunk_size, len(df) + chunk_size, chunk_size):
        yield df.iloc[:i]
        time.sleep(0.1)
