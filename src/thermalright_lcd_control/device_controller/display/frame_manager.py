# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

import glob
import os
import threading
import time
from threading import Timer
from typing import Tuple, Optional
from PIL import Image, ImageSequence

from thermalright_lcd_control.device_controller.display.config import BackgroundType, DisplayConfig
from thermalright_lcd_control.device_controller.metrics.cpu_metrics import CpuMetrics
from thermalright_lcd_control.device_controller.metrics.gpu_metrics import GpuMetrics
from thermalright_lcd_control.common.logging_config import get_service_logger



# Try to import OpenCV for video support
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

# Try to import window capture for iStripper and other app integration
try:
    from thermalright_lcd_control.device_controller.display.window_capture import WindowCapture
    HAS_WINDOW_CAPTURE = True
except ImportError:
    HAS_WINDOW_CAPTURE = False


class FrameManager:
    """Frame manager with real-time metrics updates and window capture support"""

    # Supported video formats
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv', '.wmv', '.m4v']
    DEFAULT_FRAME_DURATION = 2.0
    REFRESH_METRICS_INTERVAL = 5.0
    
    def __init__(self, config: DisplayConfig):
        self.config = config
        self.logger = get_service_logger()

        # Variables for managing backgrounds
        self.current_frame_index = 0
        self.background_frames = []
        self.gif_durations = []
        self.frame_duration = self.DEFAULT_FRAME_DURATION
        self.frame_start_time = 0
        self.metrics_thread: Timer | None = None
        self.metrics_running = False
        
        # Window capture for iStripper and other apps
        self.window_capture: Optional[WindowCapture] = None
        self.is_window_capture_mode = False
        
        if len(config.metrics_configs) != 0:
            # Initialize metrics collectors
            self.cpu_metrics = CpuMetrics()
            self.gpu_metrics = GpuMetrics()
            # Variables for real-time metrics
            self.current_metrics = self._get_current_metric()
            # Start metrics update
            self._start_metrics_update()
        else:
            self.cpu_metrics = None
            self.gpu_metrics = None
            self.current_metrics = {}
            self._stop_metrics_update()

        # Load background
        self._load_background()

    def _is_video_file(self, file_path: str) -> bool:
        """Check if the file is a supported video format"""
        if not file_path:
            return False

        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.SUPPORTED_VIDEO_FORMATS

    def _load_background(self):
        """Load background based on its type and set frame duration"""
        try:
            if self.config.background_type == BackgroundType.IMAGE:
                self._load_static_image()
            elif self.config.background_type == BackgroundType.GIF:
                self._load_gif()
            elif self.config.background_type == BackgroundType.VIDEO:
                if HAS_OPENCV and self._is_video_file(self.config.background_path):
                    self._load_video()
                else:
                    if not HAS_OPENCV:
                        self.logger.warning(
                            "OpenCV not available. Video background type is not supported. Falling back to static image.")
                    else:
                        self.logger.warning(
                            f"Unsupported video format. Supported formats: {', '.join(self.SUPPORTED_VIDEO_FORMATS)}. Falling back to static image.")
                    # Fallback to treating video path as a static image
                    self._load_static_image()
            elif self.config.background_type == BackgroundType.IMAGE_COLLECTION:
                self._load_image_collection()
            elif self.config.background_type == BackgroundType.WINDOW_CAPTURE:
                self._load_window_capture()

            self.frame_start_time = time.time()
            self.logger.info(
                f"Background loaded: {self.config.background_type}, frame_duration: {self.frame_duration}s")

        except Exception as e:
            self.logger.error(f"Error loading background: {e}")
            raise

    def _load_static_image(self) -> None:
        """Load a static image"""
        if not os.path.exists(self.config.background_path):
            raise FileNotFoundError(f"Background image not found: {self.config.background_path}")

        image = Image.open(self.config.background_path)
        image = self._resize_image(image)
        self.background_frames = [image]

    def _resize_image(self, image: Image.Image) -> Image.Image:
        image = image.resize((self.config.output_width, self.config.output_height), Image.Resampling.LANCZOS)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        return image

    def _load_gif(self):
        """
        Load an animated GIF and retrieve duration from metadata.
        
        GIFs will loop continuously until a different background is selected.
        """
        if not os.path.exists(self.config.background_path):
            raise FileNotFoundError(f"Background GIF not found: {self.config.background_path}")

        gif = Image.open(self.config.background_path)

        self.background_frames = []

        # Extract all frames from GIF
        for frame in ImageSequence.Iterator(gif):
            gif_frame_duration = self._gif_duration(frame)
            self.logger.debug(f"Extracting GIF frame with duration: {gif_frame_duration:.3f}s")
            frame_copy = frame.copy()
            frame_copy = self._resize_image(frame_copy)
            self.background_frames.append(frame_copy)
            self.gif_durations.append(gif_frame_duration)

        self.frame_duration = self.gif_durations[0]
        self.logger.info(f"GIF loaded: {len(self.background_frames)} frames, loops continuously")

    def _load_video(self):
        """
        Load a video and retrieve FPS from metadata.
        
        Note: OpenCV VideoCapture only reads video frames - audio is automatically
        ignored and will NOT be played. This ensures silent video playback for the
        LCD display.
        
        Videos will loop continuously until a different background is selected.
        """
        if not os.path.exists(self.config.background_path):
            raise FileNotFoundError(f"Background video not found: {self.config.background_path}")

        if not HAS_OPENCV:
            raise RuntimeError("OpenCV is required for video support but is not available")

        # Verify file format
        if not self._is_video_file(self.config.background_path):
            file_ext = os.path.splitext(self.config.background_path)[1].lower()
            raise RuntimeError(
                f"Unsupported video format '{file_ext}'. Supported formats: {', '.join(self.SUPPORTED_VIDEO_FORMATS)}")

        # OpenCV VideoCapture reads only video frames, audio is automatically ignored
        video_capture = cv2.VideoCapture(self.config.background_path)
        if not video_capture.isOpened():
            raise RuntimeError(
                f"Cannot open video: {self.config.background_path}. Please check if the file is corrupted or if OpenCV supports this codec.")

        # Get video properties
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        self.frame_duration = 1.0 / fps if fps > 0 else 1.0 / 30  # Fallback 30 FPS

        for i in range(frame_count):
            ret, frame = video_capture.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = self._resize_image(Image.fromarray(frame_rgb))
            self.background_frames.append(image)

        video_capture.release()

        self.logger.info(f"Video loaded: {os.path.basename(self.config.background_path)} (audio disabled, loops continuously)")
        self.logger.info(f"  Format: {os.path.splitext(self.config.background_path)[1].upper()}")
        self.logger.info(f"  FPS: {fps:.2f}")
        self.logger.info(f"  Duration: {duration:.1f}s per loop")
        self.logger.info(f"  Frame duration: {self.frame_duration:.3f}s")
        self.logger.info(f"  Total frames loaded: {len(self.background_frames)}")

    def _load_image_collection(self):
        """
        Load an image collection from a folder.
        
        Image collections will cycle/loop continuously through all images until
        a different background is selected.
        """
        if not os.path.isdir(self.config.background_path):
            raise NotADirectoryError(f"Background directory not found: {self.config.background_path}")

        # Search for all images in the folder
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(self.config.background_path, ext)))
            image_files.extend(glob.glob(os.path.join(self.config.background_path, ext.upper())))

        image_files.sort()  # Alphabetical sort

        if not image_files:
            raise RuntimeError(f"No images found in directory: {self.config.background_path}")

        for image_path in image_files:
            image = Image.open(image_path)
            image = self._resize_image(image)
            self.background_frames.append(image)

        self.logger.info(f"Image collection loaded: {len(image_files)} images, loops continuously")

    def _load_window_capture(self):
        """
        Initialize window capture for displaying application content (e.g., iStripper).
        
        Captures the specified application window in real-time and displays it on the LCD.
        Requires window_title to be set in config.
        """
        if not HAS_WINDOW_CAPTURE:
            raise RuntimeError(
                "Window capture not available. Install required packages:\n"
                "  Windows: pip install mss pygetwindow\n"
                "  Linux: pip install python-xlib"
            )
        
        if not self.config.window_title:
            raise ValueError("window_title must be specified for WINDOW_CAPTURE background type")
        
        # Initialize window capture
        self.window_capture = WindowCapture(
            window_title=self.config.window_title,
            target_width=self.config.output_width,
            target_height=self.config.output_height,
            fps=self.config.capture_fps
        )
        
        self.is_window_capture_mode = True
        self.frame_duration = 1.0 / self.config.capture_fps
        
        # Pre-load one black frame as fallback
        black_frame = Image.new('RGBA', (self.config.output_width, self.config.output_height), (0, 0, 0, 255))
        self.background_frames = [black_frame]
        
        self.logger.info(f"Window capture initialized: '{self.config.window_title}' at {self.config.capture_fps} FPS")

    def _start_metrics_update(self):
        """Start the metrics update thread every second"""
        self.logger.info("Starting metrics update thread ...")
        self.metrics_running = True
        self.metrics_thread = threading.Timer(interval=self.REFRESH_METRICS_INTERVAL,function=self._metrics_update_loop)
        self.metrics_thread.start()
        self.logger.debug("Metrics update thread started")

    def _stop_metrics_update(self):
        """Start the metrics update thread every second"""
        self.metrics_running = False
        if self.metrics_thread:
            self.metrics_thread.cancel()
            self.metrics_thread = None
        self.logger.debug("Metrics update thread started")

    def _metrics_update_loop(self):
        new_metrics = self._get_current_metric()
        self.current_metrics = new_metrics
        if self.metrics_running:
            self.metrics_thread = threading.Timer(interval=self.REFRESH_METRICS_INTERVAL, function=self._metrics_update_loop)
            self.metrics_thread.start()

    def _get_current_metric(self):
        try:
            # Collect CPU and GPU metrics
            cpu_data = self.cpu_metrics.get_all_metrics()
            gpu_data = self.gpu_metrics.get_all_metrics()
            # Update metrics in a thread-safe manner
            return {
                # CPU metrics
                'cpu_temperature': cpu_data.get('temperature'),
                'cpu_usage': cpu_data.get('usage_percentage'),
                'cpu_frequency': cpu_data.get('frequency'),

                # GPU metrics
                'gpu_temperature': gpu_data.get('temperature'),
                'gpu_usage': gpu_data.get('usage_percentage'),
                'gpu_frequency': gpu_data.get('frequency'),
                'gpu_vendor': gpu_data.get('vendor'),
                'gpu_name': gpu_data.get('name')
            }
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
            raise e

    def _gif_duration(self, frame: Image.Image) -> float:
        # Get duration from GIF metadata
        try:
            return frame.info.get('duration', 100) / 1000.0  # Convert ms to seconds
        except:
            return 0.1  # Default fallback

    def get_current_frame(self) -> Image.Image:
        """
        Get the current background frame.
        
        Automatically loops through all frames (for videos, GIFs, and image collections)
        until a different media is selected. The looping is continuous and seamless.
        
        For window capture mode (iStripper), captures a fresh frame in real-time.
        """
        # Handle window capture mode (iStripper, etc.)
        if self.is_window_capture_mode and self.window_capture:
            current_time = time.time()
            
            # Check if it's time to capture a new frame
            if current_time - self.frame_start_time >= self.frame_duration:
                self.frame_start_time = current_time
                
                # Capture new frame from window
                captured_frame = self.window_capture.capture_frame()
                
                if captured_frame:
                    # Successfully captured - update the frame
                    return captured_frame
                else:
                    # Window not found or capture failed - return black frame
                    self.logger.debug(f"Window '{self.config.window_title}' not available, using fallback frame")
                    return self.background_frames[0]  # Return black fallback frame
            else:
                # Return the last captured frame (stored in background_frames[0] if needed)
                # For window capture, we return a new capture each time
                return self.window_capture.capture_frame() or self.background_frames[0]
        
        # Handle standard media types (images, videos, GIFs, collections)
        current_time = time.time()

        if current_time - self.frame_start_time >= self.frame_duration:
            self.frame_start_time = current_time
            # Advance to next frame with wraparound (loop back to start when reaching the end)
            previous_index = self.current_frame_index
            self.current_frame_index = (self.current_frame_index + 1) % len(self.background_frames)
            
            # Log when video/animation loops back to start
            if previous_index > 0 and self.current_frame_index == 0:
                media_type = "video" if self.config.background_type == BackgroundType.VIDEO else \
                            "GIF" if self.config.background_type == BackgroundType.GIF else \
                            "image collection"
                self.logger.debug(f"{media_type.capitalize()} looping back to start (frame 0/{len(self.background_frames)-1})")

        if self.config.background_type == BackgroundType.GIF:
            self.frame_duration = self.gif_durations[self.current_frame_index]

        return self.background_frames[self.current_frame_index]

    def get_current_frame_info(self) -> Tuple[int, float]:
        """
        Get information about the current frame

        Returns:
            Tuple[int, float]: (frame_index, display_duration)
        """
        display_duration = self.wait_duration if self.wait_duration else self.frame_duration
        return self.current_frame_index, display_duration

    def get_current_metrics(self) -> dict:
        """Get current metrics in a thread-safe manner"""
        return self.current_metrics

    def cleanup(self):
        """Clean up resources"""
        self.metrics_running = False
        if self.metrics_thread:
            self.metrics_thread.cancel()
            self.metrics_thread = None
        
        # Clean up window capture if active
        if self.window_capture:
            self.window_capture.cleanup()
            self.window_capture = None

        self.logger.debug("FrameManager cleaned up")

    def __del__(self):
        """Destructor to automatically clean up"""
        self.cleanup()
