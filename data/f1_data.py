import fastf1
import pandas as pd
import os

# Cache klasörü
cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

def get_session(year, round_number, session_type):
    """Seans yükle: R=Race, Q=Qualifying, FP1/FP2/FP3"""
    session = fastf1.get_session(year, round_number, session_type)
    session.load()
    return session

def get_race_positions(session):
    """Yarış boyunca sürücü pozisyonları"""
    pos = session.pos_data
    return pos

def get_lap_times(session):
    """Tüm sürücülerin tur süreleri"""
    laps = session.laps[['Driver', 'LapNumber', 'LapTime', 'Compound', 'TyreLife', 'PitInTime', 'PitOutTime']]
    return laps.dropna(subset=['LapTime'])

def get_driver_telemetry(session, driver):
    """Belirli sürücünün en hızlı tur telemetrisi"""
    lap = session.laps.pick_driver(driver).pick_fastest()
    tel = lap.get_telemetry()
    return tel

def get_event_schedule(year):
    """Sezon takvimi"""
    schedule = fastf1.get_event_schedule(year)
    return schedule[['RoundNumber', 'EventName', 'EventDate', 'Country']]