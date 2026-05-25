import customtkinter as ctk
from data.f1_data import get_session
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class ComparisonPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=app.DARK)
        self.app = app
        self.session = None

        # Title
        ctk.CTkLabel(self, text="🔵 Driver Comparison",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=app.RED).pack(pady=(30, 10))

        # Control panel
        control = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        control.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(control, text="Year:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(20, 5), pady=15)
        self.year_var = ctk.StringVar(value="2024")
        ctk.CTkEntry(control, textvariable=self.year_var, width=70).pack(side="left", padx=5)

        ctk.CTkLabel(control, text="Round:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5))
        self.round_var = ctk.StringVar(value="1")
        ctk.CTkEntry(control, textvariable=self.round_var, width=60).pack(side="left", padx=5)

        ctk.CTkLabel(control, text="Session:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5))
        self.session_var = ctk.StringVar(value="R")
        ctk.CTkOptionMenu(control, values=["R", "Q", "FP1", "FP2", "FP3"],
                          variable=self.session_var, fg_color=app.GRAY,
                          button_color=app.RED, button_hover_color="#b30000",
                          width=80).pack(side="left", padx=5)

        ctk.CTkLabel(control, text="Driver 1:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5))
        self.driver1_var = ctk.StringVar(value="VER")
        ctk.CTkEntry(control, textvariable=self.driver1_var, width=60).pack(side="left", padx=5)

        ctk.CTkLabel(control, text="Driver 2:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5))
        self.driver2_var = ctk.StringVar(value="HAM")
        ctk.CTkEntry(control, textvariable=self.driver2_var, width=60).pack(side="left", padx=5)

        self.load_btn = ctk.CTkButton(control, text="Compare",
                                       fg_color=app.RED, hover_color="#b30000",
                                       command=self.load_comparison)
        self.load_btn.pack(side="left", padx=20, pady=15)

        self.status = ctk.CTkLabel(control, text="", font=ctk.CTkFont(size=12), text_color="#888888")
        self.status.pack(side="left", padx=10)

        # Charts
        self.chart_frame = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        self.chart_frame.pack(fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(self.chart_frame,
                     text="Select two drivers and click Compare",
                     font=ctk.CTkFont(size=14), text_color="#555555").pack(expand=True)

    def load_comparison(self):
        self.load_btn.configure(state="disabled")
        self.status.configure(text="⏳ Loading...")
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        try:
            year = int(self.year_var.get())
            round_num = int(self.round_var.get())
            session_type = self.session_var.get()
            self.session = get_session(year, round_num, session_type)
            self.after(0, self._draw_charts)
        except Exception as e:
            self.after(0, lambda: self.status.configure(text=f"❌ Error: {str(e)[:50]}"))
        finally:
            self.after(0, lambda: self.load_btn.configure(state="normal"))

    def _draw_charts(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        d1 = self.driver1_var.get().upper()
        d2 = self.driver2_var.get().upper()

        try:
            laps1 = self.session.laps.pick_driver(d1)
            laps2 = self.session.laps.pick_driver(d2)
        except Exception as e:
            self.status.configure(text=f"❌ Driver not found: {e}")
            return

        fig, axes = plt.subplots(2, 2, figsize=(12, 7))
        fig.patch.set_facecolor("#2a2a2a")
        fig.suptitle(f"{d1} vs {d2}", color="white", fontsize=14, fontweight="bold")

        for ax in axes.flatten():
            ax.set_facecolor("#1e1e1e")
            ax.tick_params(colors="white")
            ax.spines['bottom'].set_color('#444')
            ax.spines['left'].set_color('#444')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        # 1. Lap times
        ax1 = axes[0][0]
        t1 = laps1['LapTime'].dt.total_seconds().dropna()
        t2 = laps2['LapTime'].dt.total_seconds().dropna()
        ax1.plot(laps1['LapNumber'][:len(t1)], t1, color="#E10600", label=d1, linewidth=1.5)
        ax1.plot(laps2['LapNumber'][:len(t2)], t2, color="#27F4D2", label=d2, linewidth=1.5)
        ax1.set_title("Lap Times (s)", color="white")
        ax1.set_xlabel("Lap", color="white")
        ax1.legend(facecolor="#2a2a2a", labelcolor="white", fontsize=9)

        # 2. Fastest lap telemetry - Speed
        ax2 = axes[0][1]
        try:
            fast1 = laps1.pick_fastest().get_telemetry()
            fast2 = laps2.pick_fastest().get_telemetry()
            ax2.plot(fast1['Distance'], fast1['Speed'], color="#E10600", label=d1, linewidth=1.5)
            ax2.plot(fast2['Distance'], fast2['Speed'], color="#27F4D2", label=d2, linewidth=1.5)
            ax2.set_title("Fastest Lap - Speed (km/h)", color="white")
            ax2.set_xlabel("Distance (m)", color="white")
            ax2.legend(facecolor="#2a2a2a", labelcolor="white", fontsize=9)
        except:
            ax2.set_title("Speed — No data", color="white")

        # 3. Tyre strategy
        ax3 = axes[1][0]
        tyre_colors = {'SOFT': '#E8002D', 'MEDIUM': '#FFF200', 'HARD': '#FFFFFF',
                       'INTERMEDIATE': '#43B02A', 'WET': '#0067FF'}
        for lap_row in laps1.itertuples():
            c = tyre_colors.get(lap_row.Compound, '#888888')
            ax3.bar(lap_row.LapNumber, 1, color=c, alpha=0.8)
        for lap_row in laps2.itertuples():
            c = tyre_colors.get(lap_row.Compound, '#888888')
            ax3.bar(lap_row.LapNumber, -1, color=c, alpha=0.8)
        ax3.set_title(f"Tyre Strategy  (+{d1} / -{d2})", color="white")
        ax3.set_xlabel("Lap", color="white")
        ax3.axhline(0, color='white', linewidth=0.5)

        # 4. Throttle comparison
        ax4 = axes[1][1]
        try:
            ax4.plot(fast1['Distance'], fast1['Throttle'], color="#E10600", label=d1, linewidth=1.2)
            ax4.plot(fast2['Distance'], fast2['Throttle'], color="#27F4D2", label=d2, linewidth=1.2)
            ax4.set_title("Fastest Lap - Throttle (%)", color="white")
            ax4.set_xlabel("Distance (m)", color="white")
            ax4.legend(facecolor="#2a2a2a", labelcolor="white", fontsize=9)
        except:
            ax4.set_title("Throttle — No data", color="white")

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.status.configure(text="✅ Loaded!")