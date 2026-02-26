# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Simulated tests for the lazy-import fix and Windows 11 dependency validation.

These tests run on any platform (Linux CI included) by monkey-patching the
native library load so they do not require a physical HID device or the
hidapi/libusb shared libraries to be installed.
"""

import importlib
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_broken_hid(message: str) -> types.ModuleType:
    """Return a fake 'hid' module whose import raises ImportError."""
    mod = types.ModuleType("hid")

    def _raise(*_a, **_kw):
        raise ImportError(message)

    mod.Device = _raise
    # Simulate the library-load failure that the real hid package performs in
    # its __init__.py (line 31 in hid 1.0.8).
    mod.__spec__ = None
    raise ImportError(message)  # will be caught by the caller


class _BrokenHidFinder(importlib.abc.MetaPathFinder):
    """Meta-path finder that makes 'import hid' raise ImportError."""

    def __init__(self, message: str):
        self.message = message

    def find_spec(self, fullname, path, target=None):
        if fullname == "hid":
            raise ImportError(self.message)
        return None


# ---------------------------------------------------------------------------
# 1. Lazy import: module-level import chain must not crash
# ---------------------------------------------------------------------------

class TestHidLazyImport(unittest.TestCase):
    """The hid_devices module must be importable even when hidapi.dll is absent."""

    def setUp(self):
        # Remove cached modules so each test starts clean
        for key in list(sys.modules):
            if key.startswith("thermalright_lcd_control"):
                del sys.modules[key]

    def test_hid_devices_module_imports_without_native_library(self):
        """hid_devices.py must not trigger the native-library load at import time."""
        # Inject a broken 'hid' finder so any 'import hid' fails immediately
        bad_message = (
            "Unable to load any of the following libraries:"
            "libhidapi-hidraw.so libhidapi-hidraw.so.0 "
            "libhidapi-libusb.so libhidapi-libusb.so.0 "
            "libhidapi-iohidmanager.so libhidapi-iohidmanager.so.0 "
            "libhidapi.dylib hidapi.dll libhidapi-0.dll"
        )
        finder = _BrokenHidFinder(bad_message)
        sys.meta_path.insert(0, finder)
        # Also remove any previously loaded 'hid' module
        sys.modules.pop("hid", None)
        try:
            # This must NOT raise – hid is only imported inside __init__
            from thermalright_lcd_control.device_controller.display import hid_devices  # noqa: F401
        finally:
            sys.meta_path.remove(finder)

    def test_supported_devices_imports_without_native_library(self):
        """supported_devices.py must be importable without the hidapi native DLL."""
        bad_message = "Unable to load: hidapi.dll libhidapi-0.dll"
        finder = _BrokenHidFinder(bad_message)
        sys.meta_path.insert(0, finder)
        sys.modules.pop("hid", None)
        try:
            from thermalright_lcd_control.common.supported_devices import SUPPORTED_DEVICES
            self.assertEqual(len(SUPPORTED_DEVICES), 3)
        finally:
            sys.meta_path.remove(finder)

    def test_static_info_methods_work_without_native_library(self):
        """DisplayDevice*.info() must return correct metadata without hidapi."""
        bad_message = "hidapi.dll not found"
        finder = _BrokenHidFinder(bad_message)
        sys.meta_path.insert(0, finder)
        sys.modules.pop("hid", None)
        try:
            from thermalright_lcd_control.device_controller.display.hid_devices import (
                DisplayDevice04185304,
                DisplayDevice04165302,
            )
            info_a = DisplayDevice04185304.info()
            self.assertEqual(info_a["vid"], 0x0418)
            self.assertEqual(info_a["pid"], 0x5304)
            self.assertEqual(info_a["width"], 480)
            self.assertEqual(info_a["height"], 480)

            info_b = DisplayDevice04165302.info()
            self.assertEqual(info_b["vid"], 0x0416)
            self.assertEqual(info_b["pid"], 0x5302)
            self.assertEqual(info_b["width"], 320)
            self.assertEqual(info_b["height"], 240)
        finally:
            sys.meta_path.remove(finder)

    def test_hid_device_init_triggers_import(self):
        """HidDevice.__init__ must call 'import hid' (the lazy load point)."""
        # Confirm that hid import is attempted only during instantiation
        bad_message = "hidapi.dll not found"
        finder = _BrokenHidFinder(bad_message)
        sys.meta_path.insert(0, finder)
        sys.modules.pop("hid", None)
        try:
            from thermalright_lcd_control.device_controller.display.hid_devices import (
                DisplayDevice04185304,
            )
            with self.assertRaises(ImportError) as ctx:
                DisplayDevice04185304("/tmp")
            self.assertIn("hidapi", str(ctx.exception).lower() + "dll")
        finally:
            sys.meta_path.remove(finder)


# ---------------------------------------------------------------------------
# 2. system_checker: dependency check produces correct messages
# ---------------------------------------------------------------------------

class TestSystemCheckerDependencies(unittest.TestCase):
    """system_checker.check_dependencies() must report hid native-lib failures clearly."""

    def setUp(self):
        for key in list(sys.modules):
            if key.startswith("thermalright_lcd_control"):
                del sys.modules[key]

    def _run_dep_check_with_hid_error(self, error_message: str):
        """Helper: run check_dependencies with a simulated hid ImportError."""
        from thermalright_lcd_control.diagnostics.system_checker import SystemChecker
        checker = SystemChecker()

        def fake_import(name, *args, **kwargs):
            if name == "hid":
                raise ImportError(error_message)
            return original_import(name, *args, **kwargs)

        original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

        with patch("builtins.__import__", side_effect=fake_import):
            checker.check_dependencies()

        return checker.checks[0]

    def test_hid_native_library_error_message_is_descriptive(self):
        """When hidapi DLL is missing the display message must mention the native library."""
        bad_message = (
            "Unable to load any of the following libraries:"
            "libhidapi-hidraw.so libhidapi-hidraw.so.0 "
            "hidapi.dll libhidapi-0.dll"
        )
        # Simulate: hid is importable at the outer level so we test the checker directly
        from thermalright_lcd_control.diagnostics.system_checker import SystemChecker
        checker = SystemChecker()

        # Temporarily replace hid in sys.modules with a broken entry
        broken = MagicMock(side_effect=ImportError(bad_message))
        with patch.dict(sys.modules, {"hid": None}):
            # Force the import inside check_dependencies to raise
            original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

            def fake_import(name, *args, **kwargs):
                if name == "hid":
                    raise ImportError(bad_message)
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=fake_import):
                checker.check_dependencies()

        check = checker.checks[0]
        self.assertFalse(check.passed)
        self.assertIn("native hidapi library missing", check.message)

    def test_hid_native_library_fix_hint_uses_pip_name(self):
        """fix_hint must contain the plain pip package name 'hid', not the verbose label."""
        bad_message = "hidapi.dll not found"
        from thermalright_lcd_control.diagnostics.system_checker import SystemChecker
        checker = SystemChecker()

        original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

        def fake_import(name, *args, **kwargs):
            if name == "hid":
                raise ImportError(bad_message)
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            checker.check_dependencies()

        check = checker.checks[0]
        self.assertIsNotNone(check.fix_hint)
        # fix_hint should say "pip install hid", NOT "pip install hid (native..."
        self.assertIn("pip install", check.fix_hint)
        self.assertNotIn("native hidapi library missing", check.fix_hint)

    def test_all_packages_present_passes(self):
        """check_dependencies must pass when all packages import successfully."""
        from thermalright_lcd_control.diagnostics.system_checker import SystemChecker

        mock_module = MagicMock()
        packages_to_mock = {
            "PySide6": mock_module,
            "psutil": mock_module,
            "cv2": mock_module,
            "usb": mock_module,
            "PIL": mock_module,
            "yaml": mock_module,
            "hid": mock_module,
        }
        with patch.dict(sys.modules, packages_to_mock):
            checker = SystemChecker()
            checker.check_dependencies()

        check = checker.checks[0]
        self.assertTrue(check.passed)
        self.assertEqual(check.message, "All required packages are installed")


# ---------------------------------------------------------------------------
# 3. system_checker: Windows-specific HID/libusb checks
# ---------------------------------------------------------------------------

class TestSystemCheckerWindowsChecks(unittest.TestCase):
    """_check_hidapi_native_library and _check_libusb_native_library behave correctly."""

    def setUp(self):
        for key in list(sys.modules):
            if key.startswith("thermalright_lcd_control"):
                del sys.modules[key]

    def test_hidapi_check_passes_when_hid_loads(self):
        from thermalright_lcd_control.diagnostics.system_checker import SystemChecker
        checker = SystemChecker()
        with patch.dict(sys.modules, {"hid": MagicMock()}):
            checker._check_hidapi_native_library()
        self.assertTrue(checker.checks[0].passed)
        self.assertIn("successfully", checker.checks[0].message)

    def test_hidapi_check_fails_with_actionable_hint(self):
        from thermalright_lcd_control.diagnostics.system_checker import SystemChecker
        checker = SystemChecker()

        original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

        def fake_import(name, *args, **kwargs):
            if name == "hid":
                raise ImportError("hidapi.dll not found")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            checker._check_hidapi_native_library()

        check = checker.checks[0]
        self.assertFalse(check.passed)
        self.assertIsNotNone(check.fix_hint)
        self.assertIn("hidapi/releases", check.fix_hint)

    def test_libusb_check_passes_when_backend_available(self):
        from thermalright_lcd_control.diagnostics.system_checker import SystemChecker
        checker = SystemChecker()

        mock_backend = MagicMock()
        # Patch at the attribute level so the already-imported module is affected
        with patch("usb.backend.libusb1.get_backend", return_value=mock_backend):
            checker._check_libusb_native_library()

        self.assertTrue(checker.checks[0].passed)

    def test_libusb_check_fails_with_actionable_hint(self):
        from thermalright_lcd_control.diagnostics.system_checker import SystemChecker
        checker = SystemChecker()

        mock_libusb1 = MagicMock()
        mock_libusb1.get_backend.return_value = None  # no backend found

        with patch.dict(sys.modules, {"usb.backend.libusb1": mock_libusb1}):
            checker._check_libusb_native_library()

        check = checker.checks[0]
        self.assertFalse(check.passed)
        self.assertIn("libusb-package", check.fix_hint)


# ---------------------------------------------------------------------------
# 4. supported_devices: registry integrity
# ---------------------------------------------------------------------------

class TestSupportedDevicesRegistry(unittest.TestCase):
    """SUPPORTED_DEVICES must contain the expected VID/PID entries."""

    def setUp(self):
        for key in list(sys.modules):
            if key.startswith("thermalright_lcd_control"):
                del sys.modules[key]
        sys.modules.pop("hid", None)

    def test_all_three_device_families_present(self):
        from thermalright_lcd_control.common.supported_devices import SUPPORTED_DEVICES
        vids_pids = {(v, p) for v, p, _ in SUPPORTED_DEVICES}
        self.assertIn((0x0418, 0x5304), vids_pids)
        self.assertIn((0x0416, 0x5302), vids_pids)
        self.assertIn((0x87AD, 0x70DB), vids_pids)

    def test_each_entry_has_device_info_list(self):
        from thermalright_lcd_control.common.supported_devices import SUPPORTED_DEVICES
        for vid, pid, devices in SUPPORTED_DEVICES:
            self.assertIsInstance(devices, list)
            self.assertGreater(len(devices), 0)
            for info in devices:
                self.assertIn("class_name", info)
                self.assertIn("width", info)
                self.assertIn("height", info)


if __name__ == "__main__":
    unittest.main()
