import customtkinter as ctk
import fastf1
import threading

class StandingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=app.DARK)
        self.app = app

        # Title
        ctk.CTkLabel(self, text="🏆 Season Standings",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=app.RED).pack(pady=(30, 10))

        # Control panel
        control = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        control.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(control, text="Year:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(20, 5), pady=15)
        self.year_var = ctk.StringVar(value="2024")
        ctk.CTkEntry(control, textvariable=self.year_var, width=70).pack(side="left", padx=5)

        self.load_btn = ctk.CTkButton(control, text="Load Standings",
                                       fg_color=app.RED, hover_color="#b30000",
                                       command=self.load_standings)
        self.load_btn.pack(side="left", padx=20, pady=15)

        self.status = ctk.CTkLabel(control, text="", font=ctk.CTkFont(size=12), text_color="#888888")
        self.status.pack(side="left", padx=10)

        # Two panels
        panels = ctk.CTkFrame(self, fg_color="transparent")
        panels.pack(fill="both", expand=True, padx=30, pady=10)

        # Driver standings
        left = ctk.CTkFrame(panels, fg_color=app.GRAY, corner_radius=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(left, text="Driver Standings",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self.driver_frame = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.driver_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Constructor standings
        right = ctk.CTkFrame(panels, fg_color=app.GRAY, corner_radius=10)
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(right, text="Constructor Standings",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        self.constructor_frame = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.constructor_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Calendar
        cal_frame = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        cal_frame.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(cal_frame, text="📅 Race Calendar",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        self.calendar_frame = ctk.CTkScrollableFrame(cal_frame, fg_color="transparent", height=120)
        self.calendar_frame.pack(fill="x", padx=5, pady=(0, 10))

        ctk.CTkLabel(self.driver_frame, text="Load standings to see data",
                     font=ctk.CTkFont(size=13), text_color="#555555").pack(expand=True, pady=50)
        ctk.CTkLabel(self.constructor_frame, text="Load standings to see data",
                     font=ctk.CTkFont(size=13), text_color="#555555").pack(expand=True, pady=50)

    def load_standings(self):
        self.load_btn.configure(state="disabled")
        self.status.configure(text="⏳ Loading...")
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        try:
            year = int(self.year_var.get())
            schedule = fastf1.get_event_schedule(year)
            self.after(0, lambda: self._draw_standings(year, schedule))
        except Exception as e:
            self.after(0, lambda: self.status.configure(text=f"❌ Error: {str(e)[:50]}"))
            self.after(0, lambda: self.load_btn.configure(state="normal"))

    def _draw_standings(self, year, schedule):
        # Clear frames
        for w in self.driver_frame.winfo_children():
            w.destroy()
        for w in self.constructor_frame.winfo_children():
            w.destroy()
        for w in self.calendar_frame.winfo_children():
            w.destroy()

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

        # Mock driver standings (FastF1 doesn't provide points directly)
        drivers_2024 = [
            ("VER", "Max Verstappen", "Red Bull Racing", 575),
            ("LEC", "Charles Leclerc", "Ferrari", 356),
            ("NOR", "Lando Norris", "McLaren", 374),
            ("SAI", "Carlos Sainz", "Ferrari", 340),
            ("PIA", "Oscar Piastri", "McLaren", 292),
            ("HAM", "Lewis Hamilton", "Mercedes", 223),
            ("RUS", "George Russell", "Mercedes", 217),
            ("PER", "Sergio Perez", "Red Bull Racing", 152),
            ("ALO", "Fernando Alonso", "Aston Martin", 70),
            ("STR", "Lance Stroll", "Aston Martin", 24),
        ]

        for i, (code, name, team, pts) in enumerate(drivers_2024):
            color = team_colors.get(team, '#888888')
            row = ctk.CTkFrame(self.driver_frame,
                               fg_color="#1e1e1e" if i % 2 == 0 else "#252525",
                               corner_radius=4, height=32)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            ctk.CTkFrame(row, fg_color=color, width=4, height=24, corner_radius=2).pack(side="left", padx=5, pady=4)
            ctk.CTkLabel(row, text=f"P{i+1}", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=self.app.RED, width=30).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=code, font=ctk.CTkFont(size=12, weight="bold"),
                         width=40).pack(side="left")
            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=11),
                         text_color="#aaaaaa").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{pts} pts", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="white").pack(side="right", padx=15)

        # Constructor standings
        constructors_2024 = [
            ("McLaren", 636),
            ("Ferrari", 652),
            ("Red Bull Racing", 589),
            ("Mercedes", 430),
            ("Aston Martin", 94),
            ("Alpine", 65),
            ("Haas F1 Team", 58),
            ("RB", 46),
            ("Williams", 17),
            ("Sauber", 4),
        ]

        for i, (team, pts) in enumerate(constructors_2024):
            color = team_colors.get(team, '#888888')
            row = ctk.CTkFrame(self.constructor_frame,
                               fg_color="#1e1e1e" if i % 2 == 0 else "#252525",
                               corner_radius=4, height=32)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            ctk.CTkFrame(row, fg_color=color, width=4, height=24, corner_radius=2).pack(side="left", padx=5, pady=4)
            ctk.CTkLabel(row, text=f"P{i+1}", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=self.app.RED, width=30).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=team, font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{pts} pts", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="white").pack(side="right", padx=15)

        # Calendar
        races = schedule[schedule['EventFormat'] != 'testing'][['RoundNumber', 'EventName', 'EventDate', 'Country']]
        for _, race in races.iterrows():
            date_str = str(race['EventDate'])[:10]
            card = ctk.CTkFrame(self.calendar_frame, fg_color="#1e1e1e", corner_radius=8, width=160, height=80)
            card.pack(side="left", padx=5, pady=5)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=f"R{int(race['RoundNumber'])}",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=self.app.RED).pack(pady=(8, 0))
            ctk.CTkLabel(card, text=race['Country'],
                         font=ctk.CTkFont(size=11, weight="bold")).pack()
            ctk.CTkLabel(card, text=date_str,
                         font=ctk.CTkFont(size=10), text_color="#888888").pack()

        self.status.configure(text="✅ Loaded!")
        self.load_btn.configure(state="normal")