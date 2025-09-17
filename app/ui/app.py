import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os
import atexit
import pywinstyles

# Set CustomTkinter theme and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Lush Forest Color Palette
LUSH_FOREST_COLORS = {
    "primary": "#2E6F40",      # Dark forest green - primary buttons/text
    "light": "#CFFFDC",        # Very light mint green - backgrounds and subtle accents
    "secondary": "#68BA7F",    # Medium green - secondary elements
    "dark": "#1A2B1F",         # Very dark green - text and borders (darker)
    "accent": "#4A7C59",       # Slightly lighter than primary for hover states
    "text_dark": "#0F1A12",    # Extra dark for better readability
    "text_medium": "#2D3B30"   # Medium dark for secondary text
}
from app.ui.pages.home import HomePage
from app.ui.pages.login import LoginPage
from app.ui.pages.register import RegisterPage
from app.ui.pages.shell import Shell
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.students import StudentsPage
from app.ui.pages.attendance import AttendancePage
from app.utils.dev_state import DevStateManager, save_app_state, load_app_state

class Root(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("School Attendance — Step 1")
        self.geometry("980x640")
        self.resizable(True, True)
        
        # Customize window appearance to match lush forest theme
        self.configure(fg_color=LUSH_FOREST_COLORS["light"])
        
        # Set window styling to match lush forest theme
        try:
            # Configure the root window background
            self.configure(bg=LUSH_FOREST_COLORS["light"])
            
            # Set window attributes for better theming
            self.attributes('-alpha', 0.98)  # Slight transparency for modern look
            
            # Try to set window icon (if you have an icon file)
            # self.iconbitmap('path/to/icon.ico')  # Uncomment if you have an icon
            
        except Exception as e:
            print(f"⚠️ Window styling note: {e}")
            pass
        
        # Development mode features
        self.bind('<F5>', lambda e: self._reload_app())
        self.bind('<Control-r>', lambda e: self._reload_app())
        self.bind('<Control-t>', lambda e: self._toggle_theme())  # Ctrl+T to toggle theme

        self.container = ctk.CTkFrame(self, fg_color=LUSH_FOREST_COLORS["light"]); self.container.pack(fill="both", expand=True, padx=10, pady=10)
        self.shell = None
        self.current_user = None
        self.current_route = "home"
        
        # Setup state saving on exit para sa dev mode
        if DevStateManager.is_dev_mode():
            atexit.register(self._save_state_on_exit)
        
        # Restore state kung dev mode at may saved state
        self._restore_dev_state()
        
        # Apply window styling after window is created
        self.after(100, self._apply_window_styling)
        
        # Set initial icon
        self._set_window_icon("dark")
        
        # Bind theme change events
        self.bind('<Configure>', self._on_window_configure)

    def _apply_window_styling(self):
        """Apply window styling after window is fully created using pywinstyles"""
        try:
            # Windows-specific styling using pywinstyles
            if hasattr(self, 'tk') and self.tk.call('tk', 'windowingsystem') == 'win32':
                # Get window handle
                hwnd = self.winfo_id()
                
                # Apply modern window styling with pywinstyles
                pywinstyles.apply_style(self, "mica")  # Modern Windows 11 mica style
                
                # Set title bar color to match our lush forest theme
                primary_color = LUSH_FOREST_COLORS["primary"]
                pywinstyles.change_border_color(self, color=primary_color)
                
                print("✅ Window styling applied successfully with pywinstyles")
                
                # Also apply Windows API styling for better results
                self._apply_windows_api_styling()
                
        except Exception as e:
            print(f"⚠️ Window styling error: {e}")
            # Fallback to basic styling if pywinstyles fails
            try:
                self._apply_fallback_styling()
            except Exception as fallback_error:
                print(f"⚠️ Fallback styling also failed: {fallback_error}")
    
    def _apply_windows_api_styling(self):
        """Apply Windows API styling for better color control"""
        try:
            import ctypes
            from ctypes import wintypes
            
            hwnd = self.winfo_id()
            
            # Enable dark mode for title bar
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)  # True
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
                ctypes.byref(value), ctypes.sizeof(value)
            )
            
            # Set title bar color
            DWMWA_CAPTION_COLOR = 35
            primary_color = int(LUSH_FOREST_COLORS["primary"].replace('#', ''), 16)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_CAPTION_COLOR, 
                ctypes.byref(ctypes.c_int(primary_color)), 4
            )
            
            # Set border color
            DWMWA_BORDER_COLOR = 34
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_BORDER_COLOR, 
                ctypes.byref(ctypes.c_int(primary_color)), 4
            )
            
            print("✅ Windows API styling applied successfully")
            
        except Exception as e:
            print(f"⚠️ Windows API styling error: {e}")
    
    def _apply_fallback_styling(self):
        """Fallback styling using Windows API if pywinstyles fails"""
        import ctypes
        from ctypes import wintypes
        
        hwnd = self.winfo_id()
        DWM_BORDER_COLOR = 34  # DWMWA_BORDER_COLOR
        color = int(LUSH_FOREST_COLORS["primary"].replace('#', ''), 16)
        
        result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWM_BORDER_COLOR, ctypes.byref(ctypes.c_int(color)), 4
        )
        
        if result == 0:
            print("✅ Fallback window border color applied successfully")
        else:
            print(f"⚠️ Could not apply fallback window border color (Error: {result})")
    
    def _on_window_configure(self, event):
        """Handle window configuration changes (like theme changes)"""
        # Reapply styling when window is reconfigured
        if event.widget == self:
            self.after(100, self._apply_window_styling)
    
    def update_window_theme(self, appearance_mode: str):
        """Update window theme based on appearance mode"""
        try:
            if hasattr(self, 'tk') and self.tk.call('tk', 'windowingsystem') == 'win32':
                # Choose colors based on appearance mode
                if appearance_mode.lower() == "dark":
                    # Dark mode colors
                    border_color = LUSH_FOREST_COLORS["primary"]
                elif appearance_mode.lower() == "light":
                    # Light mode colors
                    border_color = LUSH_FOREST_COLORS["secondary"]
                else:  # System mode
                    # Use system colors but with our theme accent
                    border_color = LUSH_FOREST_COLORS["primary"]
                
                # Apply the colors using correct pywinstyles API
                pywinstyles.change_border_color(self, color=border_color)
                
                # Update icon based on theme
                self._set_window_icon(appearance_mode.lower())
                
                print(f"✅ Window theme updated to {appearance_mode} mode")
                
        except Exception as e:
            print(f"⚠️ Error updating window theme: {e}")
    
    def _toggle_theme(self):
        """Toggle between light and dark themes (for testing)"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        
        # Update CustomTkinter theme
        ctk.set_appearance_mode(new_mode)
        
        # Update window styling
        self.update_window_theme(new_mode)
        
        print(f"🎨 Theme toggled to {new_mode} mode (Ctrl+T)")
    
    def _set_window_icon(self, theme_mode: str = "dark"):
        """Set window icon based on theme"""
        try:
            # Try theme-specific icon first
            theme_icon_path = f"app/assets/icons/app_icon_{theme_mode}.ico"
            if os.path.exists(theme_icon_path):
                self.iconbitmap(theme_icon_path)
                print(f"✅ Icon set to {theme_mode} theme")
            else:
                # Fallback to default icon
                default_icon = "app/assets/icons/app_icon.ico"
                if os.path.exists(default_icon):
                    self.iconbitmap(default_icon)
                    print("✅ Default icon set")
                else:
                    print("⚠️ No icon file found")
        except Exception as e:
            print(f"⚠️ Error setting icon: {e}")

    def run(self):
        self.mainloop()
    
    def _reload_app(self):
        """Reload the app manually (F5 or Ctrl+R)"""
        print("🔄 Manual reload triggered...")
        self._save_current_state()
        self.destroy()
        # Note: This just closes the app, you need to restart manually
        
    def _save_current_state(self):
        """Save current application state para sa hot reload"""
        if DevStateManager.is_dev_mode():
            save_app_state(
                current_user=self.current_user,
                current_route=self.current_route
            )
    
    def _save_state_on_exit(self):
        """Save state when application exits"""
        self._save_current_state()
    
    def _restore_dev_state(self):
        """Restore application state from dev cache"""
        if DevStateManager.is_dev_mode():
            state = load_app_state()
            self.current_user = state.get("current_user")
            self.current_route = state.get("current_route", "home")
            
            print(f"🔄 Restoring dev state - User: {self.current_user}, Route: {self.current_route}")
            
            # Navigate to proper page based on saved state
            if self.current_user and self.current_route != "home":
                # User was logged in, go to shell
                self.show_shell(self.current_route)
            elif self.current_route == "login":
                self.show_login()
            elif self.current_route == "register":
                self.show_register()
            else:
                self.show_home()
        else:
            # Production mode - normal startup
            self.show_home()

    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_home(self):
        self.current_route = "home"
        self.current_user = None
        self._save_current_state()
        self._clear()
        HomePage(self.container, on_login=self.show_login, on_register=self.show_register).pack(fill="both", expand=True)

    def show_login(self):
        self.current_route = "login"
        self._save_current_state()
        self._clear()
        LoginPage(self.container, on_success=self._on_logged_in, on_back=self.show_home).pack(fill="both", expand=True)

    def show_register(self):
        self.current_route = "register"
        self._save_current_state()
        self._clear()
        RegisterPage(self.container, on_success=self.show_login, on_back=self.show_home).pack(fill="both", expand=True)

    def _on_logged_in(self, username: str):
        self.current_user = username
        self.show_shell("dashboard")

    def show_shell(self, route: str):
        self.current_route = route
        self._save_current_state()
        self._clear()
        self.shell = Shell(self.container, on_nav_change=self._on_nav_change)
        self._on_nav_change(route)

    def _on_nav_change(self, route: str):
        self.current_route = route
        self._save_current_state()
        
        # Use ChatGPT's approach - page caching with factories
        widget_factory = self._get_page_factory(route)
        self.shell.set_content(route, widget_factory)
    
    def _get_page_factory(self, route: str):
        """Get factory function for creating pages (ChatGPT approach)"""
        factories = {
            "dashboard": lambda: DashboardPage(self.shell.content),
            "students": lambda: StudentsPage(self.shell.content), 
            "attendance": lambda: AttendancePage(self.shell.content),
        }
        
        return factories.get(route, lambda: self._create_default_page(route))
    
    def _create_default_page(self, route: str):
        """Create default page for unknown routes"""
        default = ctk.CTkFrame(self.shell.content)
        label = ctk.CTkLabel(default, text=f"📋 {route.title()} Page\nComing Soon!")
        label.pack(expand=True)
        return default

def run_app():
    Root().run()
