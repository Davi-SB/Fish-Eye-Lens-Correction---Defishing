"""
Main script for treadmill speed estimation.
Detects black circles drawn on Post-it notes and calculates speed based 
on the time interval between circles crossing a virtual line.
"""

import cv2
import numpy as np
import time
from enum import Enum
from typing import Optional, Tuple, List
from dataclasses import dataclass

from utils import (
    FilterParams,
    BlackCircleParams,
    DetectedObject,
    process_frame_for_black_circles,
    draw_detected_circles,
    draw_virtual_line,
    draw_text
)
from calibrador import load_config_from_file, CONFIG_FILE


# =============================================================================
# CONFIGURATION - Adjust these values according to your setup
# =============================================================================

# Real distance between markers in meters (or your preferred unit)
REAL_DISTANCE_BETWEEN_MARKERS: float = 0.30  # 30 cm = 0.30 m

# Video source: 0 for webcam, or path to video file
VIDEO_SOURCE = 0

# Virtual line position as percentage of frame width (0.0 to 1.0)
# 0.5 = center of frame
VIRTUAL_LINE_POSITION: float = 0.5

# Minimum time between detections to prevent double-counting (seconds)
MIN_TIME_BETWEEN_DETECTIONS: float = 0.1

# Number of speed readings to average for smoother display
SPEED_AVERAGING_WINDOW: int = 5

# =============================================================================


class CrossingState(Enum):
    """States for the crossing detection state machine."""
    WAITING_FOR_MARKER_A = 1  # Waiting for first marker to cross
    WAITING_FOR_MARKER_B = 2  # First marker crossed, waiting for second


@dataclass
class SpeedCalculator:
    """
    Handles the speed calculation logic based on marker crossing events.
    
    The calculator works in cycles:
    1. Detect when Marker A (black circle) crosses the virtual line (start timer)
    2. Detect when Marker B (black circle) crosses the virtual line (stop timer)
    3. Calculate speed and reset for next cycle
    """
    
    real_distance: float  # Distance between markers in meters
    min_detection_interval: float = 0.1  # Minimum time between detections
    averaging_window: int = 5  # Number of readings to average
    
    def __post_init__(self):
        """Initialize internal state."""
        self.state = CrossingState.WAITING_FOR_MARKER_A
        self.t_start: Optional[float] = None
        self.last_detection_time: float = 0.0
        self.last_centroid_x: Optional[int] = None
        self.speed_history: List[float] = []
        self.current_speed: float = 0.0
        self.crossing_count: int = 0
    
    def _check_line_crossing(
        self,
        centroid_x: int,
        line_x: int,
        previous_x: Optional[int]
    ) -> bool:
        """
        Check if an object has crossed the virtual line.
        
        Args:
            centroid_x: Current X position of centroid
            line_x: X position of virtual line
            previous_x: Previous X position of centroid
            
        Returns:
            True if crossing detected
        """
        if previous_x is None:
            return False
        
        # Check if line was crossed (object moved from one side to the other)
        crossed_left_to_right = previous_x < line_x <= centroid_x
        crossed_right_to_left = previous_x > line_x >= centroid_x
        
        return crossed_left_to_right or crossed_right_to_left
    
    def _calculate_speed(self, delta_time: float) -> float:
        """
        Calculate speed from time difference.
        
        Args:
            delta_time: Time between two crossings in seconds
            
        Returns:
            Speed in meters per second
        """
        if delta_time <= 0:
            return 0.0
        
        return self.real_distance / delta_time
    
    def _add_speed_reading(self, speed: float) -> None:
        """
        Add a new speed reading and update the average.
        
        Args:
            speed: New speed reading
        """
        self.speed_history.append(speed)
        
        # Keep only the most recent readings
        if len(self.speed_history) > self.averaging_window:
            self.speed_history.pop(0)
        
        # Calculate moving average
        self.current_speed = sum(self.speed_history) / len(self.speed_history)
    
    def update(
        self,
        detected_circles: List[DetectedObject],
        line_x: int,
        current_time: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Update the speed calculator with new detection data.
        
        Args:
            detected_circles: List of detected black circles in current frame
            line_x: X position of virtual line
            current_time: Current timestamp
            
        Returns:
            Tuple of (crossing_detected, event_message)
        """
        if not detected_circles:
            self.last_centroid_x = None
            return False, None
        
        # Use the most circular detected object (most reliable marker)
        main_circle = detected_circles[0]
        centroid_x = main_circle.centroid[0]
        
        # Check minimum time interval
        time_since_last = current_time - self.last_detection_time
        if time_since_last < self.min_detection_interval:
            self.last_centroid_x = centroid_x
            return False, None
        
        # Check for line crossing
        crossing_detected = self._check_line_crossing(
            centroid_x, line_x, self.last_centroid_x
        )
        
        event_message = None
        
        if crossing_detected:
            self.crossing_count += 1
            
            if self.state == CrossingState.WAITING_FOR_MARKER_A:
                # First marker crossed - start timer
                self.t_start = current_time
                self.state = CrossingState.WAITING_FOR_MARKER_B
                self.last_detection_time = current_time
                event_message = f"Circle A crossed - Timer started (Circularity: {main_circle.circularity:.0%})"
                
            elif self.state == CrossingState.WAITING_FOR_MARKER_B:
                # Second marker crossed - calculate speed
                if self.t_start is not None:
                    delta_time = current_time - self.t_start
                    speed = self._calculate_speed(delta_time)
                    self._add_speed_reading(speed)
                    event_message = f"Circle B crossed - Speed: {speed:.3f} m/s (dt={delta_time:.3f}s)"
                
                # Reset for next cycle
                self.state = CrossingState.WAITING_FOR_MARKER_A
                self.t_start = None
                self.last_detection_time = current_time
        
        self.last_centroid_x = centroid_x
        return crossing_detected, event_message
    
    def get_speed_ms(self) -> float:
        """Get current speed in meters per second."""
        return self.current_speed
    
    def get_speed_kmh(self) -> float:
        """Get current speed in kilometers per hour."""
        return self.current_speed * 3.6
    
    def get_state_string(self) -> str:
        """Get human-readable state string."""
        if self.state == CrossingState.WAITING_FOR_MARKER_A:
            return "Waiting for Circle A"
        else:
            return "Waiting for Circle B"
    
    def reset(self) -> None:
        """Reset the calculator to initial state."""
        self.state = CrossingState.WAITING_FOR_MARKER_A
        self.t_start = None
        self.last_detection_time = 0.0
        self.last_centroid_x = None
        self.speed_history.clear()
        self.current_speed = 0.0
        self.crossing_count = 0


class TreadmillSpeedTracker:
    """
    Main application class for treadmill speed tracking using black circle detection.
    """
    
    def __init__(
        self,
        video_source=VIDEO_SOURCE,
        config_file: str = CONFIG_FILE,
        real_distance: float = REAL_DISTANCE_BETWEEN_MARKERS,
        line_position: float = VIRTUAL_LINE_POSITION
    ):
        """
        Initialize the speed tracker.
        
        Args:
            video_source: Camera index or video file path
            config_file: Path to calibration configuration file
            real_distance: Real distance between markers in meters
            line_position: Virtual line position as fraction of frame width
        """
        self.video_source = video_source
        self.line_position = line_position
        
        # Load calibration configuration
        config = load_config_from_file(config_file)
        self.filter_params: FilterParams = config["filter_params"]
        self.circle_params: BlackCircleParams = config["circle_params"]
        
        # Initialize speed calculator
        self.speed_calculator = SpeedCalculator(
            real_distance=real_distance,
            min_detection_interval=MIN_TIME_BETWEEN_DETECTIONS,
            averaging_window=SPEED_AVERAGING_WINDOW
        )
        
        # Video capture
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_width: int = 0
        self.frame_height: int = 0
        self.line_x: int = 0
        
        # Display options
        self.show_mask = False
    
    def _initialize_capture(self) -> bool:
        """
        Initialize video capture and frame dimensions.
        
        Returns:
            True if successful
        """
        self.cap = cv2.VideoCapture(self.video_source)
        
        if not self.cap.isOpened():
            print(f"[ERROR] Could not open video source: {self.video_source}")
            return False
        
        # Get frame dimensions
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate virtual line position
        self.line_x = int(self.frame_width * self.line_position)
        
        print(f"[INFO] Video initialized: {self.frame_width}x{self.frame_height}")
        print(f"[INFO] Virtual line at X={self.line_x}")
        
        return True
    
    def _draw_overlay(
        self,
        frame: np.ndarray,
        circles: List[DetectedObject]
    ) -> np.ndarray:
        """
        Draw all visual overlays on the frame.
        
        Args:
            frame: Input frame
            circles: Detected black circles
            
        Returns:
            Frame with overlays
        """
        # Draw detected circles
        frame = draw_detected_circles(frame, circles)
        
        # Draw virtual line
        frame = draw_virtual_line(frame, self.line_x, color=(255, 0, 255), thickness=3)
        
        # Draw speed information
        speed_ms = self.speed_calculator.get_speed_ms()
        speed_kmh = self.speed_calculator.get_speed_kmh()
        
        speed_text = f"Speed: {speed_ms:.3f} m/s ({speed_kmh:.2f} km/h)"
        frame = draw_text(frame, speed_text, (10, 40), font_scale=1.0, color=(0, 255, 255))
        
        # Draw state information
        state_text = f"State: {self.speed_calculator.get_state_string()}"
        frame = draw_text(frame, state_text, (10, 80), font_scale=0.7, color=(255, 255, 255))
        
        # Draw crossing count
        count_text = f"Crossings: {self.speed_calculator.crossing_count}"
        frame = draw_text(frame, count_text, (10, 115), font_scale=0.7, color=(255, 255, 255))
        
        # Draw circles detected count
        obj_text = f"Circles: {len(circles)}"
        frame = draw_text(frame, obj_text, (10, 150), font_scale=0.7, color=(255, 255, 255))
        
        # Draw detection parameters
        thresh_text = f"Threshold: {self.circle_params.black_threshold} | Circularity: {self.circle_params.min_circularity:.0%}"
        frame = draw_text(frame, thresh_text, (10, 185), font_scale=0.5, color=(200, 200, 200))
        
        # Draw instructions
        instructions = "Press 'M' for mask | 'R' to reset | 'Q' to quit"
        frame = draw_text(
            frame, instructions,
            (10, self.frame_height - 20),
            font_scale=0.5,
            color=(200, 200, 200)
        )
        
        return frame
    
    def run(self) -> None:
        """Run the main tracking loop."""
        if not self._initialize_capture():
            return
        
        print("\n" + "=" * 60)
        print("TREADMILL SPEED TRACKER - BLACK CIRCLE DETECTION")
        print("=" * 60)
        print(f"Distance between markers: {REAL_DISTANCE_BETWEEN_MARKERS} m")
        print(f"Virtual line position: {self.line_position * 100:.0f}%")
        print(f"Black threshold: {self.circle_params.black_threshold}")
        print(f"Min circularity: {self.circle_params.min_circularity:.0%}")
        print("\nControls:")
        print("  M - Toggle mask view")
        print("  R - Reset speed calculator")
        print("  Q - Quit")
        print("=" * 60 + "\n")
        
        cv2.namedWindow("Treadmill Speed Tracker", cv2.WINDOW_NORMAL)
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                # If video file, restart from beginning
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            current_time = time.time()
            
            # Process frame and detect black circles
            mask, circles = process_frame_for_black_circles(
                frame,
                self.filter_params,
                self.circle_params
            )
            
            # Update speed calculator
            crossing_detected, event_message = self.speed_calculator.update(
                circles, self.line_x, current_time
            )
            
            # Print event messages
            if event_message:
                print(f"[EVENT] {event_message}")
            
            # Draw overlays
            display_frame = self._draw_overlay(frame, circles)
            
            # Show mask if enabled
            if self.show_mask:
                mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                display_frame = np.hstack([display_frame, mask_colored])
            
            # Display
            cv2.imshow("Treadmill Speed Tracker", display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                break
            elif key == ord('m'):  # Toggle mask
                self.show_mask = not self.show_mask
                print(f"[INFO] Mask view: {'ON' if self.show_mask else 'OFF'}")
            elif key == ord('r'):  # Reset
                self.speed_calculator.reset()
                print("[INFO] Speed calculator reset")
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        
        # Print final statistics
        print("\n" + "=" * 60)
        print("SESSION STATISTICS")
        print("=" * 60)
        print(f"Total crossings detected: {self.speed_calculator.crossing_count}")
        print(f"Final average speed: {self.speed_calculator.get_speed_ms():.3f} m/s")
        print(f"Final average speed: {self.speed_calculator.get_speed_kmh():.2f} km/h")
        print("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Treadmill Speed Tracker - Black Circle Detection"
    )
    parser.add_argument(
        "--source", "-s",
        type=str,
        default=str(VIDEO_SOURCE),
        help=f"Video source: camera index or file path (default: {VIDEO_SOURCE})"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=CONFIG_FILE,
        help=f"Calibration config file (default: {CONFIG_FILE})"
    )
    parser.add_argument(
        "--distance", "-d",
        type=float,
        default=REAL_DISTANCE_BETWEEN_MARKERS,
        help=f"Real distance between markers in meters (default: {REAL_DISTANCE_BETWEEN_MARKERS})"
    )
    parser.add_argument(
        "--line", "-l",
        type=float,
        default=VIRTUAL_LINE_POSITION,
        help=f"Virtual line position as fraction of width (default: {VIRTUAL_LINE_POSITION})"
    )
    
    args = parser.parse_args()
    
    # Parse video source
    try:
        video_source = int(args.source)
    except ValueError:
        video_source = args.source
    
    # Create and run tracker
    tracker = TreadmillSpeedTracker(
        video_source=video_source,
        config_file=args.config,
        real_distance=args.distance,
        line_position=args.line
    )
    tracker.run()


if __name__ == "__main__":
    main()
