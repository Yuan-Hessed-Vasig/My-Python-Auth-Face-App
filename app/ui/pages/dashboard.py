from tkinter import ttk

class DashboardPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="Dashboard", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(self, text="(Content placeholder)").pack(anchor="w", pady=8)
