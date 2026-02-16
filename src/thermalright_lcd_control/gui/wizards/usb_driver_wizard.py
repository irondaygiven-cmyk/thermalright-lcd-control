# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
USB Driver Installation Wizard for Windows 11

Provides a GUI wizard for USB driver installation using Zadig with:
- Device detection
- Automatic Zadig download
- Step-by-step instructions
- Visual guides
"""

import sys
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTextEdit, QProgressBar, QListWidget, QListWidgetItem,
        QApplication, QMessageBox, QGroupBox
    )
    from PySide6.QtCore import Qt, QThread, Signal
    from PySide6.QtGui import QFont
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False

from thermalright_lcd_control.common.logging_config import get_gui_logger
from thermalright_lcd_control.utils.zadig_manager import ZadigManager


class ZadigDownloadThread(QThread):
    """Thread for downloading Zadig"""
    
    progress = Signal(int)
    finished = Signal(bool, str)
    
    def __init__(self, zadig_manager):
        super().__init__()
        self.zadig_manager = zadig_manager
    
    def run(self):
        """Download Zadig"""
        try:
            success = self.zadig_manager.download_zadig(
                progress_callback=lambda p: self.progress.emit(p)
            )
            
            if success:
                self.finished.emit(True, "Download successful")
            else:
                self.finished.emit(False, "Download failed")
                
        except Exception as e:
            self.finished.emit(False, str(e))


class USBDriverWizard(QDialog):
    """
    GUI Wizard for USB driver installation
    
    Features:
    - Detect Thermalright devices
    - Download Zadig automatically
    - Show installation instructions
    - Launch Zadig with guidance
    """
    
    def __init__(self, parent=None):
        """Initialize USB driver wizard"""
        if not HAS_PYSIDE:
            raise RuntimeError("PySide6 is required for the wizard")
        
        super().__init__(parent)
        self.logger = get_gui_logger()
        
        self.zadig_manager = ZadigManager()
        self.detected_devices = []
        self.selected_device = None
        self.download_thread = None
        
        self.setup_ui()
        self.check_zadig()
        self.detect_devices()
    
    def setup_ui(self):
        """Setup the wizard UI"""
        self.setWindowTitle("USB Driver Installation Wizard")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("USB Driver Installation Wizard")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        subtitle = QLabel("Install WinUSB driver for Thermalright LCD devices using Zadig")
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        
        # Zadig section
        zadig_group = self.create_zadig_section()
        layout.addWidget(zadig_group)
        
        # Device detection section
        device_group = self.create_device_section()
        layout.addWidget(device_group)
        
        # Instructions section
        instructions_group = self.create_instructions_section()
        layout.addWidget(instructions_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.launch_button = QPushButton("Launch Zadig")
        self.launch_button.clicked.connect(self.launch_zadig)
        self.launch_button.setEnabled(False)
        button_layout.addWidget(self.launch_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def create_zadig_section(self) -> QGroupBox:
        """Create Zadig download section"""
        group = QGroupBox("1. Zadig Tool")
        layout = QVBoxLayout(group)
        
        # Status label
        self.zadig_status_label = QLabel("Checking Zadig...")
        layout.addWidget(self.zadig_status_label)
        
        # Download button
        self.download_button = QPushButton("Download Zadig")
        self.download_button.clicked.connect(self.download_zadig)
        self.download_button.setVisible(False)
        layout.addWidget(self.download_button)
        
        # Progress bar
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        layout.addWidget(self.download_progress)
        
        return group
    
    def create_device_section(self) -> QGroupBox:
        """Create device detection section"""
        group = QGroupBox("2. Device Detection")
        layout = QVBoxLayout(group)
        
        # Device list
        self.device_list = QListWidget()
        self.device_list.itemClicked.connect(self.on_device_selected)
        layout.addWidget(self.device_list)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh Devices")
        refresh_button.clicked.connect(self.detect_devices)
        refresh_layout.addWidget(refresh_button)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)
        
        return group
    
    def create_instructions_section(self) -> QGroupBox:
        """Create instructions section"""
        group = QGroupBox("3. Installation Instructions")
        layout = QVBoxLayout(group)
        
        # Instructions text
        self.instructions_text = QTextEdit()
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setMaximumHeight(200)
        layout.addWidget(self.instructions_text)
        
        return group
    
    def check_zadig(self):
        """Check if Zadig is available"""
        if self.zadig_manager.is_zadig_available():
            self.zadig_status_label.setText(f"✓ Zadig available at {self.zadig_manager.zadig_path}")
            self.download_button.setVisible(False)
        else:
            self.zadig_status_label.setText(f"✗ Zadig not found")
            self.download_button.setVisible(True)
    
    def download_zadig(self):
        """Download Zadig tool"""
        self.download_button.setEnabled(False)
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        
        self.zadig_status_label.setText("Downloading Zadig...")
        
        # Start download in thread
        self.download_thread = ZadigDownloadThread(self.zadig_manager)
        self.download_thread.progress.connect(self.download_progress.setValue)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()
    
    def on_download_finished(self, success: bool, message: str):
        """Handle download completion"""
        self.download_progress.setVisible(False)
        
        if success:
            self.zadig_status_label.setText(f"✓ Zadig downloaded successfully")
            self.download_button.setVisible(False)
            
            if self.detected_devices:
                self.launch_button.setEnabled(True)
        else:
            self.zadig_status_label.setText(f"✗ Download failed: {message}")
            self.download_button.setEnabled(True)
            
            QMessageBox.warning(self, "Download Failed",
                              f"Failed to download Zadig:\n{message}\n\n"
                              "You can download it manually from:\n"
                              "https://zadig.akeo.ie/")
    
    def detect_devices(self):
        """Detect Thermalright devices"""
        self.device_list.clear()
        self.detected_devices = self.zadig_manager.detect_thermalright_devices()
        
        if not self.detected_devices:
            item = QListWidgetItem("No Thermalright devices detected")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.device_list.addItem(item)
            
            self.instructions_text.setPlainText(
                "No devices detected.\n\n"
                "Please ensure:\n"
                "1. Your Thermalright LCD device is connected\n"
                "2. USB cable is properly connected\n"
                "3. Try a different USB port\n\n"
                "Click 'Refresh Devices' after connecting."
            )
            
            self.launch_button.setEnabled(False)
        else:
            for device in self.detected_devices:
                status_icon = "✓" if device['driver_status']['status'] == 'accessible' else "✗"
                item_text = f"{status_icon} {device['name']} (VID:{device['vid']:04x} PID:{device['pid']:04x})"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, device)
                self.device_list.addItem(item)
            
            # Auto-select first device needing driver
            for i in range(self.device_list.count()):
                item = self.device_list.item(i)
                device = item.data(Qt.UserRole)
                if device and device['driver_status']['status'] != 'accessible':
                    self.device_list.setCurrentItem(item)
                    self.on_device_selected(item)
                    break
            
            if self.zadig_manager.is_zadig_available():
                self.launch_button.setEnabled(True)
    
    def on_device_selected(self, item):
        """Handle device selection"""
        device = item.data(Qt.UserRole)
        if not device:
            return
        
        self.selected_device = device
        
        # Get installation instructions
        instructions = self.zadig_manager.get_installation_instructions(
            device['vid'],
            device['pid']
        )
        
        # Format instructions
        text = f"Device: {instructions['device']}\n"
        text += f"VID:PID: {instructions['vid']}:{instructions['pid']}\n"
        text += f"Recommended Driver: {instructions['driver']}\n\n"
        
        text += "Installation Steps:\n"
        text += "=" * 40 + "\n\n"
        
        for step in instructions['steps']:
            text += f"Step {step['number']}: {step['title']}\n"
            text += f"{step['description']}\n"
            if 'note' in step:
                text += f"  Note: {step['note']}\n"
            if 'warning' in step:
                text += f"  ⚠ {step['warning']}\n"
            text += "\n"
        
        text += "\nImportant Notes:\n"
        for note in instructions['notes']:
            text += f"• {note}\n"
        
        self.instructions_text.setPlainText(text)
    
    def launch_zadig(self):
        """Launch Zadig tool"""
        if not self.selected_device:
            QMessageBox.warning(self, "No Device Selected",
                              "Please select a device from the list first.")
            return
        
        if not self.zadig_manager.is_zadig_available():
            QMessageBox.warning(self, "Zadig Not Available",
                              "Please download Zadig first.")
            return
        
        # Show confirmation
        response = QMessageBox.question(
            self,
            "Launch Zadig",
            f"This will launch Zadig to install the driver for:\n"
            f"{self.selected_device['name']}\n\n"
            f"Follow the instructions shown above.\n\n"
            f"Administrator privileges are required.\n\n"
            f"Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if response == QMessageBox.Yes:
            if self.zadig_manager.launch_zadig_for_device(
                self.selected_device['vid'],
                self.selected_device['pid']
            ):
                QMessageBox.information(
                    self,
                    "Zadig Launched",
                    "Zadig has been launched.\n\n"
                    "Follow the installation steps shown above.\n\n"
                    "After installation completes:\n"
                    "1. Close Zadig\n"
                    "2. Click 'Refresh Devices' to verify\n"
                    "3. Restart Thermalright LCD Control"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Launch Failed",
                    "Failed to launch Zadig.\n\n"
                    "Try running it manually from:\n"
                    f"{self.zadig_manager.zadig_path}"
                )


def main():
    """Test the wizard"""
    app = QApplication(sys.argv)
    
    wizard = USBDriverWizard()
    wizard.exec()
    
    sys.exit(0)


if __name__ == '__main__':
    main()
