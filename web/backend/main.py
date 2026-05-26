from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastf1
import os

app = FastAPI(title="F1 Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache
cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

@app.get("/")
def root():
    return {"message": "F1 Dashboard API", "status": "running"}

@app.get("/schedule/{year}")
def get_schedule(year: int):
    schedule = fastf1.get_event_schedule(year)
    races = schedule[schedule['EventFormat'] != 'testing']
    return races[['RoundNumber', 'EventName', 'EventDate', 'Country']].to_dict(orient='records')

@app.get("/race/{year}/{round}/laps")
def get_race_laps(year: int, round: int):
    session = fastf1.get_session(year, round, 'R')
    session.load()
    laps = session.laps[['Driver', 'LapNumber', 'LapTime', 'Compound']].dropna(subset=['LapTime'])
    laps['LapTime'] = laps['LapTime'].dt.total_seconds()
    return laps.to_dict(orient='records')

@app.get("/telemetry/{year}/{round}/{driver}")
def get_telemetry(year: int, round: int, driver: str):
    session = fastf1.get_session(year, round, 'R')
    session.load()
    lap = session.laps.pick_driver(driver.upper()).pick_fastest()
    tel = lap.get_telemetry()[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear']]
    return tel.to_dict(orient='records')

@app.get("/standings/{year}/drivers")
def get_driver_standings(year: int):
    import requests
    r = requests.get(f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json")
    data = r.json()['MRData']['StandingsTable']['StandingsLists']
    if not data:
        return []
    return data[0]['DriverStandings']

@app.get("/standings/{year}/constructors")
def get_constructor_standings(year: int):
    import requests
    r = requests.get(f"https://api.jolpi.ca/ergast/f1/{year}/constructorStandings.json")
    data = r.json()['MRData']['StandingsTable']['StandingsLists']
    if not data:
        return []
    return data[0]['ConstructorStandings']