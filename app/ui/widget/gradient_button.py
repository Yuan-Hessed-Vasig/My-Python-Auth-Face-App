import customtkinter as ctk
from app.ui.widget.gradient_button import GradientButton


class HomePage(ctk.CTkFrame):
    def __init__(self, master, on_login, on_register):
        super().__init__(master, corner_radius=15)
        self.on_login = on_login
        self.on_register = on_register
        self._build()

    def _build(self):
        # Welcome title
        title = ctk.CTkLabel(
            self,
            text="Welcome to School Attendance System",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.pack(pady=(50, 20))

        # Subtitle
        subtitle = ctk.CTkLabel(
            self,
            text="Secure face-based authentication for students",
            font=ctk.CTkFont(size=14),
        )
        subtitle.pack(pady=(0, 40))

        # Button container
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        # Login gradient button
        login_btn = GradientButton(
            button_frame,
            text="🔑 Login",
            command=self.on_login,
            width=180,
            height=55,
            start_color="#8972f5",
            end_color="#6061dd",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12,
        )
        login_btn.pack(side="left", padx=15)

        # Register gradient button
        register_btn = GradientButton(
            button_frame,
            text="✨ Register",
            command=self.on_register,
            width=180,
            height=55,
            start_color="#6061dd",
            end_color="#8972f5",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12,
        )
        register_btn.pack(side="left", padx=15)
