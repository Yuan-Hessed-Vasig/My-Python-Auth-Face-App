import customtkinter as ctk
from datetime import datetime
from app.ui.widget.gradient_button import GradientButton
from app.ui.widget.data_table import DataTable
from app.services.attendance_service import AttendanceService
from app.ui.app import LUSH_FOREST_COLORS
import threading
import cv2
from PIL import Image, ImageTk
from app.services.face.detector import detect_faces
from app.services.face.recognition_algorithm import (
    FaceRecognitionEngine,
)
from app.utils.performance_config import PerformanceConfig
from app.services.students_service import StudentsService
import time
import os

class AttendancePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=LUSH_FOREST_COLORS["light"])
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
            self._last_logged_at_by_student_id = {}
            self._detected_card_ids = set()
            self._build()
        except Exception as e:
            print(f"❌ Error building attendance page: {e}")
            self._build_fallback()
    
    def _build(self):
        # Apply lush forest background
        self.configure(fg_color=LUSH_FOREST_COLORS["light"])
        
        # Main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header section
        header_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="white")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📹 Attendance Tracking",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=LUSH_FOREST_COLORS["text_dark"]
        )
        title_label.grid(row=0, column=0, sticky="w", padx=30, pady=20)
        
        # Control buttons
        controls_frame = ctk.CTkFrame(header_frame, fg_color="white")
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
        content_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="white")
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_columnconfigure((0, 1), weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Camera section
        camera_frame = ctk.CTkFrame(content_frame, corner_radius=10, fg_color=LUSH_FOREST_COLORS["light"])
        camera_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        camera_frame.grid_columnconfigure(0, weight=1)
        camera_frame.grid_rowconfigure(1, weight=1)
        
        camera_title = ctk.CTkLabel(
            camera_frame,
            text="📹 Face Recognition Camera",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=LUSH_FOREST_COLORS["text_dark"]
        )
        camera_title.grid(row=0, column=0, pady=(20, 10))
        
        # Camera placeholder
        self.camera_placeholder = ctk.CTkFrame(camera_frame, corner_radius=10, fg_color=LUSH_FOREST_COLORS["light"])
        self.camera_placeholder.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Image label (will display camera frames)
        self.camera_label = ctk.CTkLabel(
            self.camera_placeholder,
            text="📷\n\nCamera Feed\nComing Soon!\n\nFeatures:\n• Real-time face detection\n• Student recognition\n• Automatic attendance marking\n• Live preview\n• Multiple face detection",
            font=ctk.CTkFont(size=16),
            text_color=LUSH_FOREST_COLORS["text_medium"],
            justify="center"
        )
        self.camera_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Attendance log section
        log_frame = ctk.CTkFrame(content_frame, corner_radius=10, fg_color=LUSH_FOREST_COLORS["light"])
        log_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        log_title = ctk.CTkLabel(
            log_frame,
            text="📋 Today's Attendance Log",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=LUSH_FOREST_COLORS["text_dark"]
        )
        log_title.grid(row=0, column=0, pady=(20, 10))
        
        # Detected students cards (shows each recognized student once per session)
        self.detected_cards_frame = ctk.CTkScrollableFrame(
            log_frame,
            corner_radius=10,
            height=400,  # Increased height since we removed the table
            fg_color=LUSH_FOREST_COLORS["light"]
        )
        self.detected_cards_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Add placeholder content to make the log area look better
        self.placeholder_label = ctk.CTkLabel(
            self.detected_cards_frame,
            text="📋 No attendance records yet\n\nWhen students are detected by the camera,\ntheir attendance will appear here.",
            font=ctk.CTkFont(size=14),
            text_color=LUSH_FOREST_COLORS["text_medium"],
            justify="center"
        )
        self.placeholder_label.pack(expand=True, fill="both", padx=20, pady=50)
        
    
    
    
    
    
    def _start_camera(self):
        """Handle start camera button click"""
        if self._camera_running:
            print("ℹ️ Camera already running")
            return
        
        # Ensure previous camera is properly stopped
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
        
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
        
        # Properly release camera resources
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception as e:
                print(f"⚠️ Error releasing camera: {e}")
            self._cap = None
        
        # Wait for thread to exit
        if self._camera_thread and self._camera_thread.is_alive():
            self._camera_thread.join(timeout=2.0)
        self._camera_thread = None
        
        # Clear image references to prevent memory leaks
        self._latest_photo = None
        
        # Clear image display safely
        def clear_label():
            try:
                self.camera_label.configure(image=None, text="📷\n\nCamera Stopped")
            except Exception as e:
                print(f"⚠️ Error clearing camera label: {e}")
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
                try:
                    # Only update if camera is still running and label exists
                    if self._camera_running and self.camera_label.winfo_exists():
                        self.camera_label.configure(image=photo, text="")
                except Exception as e:
                    print(f"⚠️ Error updating camera image: {e}")

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
            student_info = d.get("student_info")
            display_name = d.get("display_name", "UNKNOWN")

            if is_known and student_info:
                # Use the student info directly from detection
                section = student_info.get("section") or ""
                student_no = student_info.get("student_id") or ""
                
                # Create label text
                label_text = display_name
                if section or student_no:
                    label_text = f"{display_name} | {student_no or section}"
                
                # Log attendance with cooldown (60s per student)
                try:
                    student_pk = student_info.get("id")
                    if student_pk:
                        now = time.time()
                        last = self._last_logged_at_by_student_id.get(student_pk, 0)
                        if now - last > 60:  # 60 second cooldown
                            if AttendanceService.create_today_once(student_pk, "present"):
                                self._last_logged_at_by_student_id[student_pk] = now
                                print(f"✅ Logged attendance for {display_name} (ID: {student_pk})")
                                
                                # No need to refresh table or stats since we removed them
                        
                        # Push a one-time UI card for this student in this session
                        if student_pk and student_pk not in self._detected_card_ids:
                            self._detected_card_ids.add(student_pk)
                            self.after(0, lambda info=student_info: self._push_detected_card(info))
                            
                except Exception as e:
                    print(f"⚠️ Attendance log failed for {display_name}: {e}")

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
        default_dir = os.path.join(project_root, "app", "data", "images", "students")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    def _push_detected_card(self, student_info: dict):
        """Create and display a compact card for a newly detected student once per session."""
        try:
            if not hasattr(self, 'detected_cards_frame') or not self.detected_cards_frame.winfo_exists():
                return

            # Remove placeholder text if it exists
            if hasattr(self, 'placeholder_label') and self.placeholder_label.winfo_exists():
                self.placeholder_label.destroy()

            full_name = f"{student_info.get('first_name','')} {student_info.get('last_name','')}".strip()
            student_no = student_info.get('student_id', '')
            section = student_info.get('section', '') or 'N/A'
            timestamp = datetime.now().strftime("%H:%M:%S")
            student_pk = student_info.get('id')

            card = ctk.CTkFrame(self.detected_cards_frame, corner_radius=10, fg_color=LUSH_FOREST_COLORS["light"])
            card.pack(fill='x', padx=10, pady=6)

            # Left: initials circle
            left = ctk.CTkFrame(card, width=48, height=48, corner_radius=24, fg_color=LUSH_FOREST_COLORS["primary"])
            left.grid(row=0, column=0, padx=10, pady=10)
            left.grid_propagate(False)
            initials = ''.join([p[0] for p in full_name.split() if p])[:2].upper() or '?'
            initials_lbl = ctk.CTkLabel(left, text=initials, font=ctk.CTkFont(size=16, weight='bold'), text_color="white")
            initials_lbl.place(relx=0.5, rely=0.5, anchor='center')

            # Middle: name + meta
            mid = ctk.CTkFrame(card, fg_color='transparent')
            mid.grid(row=0, column=1, sticky='w', padx=5, pady=10)
            name_lbl = ctk.CTkLabel(mid, text=full_name or 'UNKNOWN', font=ctk.CTkFont(size=14, weight='bold'), text_color=LUSH_FOREST_COLORS["text_dark"])
            name_lbl.pack(anchor='w')
            meta_lbl = ctk.CTkLabel(mid, text=f"{student_no} • {section} • {timestamp}", font=ctk.CTkFont(size=12), text_color=LUSH_FOREST_COLORS["text_medium"])
            meta_lbl.pack(anchor='w')

            # Right: status and remove button
            right_frame = ctk.CTkFrame(card, fg_color='transparent')
            right_frame.grid(row=0, column=2, padx=10, pady=10)
            
            status_lbl = ctk.CTkLabel(right_frame, text='✅ Present', font=ctk.CTkFont(size=12, weight='bold'), text_color=LUSH_FOREST_COLORS["primary"])
            status_lbl.pack(anchor='e')
            
            # Remove button
            remove_btn = ctk.CTkButton(
                right_frame,
                text="🗑️ Remove",
                command=lambda: self._remove_detected_card(card, student_pk),
                width=80,
                height=25,
                font=ctk.CTkFont(size=10),
                fg_color="#ef4444",
                hover_color="#dc2626",
                corner_radius=12
            )
            remove_btn.pack(anchor='e', pady=(5, 0))

            # Layout
            card.grid_columnconfigure(1, weight=1)
            
            # Add a subtle animation effect
            card.configure(fg_color=LUSH_FOREST_COLORS["light"])
            self.after(100, lambda: card.configure(fg_color=LUSH_FOREST_COLORS["light"]))
            
        except Exception as e:
            print(f"⚠️ Failed to push detected card: {e}")

    def _remove_detected_card(self, card, student_pk):
        """Remove a detected card and revert the active state to allow re-detection."""
        try:
            if not card or not card.winfo_exists():
                return
                
            # Remove the card from the UI
            card.destroy()
            
            # Remove from detected card IDs set to allow re-detection
            if student_pk and student_pk in self._detected_card_ids:
                self._detected_card_ids.remove(student_pk)
                print(f"✅ Removed card for student ID {student_pk} - can be detected again")
            
            # Optional: Remove the attendance record from database
            # This allows the student to be marked present again
            if student_pk:
                try:
                    # Get today's attendance record for this student
                    today = datetime.now().date()
                    query = """
                        SELECT id FROM attendance
                        WHERE student_id = %s AND DATE(timestamp) = %s
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """
                    from app.services.data_service import DataService
                    attendance_record = DataService.execute_query(query, (student_pk, today))
                    
                    if attendance_record:
                        attendance_id = attendance_record[0]['id']
                        # Delete the attendance record
                        delete_query = "DELETE FROM attendance WHERE id = %s"
                        DataService.execute_query(delete_query, (attendance_id,))
                        print(f"✅ Removed attendance record for student ID {student_pk}")
                        
                except Exception as e:
                    print(f"⚠️ Failed to remove attendance record: {e}")
            
        except Exception as e:
            print(f"⚠️ Failed to remove detected card: {e}")

    def _init_recognition_engine(self):
        """Initialize FaceRecognitionEngine by loading encodings if folder exists."""
        try:
            if os.path.isdir(self._students_dir):
                # Use performance configuration
                performance_mode = PerformanceConfig.get_current_mode()
                engine = FaceRecognitionEngine(performance_mode=performance_mode)
                # Load encodings lazily on demand to avoid blocking UI thread
                def _load():
                    try:
                        engine.update_known_from_directory(self._students_dir)
                        print(f"✅ Loaded {len(engine.known_encodings)} face encodings for {len(engine.known_student_info)} students from {self._students_dir}")
                        for student in engine.known_student_info:
                            if student.get('id'):
                                print(f"   - {student.get('first_name', '')} {student.get('last_name', '')} (ID: {student.get('id')})")
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
                text_color=LUSH_FOREST_COLORS["text_medium"],
                justify="center"
            )
            error_label.pack(expand=True, fill="both", padx=50, pady=50)
        except Exception as e:
            print(f"❌ Error creating fallback attendance page: {e}")
    
    def cleanup(self):
        """Clean up camera resources when page is destroyed"""
        try:
            self._camera_running = False
            if self._cap is not None:
                self._cap.release()
                self._cap = None
            if self._camera_thread and self._camera_thread.is_alive():
                self._camera_thread.join(timeout=1.0)
            self._camera_thread = None
            self._latest_photo = None
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
