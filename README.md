# 🏎️ F1 Dashboard

An interactive Formula 1 data analysis and race replay application built with Python and React.

## Features

- 🏁 **Race Analysis** — Lap-by-lap time charts for all drivers
- 🔧 **Practice Analysis** — FP1/FP2/FP3 session data with fastest laps and tyre usage
- 🎬 **Race Replay** — Interactive track animation with live driver positions and leaderboard
- ⚖️ **Driver Comparison** — Head-to-head season statistics
- 📡 **Telemetry Analysis** — Speed, throttle and brake data
- 🏆 **Season Standings** — Live driver and constructor standings via Jolpica API

## Tech Stack

- **Python** — Core language
- **FastF1** — F1 telemetry and session data
- **FastAPI** — Backend REST API
- **React + Vite** — Web frontend
- **CustomTkinter** — Desktop UI
- **Matplotlib** — Charts and graphs
- **Arcade** — Race replay visualization

## Installation

```bash
git clone https://github.com/begumonegi/f1.git
cd f1
python -m venv venv
venv\Scripts\activate
pip install fastf1 customtkinter matplotlib pandas pillow arcade requests fastapi uvicorn
```

## Usage

```bash
venv\Scripts\activate
python main.py
```

Or simply double-click `run.bat`

## Data Source

All F1 data is powered by [FastF1](https://github.com/theOehrly/Fast-F1) and [Jolpica API](https://api.jolpi.ca).