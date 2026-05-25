import customtkinter as ctk
from data.f1_data import get_session, get_lap_times
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class RacePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=app.DARK)
        self.app = app
        self.session = None

        # Başlık
        ctk.CTkLabel(
            self,
            text="🏁 Race Analysis",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=app.RED
        ).pack(pady=(30, 10))

        # Kontrol paneli
        control = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        control.pack(fill="x", padx=30, pady=10)

        # Year
        ctk.CTkLabel(control, text="Year:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(20, 5), pady=15)
        self.year_var = ctk.StringVar(value="2024")
        ctk.CTkEntry(control, textvariable=self.year_var, width=70).pack(side="left", padx=5)

        # Round
        ctk.CTkLabel(control, text="Round:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5))
        self.round_var = ctk.StringVar(value="1")
        ctk.CTkEntry(control, textvariable=self.round_var, width=60).pack(side="left", padx=5)

        # Load butonu
        self.load_btn = ctk.CTkButton(
            control,
            text="Load Race",
            fg_color=app.RED,
            hover_color="#b30000",
            command=self.load_race
        )
        self.load_btn.pack(side="left", padx=20, pady=15)

        # Status label
        self.status = ctk.CTkLabel(control, text="", font=ctk.CTkFont(size=12), text_color="#888888")
        self.status.pack(side="left", padx=10)

        # Grafik alanı
        self.chart_frame = ctk.CTkFrame(self, fg_color=app.GRAY, corner_radius=10)
        self.chart_frame.pack(fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(
            self.chart_frame,
            text="Load a race to see lap time analysis",
            font=ctk.CTkFont(size=14),
            text_color="#555555"
        ).pack(expand=True)

    def load_race(self):
        self.load_btn.configure(state="disabled")
        self.status.configure(text="⏳ Loading...")
        thread = threading.Thread(target=self._load_data)
        thread.daemon = True
        thread.start()

    def _load_data(self):
        try:
            year = int(self.year_var.get())
            round_num = int(self.round_var.get())
            self.session = get_session(year, round_num, "R")
            laps = get_lap_times(self.session)
            self.after(0, lambda: self._draw_chart(laps))
        except Exception as e:
            self.after(0, lambda: self.status.configure(text=f"❌ Error: {str(e)[:40]}"))
        finally:
            self.after(0, lambda: self.load_btn.configure(state="normal"))

    def _draw_chart(self, laps):
        # Eski grafiği temizle
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        self.status.configure(text="✅ Loaded!")

        fig, ax = plt.subplots(figsize=(9, 4))
        fig.patch.set_facecolor("#2a2a2a")
        ax.set_facecolor("#1e1e1e")

        drivers = laps['Driver'].unique()[:10]
        colors = plt.cm.tab10.colors

        for i, driver in enumerate(drivers):
            d_laps = laps[laps['Driver'] == driver]
            lap_secs = d_laps['LapTime'].dt.total_seconds()
            ax.plot(d_laps['LapNumber'], lap_secs, label=driver, color=colors[i], linewidth=1.5)

        ax.set_xlabel("Lap", color="white")
        ax.set_ylabel("Lap Time (s)", color="white")
        ax.set_title("Lap Times by Driver", color="white", fontsize=13)
        ax.tick_params(colors="white")
        ax.legend(fontsize=8, facecolor="#2a2a2a", labelcolor="white")
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)