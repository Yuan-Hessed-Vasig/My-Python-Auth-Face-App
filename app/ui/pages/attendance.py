import customtkinter as ctk
from datetime import datetime
from app.ui.widget.gradient_button import GradientButton

class AttendancePage(ctk.CTkFrame):
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
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📹 Attendance Tracking",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=30, pady=20)
        
        # Control buttons
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=1, sticky="e", padx=30, pady=20)
        
        try:
            start_btn = GradientButton(
                controls_frame,
                text="📷 Start Camera",
                command=self._start_camera,
                width=130,
                height=40,
                start_color="#10b981",
                end_color="#047857",
                corner_radius=20
            )
            start_btn.pack(side="left", padx=(0, 10))
            
            stop_btn = GradientButton(
                controls_frame,
                text="⏹️ Stop",
                command=self._stop_camera,
                width=100,
                height=40,
                start_color="#ef4444",
                end_color="#dc2626",
                corner_radius=20
            )
            stop_btn.pack(side="left")
        except:
            start_btn = ctk.CTkButton(
                controls_frame,
                text="📷 Start Camera",
                command=self._start_camera,
                width=130,
                height=40,
                fg_color="#10b981",
                corner_radius=20
            )
            start_btn.pack(side="left", padx=(0, 10))
            
            stop_btn = ctk.CTkButton(
                controls_frame,
                text="⏹️ Stop",
                command=self._stop_camera,
                width=100,
                height=40,
                fg_color="#ef4444",
                corner_radius=20
            )
            stop_btn.pack(side="left")
        
        # Main content area
        content_frame = ctk.CTkFrame(self, corner_radius=15)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_columnconfigure((0, 1), weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Camera section
        camera_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        camera_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        camera_frame.grid_columnconfigure(0, weight=1)
        camera_frame.grid_rowconfigure(1, weight=1)
        
        camera_title = ctk.CTkLabel(
            camera_frame,
            text="📹 Face Recognition Camera",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        camera_title.grid(row=0, column=0, pady=(20, 10))
        
        # Camera placeholder
        camera_placeholder = ctk.CTkFrame(camera_frame, corner_radius=10)
        camera_placeholder.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        camera_label = ctk.CTkLabel(
            camera_placeholder,
            text="📷\n\nCamera Feed\nComing Soon!\n\nFeatures:\n• Real-time face detection\n• Student recognition\n• Automatic attendance marking\n• Live preview\n• Multiple face detection",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40"),
            justify="center"
        )
        camera_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Attendance log section
        log_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        log_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        log_title = ctk.CTkLabel(
            log_frame,
            text="📋 Today's Attendance Log",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        log_title.grid(row=0, column=0, pady=(20, 10))
        
        # Attendance log content
        log_content = ctk.CTkScrollableFrame(log_frame)
        log_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        log_content.grid_columnconfigure(0, weight=1)
        
        # Sample attendance entries
        current_time = datetime.now()
        sample_entries = [
            ("John Doe", "SN1001", "08:15 AM", "✅ Present"),
            ("Jane Smith", "SN1002", "08:17 AM", "✅ Present"),
            ("Mike Johnson", "SN1003", "08:45 AM", "⏰ Late"),
            ("Sarah Wilson", "SN1004", "08:16 AM", "✅ Present"),
            ("David Brown", "SN1005", "09:15 AM", "⏰ Late"),
        ]
        
        for i, (name, student_no, time, status) in enumerate(sample_entries):
            self._create_attendance_entry(log_content, name, student_no, time, status, i)
        
        # Statistics at bottom
        stats_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        stats_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        current_date = datetime.now().strftime("%B %d, %Y")
        date_label = ctk.CTkLabel(
            stats_frame,
            text=f"📅 {current_date}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        date_label.grid(row=0, column=0, pady=10)
        
        self._create_stat_item(stats_frame, "✅ Present", "45", 1)
        self._create_stat_item(stats_frame, "⏰ Late", "8", 2)
        self._create_stat_item(stats_frame, "❌ Absent", "12", 3)
    
    def _create_attendance_entry(self, parent, name, student_no, time, status, row):
        """Create an attendance log entry"""
        entry_frame = ctk.CTkFrame(parent, corner_radius=8)
        entry_frame.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
        entry_frame.grid_columnconfigure(1, weight=1)
        
        # Status icon
        status_color = "#10b981" if "Present" in status else "#f59e0b" if "Late" in status else "#ef4444"
        status_label = ctk.CTkLabel(
            entry_frame,
            text=status.split()[0],  # Just the emoji
            font=ctk.CTkFont(size=20),
            width=40
        )
        status_label.grid(row=0, column=0, padx=(15, 10), pady=10)
        
        # Student info
        info_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=name,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        details_label = ctk.CTkLabel(
            info_frame,
            text=f"{student_no} • {time}",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40"),
            anchor="w"
        )
        details_label.pack(anchor="w")
        
        # Status text
        status_text = ctk.CTkLabel(
            entry_frame,
            text=status.split()[-1],  # Just the status word
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color,
            width=80
        )
        status_text.grid(row=0, column=2, padx=(10, 15), pady=10)
    
    def _create_stat_item(self, parent, title, value, col):
        """Create a statistics item"""
        stat_frame = ctk.CTkFrame(parent, corner_radius=8)
        stat_frame.grid(row=0, column=col, sticky="ew", padx=5, pady=10)
        
        title_label = ctk.CTkLabel(
            stat_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(pady=(10, 2))
        
        value_label = ctk.CTkLabel(
            stat_frame,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1f538d", "#4a9eff")
        )
        value_label.pack(pady=(0, 10))
    
    def _start_camera(self):
        """Handle start camera button click"""
        print("🔄 Starting camera for face recognition...")
        
    def _stop_camera(self):
        """Handle stop camera button click"""
        print("🔄 Stopping camera...")
