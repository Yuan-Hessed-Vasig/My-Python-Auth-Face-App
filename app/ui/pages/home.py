import customtkinter as ctk
from app.ui.app import LUSH_FOREST_COLORS


class HomePage(ctk.CTkFrame):
    def __init__(self, master, on_login, on_register):
        super().__init__(master, corner_radius=15)
        self.on_login = on_login
        self.on_register = on_register
        self._build()

    def _build(self):
        # Apply lush forest background
        self.configure(fg_color=LUSH_FOREST_COLORS["light"])
        
        # Welcome title
        title = ctk.CTkLabel(
            self,
            text="Welcome to School Attendance System",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=LUSH_FOREST_COLORS["text_dark"]
        )
        title.pack(pady=(50, 20))

        # Subtitle
        subtitle = ctk.CTkLabel(
            self,
            text="Secure face-based authentication for students",
            font=ctk.CTkFont(size=14),
            text_color=LUSH_FOREST_COLORS["text_medium"]
        )
        subtitle.pack(pady=(0, 40))

        # Button container
        button_frame = ctk.CTkFrame(self, fg_color=LUSH_FOREST_COLORS["light"])
        button_frame.pack(pady=20)

        # Login button with lush forest colors
        login_btn = ctk.CTkButton(
            button_frame,
            text="🔑 Login",
            command=self.on_login,
            width=180,
            height=55,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12,
            fg_color=LUSH_FOREST_COLORS["primary"],
            hover_color=LUSH_FOREST_COLORS["accent"],
            text_color="white"
        )
        login_btn.pack(side="left", padx=15)

        # Register button with lush forest colors
        register_btn = ctk.CTkButton(
            button_frame,
            text="✨ Register",
            command=self.on_register,
            width=180,
            height=55,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12,
            fg_color=LUSH_FOREST_COLORS["secondary"],
            hover_color=LUSH_FOREST_COLORS["accent"],
            text_color="white"
        )
        register_btn.pack(side="left", padx=15)
