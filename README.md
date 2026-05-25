# 🏎️ F1 Dashboard

An interactive Formula 1 data analysis and race replay desktop application built with Python.

## Features

- 🏁 **Race Analysis** — Lap-by-lap time charts for all drivers
- 🔧 **Practice Analysis** — FP1/FP2/FP3 session data with fastest laps and tyre usage
- 🎬 **Race Replay** — Interactive track animation with live driver positions, leaderboard, weather info and progress bar

## Screenshots

> Race Replay with live driver positions, leaderboard and weather panel

## Tech Stack

- **Python** — Core language
- **FastF1** — F1 telemetry and session data
- **CustomTkinter** — Modern desktop UI
- **Matplotlib** — Charts and graphs
- **Arcade** — Race replay visualization

## Installation

```bash
# Clone the repository
git clone https://github.com/begumonegi/f1.git
cd f1

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install fastf1 customtkinter matplotlib pandas pillow arcade
```

## Usage

```bash
venv\Scripts\activate
python main.py
```

Or simply double-click `run.bat`

## Data Source

All F1 data is powered by [FastF1](https://github.com/theOehrly/Fast-F1) — an unofficial F1 telemetry API.