import customtkinter as ctk
from datetime import datetime
from app.services.students_service import StudentsService
from app.services.attendance_service import AttendanceService
import threading

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        try:
            self._build()
        except Exception as e:
            print(f"❌ Error building dashboard: {e}")
            self._build_fallback()
    
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
        
        # Load real stats data
        self._load_and_display_dashboard_stats(stats_frame)
        
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
    
    def _load_and_display_dashboard_stats(self, parent):
        """Load and display real dashboard statistics"""
        # Create stats immediately with loading text
        self._create_stat_card(parent, "👥 Total Students", "Loading...", "Loading data", 0, 0)
        self._create_stat_card(parent, "✅ Present Today", "Loading...", "Loading data", 0, 1)
        self._create_stat_card(parent, "⏰ Late Arrivals", "Loading...", "Loading data", 0, 2)
        
        # Store parent reference for updating
        self.dashboard_stats_parent = parent
        
        def load_stats():
            try:
                # Load students count
                students_stats = StudentsService.get_students_count()
                total_students = students_stats.get("total", 0)
                
                # Load attendance stats
                attendance_stats = AttendanceService.get_attendance_stats()
                present_today = attendance_stats.get("present", 0)
                late_today = attendance_stats.get("late", 0)
                
                # Calculate attendance percentage
                total_attendance = present_today + late_today + attendance_stats.get("absent", 0)
                attendance_percentage = int((present_today / total_attendance * 100)) if total_attendance > 0 else 0
                
                # Update UI in main thread
                self.after(0, lambda: self._update_dashboard_stats_display(
                    total_students, present_today, late_today, attendance_percentage
                ))
                
            except Exception as e:
                print(f"❌ Error loading dashboard stats: {e}")
                # Show error stats
                self.after(0, lambda: self._update_dashboard_stats_display(0, 0, 0, 0))
        
        thread = threading.Thread(target=load_stats, daemon=True)
        thread.start()
    
    def _update_dashboard_stats_display(self, total_students, present_today, late_today, attendance_percentage):
        """Update existing dashboard stats display"""
        # Clear and recreate stats
        if hasattr(self, 'dashboard_stats_parent') and self.dashboard_stats_parent.winfo_exists():
            for widget in self.dashboard_stats_parent.winfo_children()[:3]:  # Only first 3 stat cards
                widget.destroy()
            
            self._create_stat_card(self.dashboard_stats_parent, "👥 Total Students", f"{total_students:,}", "Active learners", 0, 0)
            self._create_stat_card(self.dashboard_stats_parent, "✅ Present Today", f"{present_today:,}", f"{attendance_percentage}% attendance", 0, 1)
            self._create_stat_card(self.dashboard_stats_parent, "⏰ Late Arrivals", f"{late_today:,}", f"{late_today} students", 0, 2)
    
    def _build_fallback(self):
        """Build fallback dashboard when main build fails"""
        try:
            error_label = ctk.CTkLabel(
                self,
                text="⚠️ Dashboard Error\n\nUnable to load dashboard properly.\nPlease check your database connection.",
                font=ctk.CTkFont(size=16),
                text_color=("gray60", "gray40"),
                justify="center"
            )
            error_label.pack(expand=True, fill="both", padx=50, pady=50)
        except Exception as e:
            print(f"❌ Error creating fallback dashboard: {e}")
