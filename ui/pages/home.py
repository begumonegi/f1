
import customtkinter as ctk

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=app.DARK)
        self.app = app

        # Başlık
        ctk.CTkLabel(
            self,
            text="Welcome to F1 Dashboard",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=app.RED
        ).pack(pady=(60, 10))

        ctk.CTkLabel(
            self,
            text="Your personal Formula 1 data analysis tool",
            font=ctk.CTkFont(size=16),
            text_color="#888888"
        ).pack(pady=(0, 50))

        # Kart grid
        card_frame = ctk.CTkFrame(self, fg_color="transparent")
        card_frame.pack(pady=20)

        cards = [
            ("🏁", "Race Replay", "Lap-by-lap position\ntracking & analysis", "race"),
            ("🔧", "Practice", "FP1 / FP2 / FP3\nsession analysis", "practice"),
        ]

        for icon, title, desc, page in cards:
            card = ctk.CTkFrame(card_frame, fg_color=app.GRAY, corner_radius=15, width=220, height=180)
            card.pack(side="left", padx=20)
            card.pack_propagate(False)

            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=36)).pack(pady=(25, 5))
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack()
            ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color="#888888").pack(pady=5)

            ctk.CTkButton(
                card,
                text="Open →",
                fg_color=app.RED,
                hover_color="#b30000",
                command=lambda p=page: app.show_page(p)
            ).pack(pady=10)

        # Alt bilgi
        ctk.CTkLabel(
            self,
            text="Data powered by FastF1",
            font=ctk.CTkFont(size=11),
            text_color="#444444"
        ).pack(side="bottom", pady=20)