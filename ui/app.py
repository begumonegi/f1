import customtkinter as ctk
from ui.pages.home import HomePage
from ui.pages.race import RacePage
from ui.pages.practice import PracticePage
from ui.pages.replay import ReplayPage
from ui.pages.comparison import ComparisonPage
from ui.pages.telemetry import TelemetryPage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("F1 Dashboard")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.RED = "#E10600"
        self.DARK = "#151515"
        self.GRAY = "#2a2a2a"

        self.configure(fg_color=self.DARK)

        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=self.GRAY, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="🏎️ F1\nDASHBOARD",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.RED
        )
        self.logo.pack(pady=30)

        self.pages = {}
        self.current_page = None

        buttons = [
            ("🏠  Home", "home"),
            ("🏁  Race", "race"),
            ("🔧  Practice", "practice"),
            ("🔵  Comparison", "comparison"),
            ("📡  Telemetry", "telemetry"),
            ("🎬  Replay", "replay"),
        ]

        self.nav_buttons = {}
        for label, name in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color=self.RED,
                anchor="w",
                command=lambda n=name: self.show_page(n)
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[name] = btn

        self.content = ctk.CTkFrame(self, fg_color=self.DARK, corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

        self.pages["home"] = HomePage(self.content, self)
        self.pages["race"] = RacePage(self.content, self)
        self.pages["practice"] = PracticePage(self.content, self)
        self.pages["comparison"] = ComparisonPage(self.content, self)
        self.pages["telemetry"] = TelemetryPage(self.content, self)
        self.pages["replay"] = ReplayPage(self.content, self)

        self.show_page("home")

    def show_page(self, name):
        if self.current_page:
            self.pages[self.current_page].pack_forget()

        self.pages[name].pack(fill="both", expand=True)
        self.current_page = name

        for n, btn in self.nav_buttons.items():
            if n == name:
                btn.configure(fg_color=self.RED)
            else:
                btn.configure(fg_color="transparent")