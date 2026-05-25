import customtkinter as ctk
from data.f1_data import get_session, get_lap_times
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class PracticePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=app.DARK)
        self.app = app
        self.session = None

        # Başlık
        ctk.CTkLabel(
            self,
            text="🔧 Practice Analysis",
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

        # Session seçici
        ctk.CTkLabel(control, text="Session:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5))
        self.session_var = ctk.StringVar(value="FP1")
        ctk.CTkOptionMenu(
            control,
            values=["FP1", "FP2", "FP3"],
            variable=self.session_var,
            fg_color=app.GRAY,
            button_color=app.RED,
            button_hover_color="#b30000"
        ).pack(side="left", padx=5)

        # Load butonu
        self.load_btn = ctk.CTkButton(
            control,
            text="Load Session",
            fg_color=app.RED,
            hover_color="#b30000",
            command=self.load_session
        )
        self.load_btn.pack(side="left", padx=20, pady=15)

        # Status
        self.status = ctk.CTkLabel(control, text="", font=ctk.CTkFont(size=12), text_color="#888888")
        self.status.pack(side="left", padx=10)

        # İki panel: en hızlı turlar + lastik analizi
        panels = ctk.CTkFrame(self, fg_color="transparent")
        panels.pack(fill="both", expand=True, padx=30, pady=10)

        # Sol panel - En hızlı turlar
        self.left_frame = ctk.CTkFrame(panels, fg_color=app.GRAY, corner_radius=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(
            self.left_frame,
            text="Fastest Laps",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)

        self.left_placeholder = ctk.CTkLabel(
            self.left_frame,
            text="Load a session to see data",
            font=ctk.CTkFont(size=13),
            text_color="#555555"
        )
        self.left_placeholder.pack(expand=True)

        # Sağ panel - Lastik analizi
        self.right_frame = ctk.CTkFrame(panels, fg_color=app.GRAY, corner_radius=10)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(
            self.right_frame,
            text="Tyre Compounds",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)

        self.right_placeholder = ctk.CTkLabel(
            self.right_frame,
            text="Load a session to see data",
            font=ctk.CTkFont(size=13),
            text_color="#555555"
        )
        self.right_placeholder.pack(expand=True)

    def load_session(self):
        self.load_btn.configure(state="disabled")
        self.status.configure(text="⏳ Loading...")
        thread = threading.Thread(target=self._load_data)
        thread.daemon = True
        thread.start()

    def _load_data(self):
        try:
            year = int(self.year_var.get())
            round_num = int(self.round_var.get())
            session_type = self.session_var.get()
            self.session = get_session(year, round_num, session_type)
            laps = get_lap_times(self.session)
            self.after(0, lambda: self._draw_charts(laps))
        except Exception as e:
            self.after(0, lambda: self.status.configure(text=f"❌ Error: {str(e)[:40]}"))
        finally:
            self.after(0, lambda: self.load_btn.configure(state="normal"))

    def _draw_charts(self, laps):
        self.status.configure(text="✅ Loaded!")

        # Sol panel - En hızlı turlar tablosu
        self.left_placeholder.destroy()
        for widget in self.left_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") != "Fastest Laps":
                widget.destroy()

        fastest = laps.groupby('Driver')['LapTime'].min().sort_values()
        for i, (driver, laptime) in enumerate(fastest.head(10).items()):
            secs = laptime.total_seconds()
            mins = int(secs // 60)
            s = secs % 60
            row = ctk.CTkFrame(self.left_frame, fg_color="#1e1e1e" if i % 2 == 0 else "#252525", corner_radius=5)
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=f"P{i+1}", font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=self.app.RED, width=30).pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(row, text=driver, font=ctk.CTkFont(size=12), width=50).pack(side="left")
            ctk.CTkLabel(row, text=f"{mins}:{s:06.3f}", font=ctk.CTkFont(size=12),
                        text_color="#aaaaaa").pack(side="right", padx=10)

        # Sağ panel - Lastik pasta grafiği
        for widget in self.right_frame.winfo_children():
            if not isinstance(widget, ctk.CTkLabel):
                widget.destroy()
        self.right_placeholder.destroy() if hasattr(self, 'right_placeholder') else None

        compound_counts = laps['Compound'].value_counts()
        colors_map = {
            'SOFT': '#E8002D',
            'MEDIUM': '#FFF200',
            'HARD': '#FFFFFF',
            'INTERMEDIATE': '#43B02A',
            'WET': '#0067FF'
        }
        colors = [colors_map.get(c, '#888888') for c in compound_counts.index]

        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_facecolor("#2a2a2a")
        ax.pie(compound_counts.values, labels=compound_counts.index,
               colors=colors, autopct='%1.0f%%', textprops={'color': 'white'})
        ax.set_title("Tyre Usage", color="white")

        canvas = FigureCanvasTkAgg(fig, master=self.right_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)