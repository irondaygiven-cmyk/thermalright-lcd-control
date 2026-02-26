# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Window capture functionality for capturing content from application windows.
Supports capturing from iStripper and other applications for display on LCD.
"""

import time
from typing import Optional
from PIL import Image

from thermalright_lcd_control.common.platform_utils import is_windows, is_linux
from thermalright_lcd_control.common.logging_config import get_service_logger


class WindowCapture:
    """
    Cross-platform window capture for displaying application content on LCD.
    
    Supports:
    - Windows: Uses mss (screenshot library) or pygetwindow + PIL
    - Linux: Uses python-xlib or scrot
    
    Use cases:
    - Capture iStripper application for LCD display
    - Capture any application window by title
    - Real-time screen capture at configurable FPS
    """
    
    def __init__(self, window_title: str, target_width: int = 320, target_height: int = 240, fps: int = 30, scale_factor: float = 1.0):
        """
        Initialize window capture.
        
        Args:
            window_title: Title of the window to capture (e.g., "iStripper")
            target_width: Target width for captured frames
            target_height: Target height for captured frames  
            fps: Frames per second for capture rate
            scale_factor: Scaling factor for zoom (1.0 = original, <1.0 = zoom out, >1.0 = zoom in)
        """
        self.logger = get_service_logger()
        self.window_title = window_title
        self.target_width = target_width
        self.target_height = target_height
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.scale_factor = scale_factor
        
        self._is_windows = is_windows()
        self._is_linux = is_linux()
        
        # Platform-specific capture backend
        self._capture_backend = None
        self._initialize_capture_backend()
        
        self.logger.info(f"Window capture initialized for '{window_title}' at {fps} FPS")
    
    def _initialize_capture_backend(self):
        """Initialize platform-specific window capture backend"""
        if self._is_windows:
            self._initialize_windows_backend()
        elif self._is_linux:
            self._initialize_linux_backend()
        else:
            self.logger.error("Unsupported platform for window capture")
            raise RuntimeError("Window capture not supported on this platform")
    
    def _initialize_windows_backend(self):
        """Initialize Windows window capture using mss or pygetwindow"""
        try:
            # Try mss first (fastest, most reliable)
            import mss
            self._capture_backend = "mss"
            self._mss = mss.mss()
            self.logger.info("Using mss for window capture (Windows)")
        except ImportError:
            try:
                # Fallback to pygetwindow + PIL ImageGrab
                import pygetwindow as gw
                from PIL import ImageGrab
                self._capture_backend = "pygetwindow"
                self.logger.info("Using pygetwindow for window capture (Windows)")
            except ImportError:
                self.logger.error("No window capture backend available. Install: pip install mss pygetwindow")
                raise RuntimeError("Window capture requires 'mss' or 'pygetwindow' package. Install with: pip install mss")
    
    def _initialize_linux_backend(self):
        """Initialize Linux window capture using python-xlib"""
        try:
            import Xlib.display
            import Xlib.X
            self._capture_backend = "xlib"
            self._display = Xlib.display.Display()
            self.logger.info("Using python-xlib for window capture (Linux)")
        except ImportError:
            self.logger.error("No window capture backend available. Install: pip install python-xlib")
            raise RuntimeError("Window capture on Linux requires 'python-xlib' package. Install with: pip install python-xlib")
    
    def find_window(self) -> Optional[dict]:
        """
        Find window by title.
        
        Returns:
            dict: Window info with 'left', 'top', 'width', 'height', or None if not found
        """
        if self._capture_backend == "mss":
            return self._find_window_mss()
        elif self._capture_backend == "pygetwindow":
            return self._find_window_pygetwindow()
        elif self._capture_backend == "xlib":
            return self._find_window_xlib()
        return None
    
    def _find_window_mss(self) -> Optional[dict]:
        """Find window using mss (Windows)"""
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                win = windows[0]
                return {
                    'left': win.left,
                    'top': win.top,
                    'width': win.width,
                    'height': win.height
                }
        except Exception as e:
            self.logger.debug(f"Could not find window '{self.window_title}': {e}")
        return None
    
    def _find_window_pygetwindow(self) -> Optional[dict]:
        """Find window using pygetwindow (Windows)"""
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                win = windows[0]
                return {
                    'left': win.left,
                    'top': win.top,
                    'width': win.width,
                    'height': win.height
                }
        except Exception as e:
            self.logger.debug(f"Could not find window '{self.window_title}': {e}")
        return None
    
    def _find_window_xlib(self) -> Optional[dict]:
        """Find window using python-xlib (Linux)"""
        try:
            import Xlib.display
            
            def get_window_geometry(window):
                """Get window geometry recursively"""
                try:
                    geom = window.get_geometry()
                    return {
                        'left': geom.x,
                        'top': geom.y,
                        'width': geom.width,
                        'height': geom.height
                    }
                except Exception:
                    return None
            
            def search_windows(window, title):
                """Recursively search for window by title"""
                try:
                    window_name = window.get_wm_name()
                    if window_name and self.window_title.lower() in window_name.lower():
                        return get_window_geometry(window)
                    
                    # Search children
                    children = window.query_tree().children
                    for child in children:
                        result = search_windows(child, title)
                        if result:
                            return result
                except Exception as e:
                    # Window may not be accessible, continue search
                    self.logger.debug(f"Error accessing window: {e}")
                return None
            
            root = self._display.screen().root
            return search_windows(root, self.window_title)
            
        except Exception as e:
            self.logger.debug(f"Could not find window '{self.window_title}': {e}")
        return None
    
    def capture_frame(self) -> Optional[Image.Image]:
        """
        Capture a single frame from the window.
        
        Returns:
            PIL.Image: Captured and resized frame, or None if capture failed
        """
        window_info = self.find_window()
        if not window_info:
            self.logger.debug(f"Window '{self.window_title}' not found")
            return None
        
        try:
            if self._capture_backend == "mss":
                return self._capture_frame_mss(window_info)
            elif self._capture_backend == "pygetwindow":
                return self._capture_frame_pygetwindow(window_info)
            elif self._capture_backend == "xlib":
                return self._capture_frame_xlib(window_info)
        except Exception as e:
            self.logger.error(f"Error capturing frame: {e}")
        
        return None
    
    def _apply_scaling(self, img: Image.Image) -> Image.Image:
        """
        Apply scaling to captured image.
        
        Args:
            img: Input image
            
        Returns:
            Scaled and cropped/padded image
        """
        # Apply scale factor if not 1.0
        if self.scale_factor != 1.0:
            # Calculate scaled dimensions
            scaled_width = int(self.target_width * self.scale_factor)
            scaled_height = int(self.target_height * self.scale_factor)
            
            # Resize to scaled dimensions first
            img = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
            
            # If scale > 1.0 (zoom in), crop to target size from center
            if self.scale_factor > 1.0:
                left = (scaled_width - self.target_width) // 2
                top = (scaled_height - self.target_height) // 2
                right = left + self.target_width
                bottom = top + self.target_height
                img = img.crop((left, top, right, bottom))
            # If scale < 1.0 (zoom out), pad with black to target size
            elif self.scale_factor < 1.0:
                result = Image.new('RGBA', (self.target_width, self.target_height), (0, 0, 0, 255))
                paste_x = (self.target_width - scaled_width) // 2
                paste_y = (self.target_height - scaled_height) // 2
                result.paste(img, (paste_x, paste_y))
                img = result
        else:
            # No scaling, just resize to fit
            img = img.resize((self.target_width, self.target_height), Image.Resampling.LANCZOS)
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        return img
    
    def _capture_frame_mss(self, window_info: dict) -> Optional[Image.Image]:
        """Capture frame using mss (Windows)"""
        monitor = {
            'left': window_info['left'],
            'top': window_info['top'],
            'width': window_info['width'],
            'height': window_info['height']
        }
        
        screenshot = self._mss.grab(monitor)
        img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
        img = self._apply_scaling(img)
        
        return img
    
    def _capture_frame_pygetwindow(self, window_info: dict) -> Optional[Image.Image]:
        """Capture frame using ImageGrab (Windows)"""
        from PIL import ImageGrab
        
        bbox = (
            window_info['left'],
            window_info['top'],
            window_info['left'] + window_info['width'],
            window_info['top'] + window_info['height']
        )
        
        img = ImageGrab.grab(bbox)
        img = self._apply_scaling(img)
        
        return img
    
    def _capture_frame_xlib(self, window_info: dict) -> Optional[Image.Image]:
        """Capture frame using python-xlib (Linux)"""
        # For Linux, we'll use a simpler approach with scrot or import
        try:
            import subprocess
            import tempfile
            import os
            
            # Use scrot to capture window
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            subprocess.run([
                'scrot',
                '-u',  # Current window
                tmp_path
            ], capture_output=True, timeout=2)
            
            if os.path.exists(tmp_path):
                img = Image.open(tmp_path)
                os.unlink(tmp_path)
                
                img = self._apply_scaling(img)
                
                return img
        except Exception as e:
            self.logger.debug(f"scrot capture failed: {e}")
        
        return None
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, '_mss'):
            self._mss.close()
        
        self.logger.debug("Window capture cleaned up")
