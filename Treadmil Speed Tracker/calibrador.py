"""
Calibration tool with GUI for adjusting black circle detection parameters.
Uses OpenCV trackbars for real-time parameter adjustment and allows saving
configurations to a JSON file.

Detects black filled circles drawn on Post-it notes.
"""

import cv2
import numpy as np
import json
import glob
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import asdict

from utils import (
    FilterParams,
    BlackCircleParams,
    preprocess_frame,
    convert_to_grayscale,
    create_black_mask,
    apply_morphological_operations,
    detect_black_circles,
    draw_detected_circles,
    draw_text
)


# Default configuration file path
CONFIG_FILE = "calibration_config.json"

# Default images folder
IMAGES_FOLDER = "images"

# Supported image extensions
IMAGE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.webp"]

# Window names
WINDOW_MAIN = "Calibration - Original + Detection"
WINDOW_FILTERED = "Calibration - Filtered Preview"
WINDOW_GRAYSCALE = "Calibration - Grayscale"
WINDOW_MASK = "Calibration - Black Mask"
WINDOW_CONTROLS = "Controls"


class Calibrator:
    """
    GUI-based calibration tool for adjusting black circle detection parameters.
    Works with images from a folder.
    """
    
    def __init__(
        self,
        images_folder: str = IMAGES_FOLDER,
        config_file: str = CONFIG_FILE
    ):
        """
        Initialize the calibrator.
        
        Args:
            images_folder: Path to folder containing images
            config_file: Path to save/load configuration
        """
        self.images_folder = Path(images_folder)
        self.config_file = Path(config_file)
        
        # Load images from folder
        self.images: List[np.ndarray] = []
        self.image_paths: List[str] = []
        self.current_image_index: int = 0
        self._load_images()
        
        # Initialize parameters with defaults or loaded values
        self.filter_params = FilterParams()
        self.circle_params = BlackCircleParams()
        
        # Load existing configuration if available
        self.load_config()
        
        # Trackbar values (will be synced with actual params)
        self._init_trackbar_values()
    
    def _load_images(self) -> None:
        """Load all images from the images folder."""
        if not self.images_folder.exists():
            print(f"[WARNING] Images folder not found: {self.images_folder}")
            print(f"[INFO] Creating folder: {self.images_folder}")
            self.images_folder.mkdir(parents=True, exist_ok=True)
            return
        
        # Find all image files
        for ext in IMAGE_EXTENSIONS:
            pattern = str(self.images_folder / ext)
            self.image_paths.extend(glob.glob(pattern))
        
        # Sort paths for consistent ordering
        self.image_paths.sort()
        
        # Load images
        for path in self.image_paths:
            img = cv2.imread(path)
            if img is not None:
                self.images.append(img)
            else:
                print(f"[WARNING] Could not load image: {path}")
        
        if self.images:
            print(f"[INFO] Loaded {len(self.images)} images from: {self.images_folder}")
        else:
            print(f"[WARNING] No images found in: {self.images_folder}")
    
    def _init_trackbar_values(self) -> None:
        """Initialize trackbar values from current parameters."""
        self.trackbar_values = {
            # Filter parameters
            "blur": self.filter_params.blur_kernel,
            "contrast": int(self.filter_params.contrast * 100),
            "saturation": int(self.filter_params.saturation * 100),
            "erode": self.filter_params.erode_iterations,
            "dilate": self.filter_params.dilate_iterations,
            
            # Black circle parameters
            "black_threshold": self.circle_params.black_threshold,
            "min_area": self.circle_params.min_area // 100,
            "max_area": self.circle_params.max_area // 100,
            "min_circularity": int(self.circle_params.min_circularity * 100),
            "use_adaptive": 1 if self.circle_params.use_adaptive else 0,
            "adaptive_block": self.circle_params.adaptive_block_size,
            "adaptive_c": self.circle_params.adaptive_c
        }
    
    def _create_trackbar_callback(self, name: str):
        """Create a callback function for a trackbar."""
        def callback(value: int) -> None:
            self.trackbar_values[name] = value
            self._update_params_from_trackbars()
        return callback
    
    def _update_params_from_trackbars(self) -> None:
        """Update parameter objects from trackbar values."""
        # Update filter parameters
        self.filter_params.blur_kernel = max(1, self.trackbar_values["blur"])
        self.filter_params.contrast = self.trackbar_values["contrast"] / 100.0
        self.filter_params.saturation = self.trackbar_values["saturation"] / 100.0
        self.filter_params.erode_iterations = self.trackbar_values["erode"]
        self.filter_params.dilate_iterations = self.trackbar_values["dilate"]
        
        # Update black circle parameters
        self.circle_params.black_threshold = self.trackbar_values["black_threshold"]
        self.circle_params.min_area = max(1, self.trackbar_values["min_area"] * 100)
        self.circle_params.max_area = max(1, self.trackbar_values["max_area"] * 100)
        self.circle_params.min_circularity = self.trackbar_values["min_circularity"] / 100.0
        self.circle_params.use_adaptive = self.trackbar_values["use_adaptive"] == 1
        self.circle_params.adaptive_block_size = max(3, self.trackbar_values["adaptive_block"])
        self.circle_params.adaptive_c = self.trackbar_values["adaptive_c"]
    
    def _create_windows(self) -> None:
        """Create OpenCV windows and trackbars."""
        # Create windows
        cv2.namedWindow(WINDOW_MAIN, cv2.WINDOW_NORMAL)
        cv2.namedWindow(WINDOW_FILTERED, cv2.WINDOW_NORMAL)
        cv2.namedWindow(WINDOW_GRAYSCALE, cv2.WINDOW_NORMAL)
        cv2.namedWindow(WINDOW_MASK, cv2.WINDOW_NORMAL)
        cv2.namedWindow(WINDOW_CONTROLS, cv2.WINDOW_NORMAL)
        
        # Resize control window
        cv2.resizeWindow(WINDOW_CONTROLS, 450, 700)
        
        # === Filter Parameters ===
        cv2.createTrackbar(
            "Blur", WINDOW_CONTROLS,
            self.trackbar_values["blur"], 255,
            self._create_trackbar_callback("blur")
        )
        cv2.createTrackbar(
            "Contrast", WINDOW_CONTROLS,
            self.trackbar_values["contrast"], 300,
            self._create_trackbar_callback("contrast")
        )
        cv2.createTrackbar(
            "Saturation", WINDOW_CONTROLS,
            self.trackbar_values["saturation"], 500,
            self._create_trackbar_callback("saturation")
        )
        cv2.createTrackbar(
            "Erode", WINDOW_CONTROLS,
            self.trackbar_values["erode"], 10,
            self._create_trackbar_callback("erode")
        )
        cv2.createTrackbar(
            "Dilate", WINDOW_CONTROLS,
            self.trackbar_values["dilate"], 10,
            self._create_trackbar_callback("dilate")
        )
        
        # === Black Circle Detection Parameters ===
        cv2.createTrackbar(
            "Black Threshold", WINDOW_CONTROLS,
            self.trackbar_values["black_threshold"], 255,
            self._create_trackbar_callback("black_threshold")
        )
        cv2.createTrackbar(
            "Min Area (x100)", WINDOW_CONTROLS,
            self.trackbar_values["min_area"], 500,
            self._create_trackbar_callback("min_area")
        )
        cv2.createTrackbar(
            "Max Area (x100)", WINDOW_CONTROLS,
            self.trackbar_values["max_area"], 1000,
            self._create_trackbar_callback("max_area")
        )
        cv2.createTrackbar(
            "Min Circularity %", WINDOW_CONTROLS,
            self.trackbar_values["min_circularity"], 100,
            self._create_trackbar_callback("min_circularity")
        )
        
        # === Adaptive Threshold Parameters ===
        cv2.createTrackbar(
            "Use Adaptive (0/1)", WINDOW_CONTROLS,
            self.trackbar_values["use_adaptive"], 1,
            self._create_trackbar_callback("use_adaptive")
        )
        cv2.createTrackbar(
            "Adaptive Block", WINDOW_CONTROLS,
            self.trackbar_values["adaptive_block"], 101,
            self._create_trackbar_callback("adaptive_block")
        )
        cv2.createTrackbar(
            "Adaptive C", WINDOW_CONTROLS,
            self.trackbar_values["adaptive_c"], 50,
            self._create_trackbar_callback("adaptive_c")
        )
    
    def save_config(self) -> None:
        """Save current configuration to JSON file."""
        config = {
            "filter_params": asdict(self.filter_params),
            "circle_params": asdict(self.circle_params)
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)
        
        print(f"[INFO] Configuration saved to: {self.config_file}")
    
    def load_config(self) -> bool:
        """
        Load configuration from JSON file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.config_file.exists():
            print(f"[INFO] No config file found. Using defaults.")
            return False
        
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            
            # Load filter parameters
            if "filter_params" in config:
                self.filter_params = FilterParams(**config["filter_params"])
            
            # Load circle parameters
            if "circle_params" in config:
                self.circle_params = BlackCircleParams(**config["circle_params"])
            
            print(f"[INFO] Configuration loaded from: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            return False
    
    def run(self) -> None:
        """Run the calibration GUI with images from folder."""
        if not self.images:
            print(f"[ERROR] No images to display. Add images to: {self.images_folder}")
            print(f"[INFO] Supported formats: {', '.join(IMAGE_EXTENSIONS)}")
            return
        
        # Create windows and trackbars
        self._create_windows()
        
        print("\n" + "=" * 60)
        print("BLACK CIRCLE CALIBRATION TOOL")
        print("=" * 60)
        print("Press 'S' to save configuration")
        print("Press 'R' to reset to defaults")
        print("Press 'N' or RIGHT ARROW for next image")
        print("Press 'P' or LEFT ARROW for previous image")
        print("Press 'Q' or ESC to quit")
        print("=" * 60)
        print("\nTips for calibration:")
        print("1. Adjust 'Black Threshold' to capture the black circle")
        print("2. Use 'Min/Max Area' to filter by circle size")
        print("3. 'Min Circularity' filters out non-circular shapes")
        print("4. Enable 'Adaptive' for varying lighting conditions")
        print("=" * 60 + "\n")
        
        while True:
            # Get current image
            frame = self.images[self.current_image_index].copy()
            
            # Preprocess frame
            processed = preprocess_frame(frame, self.filter_params)
            
            # Convert to grayscale
            gray = convert_to_grayscale(processed)
            
            # Create black mask
            mask = create_black_mask(gray, self.circle_params)
            
            # Apply morphological operations
            mask_morphed = apply_morphological_operations(
                mask.copy(),
                self.filter_params.erode_iterations,
                self.filter_params.dilate_iterations
            )
            
            # Detect circles
            circles = detect_black_circles(mask_morphed, self.circle_params)
            
            # === Draw on display frame ===
            display_frame = frame.copy()
            display_frame = draw_detected_circles(display_frame, circles)
            
            # Draw image info
            image_name = Path(self.image_paths[self.current_image_index]).name
            img_info = f"Image {self.current_image_index + 1}/{len(self.images)}: {image_name}"
            display_frame = draw_text(display_frame, img_info, (10, 30), font_scale=0.6)
            
            # Draw detection info
            info_text = f"Circles detected: {len(circles)}"
            display_frame = draw_text(display_frame, info_text, (10, 60), color=(0, 255, 255))
            
            # Draw threshold info
            thresh_mode = "Adaptive" if self.circle_params.use_adaptive else "Simple"
            thresh_text = f"Threshold: {thresh_mode} ({self.circle_params.black_threshold})"
            display_frame = draw_text(display_frame, thresh_text, (10, 95), font_scale=0.6)
            
            # Draw circularity info
            circ_text = f"Min Circularity: {self.circle_params.min_circularity:.0%}"
            display_frame = draw_text(display_frame, circ_text, (10, 125), font_scale=0.6)
            
            # Draw navigation hint
            nav_text = "[N/P] Next/Prev | [S] Save | [R] Reset | [Q] Quit"
            h = display_frame.shape[0]
            display_frame = draw_text(display_frame, nav_text, (10, h - 20), font_scale=0.5)
            
            # === Filtered preview ===
            filtered_display = processed.copy()
            filter_info = f"Blur: {self.filter_params.blur_kernel} | " \
                         f"Contrast: {self.filter_params.contrast:.2f} | " \
                         f"Saturation: {self.filter_params.saturation:.2f}"
            filtered_display = draw_text(filtered_display, "FILTERED PREVIEW", (10, 30), font_scale=0.7, color=(0, 255, 255))
            filtered_display = draw_text(filtered_display, filter_info, (10, 65), font_scale=0.6)
            morph_info = f"Erode: {self.filter_params.erode_iterations} | Dilate: {self.filter_params.dilate_iterations}"
            filtered_display = draw_text(filtered_display, morph_info, (10, 95), font_scale=0.6)
            
            # === Grayscale preview ===
            gray_display = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            gray_display = draw_text(gray_display, "GRAYSCALE", (10, 30), font_scale=0.7, color=(0, 255, 255))
            
            # === Mask preview ===
            mask_display = cv2.cvtColor(mask_morphed, cv2.COLOR_GRAY2BGR)
            mask_display = draw_text(mask_display, "BLACK MASK", (10, 30), font_scale=0.7, color=(0, 255, 255))
            
            # Show windows
            cv2.imshow(WINDOW_MAIN, display_frame)
            cv2.imshow(WINDOW_FILTERED, filtered_display)
            cv2.imshow(WINDOW_GRAYSCALE, gray_display)
            cv2.imshow(WINDOW_MASK, mask_display)
            
            # Handle keyboard input
            key = cv2.waitKey(30) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                break
            elif key == ord('s'):  # Save
                self.save_config()
            elif key == ord('r'):  # Reset
                self.filter_params = FilterParams()
                self.circle_params = BlackCircleParams()
                self._init_trackbar_values()
                self._update_trackbar_positions()
                print("[INFO] Parameters reset to defaults")
            elif key == ord('n') or key == 83 or key == 3:  # N or Right Arrow
                self.current_image_index = (self.current_image_index + 1) % len(self.images)
                print(f"[INFO] Showing image {self.current_image_index + 1}/{len(self.images)}")
            elif key == ord('p') or key == 81 or key == 2:  # P or Left Arrow
                self.current_image_index = (self.current_image_index - 1) % len(self.images)
                print(f"[INFO] Showing image {self.current_image_index + 1}/{len(self.images)}")
        
        # Cleanup
        cv2.destroyAllWindows()
    
    def _update_trackbar_positions(self) -> None:
        """Update trackbar positions to match current values."""
        cv2.setTrackbarPos("Blur", WINDOW_CONTROLS, self.trackbar_values["blur"])
        cv2.setTrackbarPos("Contrast", WINDOW_CONTROLS, self.trackbar_values["contrast"])
        cv2.setTrackbarPos("Saturation", WINDOW_CONTROLS, self.trackbar_values["saturation"])
        cv2.setTrackbarPos("Erode", WINDOW_CONTROLS, self.trackbar_values["erode"])
        cv2.setTrackbarPos("Dilate", WINDOW_CONTROLS, self.trackbar_values["dilate"])
        cv2.setTrackbarPos("Black Threshold", WINDOW_CONTROLS, self.trackbar_values["black_threshold"])
        cv2.setTrackbarPos("Min Area (x100)", WINDOW_CONTROLS, self.trackbar_values["min_area"])
        cv2.setTrackbarPos("Max Area (x100)", WINDOW_CONTROLS, self.trackbar_values["max_area"])
        cv2.setTrackbarPos("Min Circularity %", WINDOW_CONTROLS, self.trackbar_values["min_circularity"])
        cv2.setTrackbarPos("Use Adaptive (0/1)", WINDOW_CONTROLS, self.trackbar_values["use_adaptive"])
        cv2.setTrackbarPos("Adaptive Block", WINDOW_CONTROLS, self.trackbar_values["adaptive_block"])
        cv2.setTrackbarPos("Adaptive C", WINDOW_CONTROLS, self.trackbar_values["adaptive_c"])


def load_config_from_file(config_file: str = CONFIG_FILE) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Dictionary with filter_params and circle_params
    """
    config_path = Path(config_file)
    
    if not config_path.exists():
        print(f"[WARNING] Config file not found: {config_file}")
        return {
            "filter_params": FilterParams(),
            "circle_params": BlackCircleParams()
        }
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    return {
        "filter_params": FilterParams(**config.get("filter_params", {})),
        "circle_params": BlackCircleParams(**config.get("circle_params", {}))
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Black circle calibration tool for treadmill speed tracker"
    )
    parser.add_argument(
        "--images", "-i",
        type=str,
        default=IMAGES_FOLDER,
        help=f"Path to images folder (default: {IMAGES_FOLDER})"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=CONFIG_FILE,
        help=f"Configuration file path (default: {CONFIG_FILE})"
    )
    
    args = parser.parse_args()
    
    # Run calibrator
    calibrator = Calibrator(
        images_folder=args.images,
        config_file=args.config
    )
    calibrator.run()
