# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
iStripper Configuration Wizard for Windows 11

Provides a GUI wizard for easy iStripper integration setup with:
- Automatic detection
- Live preview
- Visual region selection
- One-click configuration
"""

import sys
from pathlib import Path
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QSlider, QSpinBox, QComboBox, QGroupBox, QRadioButton,
        QApplication, QMessageBox, QProgressBar
    )
    from PySide6.QtCore import Qt, QTimer, Signal
    from PySide6.QtGui import QPixmap, QImage
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False

from thermalright_lcd_control.common.logging_config import get_gui_logger
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager


class IStripperWizard(QDialog):
    """
    GUI Wizard for iStripper configuration
    
    Features:
    - Auto-detect iStripper installation
    - Live capture preview
    - Adjust scale, rotation, FPS
    - Test configuration
    - One-click save
    """
    
    configuration_saved = Signal(dict)
    
    def __init__(self, parent=None, target_width=320, target_height=240):
        """
        Initialize iStripper wizard
        
        Args:
            parent: Parent widget
            target_width: LCD target width
            target_height: LCD target height
        """
        if not HAS_PYSIDE:
            raise RuntimeError("PySide6 is required for the wizard")
        
        super().__init__(parent)
        self.logger = get_gui_logger()
        
        self.target_width = target_width
        self.target_height = target_height
        
        self.istripper_manager = IStripperManager()
        self.istripper_path = None
        self.is_running = False
        
        # Configuration state
        self.window_title = "iStripper"
        self.capture_fps = 30
        self.scale_factor = 1.5
        self.rotation = 0
        
        # Preview state
        self.preview_timer = None
        self.capture_preview = None
        
        self.setup_ui()
        self.detect_istripper()
    
    def setup_ui(self):
        """Setup the wizard UI"""
        self.setWindowTitle("iStripper Configuration Wizard")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("iStripper Integration Setup")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Detection section
        detection_group = self.create_detection_section()
        layout.addWidget(detection_group)
        
        # Preview section
        preview_group = self.create_preview_section()
        layout.addWidget(preview_group)
        
        # Configuration section
        config_group = self.create_configuration_section()
        layout.addWidget(config_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Test Configuration")
        self.test_button.clicked.connect(self.test_configuration)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.save_button = QPushButton("Save Configuration")
        self.save_button.clicked.connect(self.save_configuration)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def create_detection_section(self) -> QGroupBox:
        """Create detection section"""
        group = QGroupBox("1. iStripper Detection")
        layout = QVBoxLayout(group)
        
        # Status label
        self.detection_label = QLabel("Detecting iStripper...")
        layout.addWidget(self.detection_label)
        
        # Path label
        self.path_label = QLabel("")
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)
        
        # Process status
        self.process_label = QLabel("")
        layout.addWidget(self.process_label)
        
        # Manual detection button
        detect_button = QPushButton("Re-detect")
        detect_button.clicked.connect(self.detect_istripper)
        layout.addWidget(detect_button)
        
        return group
    
    def create_preview_section(self) -> QGroupBox:
        """Create preview section"""
        group = QGroupBox("2. Live Preview")
        layout = QVBoxLayout(group)
        
        # Preview label
        self.preview_label = QLabel("Preview will appear here when iStripper is running")
        self.preview_label.setMinimumSize(self.target_width, self.target_height)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: black;")
        layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)
        
        # Preview controls
        control_layout = QHBoxLayout()
        
        self.start_preview_button = QPushButton("Start Preview")
        self.start_preview_button.clicked.connect(self.toggle_preview)
        self.start_preview_button.setEnabled(False)
        control_layout.addWidget(self.start_preview_button)
        
        self.preview_status_label = QLabel("Preview stopped")
        control_layout.addWidget(self.preview_status_label)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        return group
    
    def create_configuration_section(self) -> QGroupBox:
        """Create configuration section"""
        group = QGroupBox("3. Configuration")
        layout = QVBoxLayout(group)
        
        # Window title
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Window Title:"))
        self.title_combo = QComboBox()
        self.title_combo.addItems(["iStripper", "VirtuaGirl HD"])
        self.title_combo.setEditable(True)
        self.title_combo.currentTextChanged.connect(self.on_config_changed)
        title_layout.addWidget(self.title_combo)
        layout.addLayout(title_layout)
        
        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("Capture FPS:"))
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setMinimum(15)
        self.fps_slider.setMaximum(60)
        self.fps_slider.setValue(30)
        self.fps_slider.setTickPosition(QSlider.TicksBelow)
        self.fps_slider.setTickInterval(15)
        self.fps_slider.valueChanged.connect(self.on_fps_changed)
        fps_layout.addWidget(self.fps_slider)
        self.fps_label = QLabel("30")
        fps_layout.addWidget(self.fps_label)
        layout.addLayout(fps_layout)
        
        # Scale factor
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale Factor:"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(50)  # 0.5x
        self.scale_slider.setMaximum(300)  # 3.0x
        self.scale_slider.setValue(150)  # 1.5x
        self.scale_slider.setTickPosition(QSlider.TicksBelow)
        self.scale_slider.setTickInterval(50)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        scale_layout.addWidget(self.scale_slider)
        self.scale_label = QLabel("1.50x")
        scale_layout.addWidget(self.scale_label)
        layout.addLayout(scale_layout)
        
        # Rotation
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotation:"))
        self.rotation_combo = QComboBox()
        self.rotation_combo.addItems(["0°", "90°", "180°", "270°"])
        self.rotation_combo.currentTextChanged.connect(self.on_rotation_changed)
        rotation_layout.addWidget(self.rotation_combo)
        rotation_layout.addStretch()
        layout.addLayout(rotation_layout)
        
        return group
    
    def detect_istripper(self):
        """Detect iStripper installation"""
        self.detection_label.setText("Detecting iStripper...")
        
        # Try to detect
        path = self.istripper_manager.detect_installation(use_cache=False)
        
        if path:
            self.istripper_path = path
            self.detection_label.setText("✓ iStripper detected")
            self.path_label.setText(f"Path: {path}")
            
            # Check if running
            self.check_process_status()
            
        else:
            self.detection_label.setText("✗ iStripper not found")
            self.path_label.setText("Please ensure iStripper is installed")
            self.process_label.setText("")
            self.start_preview_button.setEnabled(False)
    
    def check_process_status(self):
        """Check if iStripper is running"""
        is_running = self.istripper_manager.is_process_running()
        
        if is_running:
            self.process_label.setText("✓ iStripper is running")
            self.start_preview_button.setEnabled(True)
            self.is_running = True
        else:
            self.process_label.setText("○ iStripper is not running - start it to enable preview")
            self.start_preview_button.setEnabled(False)
            self.is_running = False
    
    def toggle_preview(self):
        """Start or stop preview"""
        if self.preview_timer and self.preview_timer.isActive():
            self.stop_preview()
        else:
            self.start_preview()
    
    def start_preview(self):
        """Start live preview"""
        try:
            # Import window capture
            from thermalright_lcd_control.device_controller.display.window_capture import WindowCapture
            
            self.capture_preview = WindowCapture(
                window_title=self.window_title,
                target_width=self.target_width,
                target_height=self.target_height,
                fps=self.capture_fps,
                scale_factor=self.scale_factor
            )
            
            # Start preview timer
            self.preview_timer = QTimer(self)
            self.preview_timer.timeout.connect(self.update_preview)
            self.preview_timer.start(1000 // self.capture_fps)  # Update at FPS rate
            
            self.start_preview_button.setText("Stop Preview")
            self.preview_status_label.setText("Preview running")
            self.save_button.setEnabled(True)
            
        except Exception as e:
            self.logger.error(f"Error starting preview: {e}")
            QMessageBox.warning(self, "Preview Error", 
                              f"Failed to start preview:\n{str(e)}\n\n"
                              "Make sure iStripper window is visible and not minimized.")
    
    def stop_preview(self):
        """Stop live preview"""
        if self.preview_timer:
            self.preview_timer.stop()
            self.preview_timer = None
        
        if self.capture_preview:
            self.capture_preview = None
        
        self.start_preview_button.setText("Start Preview")
        self.preview_status_label.setText("Preview stopped")
        self.preview_label.setText("Preview stopped")
    
    def update_preview(self):
        """Update preview frame"""
        try:
            if self.capture_preview:
                frame = self.capture_preview.get_next_frame()
                
                if frame is not None:
                    # Convert PIL image to QPixmap
                    if frame.mode != 'RGB':
                        frame = frame.convert('RGB')
                    
                    width, height = frame.size
                    image_data = frame.tobytes("raw", "RGB")
                    qimage = QImage(image_data, width, height, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimage)
                    
                    self.preview_label.setPixmap(pixmap)
                else:
                    self.preview_label.setText("No frame captured")
        
        except Exception as e:
            self.logger.error(f"Error updating preview: {e}")
            self.stop_preview()
    
    def on_config_changed(self):
        """Handle configuration changes"""
        self.window_title = self.title_combo.currentText()
    
    def on_fps_changed(self, value):
        """Handle FPS slider change"""
        self.capture_fps = value
        self.fps_label.setText(str(value))
        
        # Restart preview if running
        if self.preview_timer and self.preview_timer.isActive():
            self.stop_preview()
            self.start_preview()
    
    def on_scale_changed(self, value):
        """Handle scale slider change"""
        self.scale_factor = value / 100.0
        self.scale_label.setText(f"{self.scale_factor:.2f}x")
        
        # Restart preview if running
        if self.preview_timer and self.preview_timer.isActive():
            self.stop_preview()
            self.start_preview()
    
    def on_rotation_changed(self, text):
        """Handle rotation combo change"""
        self.rotation = int(text.replace("°", ""))
    
    def test_configuration(self):
        """Test the configuration"""
        if not self.is_running:
            QMessageBox.information(self, "Test Configuration",
                                  "Please start iStripper first to test the configuration.")
            return
        
        # Start preview to test
        if not self.preview_timer or not self.preview_timer.isActive():
            self.start_preview()
        
        QMessageBox.information(self, "Test Configuration",
                              "Preview started. Check if the capture looks correct.\n\n"
                              "Adjust Scale Factor and Rotation as needed.")
    
    def save_configuration(self):
        """Save configuration"""
        config = {
            'display': {
                'background': {
                    'type': 'window_capture',
                    'path': '',
                },
                'window_title': self.window_title,
                'capture_fps': self.capture_fps,
                'scale_factor': self.scale_factor,
                'rotation': self.rotation,
            }
        }
        
        self.configuration_saved.emit(config)
        
        QMessageBox.information(self, "Configuration Saved",
                              f"iStripper configuration saved:\n\n"
                              f"Window: {self.window_title}\n"
                              f"FPS: {self.capture_fps}\n"
                              f"Scale: {self.scale_factor}x\n"
                              f"Rotation: {self.rotation}°\n\n"
                              "Apply this configuration to your display config.")
        
        self.accept()
    
    def closeEvent(self, event):
        """Handle dialog close"""
        self.stop_preview()
        super().closeEvent(event)


def main():
    """Test the wizard"""
    app = QApplication(sys.argv)
    
    wizard = IStripperWizard(target_width=320, target_height=240)
    result = wizard.exec()
    
    if result == QDialog.Accepted:
        print("Configuration saved")
    else:
        print("Configuration cancelled")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
