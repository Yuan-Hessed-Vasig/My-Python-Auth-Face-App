import customtkinter as ctk
from app.ui.components.navbar import Navbar
from app.ui.components.sidebar import Sidebar

class Shell(ctk.CTkFrame):
    def __init__(self, master, on_nav_change):
        super().__init__(master, corner_radius=15)
        self.pack(fill="both", expand=True)
        self.on_nav_change = on_nav_change

        # Navbar
        self.navbar = Navbar(self, title="🎓 School Attendance System")
        
        # Body container
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Sidebar
        self.sidebar = Sidebar(self.body, on_nav=self.on_nav_change)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))

        # Content area
        self.content = ctk.CTkFrame(self.body, corner_radius=10)
        self.content.pack(side="left", fill="both", expand=True)

    def set_content(self, widget):
        for w in self.content.winfo_children():
            w.destroy()
        widget.pack(fill="both", expand=True, padx=20, pady=20)
