import customtkinter as ctk
from datetime import datetime

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._build()
    
    def _build(self):
        # Main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header section
        header_frame = ctk.CTkFrame(self, corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Welcome title
        welcome_label = ctk.CTkLabel(
            header_frame,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        welcome_label.grid(row=0, column=0, sticky="w", padx=30, pady=20)
        
        # Current date/time
        current_time = datetime.now().strftime("%B %d, %Y - %I:%M %p")
        time_label = ctk.CTkLabel(
            header_frame,
            text=current_time,
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        time_label.grid(row=0, column=1, sticky="e", padx=30, pady=20)
        
        # Stats cards container
        stats_frame = ctk.CTkFrame(self, corner_radius=15)
        stats_frame.grid(row=1, column=0, sticky="nsew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        stats_frame.grid_rowconfigure((0, 1), weight=1)
        
        # Stats cards
        self._create_stat_card(stats_frame, "👥 Total Students", "1,234", "Active learners", 0, 0)
        self._create_stat_card(stats_frame, "✅ Present Today", "1,089", "88% attendance", 0, 1)
        self._create_stat_card(stats_frame, "⏰ Late Arrivals", "45", "4% of students", 0, 2)
        
        # Recent activity section
        activity_frame = ctk.CTkFrame(stats_frame, corner_radius=10)
        activity_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=20, pady=20)
        activity_frame.grid_columnconfigure(0, weight=1)
        
        activity_title = ctk.CTkLabel(
            activity_frame,
            text="📋 Recent Activity",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        activity_title.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Activity list
        activities = [
            "🔔 New student John Doe registered",
            "📊 Attendance report generated for Grade 10-A",
            "👤 Teacher Mary Smith logged in",
            "⚠️ 5 students marked as absent in Grade 9-B",
            "✅ Face recognition system updated"
        ]
        
        for i, activity in enumerate(activities):
            activity_label = ctk.CTkLabel(
                activity_frame,
                text=activity,
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            activity_label.grid(row=i+1, column=0, sticky="ew", padx=20, pady=5)
    
    def _create_stat_card(self, parent, title, value, subtitle, row, col):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=row, column=col, sticky="nsew", padx=20, pady=20)
        card.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=("#1f538d", "#4a9eff")
        )
        value_label.grid(row=1, column=0, pady=5)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        subtitle_label.grid(row=2, column=0, pady=(5, 20))
