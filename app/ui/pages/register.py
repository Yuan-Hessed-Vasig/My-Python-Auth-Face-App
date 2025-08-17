import tkinter as tk
from tkinter import ttk, messagebox
from app.services.auth_service import register_user

class RegisterPage(ttk.Frame):
    def __init__(self, master, on_success, on_back):
        super().__init__(master)
        self.on_success = on_success
        self.on_back = on_back
        self._build()

    def _build(self):
        ttk.Label(self, text="Register", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(30,10))
        ttk.Label(self, text="Username").grid(row=1, column=0, sticky="e", padx=10, pady=8)
        ttk.Label(self, text="Password").grid(row=2, column=0, sticky="e", padx=10, pady=8)
        self.username = ttk.Entry(self, width=26)
        self.password = ttk.Entry(self, width=26, show="*")
        self.username.grid(row=1, column=1, pady=8)
        self.password.grid(row=2, column=1, pady=8)

        btns = ttk.Frame(self); btns.grid(row=3, column=0, columnspan=2, pady=14)
        ttk.Button(btns, text="Back", command=self.on_back).pack(side="left", padx=6)
        ttk.Button(btns, text="Register", command=self._do_register).pack(side="left", padx=6)

    def _do_register(self):
        ok, msg = register_user(self.username.get().strip(), self.password.get().strip())
        if ok:
            messagebox.showinfo("Register", msg)
            self.on_success()
        else:
            messagebox.showerror("Register", msg)
