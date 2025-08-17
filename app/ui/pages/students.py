import customtkinter as ctk
from app.ui.widget.gradient_button import GradientButton

class StudentsPage(ctk.CTkFrame):
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
            text="👥 Students Management",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=30, pady=20)
        
        # Add student button
        try:
            add_btn = GradientButton(
                header_frame,
                text="➕ Add Student",
                command=self._add_student,
                width=150,
                height=40,
                corner_radius=20
            )
            add_btn.grid(row=0, column=1, sticky="e", padx=30, pady=20)
        except:
            add_btn = ctk.CTkButton(
                header_frame,
                text="➕ Add Student",
                command=self._add_student,
                width=150,
                height=40,
                corner_radius=20
            )
            add_btn.grid(row=0, column=1, sticky="e", padx=30, pady=20)
        
        # Main content area
        content_frame = ctk.CTkFrame(self, corner_radius=15)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Search and filter section
        search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Search label
        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Search Students:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        search_label.grid(row=0, column=0, sticky="w", pady=5)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by name, student number, or section...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Table section (placeholder for now)
        table_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Table placeholder
        table_placeholder = ctk.CTkLabel(
            table_frame,
            text="📋 Students Table\n\n🚧 Table implementation coming soon!\n\nThis will show:\n• Student names and photos\n• Student numbers\n• Sections and grades\n• Enrollment status\n• Face recognition status\n\nFeatures:\n✅ Search and filter\n✅ Add/Edit/Delete students\n✅ Import from CSV\n✅ Export reports",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40"),
            justify="center"
        )
        table_placeholder.grid(row=0, column=0, padx=40, pady=40)
        
        # Quick stats
        stats_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self._create_quick_stat(stats_frame, "📊 Total Students", "1,234", 0)
        self._create_quick_stat(stats_frame, "🎯 Active", "1,189", 1)
        self._create_quick_stat(stats_frame, "⏸️ Inactive", "45", 2)
    
    def _create_quick_stat(self, parent, title, value, col):
        """Create a quick stat widget"""
        stat_frame = ctk.CTkFrame(parent, corner_radius=10)
        stat_frame.grid(row=0, column=col, sticky="ew", padx=10)
        
        title_label = ctk.CTkLabel(
            stat_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            stat_frame,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1f538d", "#4a9eff")
        )
        value_label.pack(pady=(0, 15))
    
    def _add_student(self):
        """Handle add student button click"""
        print("🔄 Add student functionality will be implemented with table")
