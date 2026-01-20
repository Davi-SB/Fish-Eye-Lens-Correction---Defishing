"""
User-friendly real-time speed tracking with modern GUI.
"""

import cv2
import numpy as np
import json
import time
from pathlib import Path
from dataclasses import asdict
from collections import deque
from enum import Enum
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading

from utils import (
    FilterParams,
    BlackCircleParams,
    process_frame_for_black_circles,
    draw_detected_circles
)


CONFIG_FILE = "config_1.json"
VIDEO_SOURCE = 0
REAL_DISTANCE_BETWEEN_MARKERS = 0.30  # meters
VIRTUAL_LINE_POSITION = 0.5  # center of frame


class CrossingState(Enum):
    """State for marker crossing detection."""
    WAITING_FOR_MARKER_A = 1
    WAITING_FOR_MARKER_B = 2


class SpeedCalculator:
    """Calculate speed based on marker crossings."""
    
    def __init__(self, distance_between_markers: float, moving_avg_window: int = 5):
        self.distance = distance_between_markers
        self.state = CrossingState.WAITING_FOR_MARKER_A
        self.marker_a_time = None
        self.marker_b_time = None
        self.speed_history = deque(maxlen=moving_avg_window)
        self.crossing_count = 0
        self.last_speed = 0.0
    
    def process_crossing(self, crossed: bool) -> float:
        """Process a crossing event and return speed."""
        if not crossed:
            return self.get_average_speed()
        
        current_time = time.time()
        
        if self.state == CrossingState.WAITING_FOR_MARKER_A:
            self.marker_a_time = current_time
            self.state = CrossingState.WAITING_FOR_MARKER_B
            self.crossing_count += 1
            
        elif self.state == CrossingState.WAITING_FOR_MARKER_B:
            self.marker_b_time = current_time
            
            if self.marker_a_time is not None:
                time_diff = self.marker_b_time - self.marker_a_time
                
                if time_diff > 0:
                    speed = self.distance / time_diff
                    self.speed_history.append(speed)
                    self.last_speed = speed
                    self.crossing_count += 1
            
            self.state = CrossingState.WAITING_FOR_MARKER_A
        
        return self.get_average_speed()
    
    def get_average_speed(self) -> float:
        """Get smoothed average speed."""
        if not self.speed_history:
            return 0.0
        return sum(self.speed_history) / len(self.speed_history)
    
    def reset(self):
        """Reset calculator state."""
        self.state = CrossingState.WAITING_FOR_MARKER_A
        self.marker_a_time = None
        self.marker_b_time = None
        self.speed_history.clear()
        self.crossing_count = 0
        self.last_speed = 0.0


class SpeedTrackerGUI:
    """Modern GUI for speed tracking."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏃 Treadmill Speed Tracker")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2b2b2b")
        
        # Load configuration
        self.filter_params = FilterParams()
        self.circle_params = BlackCircleParams()
        self.config_file = Path(CONFIG_FILE)
        self._load_config()
        
        # Video settings
        self.video_source = VIDEO_SOURCE
        self.distance = REAL_DISTANCE_BETWEEN_MARKERS
        self.line_position = VIRTUAL_LINE_POSITION
        
        # Video capture
        self.cap = None
        self.is_running = False
        self.thread = None
        
        # Speed calculator
        self.speed_calc = SpeedCalculator(self.distance)
        
        # Setup GUI
        self._create_widgets()
        
        # Start video
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _load_config(self):
        """Load configuration from file."""
        if not self.config_file.exists():
            messagebox.showwarning(
                "No Configuration",
                f"Configuration file '{CONFIG_FILE}' not found.\n"
                "Please run the calibrator first.\n\n"
                "Using default parameters."
            )
            return
        
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            
            if "filter_params" in config:
                self.filter_params = FilterParams(**config["filter_params"])
            if "circle_params" in config:
                self.circle_params = BlackCircleParams(**config["circle_params"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config:\n{e}")
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Top bar - Controls
        top_bar = tk.Frame(self.root, bg="#1e1e1e", height=120)
        top_bar.pack(fill=tk.X, padx=10, pady=(10, 0))
        top_bar.pack_propagate(False)
        
        # Title
        tk.Label(
            top_bar,
            text="🏃 Treadmill Speed Tracker",
            font=("Arial", 20, "bold"),
            bg="#1e1e1e",
            fg="white"
        ).pack(pady=(10, 5))
        
        # Controls
        control_frame = tk.Frame(top_bar, bg="#1e1e1e")
        control_frame.pack(pady=10)
        
        self.start_btn = tk.Button(
            control_frame,
            text="▶ Start",
            command=self._start_tracking,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            width=12,
            height=2
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏸ Stop",
            command=self._stop_tracking,
            font=("Arial", 12, "bold"),
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            width=12,
            height=2,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="🔄 Reset",
            command=self._reset_stats,
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda",
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="⚙️ Settings",
            command=self._show_settings,
            font=("Arial", 12, "bold"),
            bg="#9C27B0",
            fg="white",
            activebackground="#7B1FA2",
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        # Main area
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left - Video
        left_panel = tk.Frame(main_frame, bg="#1e1e1e")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        video_label = tk.Label(
            left_panel,
            text="📹 Live Feed",
            font=("Arial", 14, "bold"),
            bg="#1e1e1e",
            fg="white"
        )
        video_label.pack(pady=10)
        
        self.video_canvas = tk.Label(left_panel, bg="black")
        self.video_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right - Stats
        right_panel = tk.Frame(main_frame, bg="#1e1e1e", width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        tk.Label(
            right_panel,
            text="📊 Statistics",
            font=("Arial", 16, "bold"),
            bg="#1e1e1e",
            fg="white"
        ).pack(pady=15)
        
        # Speed display (large)
        speed_frame = tk.Frame(right_panel, bg="#2b2b2b", relief=tk.RAISED, bd=2)
        speed_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            speed_frame,
            text="Current Speed",
            font=("Arial", 12),
            bg="#2b2b2b",
            fg="#9E9E9E"
        ).pack(pady=(10, 5))
        
        self.speed_label_ms = tk.Label(
            speed_frame,
            text="0.00 m/s",
            font=("Arial", 32, "bold"),
            bg="#2b2b2b",
            fg="#4CAF50"
        )
        self.speed_label_ms.pack()
        
        self.speed_label_kmh = tk.Label(
            speed_frame,
            text="0.00 km/h",
            font=("Arial", 18),
            bg="#2b2b2b",
            fg="#4CAF50"
        )
        self.speed_label_kmh.pack(pady=(0, 10))
        
        # Other stats
        stats_container = tk.Frame(right_panel, bg="#1e1e1e")
        stats_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self._create_stat_row(stats_container, "State:", "state_label", "⏸ Idle")
        self._create_stat_row(stats_container, "Circles:", "circles_label", "0")
        self._create_stat_row(stats_container, "Crossings:", "crossings_label", "0")
        self._create_stat_row(stats_container, "Distance:", "distance_label", f"{self.distance:.2f} m")
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="● Ready - Press Start to begin tracking",
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="#4CAF50",
            anchor="w",
            padx=10
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _create_stat_row(self, parent, label_text, var_name, default):
        """Create a statistics row."""
        frame = tk.Frame(parent, bg="#2b2b2b", relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            frame,
            text=label_text,
            font=("Arial", 12),
            bg="#2b2b2b",
            fg="#9E9E9E"
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        label = tk.Label(
            frame,
            text=default,
            font=("Arial", 12, "bold"),
            bg="#2b2b2b",
            fg="white"
        )
        label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        setattr(self, var_name, label)
    
    def _start_tracking(self):
        """Start video capture and tracking."""
        if self.is_running:
            return
        
        try:
            self.cap = cv2.VideoCapture(self.video_source)
            if not self.cap.isOpened():
                raise Exception(f"Cannot open video source {self.video_source}")
            
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.status_bar.config(
                text="● Tracking active",
                fg="#4CAF50"
            )
            
            # Start processing thread
            self.thread = threading.Thread(target=self._process_video, daemon=True)
            self.thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start tracking:\n{e}")
            self.is_running = False
    
    def _stop_tracking(self):
        """Stop video capture."""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.status_bar.config(
            text="⏸ Tracking paused",
            fg="#FF9800"
        )
    
    def _process_video(self):
        """Process video frames in background thread."""
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                break
            
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Process frame
            mask, circles = process_frame_for_black_circles(
                frame,
                self.filter_params,
                self.circle_params
            )
            
            # Draw virtual line
            height, width = frame.shape[:2]
            line_x = int(width * self.line_position)
            cv2.line(frame, (line_x, 0), (line_x, height), (0, 255, 255), 2)
            
            # Draw circles
            display_frame = draw_detected_circles(frame, circles)
            
            # Check crossings
            crossed = False
            for circle in circles:
                cx, cy = circle.centroid
                if abs(cx - line_x) < 20:
                    crossed = True
                    cv2.circle(display_frame, (int(cx), int(cy)), 15, (0, 255, 0), 3)
            
            # Calculate speed
            speed = self.speed_calc.process_crossing(crossed)
            
            # Update GUI
            self.root.after(0, self._update_display, display_frame, speed, len(circles))
    
    def _update_display(self, frame, speed, circle_count):
        """Update display with new frame and stats."""
        # Update video
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (640, 480))
        img = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(img)
        self.video_canvas.config(image=photo)
        self.video_canvas.image = photo
        
        # Update stats
        self.speed_label_ms.config(text=f"{speed:.2f} m/s")
        self.speed_label_kmh.config(text=f"{speed * 3.6:.2f} km/h")
        
        state_text = "🔴 A" if self.speed_calc.state == CrossingState.WAITING_FOR_MARKER_A else "🔵 B"
        self.state_label.config(text=state_text)
        
        self.circles_label.config(text=str(circle_count))
        self.crossings_label.config(text=str(self.speed_calc.crossing_count))
    
    def _reset_stats(self):
        """Reset all statistics."""
        self.speed_calc.reset()
        self.speed_label_ms.config(text="0.00 m/s")
        self.speed_label_kmh.config(text="0.00 km/h")
        self.state_label.config(text="⏸ Idle")
        self.crossings_label.config(text="0")
        
        messagebox.showinfo("✅ Reset", "Statistics reset successfully!")
    
    def _show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg="#2b2b2b")
        settings_window.transient(self.root)
        
        tk.Label(
            settings_window,
            text="⚙️ Tracking Settings",
            font=("Arial", 16, "bold"),
            bg="#2b2b2b",
            fg="white"
        ).pack(pady=20)
        
        # Distance
        frame1 = tk.Frame(settings_window, bg="#2b2b2b")
        frame1.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(
            frame1,
            text="Distance between markers (m):",
            font=("Arial", 11),
            bg="#2b2b2b",
            fg="white"
        ).pack(side=tk.LEFT)
        
        distance_var = tk.DoubleVar(value=self.distance)
        tk.Entry(
            frame1,
            textvariable=distance_var,
            font=("Arial", 11),
            width=10
        ).pack(side=tk.RIGHT)
        
        # Video source
        frame2 = tk.Frame(settings_window, bg="#2b2b2b")
        frame2.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(
            frame2,
            text="Video source (0=webcam):",
            font=("Arial", 11),
            bg="#2b2b2b",
            fg="white"
        ).pack(side=tk.LEFT)
        
        source_var = tk.IntVar(value=self.video_source)
        tk.Entry(
            frame2,
            textvariable=source_var,
            font=("Arial", 11),
            width=10
        ).pack(side=tk.RIGHT)
        
        # Line position
        frame3 = tk.Frame(settings_window, bg="#2b2b2b")
        frame3.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(
            frame3,
            text="Virtual line position (0-1):",
            font=("Arial", 11),
            bg="#2b2b2b",
            fg="white"
        ).pack(side=tk.LEFT)
        
        line_var = tk.DoubleVar(value=self.line_position)
        tk.Entry(
            frame3,
            textvariable=line_var,
            font=("Arial", 11),
            width=10
        ).pack(side=tk.RIGHT)
        
        # Save button
        def save_settings():
            self.distance = distance_var.get()
            self.video_source = source_var.get()
            self.line_position = max(0.0, min(1.0, line_var.get()))
            self.speed_calc.distance = self.distance
            self.distance_label.config(text=f"{self.distance:.2f} m")
            messagebox.showinfo("✅ Saved", "Settings updated!")
            settings_window.destroy()
        
        tk.Button(
            settings_window,
            text="💾 Save",
            command=save_settings,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            width=15,
            height=2
        ).pack(pady=20)
    
    def _on_closing(self):
        """Handle window close."""
        self._stop_tracking()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTrackerGUI(root)
    root.mainloop()
