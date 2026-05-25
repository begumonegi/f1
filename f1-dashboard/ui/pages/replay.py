import customtkinter as ctk
from data.f1_data import get_session
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class ReplayPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=app.DARK)
        self.app = app
        self.session = None
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.driver_positions = {}
        self.driver_colors = {}
        self.drivers = []
        self.dots = {}
        self.labels = {}

        # Title
        ctk.CTkLabel(
            self,
            text="🎬 Race Replay",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=app.RED
        ).pack(pady=(30, 10))

        # Control panel
        control = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        control.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(control, text="Year:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(20, 5), pady=15)
        self.year_var = ctk.StringVar(value="2024")
        ctk.CTkEntry(control, textvariable=self.year_var, width=70).pack(side="left", padx=5)

        ctk.CTkLabel(control, text="Round:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5))
        self.round_var = ctk.StringVar(value="1")
        ctk.CTkEntry(control, textvariable=self.round_var, width=60).pack(side="left", padx=5)

        self.load_btn = ctk.CTkButton(
            control,
            text="Load Race",
            fg_color=app.RED,
            hover_color="#b30000",
            command=self.load_race
        )
        self.load_btn.pack(side="left", padx=20, pady=15)

        self.status = ctk.CTkLabel(control, text="", font=ctk.CTkFont(size=12), text_color="#888888")
        self.status.pack(side="left", padx=10)

        # Playback controls
        playback = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        playback.pack(fill="x", padx=30, pady=(0, 10))

        self.play_btn = ctk.CTkButton(
            playback,
            text="▶ Play",
            fg_color=app.RED,
            hover_color="#b30000",
            width=100,
            command=self.toggle_play,
            state="disabled"
        )
        self.play_btn.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(playback, text="Speed:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(20, 5))
        self.speed_var = ctk.StringVar(value="1x")
        ctk.CTkOptionMenu(
            playback,
            values=["0.5x", "1x", "2x", "4x"],
            variable=self.speed_var,
            fg_color=app.GRAY,
            button_color=app.RED,
            button_hover_color="#b30000",
            width=80
        ).pack(side="left", padx=5, pady=10)

        self.lap_label = ctk.CTkLabel(playback, text="Lap: -", font=ctk.CTkFont(size=13), text_color="#aaaaaa")
        self.lap_label.pack(side="left", padx=30)

        self.restart_btn = ctk.CTkButton(
            playback,
            text="↺ Restart",
            fg_color=app.GRAY,
            hover_color="#444444",
            border_color=app.RED,
            border_width=1,
            width=100,
            command=self.restart,
            state="disabled"
        )
        self.restart_btn.pack(side="left", padx=10)

        # Track canvas
        self.chart_frame = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        self.chart_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        ctk.CTkLabel(
            self.chart_frame,
            text="Load a race to start the replay",
            font=ctk.CTkFont(size=14),
            text_color="#555555"
        ).pack(expand=True)

    def load_race(self):
        self.load_btn.configure(state="disabled")
        self.play_btn.configure(state="disabled")
        self.restart_btn.configure(state="disabled")
        self.is_playing = False
        self.status.configure(text="⏳ Loading...")
        thread = threading.Thread(target=self._load_data)
        thread.daemon = True
        thread.start()

    def _load_data(self):
        try:
            year = int(self.year_var.get())
            round_num = int(self.round_var.get())
            self.session = get_session(year, round_num, "R")
            self.after(0, self._prepare_replay)
        except Exception as e:
            self.after(0, lambda: self.status.configure(text=f"❌ Error: {str(e)[:50]}"))
            self.after(0, lambda: self.load_btn.configure(state="normal"))

    def _prepare_replay(self):
        try:
            fastest = self.session.laps.pick_fastest()
            tel = fastest.get_telemetry()
            self.track_x = tel['X'].values
            self.track_y = tel['Y'].values

            self.drivers = list(self.session.drivers[:10])
            colors = list(plt.cm.tab10.colors)

            team_colors = {
                'Red Bull Racing': '#3671C6',
                'Ferrari': '#E8002D',
                'Mercedes': '#27F4D2',
                'McLaren': '#FF8000',
                'Aston Martin': '#229971',
                'Alpine': '#FF87BC',
                'Williams': '#64C4FF',
                'RB': '#6692FF',
                'Haas F1 Team': '#B6BABD',
                'Sauber': '#52E252',
            }

            self.driver_positions = {}
            self.driver_colors = {}

            for i, drv in enumerate(self.drivers):
                try:
                    drv_laps = self.session.laps.pick_driver(drv)
                    tel_data = drv_laps.get_telemetry()
                    self.driver_positions[drv] = {
                        'x': tel_data['X'].values,
                        'y': tel_data['Y'].values,
                    }
                    info = self.session.get_driver(drv)
                    team = info.get('TeamName', '')
                    self.driver_colors[drv] = team_colors.get(
                        team,
                        f'#{int(colors[i][0]*255):02x}{int(colors[i][1]*255):02x}{int(colors[i][2]*255):02x}'
                    )
                except:
                    self.driver_positions[drv] = {'x': [], 'y': []}
                    self.driver_colors[drv] = '#ffffff'

            self.total_frames = max(
                (len(v['x']) for v in self.driver_positions.values() if len(v['x']) > 0),
                default=0
            )
            self.current_frame = 0
            self._build_canvas()
            self.status.configure(text="✅ Loaded!")
            self.load_btn.configure(state="normal")
            self.play_btn.configure(state="normal")
            self.restart_btn.configure(state="normal")
        except Exception as e:
            self.status.configure(text=f"❌ Error: {str(e)[:50]}")
            self.load_btn.configure(state="normal")

    def _build_canvas(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.patch.set_facecolor("#1e1e1e")
        self.ax.set_facecolor("#1e1e1e")
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        self.ax.plot(self.track_x, self.track_y, color='#333333', linewidth=12, solid_capstyle='round')
        self.ax.plot(self.track_x, self.track_y, color='#555555', linewidth=8, solid_capstyle='round')

        self.dots = {}
        self.labels = {}
        for drv in self.drivers:
            pos = self.driver_positions[drv]
            if len(pos['x']) > 0:
                dot, = self.ax.plot(pos['x'][0], pos['y'][0], 'o',
                                    color=self.driver_colors[drv], markersize=10, zorder=5)
                label = self.ax.text(pos['x'][0], pos['y'][0] + 50, drv,
                                     color='white', fontsize=7, ha='center', zorder=6)
                self.dots[drv] = dot
                self.labels[drv] = label

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def toggle_play(self):
        if self.is_playing:
            self.is_playing = False
            self.play_btn.configure(text="▶ Play")
        else:
            self.is_playing = True
            self.play_btn.configure(text="⏸ Pause")
            self._animate()

    def _animate(self):
        if not self.is_playing:
            return

        speed_map = {"0.5x": 1, "1x": 2, "2x": 4, "4x": 8}
        step = speed_map.get(self.speed_var.get(), 2)
        self.current_frame += step

        if self.current_frame >= self.total_frames:
            self.current_frame = 0

        for drv in self.drivers:
            pos = self.driver_positions[drv]
            if len(pos['x']) > 0 and drv in self.dots:
                idx = min(self.current_frame, len(pos['x']) - 1)
                self.dots[drv].set_data([pos['x'][idx]], [pos['y'][idx]])
                self.labels[drv].set_position((pos['x'][idx], pos['y'][idx] + 50))

        self.canvas.draw_idle()

        lap_approx = int(self.current_frame / max(self.total_frames, 1) * self.session.total_laps) + 1
        self.lap_label.configure(text=f"Lap: {min(lap_approx, self.session.total_laps)}/{self.session.total_laps}")

        self.after(30, self._animate)

    def restart(self):
        self.current_frame = 0
        self.is_playing = False
        self.play_btn.configure(text="▶ Play")