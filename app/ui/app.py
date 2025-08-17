import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

# Set CustomTkinter theme and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
from app.ui.pages.home import HomePage
from app.ui.pages.login import LoginPage
from app.ui.pages.register import RegisterPage
from app.ui.pages.shell import Shell
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.students import StudentsPage
from app.ui.pages.attendance import AttendancePage

class Root(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("School Attendance — Step 1")
        self.geometry("980x640")
        self.resizable(True, True)
        
        # Development mode features
        self.bind('<F5>', lambda e: self._reload_app())
        self.bind('<Control-r>', lambda e: self._reload_app())

        self.container = ctk.CTkFrame(self); self.container.pack(fill="both", expand=True, padx=10, pady=10)
        self.shell = None
        self.current_user = None
        self.show_home()

    def run(self):
        self.mainloop()
    
    def _reload_app(self):
        """Reload the app manually (F5 or Ctrl+R)"""
        print("🔄 Manual reload triggered...")
        self.destroy()
        # Note: This just closes the app, you need to restart manually

    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_home(self):
        self._clear()
        HomePage(self.container, on_login=self.show_login, on_register=self.show_register).pack(fill="both", expand=True)

    def show_login(self):
        self._clear()
        LoginPage(self.container, on_success=self._on_logged_in, on_back=self.show_home).pack(fill="both", expand=True)

    def show_register(self):
        self._clear()
        RegisterPage(self.container, on_success=self.show_login, on_back=self.show_home).pack(fill="both", expand=True)

    def _on_logged_in(self, username: str):
        self.current_user = username
        self.show_shell("dashboard")

    def show_shell(self, route: str):
        self._clear()
        self.shell = Shell(self.container, on_nav_change=self._on_nav_change)
        self._on_nav_change(route)

    def _on_nav_change(self, route: str):
        if route == "dashboard":
            frame = DashboardPage(self.shell.content)
        elif route == "students":
            frame = StudentsPage(self.shell.content)
        elif route == "attendance":
            frame = AttendancePage(self.shell.content)
        else:
            frame = ttk.Frame(self.shell.content)
        self.shell.set_content(frame)

def run_app():
    Root().run()
