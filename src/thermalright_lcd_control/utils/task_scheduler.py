# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Windows Task Scheduler Integration

Provides functionality to create and manage scheduled tasks for auto-starting
the Thermalright LCD Control application on Windows startup.
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

from thermalright_lcd_control.common.platform_utils import is_windows
from thermalright_lcd_control.common.logging_config import get_service_logger


class TaskSchedulerManager:
    """
    Manages Windows Task Scheduler tasks for application auto-start
    
    Provides an alternative to Windows Service for auto-starting the application.
    Task Scheduler is lighter weight and doesn't require Service Control Manager.
    """
    
    TASK_NAME = "ThermalrightLCDControl"
    TASK_PATH = "\\Thermalright\\"
    
    def __init__(self):
        """Initialize Task Scheduler manager"""
        self.logger = get_service_logger()
        
        if not is_windows():
            raise RuntimeError("Task Scheduler manager only works on Windows")
    
    def is_task_installed(self) -> bool:
        """Check if the scheduled task is already installed"""
        try:
            result = subprocess.run(
                ['schtasks', '/Query', '/TN', f"{self.TASK_PATH}{self.TASK_NAME}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"Error checking task: {e}")
            return False
    
    def create_task(self, 
                    program_path: Optional[str] = None,
                    arguments: str = "",
                    start_directory: Optional[str] = None,
                    run_as_admin: bool = False) -> bool:
        """
        Create a scheduled task to run at user logon
        
        Args:
            program_path: Path to the executable (defaults to python)
            arguments: Command line arguments
            start_directory: Working directory for the task
            run_as_admin: Whether to run with highest privileges
            
        Returns:
            True if task was created successfully
        """
        try:
            # Default to python executable
            if program_path is None:
                program_path = sys.executable
            
            # Default arguments to start GUI
            if not arguments:
                arguments = "-m thermalright_lcd_control.ui.system_tray"
            
            # Default working directory
            if start_directory is None:
                start_directory = str(Path.home())
            
            # Build schtasks command
            cmd = [
                'schtasks',
                '/Create',
                '/TN', f"{self.TASK_PATH}{self.TASK_NAME}",
                '/TR', f'"{program_path}" {arguments}',
                '/SC', 'ONLOGON',  # Run at user logon
                '/RL', 'HIGHEST' if run_as_admin else 'LIMITED',
                '/F'  # Force creation (overwrites existing)
            ]
            
            # Add description
            cmd.extend(['/DESC', 'Thermalright LCD Control - Auto-start system tray application'])
            
            self.logger.info(f"Creating scheduled task: {self.TASK_NAME}")
            self.logger.debug(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info("Scheduled task created successfully")
                return True
            else:
                self.logger.error(f"Failed to create task: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating scheduled task: {e}")
            return False
    
    def delete_task(self) -> bool:
        """Delete the scheduled task"""
        try:
            self.logger.info(f"Deleting scheduled task: {self.TASK_NAME}")
            
            result = subprocess.run(
                ['schtasks', '/Delete', '/TN', f"{self.TASK_PATH}{self.TASK_NAME}", '/F'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info("Scheduled task deleted successfully")
                return True
            else:
                self.logger.error(f"Failed to delete task: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting scheduled task: {e}")
            return False
    
    def enable_task(self) -> bool:
        """Enable the scheduled task"""
        try:
            result = subprocess.run(
                ['schtasks', '/Change', '/TN', f"{self.TASK_PATH}{self.TASK_NAME}", '/ENABLE'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error enabling task: {e}")
            return False
    
    def disable_task(self) -> bool:
        """Disable the scheduled task"""
        try:
            result = subprocess.run(
                ['schtasks', '/Change', '/TN', f"{self.TASK_PATH}{self.TASK_NAME}", '/DISABLE'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error disabling task: {e}")
            return False
    
    def run_task(self) -> bool:
        """Run the scheduled task immediately"""
        try:
            result = subprocess.run(
                ['schtasks', '/Run', '/TN', f"{self.TASK_PATH}{self.TASK_NAME}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error running task: {e}")
            return False
    
    def get_task_status(self) -> dict:
        """
        Get the status of the scheduled task
        
        Returns:
            Dict with task information or empty dict if not found
        """
        try:
            result = subprocess.run(
                ['schtasks', '/Query', '/TN', f"{self.TASK_PATH}{self.TASK_NAME}", '/FO', 'LIST', '/V'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {}
            
            # Parse output
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting task status: {e}")
            return {}


def main():
    """Command-line interface for Task Scheduler management"""
    if not is_windows():
        print("Error: This tool only works on Windows")
        sys.exit(1)
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage Thermalright LCD Control Task Scheduler task"
    )
    parser.add_argument(
        'command',
        choices=['install', 'uninstall', 'enable', 'disable', 'run', 'status'],
        help="Task Scheduler command to execute"
    )
    parser.add_argument(
        '--admin',
        action='store_true',
        help="Run task with administrator privileges"
    )
    
    args = parser.parse_args()
    
    manager = TaskSchedulerManager()
    
    if args.command == 'install':
        print("Creating scheduled task for auto-start...")
        if manager.create_task(run_as_admin=args.admin):
            print("✓ Task created successfully")
            print(f"  Task will run at user logon")
            print(f"  Task name: {manager.TASK_PATH}{manager.TASK_NAME}")
        else:
            print("✗ Failed to create task")
            sys.exit(1)
    
    elif args.command == 'uninstall':
        print("Removing scheduled task...")
        if manager.delete_task():
            print("✓ Task removed successfully")
        else:
            print("✗ Failed to remove task")
            sys.exit(1)
    
    elif args.command == 'enable':
        print("Enabling scheduled task...")
        if manager.enable_task():
            print("✓ Task enabled")
        else:
            print("✗ Failed to enable task")
            sys.exit(1)
    
    elif args.command == 'disable':
        print("Disabling scheduled task...")
        if manager.disable_task():
            print("✓ Task disabled")
        else:
            print("✗ Failed to disable task")
            sys.exit(1)
    
    elif args.command == 'run':
        print("Running scheduled task...")
        if manager.run_task():
            print("✓ Task started")
        else:
            print("✗ Failed to start task")
            sys.exit(1)
    
    elif args.command == 'status':
        print("Task Status:")
        if manager.is_task_installed():
            print("  Status: Installed")
            info = manager.get_task_status()
            if info:
                for key in ['Status', 'Next Run Time', 'Last Run Time', 'Last Result']:
                    if key in info:
                        print(f"  {key}: {info[key]}")
        else:
            print("  Status: Not installed")


if __name__ == '__main__':
    main()
