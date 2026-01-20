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
CAMERA_CONFIG_FILE = "camera_config.json"
VIDEO_SOURCE = 0
REAL_DISTANCE_BETWEEN_MARKERS = 0.30  # meters
VIRTUAL_LINE_POSITION = 0.5  # center of frame

# Default camera settings for high-speed tracking
DEFAULT_FPS = 60
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_EXPOSURE = -6  # Lower exposure for fast motion


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
        
        # Camera settings
        self.camera_config = {
            "fps": DEFAULT_FPS,
            "width": DEFAULT_WIDTH,
            "height": DEFAULT_HEIGHT,
            "exposure": DEFAULT_EXPOSURE,
            "source_type": "webcam"  # webcam, rtsp, http
        }
        self._load_camera_config()
        
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
    
    def _load_camera_config(self):
        """Load camera configuration from file."""
        camera_config_path = Path(CAMERA_CONFIG_FILE)
        if not camera_config_path.exists():
            return
        
        try:
            with open(camera_config_path, "r") as f:
                saved_config = json.load(f)
                self.camera_config.update(saved_config)
        except Exception as e:
            print(f"Failed to load camera config: {e}")
    
    def _save_camera_config(self):
        """Save camera configuration to file."""
        try:
            with open(CAMERA_CONFIG_FILE, "w") as f:
                json.dump(self.camera_config, f, indent=4)
        except Exception as e:
            print(f"Failed to save camera config: {e}")
    
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
        
        tk.Button(
            control_frame,
            text="📹 Camera Setup",
            command=self._show_camera_setup,
            font=("Arial", 12, "bold"),
            bg="#00BCD4",
            fg="white",
            activebackground="#0097A7",
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
            # Initialize video capture based on source type
            source = self.video_source
            if self.camera_config["source_type"] in ["rtsp", "http"]:
                source = self.video_source  # Already a URL string
            
            self.cap = cv2.VideoCapture(source)
            if not self.cap.isOpened():
                raise Exception(f"Cannot open video source {source}")
            
            # Configure camera for high-performance capture
            self._configure_camera()
            
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
    
    def _configure_camera(self):
        """Configure camera for high-performance capture."""
        if not self.cap or not self.cap.isOpened():
            return
        
        try:
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_config["width"])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_config["height"])
            
            # Set FPS
            self.cap.set(cv2.CAP_PROP_FPS, self.camera_config["fps"])
            
            # Set exposure (lower = faster shutter = less motion blur)
            if self.camera_config.get("exposure") is not None:
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual mode
                self.cap.set(cv2.CAP_PROP_EXPOSURE, self.camera_config["exposure"])
            
            # Disable auto-focus for consistent performance
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            
            # Set buffer size to 1 for lowest latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            print(f"[INFO] Camera configured:")
            print(f"  Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            print(f"  FPS: {int(self.cap.get(cv2.CAP_PROP_FPS))}")
            print(f"  Exposure: {self.cap.get(cv2.CAP_PROP_EXPOSURE)}")
            
        except Exception as e:
            print(f"[WARNING] Failed to configure some camera settings: {e}")
    
    def _test_stream_url(self, base_url):
        """Test different stream endpoints and return working URL."""
        # Common IP Webcam endpoints
        endpoints = [
            "/video",                    # MJPEG stream
            "/videofeed",                # Alternative MJPEG
            "/video?action=stream",      # Action parameter
            "/mjpegfeed?640x480",       # Specific resolution
            "/shot.jpg",                # Single frame (fallback)
        ]
        
        # Clean base URL
        base_url = base_url.rstrip('/')
        
        print(f"[INFO] Testing stream endpoints for {base_url}...")
        
        for endpoint in endpoints:
            test_url = base_url + endpoint
            print(f"[TEST] Trying: {test_url}")
            
            try:
                cap = cv2.VideoCapture(test_url)
                if cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    
                    if ret and frame is not None:
                        print(f"[SUCCESS] ✓ Working endpoint: {test_url}")
                        return test_url
                    else:
                        print(f"[FAIL] Could not read frame")
                else:
                    print(f"[FAIL] Could not open stream")
            except Exception as e:
                print(f"[FAIL] Error: {e}")
        
        print(f"[ERROR] No working endpoints found for {base_url}")
        return None
    
    def _show_camera_setup(self):
        """Show camera setup dialog."""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("📹 Camera Setup")
        setup_window.geometry("550x700")
        setup_window.configure(bg="#2b2b2b")
        setup_window.transient(self.root)
        
        tk.Label(
            setup_window,
            text="📹 Camera Configuration",
            font=("Arial", 18, "bold"),
            bg="#2b2b2b",
            fg="white"
        ).pack(pady=20)
        
        # Source type
        source_frame = tk.LabelFrame(
            setup_window,
            text="Camera Source",
            font=("Arial", 12, "bold"),
            bg="#1e1e1e",
            fg="#4CAF50",
            padx=20,
            pady=15
        )
        source_frame.pack(fill=tk.X, padx=20, pady=10)
        
        source_type = tk.StringVar(value=self.camera_config.get("source_type", "webcam"))
        
        tk.Radiobutton(
            source_frame,
            text="💻 Webcam (USB/Built-in)",
            variable=source_type,
            value="webcam",
            font=("Arial", 11),
            bg="#1e1e1e",
            fg="white",
            selectcolor="#2b2b2b",
            activebackground="#1e1e1e"
        ).pack(anchor="w", pady=5)
        
        tk.Radiobutton(
            source_frame,
            text="📱 RTSP Stream (IP Webcam, DroidCam)",
            variable=source_type,
            value="rtsp",
            font=("Arial", 11),
            bg="#1e1e1e",
            fg="white",
            selectcolor="#2b2b2b",
            activebackground="#1e1e1e"
        ).pack(anchor="w", pady=5)
        
        tk.Radiobutton(
            source_frame,
            text="🌐 HTTP/MJPEG Stream",
            variable=source_type,
            value="http",
            font=("Arial", 11),
            bg="#1e1e1e",
            fg="white",
            selectcolor="#2b2b2b",
            activebackground="#1e1e1e"
        ).pack(anchor="w", pady=5)
        
        # Source input
        input_frame = tk.Frame(setup_window, bg="#2b2b2b")
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            input_frame,
            text="Source (0 for webcam or URL):",
            font=("Arial", 11),
            bg="#2b2b2b",
            fg="white"
        ).pack(anchor="w")
        
        source_entry = tk.Entry(
            input_frame,
            font=("Arial", 11),
            width=50
        )
        source_entry.insert(0, str(self.video_source))
        source_entry.pack(fill=tk.X, pady=5)
        
        # Test button
        def test_url():
            url = source_entry.get().strip()
            if not url or url.isdigit():
                messagebox.showinfo("Info", "Enter a URL to test")
                return
            
            # If it's just base URL, test endpoints
            if url.endswith(":8080") or url.endswith(":8080/"):
                working_url = self._test_stream_url(url)
                if working_url:
                    source_entry.delete(0, tk.END)
                    source_entry.insert(0, working_url)
                    messagebox.showinfo("✅ Success", f"Found working endpoint:\n{working_url}")
                else:
                    messagebox.showerror("❌ Failed", "No working endpoints found.\nCheck the guide for correct URLs.")
            else:
                # Test the exact URL
                try:
                    cap = cv2.VideoCapture(url)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        cap.release()
                        if ret and frame is not None:
                            messagebox.showinfo("✅ Success", "Stream is working!")
                        else:
                            messagebox.showerror("❌ Failed", "Could not read frames from stream")
                    else:
                        messagebox.showerror("❌ Failed", "Could not open stream")
                except Exception as e:
                    messagebox.showerror("❌ Error", f"Failed to test:\n{str(e)}")
        
        test_btn_frame = tk.Frame(input_frame, bg="#2b2b2b")
        test_btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            test_btn_frame,
            text="🔍 Test URL",
            command=test_url,
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            test_btn_frame,
            text="(Tests connection and finds working endpoint)",
            font=("Arial", 8, "italic"),
            bg="#2b2b2b",
            fg="#9E9E9E"
        ).pack(side=tk.LEFT, padx=5)
        
        # Examples
        examples_frame = tk.LabelFrame(
            setup_window,
            text="📝 URL Examples",
            font=("Arial", 10, "bold"),
            bg="#1e1e1e",
            fg="#2196F3",
            padx=15,
            pady=10
        )
        examples_frame.pack(fill=tk.X, padx=20, pady=10)
        
        examples_text = tk.Text(
            examples_frame,
            height=5,
            font=("Consolas", 9),
            bg="#2b2b2b",
            fg="#4CAF50",
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        examples_text.insert("1.0", 
            "Base URL (auto-detect): http://192.168.1.135:8080\\n"
            "MJPEG: http://192.168.1.135:8080/video\\n"
            "RTSP: rtsp://192.168.1.135:8080/h264_ulaw.sdp\\n"
            "Alternative: http://192.168.1.135:8080/video?action=stream"
        )
        examples_text.config(state=tk.DISABLED)
        examples_text.pack(fill=tk.X)
        
        # Performance settings
        perf_frame = tk.LabelFrame(
            setup_window,
            text="🚀 High-Performance Settings",
            font=("Arial", 12, "bold"),
            bg="#1e1e1e",
            fg="#FF9800",
            padx=20,
            pady=15
        )
        perf_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # FPS
        fps_frame = tk.Frame(perf_frame, bg="#1e1e1e")
        fps_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            fps_frame,
            text="FPS (frames/sec):",
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="white",
            width=20,
            anchor="w"
        ).pack(side=tk.LEFT)
        fps_var = tk.IntVar(value=self.camera_config.get("fps", DEFAULT_FPS))
        tk.Spinbox(
            fps_frame,
            from_=15,
            to=120,
            textvariable=fps_var,
            font=("Arial", 10),
            width=10
        ).pack(side=tk.LEFT, padx=10)
        tk.Label(
            fps_frame,
            text="(60+ recommended)",
            font=("Arial", 9, "italic"),
            bg="#1e1e1e",
            fg="#9E9E9E"
        ).pack(side=tk.LEFT)
        
        # Width
        width_frame = tk.Frame(perf_frame, bg="#1e1e1e")
        width_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            width_frame,
            text="Width (pixels):",
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="white",
            width=20,
            anchor="w"
        ).pack(side=tk.LEFT)
        width_var = tk.IntVar(value=self.camera_config.get("width", DEFAULT_WIDTH))
        tk.Spinbox(
            width_frame,
            from_=640,
            to=1920,
            increment=160,
            textvariable=width_var,
            font=("Arial", 10),
            width=10
        ).pack(side=tk.LEFT, padx=10)
        
        # Height
        height_frame = tk.Frame(perf_frame, bg="#1e1e1e")
        height_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            height_frame,
            text="Height (pixels):",
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="white",
            width=20,
            anchor="w"
        ).pack(side=tk.LEFT)
        height_var = tk.IntVar(value=self.camera_config.get("height", DEFAULT_HEIGHT))
        tk.Spinbox(
            height_frame,
            from_=480,
            to=1080,
            increment=120,
            textvariable=height_var,
            font=("Arial", 10),
            width=10
        ).pack(side=tk.LEFT, padx=10)
        
        # Exposure
        exposure_frame = tk.Frame(perf_frame, bg="#1e1e1e")
        exposure_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            exposure_frame,
            text="Exposure (lower=less blur):",
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="white",
            width=20,
            anchor="w"
        ).pack(side=tk.LEFT)
        exposure_var = tk.IntVar(value=self.camera_config.get("exposure", DEFAULT_EXPOSURE))
        tk.Spinbox(
            exposure_frame,
            from_=-13,
            to=0,
            textvariable=exposure_var,
            font=("Arial", 10),
            width=10
        ).pack(side=tk.LEFT, padx=10)
        tk.Label(
            exposure_frame,
            text="(-6 to -10 recommended)",
            font=("Arial", 9, "italic"),
            bg="#1e1e1e",
            fg="#9E9E9E"
        ).pack(side=tk.LEFT)
        
        # Save button
        def save_camera_settings():
            self.camera_config["source_type"] = source_type.get()
            self.camera_config["fps"] = fps_var.get()
            self.camera_config["width"] = width_var.get()
            self.camera_config["height"] = height_var.get()
            self.camera_config["exposure"] = exposure_var.get()
            
            source_value = source_entry.get().strip()
            try:
                self.video_source = int(source_value)
            except ValueError:
                self.video_source = source_value
            
            self._save_camera_config()
            messagebox.showinfo("✅ Saved", "Camera settings saved!\\nRestart tracking to apply changes.")
            setup_window.destroy()
        
        tk.Button(
            setup_window,
            text="💾 Save Settings",
            command=save_camera_settings,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            width=20,
            height=2
        ).pack(pady=20)
    
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
