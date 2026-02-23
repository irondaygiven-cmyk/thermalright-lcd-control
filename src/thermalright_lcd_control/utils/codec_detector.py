# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Video Codec Detection and Management for Windows 11

Detects installed video codecs, checks for K-Lite Codec Pack,
and provides guidance for codec installation.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from thermalright_lcd_control.common.platform_utils import is_windows
from thermalright_lcd_control.common.logging_config import get_gui_logger


class CodecDetector:
    """
    Detects video codecs and codec packs on Windows 11
    
    Checks for:
    - K-Lite Codec Pack
    - LAV Filters
    - FFmpeg
    - Windows Media Foundation codecs
    - DirectShow filters
    """
    
    # Common codec file locations
    CODEC_LOCATIONS = {
        'K-Lite': [
            Path(r"C:\Program Files\K-Lite Codec Pack"),
            Path(r"C:\Program Files (x86)\K-Lite Codec Pack"),
        ],
        'LAV': [
            Path(r"C:\Program Files\LAV Filters"),
            Path(r"C:\Program Files (x86)\LAV Filters"),
        ],
    }
    
    def __init__(self):
        """Initialize codec detector"""
        self.logger = get_gui_logger()
        
        if not is_windows():
            raise RuntimeError("Codec detector only works on Windows")
        
        import winreg
        self._winreg = winreg
        self.CODEC_PACK_KEYS = {
            'K-Lite Codec Pack': [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\KLCodecPack"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\KLCodecPack"),
            ],
            'LAV Filters': [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\LAV"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\LAV"),
            ],
        }
    
    def detect_all_codecs(self) -> Dict[str, any]:
        """
        Detect all installed codecs and codec packs
        
        Returns:
            Dict with codec information
        """
        result = {
            'codec_packs': self.detect_codec_packs(),
            'ffmpeg': self.detect_ffmpeg(),
            'opencv_codecs': self.detect_opencv_codecs(),
            'media_foundation': self.check_media_foundation(),
            'recommendations': []
        }
        
        # Add recommendations based on what's missing
        if not result['codec_packs']:
            result['recommendations'].append({
                'name': 'K-Lite Codec Pack Basic',
                'reason': 'No codec pack detected. K-Lite provides comprehensive video codec support.',
                'url': 'https://codecguide.com/download_kl.htm',
                'priority': 'high'
            })
        
        if not result['ffmpeg']:
            result['recommendations'].append({
                'name': 'FFmpeg',
                'reason': 'FFmpeg not found. Useful for video format conversion.',
                'url': 'https://ffmpeg.org/download.html',
                'priority': 'medium'
            })
        
        return result
    
    def detect_codec_packs(self) -> Dict[str, Dict]:
        """
        Detect installed codec packs
        
        Returns:
            Dict mapping codec pack name to installation info
        """
        detected = {}
        
        for pack_name, registry_keys in self.CODEC_PACK_KEYS.items():
            info = self._check_registry_keys(pack_name, registry_keys)
            if info:
                detected[pack_name] = info
            else:
                # Check file system as fallback
                file_info = self._check_file_locations(pack_name)
                if file_info:
                    detected[pack_name] = file_info
        
        return detected
    
    def _check_registry_keys(self, name: str, keys: List[Tuple]) -> Optional[Dict]:
        """Check registry keys for codec pack"""
        winreg = self._winreg
        try:
            for hkey, subkey in keys:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        # Try to get version and install path
                        info = {'name': name, 'source': 'registry'}
                        
                        try:
                            version = winreg.QueryValueEx(key, 'Version')[0]
                            info['version'] = version
                        except Exception:
                            pass
                        
                        try:
                            install_path = winreg.QueryValueEx(key, 'InstallDir')[0]
                            info['path'] = install_path
                        except Exception:
                            try:
                                install_path = winreg.QueryValueEx(key, 'InstallPath')[0]
                                info['path'] = install_path
                            except Exception:
                                pass
                        
                        self.logger.info(f"Found {name} via registry")
                        return info
                        
                except FileNotFoundError:
                    continue
                except Exception as e:
                    self.logger.debug(f"Error checking registry key: {e}")
                    continue
        except Exception as e:
            self.logger.debug(f"Error in registry check: {e}")
        
        return None
    
    def _check_file_locations(self, pack_name: str) -> Optional[Dict]:
        """Check common file locations for codec pack"""
        locations = self.CODEC_LOCATIONS.get(pack_name, [])
        
        for location in locations:
            if location.exists():
                self.logger.info(f"Found {pack_name} at {location}")
                return {
                    'name': pack_name,
                    'path': str(location),
                    'source': 'filesystem'
                }
        
        return None
    
    def detect_ffmpeg(self) -> Optional[Dict]:
        """Detect if FFmpeg is available"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse version from output
                version_line = result.stdout.split('\n')[0]
                return {
                    'available': True,
                    'version': version_line,
                    'path': 'In system PATH'
                }
        except FileNotFoundError:
            pass
        except Exception as e:
            self.logger.debug(f"Error detecting FFmpeg: {e}")
        
        return None
    
    def detect_opencv_codecs(self) -> Dict:
        """Detect video codecs available to OpenCV"""
        try:
            import cv2
            
            # Get OpenCV build info
            build_info = cv2.getBuildInformation()
            
            # Check for video support
            has_ffmpeg = 'ffmpeg' in build_info.lower() or 'avcodec' in build_info.lower()
            has_gstreamer = 'gstreamer' in build_info.lower()
            has_msmf = 'media foundation' in build_info.lower() or 'msmf' in build_info.lower()
            
            return {
                'opencv_version': cv2.__version__,
                'ffmpeg_support': has_ffmpeg,
                'gstreamer_support': has_gstreamer,
                'media_foundation_support': has_msmf,
                'video_backends': self._get_opencv_backends()
            }
            
        except ImportError:
            self.logger.warning("OpenCV not available")
            return {'error': 'OpenCV not installed'}
        except Exception as e:
            self.logger.error(f"Error detecting OpenCV codecs: {e}")
            return {'error': str(e)}
    
    def _get_opencv_backends(self) -> List[str]:
        """Get available OpenCV video backends"""
        try:
            import cv2
            backends = []
            
            # Common backends on Windows
            backend_names = {
                cv2.CAP_MSMF: 'Media Foundation',
                cv2.CAP_DSHOW: 'DirectShow',
                cv2.CAP_FFMPEG: 'FFmpeg',
            }
            
            for backend_id, name in backend_names.items():
                try:
                    cap = cv2.VideoCapture()
                    if cap.open(0, backend_id):
                        backends.append(name)
                        cap.release()
                except Exception:
                    pass
            
            return backends
            
        except Exception as e:
            self.logger.debug(f"Error getting OpenCV backends: {e}")
            return []
    
    def check_media_foundation(self) -> Dict:
        """Check Windows Media Foundation status"""
        try:
            # Check if Media Foundation is available
            result = subprocess.run(
                ['powershell', '-Command', 
                 'Get-WindowsOptionalFeature -Online -FeatureName MediaPlayback'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            is_enabled = 'Enabled' in result.stdout
            
            return {
                'available': is_enabled,
                'status': 'Enabled' if is_enabled else 'Disabled',
                'note': 'Windows Media Foundation for video playback'
            }
            
        except Exception as e:
            self.logger.debug(f"Error checking Media Foundation: {e}")
            return {
                'available': None,
                'status': 'Unknown',
                'error': str(e)
            }
    
    def can_play_video(self, video_path: str) -> Tuple[bool, str]:
        """
        Test if a video file can be played with current codecs
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (can_play, error_message)
        """
        try:
            import cv2
            
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return False, "Failed to open video file"
            
            # Try to read a frame
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                return True, "Video can be played"
            else:
                return False, "Failed to read video frame"
                
        except ImportError:
            return False, "OpenCV not installed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_codec_install_guide(self) -> Dict:
        """Get installation guide for missing codecs"""
        return {
            'K-Lite Codec Pack Basic': {
                'description': 'Comprehensive codec pack with LAV Filters',
                'download_url': 'https://codecguide.com/download_kl.htm',
                'install_steps': [
                    '1. Download K-Lite Codec Pack Basic from codecguide.com',
                    '2. Run the installer as Administrator',
                    '3. Use default settings (recommended)',
                    '4. Restart Thermalright LCD Control'
                ],
                'file_size': '~50 MB',
                'recommended': True
            },
            'FFmpeg': {
                'description': 'Video conversion and streaming tool',
                'download_url': 'https://ffmpeg.org/download.html',
                'install_steps': [
                    '1. Download FFmpeg for Windows',
                    '2. Extract to C:\\ffmpeg',
                    '3. Add C:\\ffmpeg\\bin to system PATH',
                    '4. Restart command prompt'
                ],
                'recommended': False
            }
        }


def main():
    """Test codec detection"""
    detector = CodecDetector()
    
    print("=" * 60)
    print("Video Codec Detection")
    print("=" * 60)
    print()
    
    result = detector.detect_all_codecs()
    
    print("Installed Codec Packs:")
    if result['codec_packs']:
        for name, info in result['codec_packs'].items():
            print(f"  ✓ {name}")
            if 'version' in info:
                print(f"    Version: {info['version']}")
            if 'path' in info:
                print(f"    Path: {info['path']}")
    else:
        print("  ✗ No codec packs detected")
    
    print()
    print("FFmpeg:")
    if result['ffmpeg']:
        print(f"  ✓ {result['ffmpeg']['version']}")
    else:
        print("  ✗ Not installed")
    
    print()
    print("OpenCV Support:")
    opencv_info = result['opencv_codecs']
    if 'error' not in opencv_info:
        print(f"  Version: {opencv_info.get('opencv_version', 'Unknown')}")
        print(f"  FFmpeg support: {'✓' if opencv_info.get('ffmpeg_support') else '✗'}")
        print(f"  Media Foundation: {'✓' if opencv_info.get('media_foundation_support') else '✗'}")
        if opencv_info.get('video_backends'):
            print(f"  Backends: {', '.join(opencv_info['video_backends'])}")
    else:
        print(f"  ✗ {opencv_info['error']}")
    
    print()
    print("Windows Media Foundation:")
    mf_info = result['media_foundation']
    print(f"  Status: {mf_info['status']}")
    
    if result['recommendations']:
        print()
        print("Recommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec['name']} ({rec['priority']} priority)")
            print(f"    {rec['reason']}")
            print(f"    Download: {rec['url']}")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
