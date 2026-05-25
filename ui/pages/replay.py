import customtkinter as ctk
import threading
import arcade
import numpy as np
from data.f1_data import get_session

TEAM_COLORS = {
    'Red Bull Racing': (54, 113, 198),
    'Ferrari': (232, 0, 45),
    'Mercedes': (39, 244, 210),
    'McLaren': (255, 128, 0),
    'Aston Martin': (34, 153, 113),
    'Alpine': (255, 135, 188),
    'Williams': (100, 196, 255),
    'RB': (102, 146, 255),
    'Haas F1 Team': (182, 186, 189),
    'Sauber': (82, 226, 82),
}

TYRE_COLORS = {
    'SOFT': (232, 0, 45),
    'MEDIUM': (255, 242, 0),
    'HARD': (255, 255, 255),
    'INTERMEDIATE': (57, 179, 39),
    'WET': (0, 103, 255),
}

class F1ReplayWindow(arcade.Window):
    def __init__(self, session):
        super().__init__(1400, 800, "F1 Race Replay", resizable=True)
        self.session = session
        self.background_color = arcade.color.BLACK
        self.is_playing = False
        self.current_frame = 0
        self.playback_speed = 1.0
        self.drivers = []
        self.driver_positions = {}
        self.driver_colors = {}
        self.driver_names = {}
        self.driver_tyres = {}
        self.track_x = []
        self.track_y = []
        self.total_frames = 0
        self.weather = {}
        self._load_data()

    def _load_data(self):
        fastest = self.session.laps.pick_fastest()
        tel = fastest.get_telemetry()
        raw_x = tel['X'].values
        raw_y = tel['Y'].values

        mx, my = np.mean(raw_x), np.mean(raw_y)
        scale = min(600 / (raw_x.max() - raw_x.min()), 500 / (raw_y.max() - raw_y.min()))
        self.track_x = (raw_x - mx) * scale + 750
        self.track_y = (raw_y - my) * scale + 400

        try:
            w = self.session.weather_data.iloc[0]
            self.weather = {
                'track': f"{w.get('TrackTemp', 0):.1f}°C",
                'air': f"{w.get('AirTemp', 0):.1f}°C",
                'humidity': f"{w.get('Humidity', 0):.0f}%",
                'wind': f"{w.get('WindSpeed', 0):.1f} km/h",
                'rain': 'Yes' if w.get('Rainfall', False) else 'No',
            }
        except:
            self.weather = {}

        self.drivers = list(self.session.drivers[:20])
        fallback = [(31,119,180),(255,127,14),(44,160,44),(214,39,40),
                    (148,103,189),(140,86,75),(227,119,194),(127,127,127),
                    (188,189,34),(23,190,207)]

        for i, drv in enumerate(self.drivers):
            try:
                drv_laps = self.session.laps.pick_driver(drv)
                tel_data = drv_laps.get_telemetry()
                rx = tel_data['X'].values
                ry = tel_data['Y'].values
                nx = (rx - mx) * scale + 750
                ny = (ry - my) * scale + 400
                self.driver_positions[drv] = {'x': nx, 'y': ny}
                info = self.session.get_driver(drv)
                team = info.get('TeamName', '')
                self.driver_colors[drv] = TEAM_COLORS.get(team, fallback[i % len(fallback)])
                self.driver_names[drv] = info.get('Abbreviation', drv)
                first_lap = drv_laps.iloc[0] if len(drv_laps) > 0 else None
                compound = first_lap['Compound'] if first_lap is not None else 'UNKNOWN'
                self.driver_tyres[drv] = compound
            except:
                self.driver_positions[drv] = {'x': np.array([750]), 'y': np.array([400])}
                self.driver_colors[drv] = fallback[i % len(fallback)]
                self.driver_names[drv] = drv
                self.driver_tyres[drv] = 'UNKNOWN'

        self.total_frames = max(
            (len(v['x']) for v in self.driver_positions.values() if len(v['x']) > 0), default=0)

    def on_draw(self):
        self.clear()

        # Track
        for i in range(len(self.track_x) - 1):
            arcade.draw_line(self.track_x[i], self.track_y[i],
                           self.track_x[i+1], self.track_y[i+1], (60, 60, 60), 14)
        for i in range(len(self.track_x) - 1):
            arcade.draw_line(self.track_x[i], self.track_y[i],
                           self.track_x[i+1], self.track_y[i+1], (100, 100, 100), 8)

        arcade.draw_circle_filled(self.track_x[0], self.track_y[0], 8, arcade.color.WHITE)

        # Drivers
        for drv in self.drivers:
            pos = self.driver_positions[drv]
            if len(pos['x']) == 0:
                continue
            idx = min(self.current_frame, len(pos['x']) - 1)
            x, y = float(pos['x'][idx]), float(pos['y'][idx])
            color = self.driver_colors[drv]
            arcade.draw_circle_filled(x, y, 9, color)
            arcade.draw_circle_outline(x, y, 9, arcade.color.WHITE, 1.5)
            arcade.draw_text(self.driver_names[drv], x, y + 12,
                           arcade.color.WHITE, 8, anchor_x="center", bold=True)

        # Weather panel
        if self.weather:
            arcade.draw_lbwh_rectangle_filled(10, self.height - 175, 260, 165, (0, 0, 0, 180))
            arcade.draw_lbwh_rectangle_outline(10, self.height - 175, 260, 165, (80, 80, 80), 1)
            arcade.draw_text("WEATHER", 20, self.height - 30, (180, 180, 180), 11, bold=True)
            arcade.draw_text(f"Track: {self.weather.get('track','—')}", 20, self.height - 55, arcade.color.WHITE, 11)
            arcade.draw_text(f"Air: {self.weather.get('air','—')}", 20, self.height - 75, arcade.color.WHITE, 11)
            arcade.draw_text(f"Humidity: {self.weather.get('humidity','—')}", 20, self.height - 95, arcade.color.WHITE, 11)
            arcade.draw_text(f"Wind: {self.weather.get('wind','—')}", 20, self.height - 115, arcade.color.WHITE, 11)
            arcade.draw_text(f"Rain: {self.weather.get('rain','—')}", 20, self.height - 135, arcade.color.WHITE, 11)

        # Lap & time
        progress = self.current_frame / max(self.total_frames, 1)
        lap = min(int(progress * self.session.total_laps) + 1, self.session.total_laps)
        race_secs = progress * 5400
        mins, secs = int(race_secs // 60), int(race_secs % 60)

        arcade.draw_text(f"Lap: {lap} / {self.session.total_laps}",
                        self.width // 2, self.height - 30,
                        arcade.color.WHITE, 18, anchor_x="center", bold=True)
        arcade.draw_text(f"Race Time: {mins:02d}:{secs:02d}  ({self.playback_speed}x)",
                        self.width // 2, self.height - 55,
                        (180, 180, 180), 13, anchor_x="center")

        # Leaderboard
        lb_x = self.width - 250
        lb_w = 240
        lb_h = min(30 + len(self.drivers) * 28, self.height - 80)
        arcade.draw_lbwh_rectangle_filled(lb_x, self.height - lb_h - 10, lb_w, lb_h, (0, 0, 0, 200))
        arcade.draw_lbwh_rectangle_outline(lb_x, self.height - lb_h - 10, lb_w, lb_h, (80, 80, 80), 1)
        arcade.draw_text("LEADERBOARD", lb_x + 10, self.height - 30, (220, 0, 0), 12, bold=True)

        for i, drv in enumerate(self.drivers):
            row_y = self.height - 55 - i * 28
            color = self.driver_colors[drv]
            name = self.driver_names[drv]
            compound = self.driver_tyres.get(drv, '?')
            tyre_color = TYRE_COLORS.get(compound, (180, 180, 180))

            if i % 2 == 0:
                arcade.draw_lbwh_rectangle_filled(lb_x + 2, row_y - 8, lb_w - 4, 26, (30, 30, 30, 150))

            # Team color bar
            arcade.draw_lbwh_rectangle_filled(lb_x + 8, row_y, 4, 18, color)
            arcade.draw_text(f"P{i+1}", lb_x + 18, row_y, (220, 0, 0), 11, bold=True)
            arcade.draw_text(name, lb_x + 50, row_y, arcade.color.WHITE, 11)
            arcade.draw_circle_filled(lb_x + 190, row_y + 7, 7, tyre_color)
            arcade.draw_text(compound[0] if compound else '?', lb_x + 187, row_y + 1, (0, 0, 0), 9, bold=True)

        # Controls bar
        arcade.draw_lbwh_rectangle_filled(0, 0, self.width, 45, (20, 20, 20, 220))
        status = "PAUSED" if not self.is_playing else "PLAYING"
        arcade.draw_text(
            f"{status}  |  [SPACE] Play/Pause  |  [R] Restart  |  [UP/DOWN] Speed  |  [ESC] Close",
            self.width // 2, 15, (150, 150, 150), 12, anchor_x="center")

        # Progress bar
        bar_w = self.width - 20
        arcade.draw_lbwh_rectangle_filled(10, 48, bar_w, 6, (50, 50, 50))
        arcade.draw_lbwh_rectangle_filled(10, 48, int(bar_w * progress), 6, (220, 0, 0))

    def on_update(self, delta_time):
        if self.is_playing:
            step = max(1, int(self.playback_speed * 3))
            self.current_frame += step
            if self.current_frame >= self.total_frames:
                self.current_frame = 0

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.is_playing = not self.is_playing
        elif key == arcade.key.R:
            self.current_frame = 0
            self.is_playing = False
        elif key == arcade.key.UP:
            speeds = [0.5, 1.0, 2.0, 4.0, 8.0]
            idx = speeds.index(self.playback_speed) if self.playback_speed in speeds else 1
            self.playback_speed = speeds[min(idx + 1, len(speeds) - 1)]
        elif key == arcade.key.DOWN:
            speeds = [0.5, 1.0, 2.0, 4.0, 8.0]
            idx = speeds.index(self.playback_speed) if self.playback_speed in speeds else 1
            self.playback_speed = speeds[max(idx - 1, 0)]
        elif key == arcade.key.ESCAPE:
            self.close()


class ReplayPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=app.DARK)
        self.app = app
        self.session = None

        ctk.CTkLabel(self, text="🎬 Race Replay",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=app.RED).pack(pady=(60, 20))

        ctk.CTkLabel(self, text="Load a race session to open the interactive replay window",
                     font=ctk.CTkFont(size=14), text_color="#888888").pack()

        control = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=12)
        control.pack(pady=40, padx=80, fill="x")

        row = ctk.CTkFrame(control, fg_color="transparent")
        row.pack(pady=20)

        ctk.CTkLabel(row, text="Year:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(20, 5))
        self.year_var = ctk.StringVar(value="2024")
        ctk.CTkEntry(row, textvariable=self.year_var, width=80).pack(side="left", padx=5)

        ctk.CTkLabel(row, text="Round:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(20, 5))
        self.round_var = ctk.StringVar(value="1")
        ctk.CTkEntry(row, textvariable=self.round_var, width=70).pack(side="left", padx=5)

        self.load_btn = ctk.CTkButton(
            row, text="🚀 Launch Replay",
            fg_color=app.RED, hover_color="#b30000",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=160, height=40, command=self.launch_replay)
        self.load_btn.pack(side="left", padx=20)

        self.status = ctk.CTkLabel(control, text="", font=ctk.CTkFont(size=12), text_color="#888888")
        self.status.pack(pady=(0, 15))

        legend = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=12)
        legend.pack(pady=10, padx=80, fill="x")

        ctk.CTkLabel(legend, text="Keyboard Controls",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=app.RED).pack(pady=(15, 8))

        keys = [("SPACE", "Play / Pause"), ("R", "Restart"),
                ("UP / DOWN", "Speed Up / Down"), ("ESC", "Close Replay")]
        for key, desc in keys:
            row2 = ctk.CTkFrame(legend, fg_color="transparent")
            row2.pack(pady=3)
            ctk.CTkLabel(row2, text=key, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="white", width=100,
                         fg_color="#333333", corner_radius=5).pack(side="left", padx=5)
            ctk.CTkLabel(row2, text=desc, font=ctk.CTkFont(size=12),
                         text_color="#aaaaaa").pack(side="left", padx=10)

        ctk.CTkLabel(legend, text="", height=10).pack()

    def launch_replay(self):
        self.load_btn.configure(state="disabled")
        self.status.configure(text="⏳ Loading session data...")
        threading.Thread(target=self._load_and_launch, daemon=True).start()

    def _load_and_launch(self):
        try:
            year = int(self.year_var.get())
            round_num = int(self.round_var.get())
            self.session = get_session(year, round_num, "R")
            self.after(0, self._open_window)
        except Exception as e:
            self.after(0, lambda: self.status.configure(text=f"❌ Error: {str(e)[:50]}"))
            self.after(0, lambda: self.load_btn.configure(state="normal"))

    def _open_window(self):
        self.status.configure(text="✅ Launching replay window...")
        self.load_btn.configure(state="normal")
        window = F1ReplayWindow(self.session)
        arcade.run()