"""
Utility functions for image processing and black circle detection.
This module provides helper functions for preprocessing, filtering,
and object detection in the treadmill speed tracker system.
Detects black filled circles drawn on Post-it notes.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
import math


@dataclass
class DetectedObject:
    """Represents a detected object with its properties."""
    contour: np.ndarray
    bounding_box: Tuple[int, int, int, int]  # (x, y, width, height)
    centroid: Tuple[int, int]  # (cx, cy)
    area: float
    circularity: float = 0.0  # How circular the object is (1.0 = perfect circle)


@dataclass
class FilterParams:
    """Parameters for image filtering."""
    blur_kernel: int = 5
    contrast: float = 1.0
    saturation: float = 1.0
    erode_iterations: int = 1
    dilate_iterations: int = 2


@dataclass
class BlackCircleParams:
    """Parameters for black circle detection."""
    # Threshold for black detection (0-255, lower = darker)
    black_threshold: int = 80
    # Minimum area for valid circles
    min_area: int = 500
    # Maximum area for valid circles
    max_area: int = 50000
    # Minimum circularity (0.0 to 1.0, where 1.0 is perfect circle)
    min_circularity: float = 0.6
    # Use adaptive threshold instead of simple threshold
    use_adaptive: bool = False
    # Block size for adaptive threshold (must be odd)
    adaptive_block_size: int = 11
    # Constant subtracted from mean in adaptive threshold
    adaptive_c: int = 2


def apply_gaussian_blur(frame: np.ndarray, kernel_size: int) -> np.ndarray:
    """
    Apply Gaussian blur to reduce noise in the image.
    
    Args:
        frame: Input BGR image
        kernel_size: Size of the Gaussian kernel (must be odd)
        
    Returns:
        Blurred image
    """
    # Ensure kernel size is odd and positive
    kernel_size = max(1, kernel_size)
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)


def adjust_contrast(frame: np.ndarray, contrast: float) -> np.ndarray:
    """
    Adjust the contrast of an image.
    
    Args:
        frame: Input BGR image
        contrast: Contrast multiplier (1.0 = no change)
        
    Returns:
        Contrast-adjusted image
    """
    return cv2.convertScaleAbs(frame, alpha=contrast, beta=0)


def adjust_saturation(frame: np.ndarray, saturation: float) -> np.ndarray:
    """
    Adjust the saturation of an image.
    
    Args:
        frame: Input BGR image
        saturation: Saturation multiplier (1.0 = no change)
        
    Returns:
        Saturation-adjusted image
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
    hsv = hsv.astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def convert_to_grayscale(frame: np.ndarray) -> np.ndarray:
    """
    Convert BGR image to grayscale.
    
    Args:
        frame: Input BGR image
        
    Returns:
        Grayscale image
    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def create_black_mask(
    gray_frame: np.ndarray,
    params: BlackCircleParams
) -> np.ndarray:
    """
    Create a binary mask to isolate black regions.
    
    Args:
        gray_frame: Input grayscale image
        params: Black circle detection parameters
        
    Returns:
        Binary mask where black regions are white
    """
    if params.use_adaptive:
        # Adaptive threshold for varying lighting conditions
        block_size = params.adaptive_block_size
        if block_size % 2 == 0:
            block_size += 1
        
        # Adaptive threshold inverted (black becomes white)
        mask = cv2.adaptiveThreshold(
            gray_frame,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            block_size,
            params.adaptive_c
        )
    else:
        # Simple threshold - pixels below threshold are considered black
        _, mask = cv2.threshold(
            gray_frame,
            params.black_threshold,
            255,
            cv2.THRESH_BINARY_INV
        )
    
    return mask


def calculate_circularity(contour: np.ndarray) -> float:
    """
    Calculate the circularity of a contour.
    Circularity = 4 * pi * area / perimeter^2
    A perfect circle has circularity = 1.0
    
    Args:
        contour: Input contour
        
    Returns:
        Circularity value (0.0 to 1.0)
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    if perimeter == 0:
        return 0.0
    
    circularity = (4 * math.pi * area) / (perimeter * perimeter)
    return min(circularity, 1.0)  # Cap at 1.0 due to discretization


def detect_black_circles(
    mask: np.ndarray,
    params: BlackCircleParams
) -> List[DetectedObject]:
    """
    Detect black circles in a binary mask.
    Filters by area and circularity to identify valid circles.
    
    Args:
        mask: Binary mask where black regions are white
        params: Detection parameters
        
    Returns:
        List of DetectedObject instances representing detected circles
    """
    contours = find_contours(mask)
    detected_circles = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by area
        if area < params.min_area or area > params.max_area:
            continue
        
        # Calculate circularity
        circularity = calculate_circularity(contour)
        
        # Filter by circularity
        if circularity < params.min_circularity:
            continue
        
        # Get centroid
        centroid = get_contour_centroid(contour)
        
        if centroid is not None:
            x, y, w, h = cv2.boundingRect(contour)
            
            detected_circles.append(DetectedObject(
                contour=contour,
                bounding_box=(x, y, w, h),
                centroid=centroid,
                area=area,
                circularity=circularity
            ))
    
    # Sort by circularity (most circular first)
    detected_circles.sort(key=lambda obj: obj.circularity, reverse=True)
    
    return detected_circles


def process_frame_for_black_circles(
    frame: np.ndarray,
    filter_params: FilterParams,
    circle_params: BlackCircleParams
) -> Tuple[np.ndarray, List[DetectedObject]]:
    """
    Complete processing pipeline for black circle detection.
    
    Args:
        frame: Input BGR image
        filter_params: Filtering parameters
        circle_params: Black circle detection parameters
        
    Returns:
        Tuple of (processed mask, list of detected circles)
    """
    # Preprocess the frame
    processed = preprocess_frame(frame, filter_params)
    
    # Convert to grayscale
    gray = convert_to_grayscale(processed)
    
    # Create black mask
    mask = create_black_mask(gray, circle_params)
    
    # Apply morphological operations
    mask = apply_morphological_operations(
        mask,
        filter_params.erode_iterations,
        filter_params.dilate_iterations
    )
    
    # Detect circles
    circles = detect_black_circles(mask, circle_params)
    
    return mask, circles


def apply_morphological_operations(
    mask: np.ndarray,
    erode_iterations: int = 1,
    dilate_iterations: int = 2
) -> np.ndarray:
    """
    Apply morphological operations (erode/dilate) to clean up the mask.
    
    Args:
        mask: Input binary mask
        erode_iterations: Number of erosion iterations
        dilate_iterations: Number of dilation iterations
        
    Returns:
        Cleaned binary mask
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    # Erode to remove small noise
    if erode_iterations > 0:
        mask = cv2.erode(mask, kernel, iterations=erode_iterations)
    
    # Dilate to restore object size and fill holes
    if dilate_iterations > 0:
        mask = cv2.dilate(mask, kernel, iterations=dilate_iterations)
    
    return mask


def find_contours(mask: np.ndarray) -> List[np.ndarray]:
    """
    Find contours in a binary mask.
    
    Args:
        mask: Input binary mask
        
    Returns:
        List of contours found
    """
    contours, _ = cv2.findContours(
        mask, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    return list(contours)


def get_contour_centroid(contour: np.ndarray) -> Optional[Tuple[int, int]]:
    """
    Calculate the centroid of a contour using image moments.
    
    Args:
        contour: Input contour
        
    Returns:
        Tuple (cx, cy) or None if moments are invalid
    """
    moments = cv2.moments(contour)
    
    if moments["m00"] > 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        return (cx, cy)
    
    return None


def detect_objects(
    mask: np.ndarray,
    min_area: float = 500.0
) -> List[DetectedObject]:
    """
    Detect objects in a binary mask and extract their properties.
    
    Args:
        mask: Input binary mask
        min_area: Minimum contour area to consider valid
        
    Returns:
        List of DetectedObject instances
    """
    contours = find_contours(mask)
    detected_objects = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if area >= min_area:
            centroid = get_contour_centroid(contour)
            
            if centroid is not None:
                x, y, w, h = cv2.boundingRect(contour)
                
                detected_objects.append(DetectedObject(
                    contour=contour,
                    bounding_box=(x, y, w, h),
                    centroid=centroid,
                    area=area
                ))
    
    # Sort by area (largest first)
    detected_objects.sort(key=lambda obj: obj.area, reverse=True)
    
    return detected_objects


def preprocess_frame(
    frame: np.ndarray,
    filter_params: FilterParams
) -> np.ndarray:
    """
    Apply all preprocessing steps to a frame.
    
    Args:
        frame: Input BGR image
        filter_params: Filtering parameters
        
    Returns:
        Preprocessed BGR image
    """
    # Apply contrast adjustment
    processed = adjust_contrast(frame, filter_params.contrast)
    
    # Apply saturation adjustment
    processed = adjust_saturation(processed, filter_params.saturation)
    
    # Apply Gaussian blur
    processed = apply_gaussian_blur(processed, filter_params.blur_kernel)
    
    return processed


def draw_bounding_box(
    frame: np.ndarray,
    bbox: Tuple[int, int, int, int],
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """
    Draw a bounding box on the frame.
    
    Args:
        frame: Input BGR image
        bbox: Bounding box (x, y, width, height)
        color: BGR color tuple
        thickness: Line thickness
        
    Returns:
        Frame with bounding box drawn
    """
    x, y, w, h = bbox
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
    return frame


def draw_centroid(
    frame: np.ndarray,
    centroid: Tuple[int, int],
    color: Tuple[int, int, int] = (0, 0, 255),
    radius: int = 5
) -> np.ndarray:
    """
    Draw a centroid point on the frame.
    
    Args:
        frame: Input BGR image
        centroid: Center point (x, y)
        color: BGR color tuple
        radius: Circle radius
        
    Returns:
        Frame with centroid drawn
    """
    cv2.circle(frame, centroid, radius, color, -1)
    return frame


def draw_virtual_line(
    frame: np.ndarray,
    line_x: int,
    color: Tuple[int, int, int] = (255, 0, 255),
    thickness: int = 2
) -> np.ndarray:
    """
    Draw a vertical virtual line on the frame.
    
    Args:
        frame: Input BGR image
        line_x: X coordinate of the vertical line
        color: BGR color tuple
        thickness: Line thickness
        
    Returns:
        Frame with virtual line drawn
    """
    height = frame.shape[0]
    cv2.line(frame, (line_x, 0), (line_x, height), color, thickness)
    return frame


def draw_text(
    frame: np.ndarray,
    text: str,
    position: Tuple[int, int],
    font_scale: float = 1.0,
    color: Tuple[int, int, int] = (255, 255, 255),
    thickness: int = 2,
    background: bool = True
) -> np.ndarray:
    """
    Draw text on the frame with optional background.
    
    Args:
        frame: Input BGR image
        text: Text to display
        position: Top-left position (x, y)
        font_scale: Font scale factor
        color: BGR text color
        thickness: Text thickness
        background: Whether to draw a background rectangle
        
    Returns:
        Frame with text drawn
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    if background:
        # Get text size for background rectangle
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        # Draw background rectangle
        x, y = position
        cv2.rectangle(
            frame,
            (x - 5, y - text_height - 10),
            (x + text_width + 5, y + baseline),
            (0, 0, 0),
            -1
        )
    
    cv2.putText(frame, text, position, font, font_scale, color, thickness)
    return frame


def draw_detected_circles(
    frame: np.ndarray,
    circles: List[DetectedObject],
    bbox_color: Tuple[int, int, int] = (0, 255, 0),
    centroid_color: Tuple[int, int, int] = (0, 0, 255),
    show_info: bool = True
) -> np.ndarray:
    """
    Draw all detected circles on the frame with circularity info.
    
    Args:
        frame: Input BGR image
        circles: List of detected circle objects
        bbox_color: Color for bounding boxes
        centroid_color: Color for centroids
        show_info: Whether to show circularity percentage
        
    Returns:
        Frame with all circles drawn
    """
    for i, obj in enumerate(circles):
        frame = draw_bounding_box(frame, obj.bounding_box, bbox_color)
        frame = draw_centroid(frame, obj.centroid, centroid_color, radius=8)
        
        if show_info:
            x, y, w, h = obj.bounding_box
            info_text = f"C:{obj.circularity:.0%}"
            cv2.putText(
                frame, info_text,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 0), 1
            )
    
    return frame


def draw_detected_objects(
    frame: np.ndarray,
    objects: List[DetectedObject],
    bbox_color: Tuple[int, int, int] = (0, 255, 0),
    centroid_color: Tuple[int, int, int] = (0, 0, 255)
) -> np.ndarray:
    """
    Draw all detected objects on the frame.
    
    Args:
        frame: Input BGR image
        objects: List of detected objects
        bbox_color: Color for bounding boxes
        centroid_color: Color for centroids
        
    Returns:
        Frame with all objects drawn
    """
    for obj in objects:
        frame = draw_bounding_box(frame, obj.bounding_box, bbox_color)
        frame = draw_centroid(frame, obj.centroid, centroid_color)
    
    return frame
