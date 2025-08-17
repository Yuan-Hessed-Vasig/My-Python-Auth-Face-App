from tkinter import ttk

class StudentsPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="Students", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(self, text="(Will add CRUD in Step 2)").pack(anchor="w", pady=8)
