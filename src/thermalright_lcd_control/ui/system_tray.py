# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
System Tray Icon for Thermalright LCD Control (Windows)

Provides a system tray icon for monitoring and controlling the Windows service.
"""

import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PySide6.QtGui import QIcon, QAction
    from PySide6.QtCore import QTimer, Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False

from thermalright_lcd_control.common.platform_utils import is_windows
from thermalright_lcd_control.common.logging_config import get_gui_logger


class SystemTrayIcon:
    """
    System tray icon for Windows service control
    
    Features:
    - Shows service status (running/stopped/error)
    - Right-click menu for service control
    - Start/Stop/Restart service
    - Open configuration
    - Exit application
    """
    
    def __init__(self, app=None):
        """Initialize system tray icon"""
        if not HAS_PYSIDE:
            raise RuntimeError("PySide6 is required for system tray icon")
        
        if not is_windows():
            raise RuntimeError("System tray icon is currently Windows-only")
        
        self.logger = get_gui_logger()
        self.app = app or QApplication.instance()
        
        if not self.app:
            self.app = QApplication(sys.argv)
        
        # Try to import service manager
        try:
            from thermalright_lcd_control.service.windows_service_manager import WindowsServiceManager
            self.service_manager = WindowsServiceManager()
            self.has_service = True
        except Exception as e:
            self.logger.warning(f"Service manager not available: {e}")
            self.service_manager = None
            self.has_service = False
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self.app)
        self.setup_icon()
        self.setup_menu()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
        
        self.current_status = "Unknown"
        self.update_status()
    
    def setup_icon(self):
        """Setup the system tray icon"""
        # For now, use a simple icon
        # TODO: Add custom icons for different states
        icon = QIcon()
        if icon.isNull():
            # Create a simple icon if no icon available
            from PySide6.QtGui import QPixmap, QPainter
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.fillRect(0, 0, 32, 32, Qt.blue)
            painter.end()
            icon = QIcon(pixmap)
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Thermalright LCD Control")
    
    def setup_menu(self):
        """Setup the right-click context menu"""
        menu = QMenu()
        
        # Service status
        self.status_action = QAction("Status: Unknown")
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        menu.addSeparator()
        
        if self.has_service:
            # Service control actions
            start_action = QAction("Start Service")
            start_action.triggered.connect(self.start_service)
            menu.addAction(start_action)
            
            stop_action = QAction("Stop Service")
            stop_action.triggered.connect(self.stop_service)
            menu.addAction(stop_action)
            
            restart_action = QAction("Restart Service")
            restart_action.triggered.connect(self.restart_service)
            menu.addAction(restart_action)
            
            menu.addSeparator()
        
        # Configuration
        config_action = QAction("Open Configuration")
        config_action.triggered.connect(self.open_configuration)
        menu.addAction(config_action)
        
        # GUI
        gui_action = QAction("Open GUI")
        gui_action.triggered.connect(self.open_gui)
        menu.addAction(gui_action)
        
        menu.addSeparator()
        
        # Exit
        exit_action = QAction("Exit")
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def update_status(self):
        """Update service status display"""
        if not self.has_service:
            self.current_status = "Service not available"
            self.status_action.setText(f"Status: {self.current_status}")
            return
        
        try:
            status = self.service_manager.service_class.get_service_status()
            self.current_status = status
            
            # Update status text and tooltip
            self.status_action.setText(f"Status: {status}")
            self.tray_icon.setToolTip(f"Thermalright LCD Control\nStatus: {status}")
            
            # TODO: Update icon based on status
            # Green for running, red for stopped, yellow for transitioning
            
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
            self.current_status = "Error"
            self.status_action.setText(f"Status: Error")
    
    def start_service(self):
        """Start the Windows service"""
        if not self.has_service:
            self.show_message("Error", "Service manager not available")
            return
        
        try:
            self.show_message("Starting Service", "Starting Thermalright LCD Control service...")
            if self.service_manager.start():
                self.show_message("Success", "Service started successfully")
                self.update_status()
            else:
                self.show_message("Error", "Failed to start service")
        except Exception as e:
            self.show_message("Error", f"Error starting service: {e}")
    
    def stop_service(self):
        """Stop the Windows service"""
        if not self.has_service:
            self.show_message("Error", "Service manager not available")
            return
        
        try:
            self.show_message("Stopping Service", "Stopping Thermalright LCD Control service...")
            if self.service_manager.stop():
                self.show_message("Success", "Service stopped successfully")
                self.update_status()
            else:
                self.show_message("Error", "Failed to stop service")
        except Exception as e:
            self.show_message("Error", f"Error stopping service: {e}")
    
    def restart_service(self):
        """Restart the Windows service"""
        if not self.has_service:
            self.show_message("Error", "Service manager not available")
            return
        
        try:
            self.show_message("Restarting Service", "Restarting Thermalright LCD Control service...")
            if self.service_manager.restart():
                self.show_message("Success", "Service restarted successfully")
                self.update_status()
            else:
                self.show_message("Error", "Failed to restart service")
        except Exception as e:
            self.show_message("Error", f"Error restarting service: {e}")
    
    def open_configuration(self):
        """Open configuration directory"""
        from thermalright_lcd_control.common.platform_utils import get_data_dir
        import subprocess
        
        config_dir = get_data_dir()
        try:
            subprocess.Popen(['explorer', config_dir])
        except Exception as e:
            self.show_message("Error", f"Failed to open configuration: {e}")
    
    def open_gui(self):
        """Open the main GUI"""
        try:
            from thermalright_lcd_control.main_gui import main
            # TODO: Implement proper GUI launching
            self.show_message("Info", "GUI launching not yet implemented from tray")
        except Exception as e:
            self.show_message("Error", f"Failed to open GUI: {e}")
    
    def exit_app(self):
        """Exit the system tray application"""
        self.status_timer.stop()
        self.tray_icon.hide()
        if self.app:
            self.app.quit()
    
    def show_message(self, title, message):
        """Show a system tray notification"""
        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.Information,
            3000  # 3 seconds
        )
    
    def show(self):
        """Show the system tray icon"""
        self.tray_icon.show()
    
    def hide(self):
        """Hide the system tray icon"""
        self.tray_icon.hide()


def main():
    """Main entry point for system tray application"""
    if not is_windows():
        print("System tray icon is currently Windows-only")
        sys.exit(1)
    
    if not HAS_PYSIDE:
        print("Error: PySide6 is required for system tray icon")
        print("Install with: pip install PySide6")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Don't quit when GUI closes
    
    tray = SystemTrayIcon(app)
    tray.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
