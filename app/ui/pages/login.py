import customtkinter as ctk
from tkinter import messagebox
from app.services.auth_service import login_user
from app.ui.app import LUSH_FOREST_COLORS

class LoginPage(ctk.CTkFrame):
    def __init__(self, master, on_success, on_back):
        super().__init__(master, corner_radius=15)
        self.on_success = on_success
        self.on_back = on_back
        self._build()

    def _build(self):
        # Apply lush forest background
        self.configure(fg_color=LUSH_FOREST_COLORS["light"])
        
        # Title
        title = ctk.CTkLabel(
            self, 
            text="🔑 Login to Your Account", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=LUSH_FOREST_COLORS["text_dark"]
        )
        title.pack(pady=(40, 30))
        
        # Form container
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        form_frame.pack(pady=20, padx=40, fill="x")
        
        # Username field
        ctk.CTkLabel(form_frame, text="Username", font=ctk.CTkFont(size=14), text_color=LUSH_FOREST_COLORS["text_dark"]).pack(pady=(20, 5))
        self.username = ctk.CTkEntry(
            form_frame, 
            width=300, 
            height=40,
            placeholder_text="Enter your username",
            font=ctk.CTkFont(size=12),
            border_color=LUSH_FOREST_COLORS["secondary"],
            fg_color=LUSH_FOREST_COLORS["light"],
            text_color=LUSH_FOREST_COLORS["text_dark"]
        )
        self.username.pack(pady=(0, 15))
        
        # Password field
        ctk.CTkLabel(form_frame, text="Password", font=ctk.CTkFont(size=14), text_color=LUSH_FOREST_COLORS["text_dark"]).pack(pady=(0, 5))
        self.password = ctk.CTkEntry(
            form_frame, 
            width=300, 
            height=40,
            placeholder_text="Enter your password",
            show="*",
            font=ctk.CTkFont(size=12),
            border_color=LUSH_FOREST_COLORS["secondary"],
            fg_color=LUSH_FOREST_COLORS["light"],
            text_color=LUSH_FOREST_COLORS["text_dark"]
        )
        self.password.pack(pady=(0, 20))
        
        # Button container
        button_frame = ctk.CTkFrame(self, fg_color=LUSH_FOREST_COLORS["light"])
        button_frame.pack(pady=20)
        
        # Back button
        back_btn = ctk.CTkButton(
            button_frame,
            text="← Back",
            command=self.on_back,
            width=120,
            height=40,
            fg_color=LUSH_FOREST_COLORS["secondary"],
            hover_color=LUSH_FOREST_COLORS["accent"],
            corner_radius=100,
            text_color="white"
        )
        back_btn.pack(side="left", padx=10)
        
        # Login button
        login_btn = ctk.CTkButton(
            button_frame,
            text="Login   ",
            command=self._do_login,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=LUSH_FOREST_COLORS["primary"],
            hover_color=LUSH_FOREST_COLORS["accent"],
            text_color="white"
        )
        login_btn.pack(side="left", padx=10)

    def _do_login(self):
        ok, msg = login_user(self.username.get().strip(), self.password.get().strip())
        if ok:
            self.on_success(self.username.get().strip())
        else:
            messagebox.showerror("Login Failed", msg)
