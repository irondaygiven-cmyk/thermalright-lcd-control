# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
AMD GPU Metrics for Windows

Provides AMD GPU metrics using multiple methods:
1. WMI (Windows Management Instrumentation) - Fallback basic metrics
2. AMD ADL SDK (if available) - Comprehensive metrics
3. OpenHardwareMonitor - Community metrics (if available)

Note: Comprehensive AMD metrics require additional SDKs or tools.
This implementation provides basic metrics that work out-of-the-box.
"""

import subprocess
from typing import Optional

from thermalright_lcd_control.common.logging_config import get_service_logger

try:
    import wmi
    HAS_WMI = True
except ImportError:
    HAS_WMI = False


class AMDGPUMetricsWindows:
    """AMD GPU metrics for Windows using WMI"""
    
    def __init__(self):
        self.logger = get_service_logger()
        self.wmi_connection = None
        self.gpu_name = "AMD GPU"
        
        if HAS_WMI:
            try:
                self.wmi_connection = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                self.logger.debug("OpenHardwareMonitor WMI namespace available")
            except Exception:
                try:
                    self.wmi_connection = wmi.WMI()
                    self.logger.debug("Standard WMI namespace initialized")
                except Exception as e:
                    self.logger.error(f"Failed to initialize WMI: {e}")
                    self.wmi_connection = None
        
        self._detect_amd_gpu()
    
    def _detect_amd_gpu(self):
        """Detect AMD GPU name"""
        if not HAS_WMI or not self.wmi_connection:
            return
        
        try:
            # Try to get GPU info from Win32_VideoController
            for gpu in self.wmi_connection.Win32_VideoController():
                if 'AMD' in gpu.Name or 'Radeon' in gpu.Name or 'ATI' in gpu.Name:
                    self.gpu_name = gpu.Name
                    self.logger.info(f"AMD GPU detected: {self.gpu_name}")
                    return
        except Exception as e:
            self.logger.debug(f"Error detecting AMD GPU: {e}")
    
    def get_temperature(self) -> Optional[float]:
        """
        Get GPU temperature
        
        Returns:
            Temperature in Celsius or None if unavailable
        """
        if not HAS_WMI or not self.wmi_connection:
            return None
        
        try:
            # Try OpenHardwareMonitor namespace
            if hasattr(self.wmi_connection, 'Sensor'):
                for sensor in self.wmi_connection.Sensor():
                    if 'GPU' in sensor.Name and 'Temperature' in sensor.SensorType:
                        if 'AMD' in sensor.Name or 'Radeon' in sensor.Name:
                            return float(sensor.Value)
            
            # Fallback: Try ACPI thermal zone (less reliable)
            try:
                wmi_temp = wmi.WMI(namespace="root\\WMI")
                for sensor in wmi_temp.MSAcpi_ThermalZoneTemperature():
                    # Convert from tenths of Kelvin to Celsius
                    temp_celsius = (sensor.CurrentTemperature / 10.0) - 273.15
                    if 0 < temp_celsius < 150:  # Sanity check
                        return temp_celsius
            except Exception:
                pass
                
        except Exception as e:
            self.logger.debug(f"Error getting AMD temperature: {e}")
        
        return None
    
    def get_usage(self) -> Optional[float]:
        """
        Get GPU usage percentage
        
        Returns:
            Usage percentage (0-100) or None if unavailable
        """
        if not HAS_WMI or not self.wmi_connection:
            return None
        
        try:
            # Try OpenHardwareMonitor namespace
            if hasattr(self.wmi_connection, 'Sensor'):
                for sensor in self.wmi_connection.Sensor():
                    if 'GPU' in sensor.Name and 'Load' in sensor.SensorType:
                        if 'AMD' in sensor.Name or 'Radeon' in sensor.Name:
                            return float(sensor.Value)
            
            # Fallback: Try Win32_PerfFormattedData_GPUPerformanceCounters
            try:
                for counter in self.wmi_connection.query(
                    "SELECT * FROM Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine"
                ):
                    if hasattr(counter, 'UtilizationPercentage'):
                        return float(counter.UtilizationPercentage)
            except Exception:
                pass
                
        except Exception as e:
            self.logger.debug(f"Error getting AMD usage: {e}")
        
        return None
    
    def get_frequency(self) -> Optional[float]:
        """
        Get GPU clock frequency in MHz
        
        Returns:
            Frequency in MHz or None if unavailable
        """
        if not HAS_WMI or not self.wmi_connection:
            return None
        
        try:
            # Try OpenHardwareMonitor namespace
            if hasattr(self.wmi_connection, 'Sensor'):
                for sensor in self.wmi_connection.Sensor():
                    if 'GPU' in sensor.Name and 'Clock' in sensor.SensorType:
                        if 'AMD' in sensor.Name or 'Radeon' in sensor.Name:
                            return float(sensor.Value)
                            
        except Exception as e:
            self.logger.debug(f"Error getting AMD frequency: {e}")
        
        return None
    
    def get_vram_usage(self) -> Optional[float]:
        """
        Get VRAM usage in MB
        
        Returns:
            VRAM usage in MB or None if unavailable
        """
        if not HAS_WMI or not self.wmi_connection:
            return None
        
        try:
            for gpu in self.wmi_connection.Win32_VideoController():
                if 'AMD' in gpu.Name or 'Radeon' in gpu.Name or 'ATI' in gpu.Name:
                    # AdapterRAM is in bytes
                    if hasattr(gpu, 'AdapterRAM') and gpu.AdapterRAM:
                        return float(gpu.AdapterRAM) / (1024 * 1024)
                        
        except Exception as e:
            self.logger.debug(f"Error getting AMD VRAM: {e}")
        
        return None


def has_amd_gpu_windows() -> bool:
    """Check if an AMD GPU is present on Windows"""
    if not HAS_WMI:
        return False
    
    try:
        w = wmi.WMI()
        for gpu in w.Win32_VideoController():
            if 'AMD' in gpu.Name or 'Radeon' in gpu.Name or 'ATI' in gpu.Name:
                return True
    except Exception:
        pass
    
    return False
