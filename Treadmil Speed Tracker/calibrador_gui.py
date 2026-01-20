"""
User-friendly calibration tool with Tkinter GUI for black circle detection.
"""

import cv2
import numpy as np
import json
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

from utils import (
    FilterParams,
    BlackCircleParams,
    preprocess_frame,
    convert_to_grayscale,
    create_black_mask,
    apply_morphological_operations,
    detect_black_circles,
    draw_detected_circles
)


CONFIG_FILE = "calibration_config.json"
IMAGES_FOLDER = "images"
IMAGE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.webp"]


class CalibrationGUI:
    """Modern GUI for black circle calibration."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Treadmill Speed Tracker - Calibration")
        self.root.geometry("1400x900")
        self.root.configure(bg="#2b2b2b")
        
        # Load images
        self.images_folder = Path(IMAGES_FOLDER)
        self.images = []
        self.image_paths = []
        self.current_image_index = 0
        self._load_images()
        
        # Parameters
        self.filter_params = FilterParams()
        self.circle_params = BlackCircleParams()
        self.config_file = Path(CONFIG_FILE)
        self._load_config()
        
        # Setup GUI
        self._create_widgets()
        self._update_display()
        
    def _load_images(self):
        """Load images from folder."""
        if not self.images_folder.exists():
            self.images_folder.mkdir(parents=True, exist_ok=True)
            return
        
        for ext in IMAGE_EXTENSIONS:
            pattern = str(self.images_folder / ext)
            self.image_paths.extend(glob.glob(pattern))
        
        self.image_paths.sort()
        
        for path in self.image_paths:
            img = cv2.imread(path)
            if img is not None:
                self.images.append(img)
        
        if not self.images:
            messagebox.showwarning(
                "No Images",
                f"No images found in '{IMAGES_FOLDER}' folder.\n"
                "Please add images and restart."
            )
    
    def _load_config(self):
        """Load configuration from file."""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            
            if "filter_params" in config:
                self.filter_params = FilterParams(**config["filter_params"])
            if "circle_params" in config:
                self.circle_params = BlackCircleParams(**config["circle_params"])
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def _save_config(self):
        """Save configuration to file."""
        config = {
            "filter_params": asdict(self.filter_params),
            "circle_params": asdict(self.circle_params)
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)
        
        messagebox.showinfo("✅ Saved", f"Configuration saved to:\n{self.config_file}")
    
    def _load_config_from_file(self):
        """Load configuration from a selected JSON file."""
        file_path = filedialog.askopenfilename(
            title="Select Configuration File",
            initialdir=".",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            defaultextension=".json"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            
            # Update parameters
            if "filter_params" in config:
                self.filter_params = FilterParams(**config["filter_params"])
            if "circle_params" in config:
                self.circle_params = BlackCircleParams(**config["circle_params"])
            
            # Update all sliders to reflect loaded values
            self.sliders["black_threshold"][0].set(self.circle_params.black_threshold)
            self.sliders["min_area"][0].set(self.circle_params.min_area // 100)
            self.sliders["max_area"][0].set(self.circle_params.max_area // 100)
            self.sliders["min_circularity"][0].set(int(self.circle_params.min_circularity * 100))
            self.sliders["use_adaptive"][0].set(self.circle_params.use_adaptive)
            self.sliders["adaptive_block"][0].set(self.circle_params.adaptive_block_size)
            self.sliders["adaptive_c"][0].set(self.circle_params.adaptive_c)
            self.sliders["blur"][0].set(self.filter_params.blur_kernel)
            self.sliders["contrast"][0].set(int(self.filter_params.contrast * 100))
            self.sliders["saturation"][0].set(int(self.filter_params.saturation * 100))
            self.sliders["erode"][0].set(self.filter_params.erode_iterations)
            self.sliders["dilate"][0].set(self.filter_params.dilate_iterations)
            
            # Update display with new parameters
            self._update_display()
            
            messagebox.showinfo(
                "✅ Loaded", 
                f"Configuration loaded from:\n{Path(file_path).name}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "❌ Error",
                f"Failed to load configuration:\n{str(e)}"
            )
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Images
        left_panel = tk.Frame(main_frame, bg="#1e1e1e", relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Image navigation
        nav_frame = tk.Frame(left_panel, bg="#1e1e1e")
        nav_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.image_label = tk.Label(
            nav_frame, 
            text="Image 1/1", 
            font=("Arial", 14, "bold"),
            bg="#1e1e1e", 
            fg="white"
        )
        self.image_label.pack(side=tk.TOP, pady=(0, 10))
        
        btn_frame = tk.Frame(nav_frame, bg="#1e1e1e")
        btn_frame.pack()
        
        tk.Button(
            btn_frame, 
            text="◀ Previous", 
            command=self._prev_image,
            font=("Arial", 11),
            bg="#4CAF50", 
            fg="white",
            activebackground="#45a049",
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame, 
            text="Next ▶", 
            command=self._next_image,
            font=("Arial", 11),
            bg="#4CAF50", 
            fg="white",
            activebackground="#45a049",
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        # Image display area (2x2 grid)
        images_container = tk.Frame(left_panel, bg="#1e1e1e")
        images_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid
        images_container.columnconfigure(0, weight=1)
        images_container.columnconfigure(1, weight=1)
        images_container.rowconfigure(0, weight=1)
        images_container.rowconfigure(1, weight=1)
        
        # Original
        frame1 = tk.LabelFrame(
            images_container, 
            text="📷 Original + Detection", 
            font=("Arial", 10, "bold"),
            bg="#2b2b2b", 
            fg="#4CAF50"
        )
        frame1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.canvas_original = tk.Label(frame1, bg="black")
        self.canvas_original.pack(fill=tk.BOTH, expand=True)
        
        # Filtered
        frame2 = tk.LabelFrame(
            images_container, 
            text="🎨 Filtered Preview", 
            font=("Arial", 10, "bold"),
            bg="#2b2b2b", 
            fg="#2196F3"
        )
        frame2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.canvas_filtered = tk.Label(frame2, bg="black")
        self.canvas_filtered.pack(fill=tk.BOTH, expand=True)
        
        # Grayscale
        frame3 = tk.LabelFrame(
            images_container, 
            text="⬛ Grayscale", 
            font=("Arial", 10, "bold"),
            bg="#2b2b2b", 
            fg="#9E9E9E"
        )
        frame3.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.canvas_gray = tk.Label(frame3, bg="black")
        self.canvas_gray.pack(fill=tk.BOTH, expand=True)
        
        # Mask
        frame4 = tk.LabelFrame(
            images_container, 
            text="🎭 Black Mask", 
            font=("Arial", 10, "bold"),
            bg="#2b2b2b", 
            fg="#FF9800"
        )
        frame4.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.canvas_mask = tk.Label(frame4, bg="black")
        self.canvas_mask.pack(fill=tk.BOTH, expand=True)
        
        # Detection info
        self.info_label = tk.Label(
            left_panel,
            text="Circles detected: 0",
            font=("Arial", 12, "bold"),
            bg="#1e1e1e",
            fg="#4CAF50"
        )
        self.info_label.pack(pady=10)
        
        # Right panel - Controls
        right_panel = tk.Frame(main_frame, bg="#1e1e1e", relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # Title
        tk.Label(
            right_panel,
            text="⚙️ Detection Parameters",
            font=("Arial", 16, "bold"),
            bg="#1e1e1e",
            fg="white"
        ).pack(pady=15)
        
        # Scrollable frame
        canvas = tk.Canvas(right_panel, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Controls in scrollable frame
        self.sliders = {}
        
        # Black Circle Detection
        self._create_section(scrollable_frame, "🔍 Black Circle Detection")
        self._create_slider(scrollable_frame, "Black Threshold", "black_threshold", 0, 255, self.circle_params.black_threshold)
        self._create_slider(scrollable_frame, "Min Area (×100)", "min_area", 1, 500, self.circle_params.min_area // 100)
        self._create_slider(scrollable_frame, "Max Area (×100)", "max_area", 1, 1000, self.circle_params.max_area // 100)
        self._create_slider(scrollable_frame, "Min Circularity %", "min_circularity", 0, 100, int(self.circle_params.min_circularity * 100))
        
        # Adaptive Threshold
        self._create_section(scrollable_frame, "🌓 Adaptive Threshold")
        self._create_checkbox(scrollable_frame, "Use Adaptive Threshold", "use_adaptive", self.circle_params.use_adaptive)
        self._create_slider(scrollable_frame, "Adaptive Block Size", "adaptive_block", 3, 101, self.circle_params.adaptive_block_size)
        self._create_slider(scrollable_frame, "Adaptive C", "adaptive_c", 0, 50, self.circle_params.adaptive_c)
        
        # Filters
        self._create_section(scrollable_frame, "🎛️ Image Filters")
        self._create_slider(scrollable_frame, "Blur", "blur", 1, 255, self.filter_params.blur_kernel)
        self._create_slider(scrollable_frame, "Contrast (×100)", "contrast", 10, 300, int(self.filter_params.contrast * 100))
        self._create_slider(scrollable_frame, "Saturation (×100)", "saturation", 10, 500, int(self.filter_params.saturation * 100))
        
        # Morphology
        self._create_section(scrollable_frame, "🔬 Morphological Operations")
        self._create_slider(scrollable_frame, "Erode", "erode", 0, 10, self.filter_params.erode_iterations)
        self._create_slider(scrollable_frame, "Dilate", "dilate", 0, 10, self.filter_params.dilate_iterations)
        
        # Action buttons
        button_frame = tk.Frame(right_panel, bg="#1e1e1e")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=15)
        
        tk.Button(
            button_frame,
            text="💾 Save Configuration",
            command=self._save_config,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            height=2
        ).pack(fill=tk.X, pady=5)
        
        tk.Button(
            button_frame,
            text="� Load Configuration",
            command=self._load_config_from_file,
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda",
            height=2
        ).pack(fill=tk.X, pady=5)
        
        tk.Button(
            button_frame,
            text="�🔄 Reset to Defaults",
            command=self._reset_params,
            font=("Arial", 12, "bold"),
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            height=2
        ).pack(fill=tk.X, pady=5)
        
        tk.Button(
            button_frame,
            text="❌ Close",
            command=self.root.quit,
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            activebackground="#da190b",
            height=2
        ).pack(fill=tk.X, pady=5)
    
    def _create_section(self, parent, title):
        """Create a section header."""
        frame = tk.Frame(parent, bg="#1e1e1e")
        frame.pack(fill=tk.X, padx=15, pady=(20, 5))
        
        tk.Label(
            frame,
            text=title,
            font=("Arial", 12, "bold"),
            bg="#1e1e1e",
            fg="#4CAF50"
        ).pack(anchor="w")
        
        tk.Frame(frame, height=2, bg="#4CAF50").pack(fill=tk.X, pady=(5, 0))
    
    def _create_slider(self, parent, label, key, min_val, max_val, default):
        """Create a labeled slider."""
        frame = tk.Frame(parent, bg="#1e1e1e")
        frame.pack(fill=tk.X, padx=15, pady=5)
        
        # Label and value
        label_frame = tk.Frame(frame, bg="#1e1e1e")
        label_frame.pack(fill=tk.X)
        
        tk.Label(
            label_frame,
            text=label,
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="white"
        ).pack(side=tk.LEFT)
        
        value_label = tk.Label(
            label_frame,
            text=str(default),
            font=("Arial", 10, "bold"),
            bg="#1e1e1e",
            fg="#4CAF50"
        )
        value_label.pack(side=tk.RIGHT)
        
        # Slider
        slider = tk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            orient=tk.HORIZONTAL,
            bg="#2b2b2b",
            fg="white",
            troughcolor="#424242",
            highlightthickness=0,
            activebackground="#4CAF50",
            showvalue=0,
            command=lambda v: self._on_slider_change(key, v, value_label)
        )
        slider.set(default)
        slider.pack(fill=tk.X)
        
        self.sliders[key] = (slider, value_label)
    
    def _create_checkbox(self, parent, label, key, default):
        """Create a checkbox."""
        frame = tk.Frame(parent, bg="#1e1e1e")
        frame.pack(fill=tk.X, padx=15, pady=5)
        
        var = tk.BooleanVar(value=default)
        
        cb = tk.Checkbutton(
            frame,
            text=label,
            variable=var,
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="white",
            selectcolor="#2b2b2b",
            activebackground="#1e1e1e",
            activeforeground="white",
            command=lambda: self._on_checkbox_change(key, var)
        )
        cb.pack(anchor="w")
        
        self.sliders[key] = (var, None)
    
    def _on_slider_change(self, key, value, label):
        """Handle slider change."""
        value = int(float(value))
        label.config(text=str(value))
        
        # Update parameters
        if key == "black_threshold":
            self.circle_params.black_threshold = value
        elif key == "min_area":
            self.circle_params.min_area = value * 100
        elif key == "max_area":
            self.circle_params.max_area = value * 100
        elif key == "min_circularity":
            self.circle_params.min_circularity = value / 100.0
        elif key == "adaptive_block":
            self.circle_params.adaptive_block_size = max(3, value)
        elif key == "adaptive_c":
            self.circle_params.adaptive_c = value
        elif key == "blur":
            self.filter_params.blur_kernel = max(1, value)
        elif key == "contrast":
            self.filter_params.contrast = value / 100.0
        elif key == "saturation":
            self.filter_params.saturation = value / 100.0
        elif key == "erode":
            self.filter_params.erode_iterations = value
        elif key == "dilate":
            self.filter_params.dilate_iterations = value
        
        self._update_display()
    
    def _on_checkbox_change(self, key, var):
        """Handle checkbox change."""
        if key == "use_adaptive":
            self.circle_params.use_adaptive = var.get()
        
        self._update_display()
    
    def _update_display(self):
        """Update all image displays."""
        if not self.images:
            return
        
        frame = self.images[self.current_image_index].copy()
        
        # Process
        processed = preprocess_frame(frame, self.filter_params)
        gray = convert_to_grayscale(processed)
        mask = create_black_mask(gray, self.circle_params)
        mask_morphed = apply_morphological_operations(
            mask.copy(),
            self.filter_params.erode_iterations,
            self.filter_params.dilate_iterations
        )
        circles = detect_black_circles(mask_morphed, self.circle_params)
        
        # Draw detections
        display_frame = frame.copy()
        display_frame = draw_detected_circles(display_frame, circles)
        
        # Update canvases
        self._update_canvas(self.canvas_original, display_frame)
        self._update_canvas(self.canvas_filtered, processed)
        self._update_canvas(self.canvas_gray, cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))
        self._update_canvas(self.canvas_mask, cv2.cvtColor(mask_morphed, cv2.COLOR_GRAY2BGR))
        
        # Update info
        self.info_label.config(text=f"✓ Circles detected: {len(circles)}")
        img_name = Path(self.image_paths[self.current_image_index]).name if self.image_paths else ""
        self.image_label.config(text=f"Image {self.current_image_index + 1}/{len(self.images)}: {img_name}")
    
    def _update_canvas(self, canvas, img):
        """Update a canvas with an image."""
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (300, 225))
        img = Image.fromarray(img)
        photo = ImageTk.PhotoImage(img)
        canvas.config(image=photo)
        canvas.image = photo
    
    def _prev_image(self):
        """Go to previous image."""
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self._update_display()
    
    def _next_image(self):
        """Go to next image."""
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self._update_display()
    
    def _reset_params(self):
        """Reset to default parameters."""
        if messagebox.askyesno("Reset", "Reset all parameters to defaults?"):
            self.filter_params = FilterParams()
            self.circle_params = BlackCircleParams()
            
            # Update sliders
            self.sliders["black_threshold"][0].set(self.circle_params.black_threshold)
            self.sliders["min_area"][0].set(self.circle_params.min_area // 100)
            self.sliders["max_area"][0].set(self.circle_params.max_area // 100)
            self.sliders["min_circularity"][0].set(int(self.circle_params.min_circularity * 100))
            self.sliders["use_adaptive"][0].set(self.circle_params.use_adaptive)
            self.sliders["adaptive_block"][0].set(self.circle_params.adaptive_block_size)
            self.sliders["adaptive_c"][0].set(self.circle_params.adaptive_c)
            self.sliders["blur"][0].set(self.filter_params.blur_kernel)
            self.sliders["contrast"][0].set(int(self.filter_params.contrast * 100))
            self.sliders["saturation"][0].set(int(self.filter_params.saturation * 100))
            self.sliders["erode"][0].set(self.filter_params.erode_iterations)
            self.sliders["dilate"][0].set(self.filter_params.dilate_iterations)
            
            self._update_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = CalibrationGUI(root)
    root.mainloop()
