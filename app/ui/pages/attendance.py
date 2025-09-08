import customtkinter as ctk
from datetime import datetime
from app.ui.widget.gradient_button import GradientButton
from app.ui.widget.data_table import DataTable, AsyncDataTable
from app.services.attendance_service import AttendanceService
import threading
import cv2
from PIL import Image, ImageTk
from app.services.face.detector import detect_faces
from app.services.face.recognition_algorithm import (
    FaceRecognitionEngine,
)
from app.services.students_service import StudentsService
import time
import os

class AttendancePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        try:
            # Camera state
            self._camera_running = False
            self._camera_thread = None
            self._cap = None
            self._latest_photo = None  # Keep reference to PhotoImage
            self._fr_engine = None
            self._students_dir = self._resolve_students_dir()
            self._init_recognition_engine()
            self._student_info_cache = {}
            self._build()
        except Exception as e:
            print(f"❌ Error building attendance page: {e}")
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
        self.camera_placeholder = ctk.CTkFrame(camera_frame, corner_radius=10)
        self.camera_placeholder.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Image label (will display camera frames)
        self.camera_label = ctk.CTkLabel(
            self.camera_placeholder,
            text="📷\n\nCamera Feed\nComing Soon!\n\nFeatures:\n• Real-time face detection\n• Student recognition\n• Automatic attendance marking\n• Live preview\n• Multiple face detection",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40"),
            justify="center"
        )
        self.camera_label.pack(expand=True, fill="both", padx=20, pady=20)
        
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
        
        # Attendance log with real data
        self.attendance_table = AsyncDataTable(
            log_frame,
            data_loader=self._load_attendance_data,
            height=300,
            on_select=self._on_attendance_select,
            on_double_click=self._on_attendance_double_click
        )
        self.attendance_table.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
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
        
        # Load real attendance stats
        self._load_and_display_attendance_stats(stats_frame)
    
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
    
    def _load_attendance_data(self):
        """Load attendance data from database"""
        try:
            headers = AttendanceService.get_table_headers()
            data = AttendanceService.get_attendance_for_table(50)  # Last 50 records
            return headers, data
        except Exception as e:
            print(f"❌ Error loading attendance: {e}")
            return ["Error"], [["Failed to load attendance data"]]
    
    def _load_and_display_attendance_stats(self, parent):
        """Load and display real attendance statistics"""
        # Create stats immediately with loading text
        self._create_stat_item(parent, "✅ Present", "Loading...", 1)
        self._create_stat_item(parent, "⏰ Late", "Loading...", 2)
        self._create_stat_item(parent, "❌ Absent", "Loading...", 3)
        
        # Store parent reference for updating
        self.attendance_stats_parent = parent
        
        def load_stats():
            try:
                stats = AttendanceService.get_attendance_stats()
                # Update UI in main thread
                self.after(0, lambda: self._update_attendance_stats_display(stats))
            except Exception as e:
                print(f"❌ Error loading attendance stats: {e}")
                # Show error stats
                error_stats = {"present": "Error", "late": "Error", "absent": "Error"}
                self.after(0, lambda: self._update_attendance_stats_display(error_stats))
        
        thread = threading.Thread(target=load_stats, daemon=True)
        thread.start()
    
    def _update_attendance_stats_display(self, stats):
        """Update existing attendance stats display"""
        # Find and update existing stat widgets instead of recreating
        if hasattr(self, 'attendance_stats_parent') and self.attendance_stats_parent.winfo_exists():
            # Clear and recreate stats
            children = self.attendance_stats_parent.winfo_children()
            for widget in children[1:]:  # Skip date label
                widget.destroy()
            
            self._create_stat_item(self.attendance_stats_parent, "✅ Present", str(stats.get("present", 0)), 1)
            self._create_stat_item(self.attendance_stats_parent, "⏰ Late", str(stats.get("late", 0)), 2)
            self._create_stat_item(self.attendance_stats_parent, "❌ Absent", str(stats.get("absent", 0)), 3)
    
    def _on_attendance_select(self, row_data):
        """Handle attendance selection in table"""
        if row_data:
            attendance_id = row_data[0]
            student_number = row_data[1]
            student_name = row_data[2]
            status = row_data[5]
            print(f"📋 Selected attendance: {student_name} ({student_number}) - {status}")
    
    def _on_attendance_double_click(self, row_data):
        """Handle attendance double click in table"""
        if row_data:
            attendance_id = row_data[0]
            student_name = row_data[2]
            print(f"✏️ Edit attendance: {student_name} (ID: {attendance_id})")
            # TODO: Open edit attendance dialog
    
    def _start_camera(self):
        """Handle start camera button click"""
        if self._camera_running:
            print("ℹ️ Camera already running")
            return
        print("🔄 Starting camera for face recognition...")

        # Try to open default camera (prefer DirectShow on Windows)
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        if not cap or not cap.isOpened():
            cap = cv2.VideoCapture(0)
        if not cap or not cap.isOpened():
            print("❌ Unable to open camera")
            return

        self._cap = cap
        self._camera_running = True

        def run_loop():
            try:
                self._camera_loop()
            except Exception as e:
                print(f"❌ Camera loop error: {e}")
            finally:
                # Ensure resources are released
                if self._cap is not None:
                    try:
                        self._cap.release()
                    except Exception:
                        pass
                self._cap = None
                self._camera_running = False

        self._camera_thread = threading.Thread(target=run_loop, daemon=True)
        self._camera_thread.start()
        
    def _stop_camera(self):
        """Handle stop camera button click"""
        if not self._camera_running:
            print("ℹ️ Camera not running")
            return
        print("🔄 Stopping camera...")
        self._camera_running = False
        # Wait briefly for thread to exit
        if self._camera_thread and self._camera_thread.is_alive():
            self._camera_thread.join(timeout=1.0)
        self._camera_thread = None
        # Clear image
        def clear_label():
            self.camera_label.configure(image=None, text="📷\n\nCamera Stopped")
        self.after(0, clear_label)

    def _camera_loop(self):
        """Read frames, detect faces, and update UI while running."""
        while self._camera_running and self._cap is not None and self._cap.isOpened():
            ret, frame_bgr = self._cap.read()
            if not ret or frame_bgr is None:
                time.sleep(0.02)
                continue

            # Perform recognition if engine available; else fallback to Haar detection
            annotated_bgr = frame_bgr
            if self._fr_engine is not None:
                try:
                    annotated_bgr, detections = self._fr_engine.recognize_frame(frame_bgr, draw_annotations=False)
                    # Draw labels and enrich with DB details
                    annotated_bgr = self._annotate_with_names(annotated_bgr, detections)
                except Exception as e:
                    print(f"⚠️ recognition error, falling back to Haar: {e}")
                    annotated_bgr = self._haar_annotate(frame_bgr)
            else:
                annotated_bgr = self._haar_annotate(frame_bgr)

            # Convert to RGB for PIL
            frame_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)

            # Resize to fit placeholder while keeping aspect ratio
            target_w = max(1, self.camera_placeholder.winfo_width())
            target_h = max(1, self.camera_placeholder.winfo_height())
            if target_w > 1 and target_h > 1:
                image = image.copy()
                image.thumbnail((target_w, target_h), Image.LANCZOS)

            photo = ImageTk.PhotoImage(image=image)
            self._latest_photo = photo  # prevent GC

            def update_image():
                self.camera_label.configure(image=photo, text="")

            self.after(0, update_image)

            # Throttle a bit
            time.sleep(0.01)

    def _haar_annotate(self, frame_bgr):
        """Fallback: detect faces via Haar cascade and draw boxes only."""
        try:
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            faces = detect_faces(gray)
            annotated = frame_bgr.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Label as UNKNOWN for clarity
                cv2.rectangle(annotated, (x, y + h - 30), (x + w, y + h), (128, 128, 128), cv2.FILLED)
                cv2.putText(annotated, "UNKNOWN", (x + 6, y + h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, lineType=cv2.LINE_AA)
            return annotated
        except Exception as e:
            print(f"⚠️ Haar detection error: {e}")
            return frame_bgr

    def _annotate_with_names(self, frame_bgr, detections):
        """Draw rectangles and labels, using DB info when recognized."""
        annotated = frame_bgr.copy()
        for d in detections:
            left, top, right, bottom = d.get("left"), d.get("top"), d.get("right"), d.get("bottom")
            is_known = d.get("is_known", False)
            name_key = d.get("name", "UNKNOWN")

            if is_known and name_key:
                # Lookup extra info from DB once; cache by uppercase name
                label_text = name_key
                try:
                    if name_key not in self._student_info_cache:
                        # Try to search by name via StudentsService
                        first_last = name_key.title().split()
                        search_term = first_last[-1]
                        matches = StudentsService.search_students(search_term)
                        info = None
                        for row in matches or []:
                            full = f"{row.get('first_name','')} {row.get('last_name','')}".strip().upper()
                            if full == name_key:
                                info = row
                                break
                        self._student_info_cache[name_key] = info
                    info = self._student_info_cache.get(name_key)
                    if info:
                        section = info.get("section") or ""
                        student_no = info.get("student_number") or ""
                        if section or student_no:
                            label_text = f"{name_key} | {student_no or section}"
                except Exception as e:
                    print(f"⚠️ Student info lookup failed for {name_key}: {e}")

                color = (0, 200, 0)
                cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
                cv2.rectangle(annotated, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(annotated, label_text, (left + 6, bottom - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, lineType=cv2.LINE_AA)
            else:
                color = (128, 128, 128)
                cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
                cv2.rectangle(annotated, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(annotated, "UNKNOWN", (left + 6, bottom - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, lineType=cv2.LINE_AA)
        return annotated

    def _resolve_students_dir(self):
        """Resolve default path to Images/Students from project root."""
        # attendance.py -> app/ui/pages/attendance.py
        # project root is three levels up from app/ui/pages
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        default_dir = os.path.join(project_root, "Images", "Students")
        return default_dir

    def _init_recognition_engine(self):
        """Initialize FaceRecognitionEngine by loading encodings if folder exists."""
        try:
            if os.path.isdir(self._students_dir):
                engine = FaceRecognitionEngine(match_threshold=0.50, process_every_n_frames=3)
                # Load encodings lazily on demand to avoid blocking UI thread
                def _load():
                    try:
                        engine.update_known_from_directory(self._students_dir)
                        print(f"✅ Loaded {len(engine.known_encodings)} encodings from {self._students_dir}")
                        self._fr_engine = engine
                    except Exception as e:
                        print(f"⚠️ Failed to load encodings: {e}")
                        self._fr_engine = None
                threading.Thread(target=_load, daemon=True).start()
            else:
                print(f"ℹ️ Students directory not found: {self._students_dir}. Using Haar cascade only.")
                self._fr_engine = None
        except Exception as e:
            print(f"⚠️ Recognition engine init error: {e}")
            self._fr_engine = None
    
    def _build_fallback(self):
        """Build fallback attendance page when main build fails"""
        try:
            error_label = ctk.CTkLabel(
                self,
                text="⚠️ Attendance Page Error\n\nUnable to load attendance page properly.\nPlease check your database connection.",
                font=ctk.CTkFont(size=16),
                text_color=("gray60", "gray40"),
                justify="center"
            )
            error_label.pack(expand=True, fill="both", padx=50, pady=50)
        except Exception as e:
            print(f"❌ Error creating fallback attendance page: {e}")
