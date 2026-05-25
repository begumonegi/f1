import customtkinter as ctk
from ui.app import App

# Tema ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

if __name__ == "__main__":
    app = App()
    app.mainloop()