# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
GPU Detector - Auto-detect and initialize the appropriate GPU metrics handler

This module detects the available GPU(s) and initializes the appropriate
metrics handler for the platform and GPU vendor.
"""

from typing import Optional, List, Dict
from thermalright_lcd_control.common.platform_utils import is_windows, is_linux
from thermalright_lcd_control.common.logging_config import get_service_logger


class GPUInfo:
    """Information about a detected GPU"""
    
    def __init__(self, vendor: str, name: str, index: int = 0):
        self.vendor = vendor  # 'nvidia', 'amd', 'intel'
        self.name = name
        self.index = index
    
    def __repr__(self):
        return f"GPUInfo(vendor='{self.vendor}', name='{self.name}', index={self.index})"


class GPUDetector:
    """
    Detect available GPUs and provide appropriate metrics handlers
    
    Supports:
    - NVIDIA GPUs (Windows and Linux via nvidia-smi)
    - AMD GPUs (Linux via sysfs, Windows via WMI)
    - Intel GPUs (Linux via sysfs, Windows via WMI)
    - Multi-GPU systems
    """
    
    def __init__(self):
        self.logger = get_service_logger()
        self.detected_gpus: List[GPUInfo] = []
        self._detect_all_gpus()
    
    def _detect_all_gpus(self):
        """Detect all available GPUs"""
        self.detected_gpus = []
        
        # Detect NVIDIA
        if self._detect_nvidia():
            self.logger.info("NVIDIA GPU(s) detected")
        
        # Detect AMD
        if self._detect_amd():
            self.logger.info("AMD GPU(s) detected")
        
        # Detect Intel
        if self._detect_intel():
            self.logger.info("Intel GPU(s) detected")
        
        if not self.detected_gpus:
            self.logger.warning("No supported GPUs detected")
    
    def _detect_nvidia(self) -> bool:
        """Detect NVIDIA GPUs"""
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=4
            )
            
            if result.returncode == 0 and result.stdout.strip():
                names = result.stdout.strip().split('\n')
                for idx, name in enumerate(names):
                    self.detected_gpus.append(GPUInfo('nvidia', name.strip(), idx))
                return True
                
        except Exception as e:
            self.logger.debug(f"NVIDIA detection failed: {e}")
        
        return False
    
    def _detect_amd(self) -> bool:
        """Detect AMD GPUs"""
        if is_linux():
            return self._detect_amd_linux()
        elif is_windows():
            return self._detect_amd_windows()
        return False
    
    def _detect_amd_linux(self) -> bool:
        """Detect AMD GPUs on Linux via sysfs"""
        try:
            import glob
            found = False
            
            for vendor_file in glob.glob("/sys/class/drm/card*/device/vendor"):
                try:
                    with open(vendor_file, 'r') as f:
                        vendor_id = f.read().strip()
                        if vendor_id == "0x1002":  # AMD vendor ID
                            # Get card name
                            card_path = vendor_file.replace('/vendor', '')
                            device_file = f"{card_path}/device"
                            
                            try:
                                with open(device_file, 'r') as df:
                                    device_id = df.read().strip()
                                    gpu_name = f"AMD GPU (Device {device_id})"
                                    
                                    # Try to get a better name from uevent
                                    uevent_file = f"{card_path}/uevent"
                                    if os.path.exists(uevent_file):
                                        with open(uevent_file, 'r') as ef:
                                            for line in ef:
                                                if 'PCI_ID' in line:
                                                    gpu_name = f"AMD GPU ({line.split('=')[1].strip()})"
                                                    break
                                    
                                    self.detected_gpus.append(GPUInfo('amd', gpu_name, len(self.detected_gpus)))
                                    found = True
                            except Exception:
                                pass
                                
                except Exception:
                    continue
            
            return found
            
        except Exception as e:
            self.logger.debug(f"AMD Linux detection failed: {e}")
        
        return False
    
    def _detect_amd_windows(self) -> bool:
        """Detect AMD GPUs on Windows via WMI"""
        try:
            from thermalright_lcd_control.device_controller.metrics.gpu_amd_windows import has_amd_gpu_windows
            
            if has_amd_gpu_windows():
                # Get GPU name from WMI
                try:
                    import wmi
                    w = wmi.WMI()
                    for gpu in w.Win32_VideoController():
                        if 'AMD' in gpu.Name or 'Radeon' in gpu.Name or 'ATI' in gpu.Name:
                            self.detected_gpus.append(GPUInfo('amd', gpu.Name, len(self.detected_gpus)))
                    return True
                except Exception:
                    # Generic AMD GPU entry
                    self.detected_gpus.append(GPUInfo('amd', 'AMD GPU', 0))
                    return True
                    
        except Exception as e:
            self.logger.debug(f"AMD Windows detection failed: {e}")
        
        return False
    
    def _detect_intel(self) -> bool:
        """Detect Intel GPUs"""
        if is_linux():
            return self._detect_intel_linux()
        elif is_windows():
            return self._detect_intel_windows()
        return False
    
    def _detect_intel_linux(self) -> bool:
        """Detect Intel GPUs on Linux via sysfs"""
        try:
            import glob
            found = False
            
            for vendor_file in glob.glob("/sys/class/drm/card*/device/vendor"):
                try:
                    with open(vendor_file, 'r') as f:
                        vendor_id = f.read().strip()
                        if vendor_id == "0x8086":  # Intel vendor ID
                            gpu_name = "Intel GPU"
                            self.detected_gpus.append(GPUInfo('intel', gpu_name, len(self.detected_gpus)))
                            found = True
                except Exception:
                    continue
            
            return found
            
        except Exception as e:
            self.logger.debug(f"Intel Linux detection failed: {e}")
        
        return False
    
    def _detect_intel_windows(self) -> bool:
        """Detect Intel GPUs on Windows via WMI"""
        try:
            from thermalright_lcd_control.device_controller.metrics.gpu_intel_windows import has_intel_gpu_windows
            
            if has_intel_gpu_windows():
                # Get GPU name from WMI
                try:
                    import wmi
                    w = wmi.WMI()
                    for gpu in w.Win32_VideoController():
                        if 'Intel' in gpu.Name:
                            self.detected_gpus.append(GPUInfo('intel', gpu.Name, len(self.detected_gpus)))
                    return True
                except Exception:
                    # Generic Intel GPU entry
                    self.detected_gpus.append(GPUInfo('intel', 'Intel GPU', 0))
                    return True
                    
        except Exception as e:
            self.logger.debug(f"Intel Windows detection failed: {e}")
        
        return False
    
    def get_primary_gpu(self) -> Optional[GPUInfo]:
        """
        Get the primary GPU
        
        Priority: NVIDIA > AMD discrete > Intel discrete > AMD integrated > Intel integrated
        
        Returns:
            GPUInfo for the primary GPU or None
        """
        if not self.detected_gpus:
            return None
        
        # Prioritize NVIDIA
        for gpu in self.detected_gpus:
            if gpu.vendor == 'nvidia':
                return gpu
        
        # Then AMD
        for gpu in self.detected_gpus:
            if gpu.vendor == 'amd':
                return gpu
        
        # Finally Intel
        for gpu in self.detected_gpus:
            if gpu.vendor == 'intel':
                return gpu
        
        return self.detected_gpus[0]
    
    def get_all_gpus(self) -> List[GPUInfo]:
        """Get all detected GPUs"""
        return self.detected_gpus.copy()
    
    def get_gpu_metrics_handler(self, gpu_info: Optional[GPUInfo] = None):
        """
        Get the appropriate metrics handler for a GPU
        
        Args:
            gpu_info: Specific GPU to get handler for, or None for primary GPU
        
        Returns:
            Metrics handler instance or None
        """
        if gpu_info is None:
            gpu_info = self.get_primary_gpu()
        
        if gpu_info is None:
            return None
        
        # Return existing GpuMetrics for now (it already handles detection)
        # In the future, this could return vendor-specific handlers
        from thermalright_lcd_control.device_controller.metrics.gpu_metrics import GpuMetrics
        return GpuMetrics()


def main():
    """Test GPU detection"""
    import os
    
    print("GPU Detection Test")
    print("=" * 60)
    print()
    
    detector = GPUDetector()
    gpus = detector.get_all_gpus()
    
    if gpus:
        print(f"Found {len(gpus)} GPU(s):")
        for i, gpu in enumerate(gpus, 1):
            print(f"  {i}. {gpu.vendor.upper()}: {gpu.name}")
        
        print()
        primary = detector.get_primary_gpu()
        if primary:
            print(f"Primary GPU: {primary.vendor.upper()} - {primary.name}")
    else:
        print("No GPUs detected")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    import os
    main()
