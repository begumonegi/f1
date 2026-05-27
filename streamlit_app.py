import os
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests
import fastf1

cache_dir = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

st.set_page_config(
    page_title="F1 Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1e1e1e; }
[data-testid="stSidebar"] * { color: #ffffff; }
.stButton > button {
    background-color: #E10600;
    color: white;
    border: none;
    font-weight: bold;
}
.stButton > button:hover { background-color: #b30000; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🏎️ F1 Dashboard")
    st.markdown("---")
    page = st.radio(
        "Sayfa",
        ["🏠 Home", "🏁 Race", "🔧 Practice", "🔵 Comparison", "📡 Telemetry", "🏆 Standings", "🎬 Replay"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Powered by FastF1 & Jolpica API")

import datetime
CURRENT_YEAR = datetime.datetime.now().year

RED = "#E10600"
TEAL = "#27F4D2"
DARK_BG = "#151515"
DARK_AX = "#1e1e1e"

TYRE_COLORS = {
    "SOFT": "#E8002D",
    "MEDIUM": "#FFF200",
    "HARD": "#FFFFFF",
    "INTERMEDIATE": "#43B02A",
    "WET": "#0067FF",
}

TEAM_COLORS = {
    "Red Bull": "#3671C6",
    "Red Bull Racing": "#3671C6",
    "Ferrari": "#E8002D",
    "Mercedes": "#27F4D2",
    "McLaren": "#FF8000",
    "Aston Martin": "#229971",
    "Alpine F1 Team": "#FF87BC",
    "Alpine": "#FF87BC",
    "Williams": "#64C4FF",
    "RB F1 Team": "#6692FF",
    "RB": "#6692FF",
    "Haas F1 Team": "#B6BABD",
    "Kick Sauber": "#52E252",
    "Sauber": "#52E252",
}


def style_axes(axes, fig):
    fig.patch.set_facecolor(DARK_BG)
    for ax in (axes if hasattr(axes, "__iter__") else [axes]):
        ax.set_facecolor(DARK_AX)
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("#444")
        ax.spines["left"].set_color("#444")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")


@st.cache_data(show_spinner="F1 verisi yükleniyor… (ilk yüklemede birkaç dakika sürebilir)")
def load_session(year: int, round_num: int, session_type: str):
    sess = fastf1.get_session(year, round_num, session_type)
    sess.load()
    return sess


@st.cache_data(show_spinner="Puan tablosu çekiliyor…")
def fetch_standings(year: int):
    r1 = requests.get(f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json", timeout=10)
    r2 = requests.get(f"https://api.jolpi.ca/ergast/f1/{year}/constructorStandings.json", timeout=10)
    schedule = fastf1.get_event_schedule(year)
    driver_data = r1.json()["MRData"]["StandingsTable"]["StandingsLists"]
    constructor_data = r2.json()["MRData"]["StandingsTable"]["StandingsLists"]
    return driver_data, constructor_data, schedule


# ── HOME ──────────────────────────────────────────────────────────────────────
if "🏠 Home" in page:
    st.title("Welcome to F1 Dashboard 🏎️")
    st.markdown("Your personal Formula 1 data analysis tool, powered by **FastF1**.")
    st.markdown("---")

    features = [
        ("🏁", "Race Analysis", "Lap-by-lap time charts for all drivers"),
        ("🔧", "Practice", "FP1/FP2/FP3 session analysis with tyre data"),
        ("🔵", "Driver Comparison", "Compare two drivers side by side"),
        ("📡", "Telemetry", "Speed, throttle, brake and gear data"),
        ("🏆", "Standings", "Driver and constructor standings + race calendar"),
        ("🎬", "Replay", "Track map with driver positions"),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f"""<div style="background:#2a2a2a;border-radius:12px;padding:20px;margin:8px 0;text-align:center;">
                <div style="font-size:2rem;">{icon}</div>
                <div style="font-size:1.1rem;font-weight:bold;color:#E10600;margin:6px 0;">{title}</div>
                <div style="color:#888;font-size:0.9rem;">{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

# ── RACE ──────────────────────────────────────────────────────────────────────
elif "🏁 Race" in page:
    st.title("🏁 Race Analysis")

    c1, c2, c3 = st.columns([1, 1, 2])
    year = c1.number_input("Year", 2018, CURRENT_YEAR, CURRENT_YEAR, step=1)
    round_num = c2.number_input("Round", 1, 24, 1, step=1)

    if c3.button("Load Race", use_container_width=True):
        try:
            session = load_session(int(year), int(round_num), "R")
            laps = session.laps[["Driver", "LapNumber", "LapTime", "Compound"]].dropna(subset=["LapTime"])

            fig, ax = plt.subplots(figsize=(12, 5))
            style_axes(ax, fig)

            drivers = laps["Driver"].unique()[:10]
            colors = plt.cm.tab10.colors
            for i, driver in enumerate(drivers):
                d_laps = laps[laps["Driver"] == driver]
                lap_secs = d_laps["LapTime"].dt.total_seconds()
                ax.plot(d_laps["LapNumber"], lap_secs, label=driver, color=colors[i], linewidth=1.5)

            ax.set_xlabel("Lap")
            ax.set_ylabel("Lap Time (s)")
            ax.set_title(f"Lap Times — {session.event['EventName']} {year}")
            ax.legend(fontsize=8, facecolor=DARK_BG, labelcolor="white")

            st.pyplot(fig)
            plt.close(fig)
            st.success("✅ Race loaded!")
        except Exception as e:
            st.error(f"❌ {e}")

# ── PRACTICE ──────────────────────────────────────────────────────────────────
elif "🔧 Practice" in page:
    st.title("🔧 Practice Analysis")

    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
    year = c1.number_input("Year", 2018, CURRENT_YEAR, CURRENT_YEAR, step=1)
    round_num = c2.number_input("Round", 1, 24, 1, step=1)
    session_type = c3.selectbox("Session", ["FP1", "FP2", "FP3"])

    if c4.button("Load Session", use_container_width=True):
        try:
            session = load_session(int(year), int(round_num), session_type)
            laps = session.laps[["Driver", "LapNumber", "LapTime", "Compound", "TyreLife"]].dropna(subset=["LapTime"])

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Fastest Laps")
                fastest = laps.groupby("Driver")["LapTime"].min().sort_values()
                rows = []
                for pos, (drv, lt) in enumerate(fastest.head(10).items(), 1):
                    s = lt.total_seconds()
                    rows.append({"Pos": f"P{pos}", "Driver": drv, "Time": f"{int(s//60)}:{s%60:06.3f}"})
                st.dataframe(pd.DataFrame(rows).set_index("Pos"), use_container_width=True)

            with col2:
                st.subheader("Tyre Compounds")
                compound_counts = laps["Compound"].value_counts()
                c_colors = [TYRE_COLORS.get(c, "#888888") for c in compound_counts.index]
                fig, ax = plt.subplots(figsize=(5, 4))
                fig.patch.set_facecolor(DARK_BG)
                ax.set_facecolor(DARK_AX)
                ax.pie(
                    compound_counts.values,
                    labels=compound_counts.index,
                    colors=c_colors,
                    autopct="%1.0f%%",
                    textprops={"color": "white"},
                )
                ax.set_title("Tyre Usage", color="white")
                st.pyplot(fig)
                plt.close(fig)

            st.success("✅ Session loaded!")
        except Exception as e:
            st.error(f"❌ {e}")

# ── COMPARISON ────────────────────────────────────────────────────────────────
elif "🔵 Comparison" in page:
    st.title("🔵 Driver Comparison")

    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
    year = c1.number_input("Year", 2018, CURRENT_YEAR, CURRENT_YEAR, step=1)
    round_num = c2.number_input("Round", 1, 24, 1, step=1)
    session_type = c3.selectbox("Session", ["R", "Q", "FP1", "FP2", "FP3"])
    driver1 = c4.text_input("Driver 1", "VER").upper()
    driver2 = c5.text_input("Driver 2", "HAM").upper()

    if st.button("Compare", use_container_width=False):
        try:
            session = load_session(int(year), int(round_num), session_type)
            laps1 = session.laps.pick_driver(driver1)
            laps2 = session.laps.pick_driver(driver2)

            fig, axes = plt.subplots(2, 2, figsize=(14, 8))
            fig.patch.set_facecolor(DARK_BG)
            fig.suptitle(f"{driver1} vs {driver2}", color="white", fontsize=14, fontweight="bold")
            style_axes(axes.flatten(), fig)

            # Lap times
            t1 = laps1["LapTime"].dt.total_seconds().dropna()
            t2 = laps2["LapTime"].dt.total_seconds().dropna()
            axes[0][0].plot(laps1["LapNumber"][: len(t1)], t1, color=RED, label=driver1, linewidth=1.5)
            axes[0][0].plot(laps2["LapNumber"][: len(t2)], t2, color=TEAL, label=driver2, linewidth=1.5)
            axes[0][0].set_title("Lap Times (s)")
            axes[0][0].set_xlabel("Lap")
            axes[0][0].legend(facecolor=DARK_BG, labelcolor="white", fontsize=9)

            # Speed telemetry
            try:
                fast1 = laps1.pick_fastest().get_telemetry()
                fast2 = laps2.pick_fastest().get_telemetry()
                axes[0][1].plot(fast1["Distance"], fast1["Speed"], color=RED, label=driver1, linewidth=1.5)
                axes[0][1].plot(fast2["Distance"], fast2["Speed"], color=TEAL, label=driver2, linewidth=1.5)
                axes[0][1].set_title("Fastest Lap — Speed (km/h)")
                axes[0][1].set_xlabel("Distance (m)")
                axes[0][1].legend(facecolor=DARK_BG, labelcolor="white", fontsize=9)
            except Exception:
                axes[0][1].set_title("Speed — No telemetry data")

            # Tyre strategy
            for lap_row in laps1.itertuples():
                axes[1][0].bar(lap_row.LapNumber, 1, color=TYRE_COLORS.get(lap_row.Compound, "#888"), alpha=0.8)
            for lap_row in laps2.itertuples():
                axes[1][0].bar(lap_row.LapNumber, -1, color=TYRE_COLORS.get(lap_row.Compound, "#888"), alpha=0.8)
            axes[1][0].set_title(f"Tyre Strategy  (+{driver1} / -{driver2})")
            axes[1][0].set_xlabel("Lap")
            axes[1][0].axhline(0, color="white", linewidth=0.5)

            # Throttle
            try:
                axes[1][1].plot(fast1["Distance"], fast1["Throttle"], color=RED, label=driver1, linewidth=1.2)
                axes[1][1].plot(fast2["Distance"], fast2["Throttle"], color=TEAL, label=driver2, linewidth=1.2)
                axes[1][1].set_title("Fastest Lap — Throttle (%)")
                axes[1][1].set_xlabel("Distance (m)")
                axes[1][1].legend(facecolor=DARK_BG, labelcolor="white", fontsize=9)
            except Exception:
                axes[1][1].set_title("Throttle — No telemetry data")

            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            st.success("✅ Comparison loaded!")
        except Exception as e:
            st.error(f"❌ {e}")

# ── TELEMETRY ─────────────────────────────────────────────────────────────────
elif "📡 Telemetry" in page:
    st.title("📡 Telemetry Analysis")

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    year = c1.number_input("Year", 2018, CURRENT_YEAR, CURRENT_YEAR, step=1)
    round_num = c2.number_input("Round", 1, 24, 1, step=1)
    session_type = c3.selectbox("Session", ["R", "Q", "FP1", "FP2", "FP3"])
    driver = c4.text_input("Driver", "VER").upper()

    if st.button("Load Telemetry"):
        try:
            session = load_session(int(year), int(round_num), session_type)
            lap = session.laps.pick_driver(driver).pick_fastest()
            tel = lap.get_telemetry()

            fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
            fig.patch.set_facecolor(DARK_BG)
            fig.suptitle(f"{driver} — Fastest Lap Telemetry", color="white", fontsize=14, fontweight="bold")

            plots = [
                ("Speed (km/h)", "Speed", RED),
                ("Throttle (%)", "Throttle", "#FF8000"),
                ("Brake", "Brake", TEAL),
                ("Gear", "nGear", "#FFF200"),
            ]

            for ax, (title, col, color) in zip(axes, plots):
                ax.set_facecolor("#151515")
                ax.tick_params(colors="white", labelsize=9)
                ax.spines["bottom"].set_color("#333")
                ax.spines["left"].set_color("#333")
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.set_ylabel(title, color="white", fontsize=9)
                if col in tel.columns:
                    ax.plot(tel["Distance"], tel[col], color=color, linewidth=1.5)
                    ax.fill_between(tel["Distance"], tel[col], alpha=0.15, color=color)
                else:
                    ax.text(0.5, 0.5, "No data", transform=ax.transAxes, color="white", ha="center")

            axes[-1].set_xlabel("Distance (m)", color="white", fontsize=10)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            st.success("✅ Telemetry loaded!")
        except Exception as e:
            st.error(f"❌ {e}")

# ── STANDINGS ─────────────────────────────────────────────────────────────────
elif "🏆 Standings" in page:
    st.title("🏆 Season Standings")

    c1, c2 = st.columns([1, 3])
    year = c1.number_input("Year", 2010, CURRENT_YEAR, CURRENT_YEAR, step=1)

    if c2.button("Load Standings"):
        try:
            driver_data, constructor_data, schedule = fetch_standings(int(year))

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Driver Standings")
                if driver_data:
                    rows = []
                    for s in driver_data[0]["DriverStandings"]:
                        drv = s["Driver"]
                        team = s["Constructors"][0]["name"] if s["Constructors"] else ""
                        name = f"{drv['givenName']} {drv['familyName']}"
                        code = drv.get("code", name[:3].upper())
                        rows.append({"Pos": f"P{s['position']}", "Code": code, "Driver": name, "Team": team, "Pts": s["points"]})
                    st.dataframe(pd.DataFrame(rows).set_index("Pos"), use_container_width=True)

            with col2:
                st.subheader("Constructor Standings")
                if constructor_data:
                    rows = []
                    for s in constructor_data[0]["ConstructorStandings"]:
                        rows.append({"Pos": f"P{s['position']}", "Team": s["Constructor"]["name"], "Pts": s["points"]})
                    st.dataframe(pd.DataFrame(rows).set_index("Pos"), use_container_width=True)

            st.subheader("📅 Race Calendar")
            races = schedule[schedule["EventFormat"] != "testing"][["RoundNumber", "EventName", "EventDate", "Country"]].copy()
            races["EventDate"] = races["EventDate"].astype(str).str[:10]
            races.columns = ["Round", "Event", "Date", "Country"]
            st.dataframe(races.set_index("Round"), use_container_width=True)

            st.success("✅ Standings loaded!")
        except Exception as e:
            st.error(f"❌ {e}")

# ── REPLAY (track map) ────────────────────────────────────────────────────────
elif "🎬 Replay" in page:
    st.title("🎬 Race Replay — Track Map")
    st.info(
        "The animated Arcade replay is desktop-only. "
        "Here you can explore the track map and see where drivers were during their fastest laps."
    )

    c1, c2, c3 = st.columns([1, 1, 2])
    year = c1.number_input("Year", 2018, CURRENT_YEAR, CURRENT_YEAR, step=1)
    round_num = c2.number_input("Round", 1, 24, 1, step=1)

    if c3.button("Load Track Map", use_container_width=True):
        try:
            import plotly.graph_objects as go

            session = load_session(int(year), int(round_num), "R")
            fastest = session.laps.pick_fastest()
            tel = fastest.get_telemetry()

            if "X" not in tel.columns or "Y" not in tel.columns:
                st.warning("No position telemetry available for this session.")
                st.stop()

            fig = go.Figure()

            # Track outline
            fig.add_trace(go.Scatter(
                x=tel["X"], y=tel["Y"],
                mode="lines",
                line=dict(color="#555555", width=12),
                showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                x=tel["X"], y=tel["Y"],
                mode="lines",
                line=dict(color="#888888", width=7),
                showlegend=False,
            ))

            # Start/finish marker
            fig.add_trace(go.Scatter(
                x=[tel["X"].iloc[0]], y=[tel["Y"].iloc[0]],
                mode="markers",
                marker=dict(size=14, color="white", symbol="square"),
                name="Start/Finish",
            ))

            # Drivers (midpoint of fastest lap telemetry)
            for drv_code in session.drivers[:20]:
                try:
                    drv_laps = session.laps.pick_driver(drv_code)
                    drv_tel = drv_laps.pick_fastest().get_telemetry()
                    info = session.get_driver(drv_code)
                    team = info.get("TeamName", "")
                    abbr = info.get("Abbreviation", drv_code)
                    color = TEAM_COLORS.get(team, "#888888")
                    mid = len(drv_tel) // 2
                    fig.add_trace(go.Scatter(
                        x=[drv_tel["X"].iloc[mid]],
                        y=[drv_tel["Y"].iloc[mid]],
                        mode="markers+text",
                        marker=dict(size=14, color=color, line=dict(color="white", width=1.5)),
                        text=[abbr],
                        textposition="top center",
                        textfont=dict(color="white", size=10),
                        name=abbr,
                    ))
                except Exception:
                    pass

            fig.update_layout(
                paper_bgcolor=DARK_BG,
                plot_bgcolor=DARK_AX,
                font=dict(color="white"),
                title=f"Track Map — {session.event['EventName']} {year}",
                title_font=dict(color="white"),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
                height=600,
            )

            st.plotly_chart(fig, use_container_width=True)
            st.success("✅ Track map loaded!")
        except Exception as e:
            st.error(f"❌ {e}")
