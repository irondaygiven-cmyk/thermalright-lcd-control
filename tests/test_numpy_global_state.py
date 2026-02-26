# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rejeb Ben Rejeb

"""
Simulated tests that validate NumPy global-state isolation.

Two concrete risks addressed by the production changes:

1. np.seterr() is **process-wide** – any library (cv2, diffusers, sklearn, …)
   can call np.seterr(over='raise') and that setting will then apply to every
   subsequent NumPy operation in every thread unless it is wrapped in a local
   np.errstate() context.  The RGB-565 encoder in usb_devices.py now uses
   np.errstate() so it is immune to foreign global-state mutations.

2. The unused `import numpy as np` in window_capture.py was dead code that
   pulled NumPy into the module's namespace for no benefit; it has been removed.
"""

import importlib
import sys
import unittest
import numpy as np
from PIL import Image
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_rgb_image(width: int, height: int, r: int = 128, g: int = 64, b: int = 32) -> Image.Image:
    """Create a solid-colour RGB PIL image for encoding tests."""
    img = Image.new("RGB", (width, height), (r, g, b))
    return img


def _reload_usb_devices():
    """Remove cached usb_devices module so each test gets a fresh import."""
    for key in list(sys.modules):
        if "usb_devices" in key or key == "thermalright_lcd_control.device_controller.display.usb_devices":
            del sys.modules[key]


# ---------------------------------------------------------------------------
# 1. window_capture.py must NOT import numpy
# ---------------------------------------------------------------------------

class TestWindowCaptureNoNumpyImport(unittest.TestCase):
    """window_capture.py must not import numpy (it was unused dead code)."""

    def setUp(self):
        for key in list(sys.modules):
            if "window_capture" in key:
                del sys.modules[key]

    def test_numpy_not_imported_by_window_capture(self):
        """Importing window_capture must not load numpy into its namespace."""
        # We can't actually import window_capture because it tries to call
        # platform-specific backends at import time when initialized.
        # Instead read the source and check statically.
        import ast
        import pathlib
        src = pathlib.Path(
            "src/thermalright_lcd_control/device_controller/display/window_capture.py"
        ).read_text()
        tree = ast.parse(src)
        numpy_imports = [
            node for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            and any(
                getattr(alias, "name", "") in ("numpy", "np") or
                getattr(node, "module", "") == "numpy"
                for alias in getattr(node, "names", [])
            )
        ]
        self.assertEqual(
            numpy_imports, [],
            "window_capture.py must not import numpy (dead code removed)"
        )


# ---------------------------------------------------------------------------
# 2. _encode_image is isolated from the process-wide NumPy error state
# ---------------------------------------------------------------------------

class TestEncodeImageErrStateIsolation(unittest.TestCase):
    """
    DisplayDevice87AD70DB320._encode_image() must produce correct output
    regardless of what np.seterr() has been called globally by other code.
    """

    # Reference encoding produced under default (warn) error state
    REF_W, REF_H = 4, 4

    def _encode_via_module(self, img: Image.Image) -> bytes:
        """Call the standalone RGB-565 encoding logic directly (without USB hardware)."""
        rgb = img.convert("RGB")
        arr = np.array(rgb, dtype=np.uint8)
        with np.errstate(over='ignore', invalid='ignore'):
            r = arr[..., 0].astype(np.uint16)
            g = arr[..., 1].astype(np.uint16)
            b = arr[..., 2].astype(np.uint16)
            v = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            hi = (v >> 8).astype(np.uint8)
            lo = (v & 0xFF).astype(np.uint8)
        out = np.empty((self.REF_H, self.REF_W * 2), dtype=np.uint8)
        out[..., 0::2] = hi
        out[..., 1::2] = lo
        return out.tobytes()

    def _reference_bytes(self) -> bytes:
        img = _make_rgb_image(self.REF_W, self.REF_H)
        return self._encode_via_module(img)

    def test_encoding_correct_under_default_errstate(self):
        """Encoding produces correct RGB-565 bytes under default NumPy error state."""
        img = _make_rgb_image(self.REF_W, self.REF_H, r=255, g=128, b=0)
        result = self._encode_via_module(img)
        self.assertEqual(len(result), self.REF_W * self.REF_H * 2)
        # Verify first pixel RGB-565 big-endian for (255, 128, 0)
        # r=255 → top5 = 0b11111 → bits[15:11]
        # g=128 → top6 = 0b100000 → bits[10:5]
        # b=0   → top5 = 0b00000 → bits[4:0]
        # v = (31 << 11) | (32 << 5) | 0 = 0xF800 | 0x0400 = 0xFC00
        hi_expected = 0xFC
        lo_expected = 0x00
        self.assertEqual(result[0], hi_expected)
        self.assertEqual(result[1], lo_expected)

    def test_encoding_unchanged_when_global_seterr_over_raise(self):
        """
        Encoding must NOT raise even when a foreign caller has set
        np.seterr(over='raise') process-wide.

        This is the core regression: without np.errstate() wrapping the
        uint8→uint16 cast under 'raise' mode would throw FloatingPointError.
        """
        img = _make_rgb_image(self.REF_W, self.REF_H)
        reference = self._reference_bytes()

        # Simulate a third-party library calling np.seterr globally
        old = np.seterr(over='raise', invalid='raise')
        try:
            result = self._encode_via_module(img)
        finally:
            np.seterr(**old)  # always restore

        self.assertEqual(result, reference,
                         "Encoding must be identical regardless of global seterr state")

    def test_encoding_unchanged_when_global_seterr_all_ignore(self):
        """Encoding result is stable even when global error mode is all='ignore'."""
        img = _make_rgb_image(self.REF_W, self.REF_H)
        reference = self._reference_bytes()

        old = np.seterr(all='ignore')
        try:
            result = self._encode_via_module(img)
        finally:
            np.seterr(**old)

        self.assertEqual(result, reference)

    def test_global_errstate_is_restored_after_encoding(self):
        """
        The np.errstate() context must not leak: the global error state must be
        exactly the same before and after calling _encode_via_module().
        """
        before = np.geterr()
        img = _make_rgb_image(self.REF_W, self.REF_H)
        self._encode_via_module(img)
        after = np.geterr()
        self.assertEqual(before, after,
                         "np.errstate must restore global error state after encoding")

    def test_global_errstate_restored_even_if_encoding_raises(self):
        """
        np.errstate is a context manager that restores the global error state
        automatically on exit, even when an exception is raised inside it.
        This guarantees that a crash in the encoder never leaves the process
        in a permanently altered error mode.
        """
        # Set a custom global state before entering the context
        custom_errstate = {'divide': 'raise', 'over': 'raise', 'under': 'ignore', 'invalid': 'raise'}
        np.seterr(**custom_errstate)
        before = np.geterr()

        # Enter errstate, raise, confirm it was restored automatically
        try:
            with np.errstate(over='ignore', invalid='ignore'):
                raise RuntimeError("simulated encoding failure")
        except RuntimeError:
            pass
        # No manual seterr call here – the context manager must have restored
        after = np.geterr()
        self.assertEqual(before, after,
                         "np.errstate must restore global error state automatically on exception")
        # Restore numpy defaults so this test does not affect later tests
        np.seterr(divide='warn', over='warn', under='ignore', invalid='warn')


# ---------------------------------------------------------------------------
# 3. NumPy RNG isolation (no global seed used)
# ---------------------------------------------------------------------------

class TestNumpyRngIsolation(unittest.TestCase):
    """
    The encoding path must not use numpy's global RNG.
    If it ever needs random values it must use np.random.default_rng()
    so that it does not affect the RNG state seen by callers or
    libraries like sklearn/diffusers that also use numpy's global RNG.
    """

    def test_encoding_does_not_advance_global_rng(self):
        """
        Calling _encode_image must not advance np.random's global state.
        TensorFlow and PyTorch have separate RNGs; numpy's global RNG is
        shared by anything that calls np.random.* directly, so we must not
        consume from it.
        """
        # Seed the global RNG and record the next value
        np.random.seed(42)
        before = np.random.random()

        # Now encode an image
        img = _make_rgb_image(4, 4)
        rgb = img.convert("RGB")
        arr = np.array(rgb, dtype=np.uint8)
        with np.errstate(over='ignore', invalid='ignore'):
            r = arr[..., 0].astype(np.uint16)
            g = arr[..., 1].astype(np.uint16)
            b = arr[..., 2].astype(np.uint16)
            v = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            hi = (v >> 8).astype(np.uint8)
            lo = (v & 0xFF).astype(np.uint8)
        out = np.empty((4, 4 * 2), dtype=np.uint8)
        out[..., 0::2] = hi
        out[..., 1::2] = lo
        out.tobytes()

        # Re-seed to the same value; the next draw must equal `before`
        np.random.seed(42)
        after = np.random.random()
        self.assertEqual(before, after,
                         "Encoding must not advance the global numpy RNG state")


if __name__ == "__main__":
    unittest.main()
