import customtkinter as ctk
from data.f1_data import get_session
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class TelemetryPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=app.DARK)
        self.app = app
        self.session = None

        # Title
        ctk.CTkLabel(self, text="📡 Telemetry Analysis",
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

        ctk.CTkLabel(control, text="Driver:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5))
        self.driver_var = ctk.StringVar(value="VER")
        ctk.CTkEntry(control, textvariable=self.driver_var, width=60).pack(side="left", padx=5)

        self.load_btn = ctk.CTkButton(control, text="Load Telemetry",
                                       fg_color=app.RED, hover_color="#b30000",
                                       command=self.load_telemetry)
        self.load_btn.pack(side="left", padx=20, pady=15)

        self.status = ctk.CTkLabel(control, text="", font=ctk.CTkFont(size=12), text_color="#888888")
        self.status.pack(side="left", padx=10)

        # Chart area
        self.chart_frame = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        self.chart_frame.pack(fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(self.chart_frame,
                     text="Select a driver and load telemetry",
                     font=ctk.CTkFont(size=14), text_color="#555555").pack(expand=True)

    def load_telemetry(self):
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

        driver = self.driver_var.get().upper()

        try:
            lap = self.session.laps.pick_driver(driver).pick_fastest()
            tel = lap.get_telemetry()
        except Exception as e:
            self.status.configure(text=f"❌ Driver not found: {e}")
            return

        fig, axes = plt.subplots(4, 1, figsize=(12, 9), sharex=True)
        fig.patch.set_facecolor("#1e1e1e")
        fig.suptitle(f"{driver} — Fastest Lap Telemetry", color="white", fontsize=14, fontweight="bold")

        plots = [
            ("Speed (km/h)", "Speed", "#E10600"),
            ("Throttle (%)", "Throttle", "#FF8000"),
            ("Brake", "Brake", "#27F4D2"),
            ("Gear", "nGear", "#FFF200"),
        ]

        for ax, (title, col, color) in zip(axes, plots):
            ax.set_facecolor("#151515")
            ax.tick_params(colors="white", labelsize=9)
            ax.spines['bottom'].set_color('#333')
            ax.spines['left'].set_color('#333')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_ylabel(title, color="white", fontsize=9)

            if col in tel.columns:
                ax.plot(tel['Distance'], tel[col], color=color, linewidth=1.5)
                ax.fill_between(tel['Distance'], tel[col], alpha=0.15, color=color)
            else:
                ax.text(0.5, 0.5, "No data", transform=ax.transAxes,
                       color="white", ha="center")

        axes[-1].set_xlabel("Distance (m)", color="white", fontsize=10)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.status.configure(text="✅ Loaded!")