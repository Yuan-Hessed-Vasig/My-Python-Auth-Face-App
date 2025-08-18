import customtkinter as ctk
from tkinter import messagebox
from app.ui.widget.gradient_button import GradientButton
from app.ui.widget.data_table import DataTable
from app.services.students_service import StudentsService
import threading

class StudentsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        try:
            self._build()
        except Exception as e:
            print(f"❌ Error building students page: {e}")
            self._build_fallback()
    
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
        
        # Search and actions section (flex row style)
        search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        search_frame.grid_columnconfigure(1, weight=1)  # Search entry expands
        
        # Left side - Search
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.grid(row=0, column=0, sticky="w")
        
        search_label = ctk.CTkLabel(
            search_container,
            text="🔍",
            font=ctk.CTkFont(size=16)
        )
        search_label.pack(side="left", padx=(0, 5))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search students...",
            height=40,
            width=300,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(10, 10), pady=5)
        
        # Right side - Action buttons
        actions_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, sticky="e")
        
        # Add student button
        try:
            add_btn = GradientButton(
                actions_frame,
                text="➕ Add",
                command=self._add_student,
                width=90,
                height=40,
                corner_radius=20
            )
            add_btn.pack(side="left", padx=(0, 5))
        except:
            add_btn = ctk.CTkButton(
                actions_frame,
                text="➕ Add",
                command=self._add_student,
                width=90,
                height=40,
                corner_radius=20,
                font=ctk.CTkFont(size=12)
            )
            add_btn.pack(side="left", padx=(0, 5))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh",
            command=self._refresh_students_data,
            width=100,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=12),
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        refresh_btn.pack(side="left")
        
        # Table section with real data
        table_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create data table with Actions column
        self.students_table = DataTable(
            table_frame,
            headers=["ID", "Student Number", "Full Name", "Section", "Created Date", "Actions"],
            data=[],  # Will be loaded asynchronously
            height=350,
            on_select=self._on_student_select,
            on_double_click=self._on_student_double_click,
            on_edit=self._edit_student_dialog,  # Handle edit clicks
            on_delete=self._delete_student_dialog,  # Handle delete clicks
            searchable=False,  # Disable built-in search since we have external search
            show_toolbar=False,  # Disable toolbar since buttons are in search area
            font_size=12,  # Better readability
            header_font_size=13  # Slightly larger headers
        )
        self.students_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Load initial data
        self._load_students_async()
        
        # Bind search entry to table search
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        
        # Quick stats
        stats_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Load real stats
        self._load_and_display_stats(stats_frame)
    
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
    
    def _load_students_data(self):
        """Load students data from database"""
        try:
            headers = StudentsService.get_table_headers()
            data = StudentsService.get_students_for_table()
            return headers, data
        except Exception as e:
            print(f"❌ Error loading students: {e}")
            return ["Error"], [["Failed to load students data"]]
    
    def _load_and_display_stats(self, parent):
        """Load and display real statistics"""
        # Create stats immediately with loading text
        self._create_quick_stat(parent, "📊 Total Students", "Loading...", 0)
        self._create_quick_stat(parent, "🎯 Active", "Loading...", 1)
        self._create_quick_stat(parent, "⏸️ Inactive", "Loading...", 2)
        
        # Store parent reference for updating
        self.stats_parent = parent
        
        def load_stats():
            try:
                stats = StudentsService.get_students_count()
                # Update UI in main thread
                self.after(0, lambda: self._update_stats_display(stats))
            except Exception as e:
                print(f"❌ Error loading stats: {e}")
                # Show error stats
                error_stats = {"total": "Error", "active": "Error", "inactive": "Error"}
                self.after(0, lambda: self._update_stats_display(error_stats))
        
        thread = threading.Thread(target=load_stats, daemon=True)
        thread.start()
    
    def _update_stats_display(self, stats):
        """Update existing stats display"""
        # Clear existing stats widgets
        if hasattr(self, 'stats_parent') and self.stats_parent.winfo_exists():
            for widget in self.stats_parent.winfo_children():
                widget.destroy()
            
            # Recreate with new data
            self._create_quick_stat(self.stats_parent, "📊 Total Students", str(stats.get("total", 0)), 0)
            self._create_quick_stat(self.stats_parent, "🎯 Active", str(stats.get("active", 0)), 1)
            self._create_quick_stat(self.stats_parent, "⏸️ Inactive", str(stats.get("inactive", 0)), 2)
    
    def _on_student_select(self, row_data):
        """Handle student selection in table"""
        if row_data:
            student_id = row_data[0]
            student_number = row_data[1]
            student_name = row_data[2]
            print(f"📋 Selected student: {student_name} ({student_number})")
    
    def _on_student_double_click(self, row_data):
        """Handle student double click in table"""
        if row_data:
            student_id = row_data[0]
            student_name = row_data[2]
            print(f"✏️ Edit student: {student_name} (ID: {student_id})")
            # TODO: Open edit student dialog
    
    def _on_search_change(self, event):
        """Handle search entry changes"""
        search_term = self.search_entry.get().strip()
        if len(search_term) >= 2:  # Start searching after 2 characters
            self._search_students(search_term)
        elif len(search_term) == 0:
            # Refresh table to show all students
            self._refresh_students_data()
    
    def _search_students(self, search_term):
        """Search students and update table"""
        def search():
            try:
                # Search students
                students = StudentsService.search_students(search_term)
                
                # Convert to table format with Actions column
                table_data = []
                for student in students:
                    row = [
                        student.get("id", ""),
                        student.get("student_number", ""),
                        f"{student.get('first_name', '')} {student.get('last_name', '')}".strip(),
                        student.get("section", ""),
                        student.get("created_at", "").strftime("%Y-%m-%d") if student.get("created_at") else "",
                        "✏️ 🗑️"  # Actions column
                    ]
                    table_data.append(row)
                
                # Update table in main thread
                headers = StudentsService.get_table_headers()
                self.after(0, lambda: self.students_table.update_data(headers, table_data))
                
            except Exception as e:
                print(f"❌ Search error: {e}")
        
        thread = threading.Thread(target=search, daemon=True)
        thread.start()
    
    def _load_students_async(self):
        """Load students data asynchronously"""
        def load_data():
            try:
                data = StudentsService.get_students_for_table()
                # Add Actions column to each row
                enhanced_data = []
                for row in data:
                    # Add action buttons as the last column
                    enhanced_row = list(row) + ["✏️ 🗑️"]  # Edit and Delete icons
                    enhanced_data.append(enhanced_row)
                
                # Update table in main thread
                self.after(0, lambda: self.students_table.update_data(data=enhanced_data))
                print(f"✅ Loaded {len(enhanced_data)} students with action buttons")
            except Exception as e:
                print(f"❌ Error loading students: {e}")
                self.after(0, lambda: self.students_table.update_data(data=[["Error loading data", "", "", "", "", ""]]))
        
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()
    
    def _refresh_students_data(self):
        """Refresh students data"""
        print("🔄 Refreshing students data...")
        self._load_students_async()
    
    def _edit_student_dialog(self, row_data):
        """Open edit student dialog"""
        if not row_data:
            return
        
        student_id = row_data[0]
        current_name = row_data[2]
        
        # Simple edit dialog for now
        dialog = ctk.CTkInputDialog(
            text=f"Edit student name (current: {current_name}):",
            title="Edit Student"
        )
        new_name = dialog.get_input()
        
        if new_name and new_name != current_name:
            # TODO: Implement actual edit in database
            print(f"✏️ Would edit student {student_id}: {current_name} → {new_name}")
            messagebox.showinfo("Info", f"Edit functionality will update: {new_name}")
    
    def _delete_student_dialog(self, row_data):
        """Open delete student confirmation"""
        if not row_data:
            return
        
        student_id = row_data[0]
        student_name = row_data[2]
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{student_name}'?\n\nThis action cannot be undone."
        )
        
        if result:
            # TODO: Implement actual delete in database
            print(f"🗑️ Would delete student {student_id}: {student_name}")
            messagebox.showinfo("Info", f"Delete functionality would remove: {student_name}")
    
    def _add_student(self):
        """Handle add student button click"""
        # Simple add dialog for now
        dialog = ctk.CTkInputDialog(
            text="Enter new student name:",
            title="Add Student"
        )
        name = dialog.get_input()
        
        if name:
            # TODO: Implement actual add to database
            print(f"➕ Would add student: {name}")
            messagebox.showinfo("Info", f"Add functionality would create: {name}")
            # Refresh table to show changes (when implemented)
            self._refresh_students_data()
    
    def _build_fallback(self):
        """Build fallback students page when main build fails"""
        try:
            error_label = ctk.CTkLabel(
                self,
                text="⚠️ Students Page Error\n\nUnable to load students page properly.\nPlease check your database connection.",
                font=ctk.CTkFont(size=16),
                text_color=("gray60", "gray40"),
                justify="center"
            )
            error_label.pack(expand=True, fill="both", padx=50, pady=50)
        except Exception as e:
            print(f"❌ Error creating fallback students page: {e}")
