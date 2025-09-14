import customtkinter as ctk
from app.ui.app import LUSH_FOREST_COLORS

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_nav):
        super().__init__(master, width=200, corner_radius=10, fg_color=LUSH_FOREST_COLORS["light"])
        self.pack_propagate(False)
        self.on_nav = on_nav
        
        # Sidebar title
        title = ctk.CTkLabel(
            self, 
            text="Navigation", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=LUSH_FOREST_COLORS["text_dark"]
        )
        title.pack(pady=(20, 10), padx=20)
        
        # Navigation buttons
        nav_items = [
            ("🏠 Dashboard", "dashboard"),
            ("👥 Students", "students"), 
            ("📋 Attendance", "attendance")
        ]
        
        for text, key in nav_items:
            btn = ctk.CTkButton(
                self,
                text=text,
                command=lambda k=key: self.on_nav(k),
                width=160,
                height=40,
                font=ctk.CTkFont(size=12),
                corner_radius=8,
                fg_color=LUSH_FOREST_COLORS["secondary"],
                hover_color=LUSH_FOREST_COLORS["accent"],
                text_color="white"
            )
            btn.pack(padx=20, pady=5, fill="x")
