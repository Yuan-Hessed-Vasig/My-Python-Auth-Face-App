from tkinter import ttk

class AttendancePage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="Attendance", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(self, text="(Camera + recognition will be added in Step 3/4)").pack(anchor="w", pady=8)
