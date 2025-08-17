#!/usr/bin/env python3
"""
Development server with auto-reload functionality

Usage:
    python dev.py    # Start development server with hot reload
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class AppReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_app()
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only restart on Python file changes
        if event.src_path.endswith('.py'):
            print(f"🔄 File changed: {event.src_path}")
            print("🚀 Restarting app...")
            self.restart_app()
    
    def restart_app(self):
        # Kill existing process
        if self.process:
            self.process.terminate()
            self.process.wait()
        
        # Start new process
        try:
            self.process = subprocess.Popen([sys.executable, "main.py"])
            print("✅ App started successfully!")
        except Exception as e:
            print(f"❌ Failed to start app: {e}")
    
    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()


def main():
    print("🔥 Starting development server with hot reload...")
    print("📁 Watching for file changes in: app/")
    print("🛑 Press Ctrl+C to stop")
    
    # Setup file watcher
    event_handler = AppReloader()
    observer = Observer()
    observer.schedule(event_handler, path="app", recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping development server...")
        observer.stop()
        event_handler.stop()
    
    observer.join()
    print("👋 Development server stopped.")


if __name__ == "__main__":
    main()
