"""Automated tests for Boxinator geometry, presets, exports, and GUI."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from boxinator.geometry import BoxDesign, edge_check
from boxinator.params import (
    BUILT_IN,
    CADDY,
    DIAMONDS,
    DRAWER_UNIT,
    FIRM,
    GENTLE,
    HEX_WINDOWS,
    HEXAGON,
    KINDS,
    LIDDED_BOX,
    OCTAGON,
    ORGANISER,
    PARTS_BIN,
    PATTERNS,
    RECTANGLE,
    RIBS,
    RINGS,
    SHAPES,
    SLIDE_IN,
    SLIDE_LID,
    SMOOTH,
    SNUG,
    SQUARE,
    TRAY_LID,
    BoxParams,
)
from boxinator.presets import GALLERY, surprise
from boxinator.report import info_html, print_steps_html
from boxinator.stl import read_stl, write_binary_stl
from boxinator.threemf import read_3mf, write_3mf


class TestBoxinator(unittest.TestCase):
    def test_all_gallery_presets_watertight_and_support_free(self):
        for title, subtitle, spec in GALLERY:
            with self.subTest(preset=title):
                p = BoxParams.from_dict(spec)
                d = BoxDesign(p)
                self.assertFalse(d.errors, f"{title} had errors: {d.errors}")
                self.assertTrue(d.closed, f"{title} mesh is not closed/watertight")
                self.assertLessEqual(
                    d.worst, p.max_overhang + 0.5, f"{title} overhang {d.worst:.1f} exceeds {p.max_overhang}"
                )
                for acc in d.accessories:
                    ok, bad = edge_check(acc["faces_bed"])
                    self.assertTrue(ok, f"{title} accessory {acc['name']} has {bad} unmatched edges")

    def test_roles_shapes_dividers_and_lids(self):
        cases = [
            dict(kind=ORGANISER, shape=RECTANGLE, div_mode=SLIDE_IN, div_x=3, div_y=2, label_slot=True),
            dict(kind=LIDDED_BOX, shape=RECTANGLE, lid_style=TRAY_LID, div_mode=BUILT_IN, div_x=2, div_y=2),
            dict(kind=LIDDED_BOX, shape=SQUARE, lid_style=SLIDE_LID, div_mode=BUILT_IN, div_x=2, div_y=2),
            dict(kind=DRAWER_UNIT, shape=RECTANGLE, div_x=2, div_y=3, drawer_stop=True),
            dict(kind=PARTS_BIN, shape=RECTANGLE, bin_scoop_pct=50.0, div_x=2, div_y=1),
            dict(kind=CADDY, shape=RECTANGLE, caddy_handle_h=32.0, div_x=2, div_y=2),
            dict(kind=ORGANISER, shape=HEXAGON, pattern=RIBS, div_x=2, div_y=1),
            dict(kind=ORGANISER, shape=OCTAGON, pattern=HEX_WINDOWS, div_x=2, div_y=2),
        ]
        for idx, spec in enumerate(cases):
            with self.subTest(case=idx, spec=spec):
                p = BoxParams.from_dict(spec)
                d = BoxDesign(p)
                self.assertFalse(d.errors)
                self.assertTrue(d.closed)
                html = info_html(d)
                self.assertIn("closed &amp; watertight ✓", html)
                steps = print_steps_html(d)
                self.assertIn("Supports off", steps)

    def test_persistence_stl_and_3mf_roundtrip(self):
        p = BoxParams(kind=DRAWER_UNIT, div_x=2, div_y=2)
        d = BoxDesign(p)
        with tempfile.TemporaryDirectory() as tmp:
            box_file = Path(tmp) / "test.box"
            p.save(box_file)
            loaded = BoxParams.load(box_file)
            self.assertEqual(loaded.to_dict(), p.to_dict())

            stl_file = Path(tmp) / "body.stl"
            write_binary_stl(stl_file, d.verts, d.faces)
            sv, sf = read_stl(stl_file)
            self.assertEqual(len(sf), len(d.faces))
            self.assertTrue(edge_check(sf)[0])

            tmf_file = Path(tmp) / "full.3mf"
            write_3mf(tmf_file, d, p)
            parts = read_3mf(tmf_file)
            self.assertEqual(len(parts), 2)  # cubby shell + sliding drawer
            for nm, pv, pf, fil, pos in parts:
                self.assertTrue(edge_check(pf)[0], f"3MF part {nm} not closed")

    def test_surprise_generator(self):
        for seed in range(8):
            p = surprise(seed=seed)
            d = BoxDesign(p)
            self.assertFalse(d.errors)
            self.assertTrue(d.closed)

    def test_gui_headless_workflow(self):
        from PySide6.QtWidgets import QApplication
        from boxinator.app import MainWindow

        app = QApplication.instance() or QApplication([])
        win = MainWindow()
        self.assertIsNotNone(win.design)
        self.assertTrue(win.design.closed)

        # Switch through view modes including 2x2 Connected Cluster, Section, Overhang, Bed
        for rb in (win.rb_cluster, win.rb_section, win.rb_overhang, win.rb_bed, win.rb_asm):
            rb.setChecked(True)
            app.processEvents()
            self.assertGreater(len(win.viewer.meshes), 0)

        # Load Side Drawer Unit preset and test undo/redo
        win._apply_preset_dict(GALLERY[1][0], GALLERY[1][2])
        self.assertEqual(win.params.kind, DRAWER_UNIT)
        self.assertEqual(len(win.design.accessories), 1)
        win._on_undo()
        self.assertEqual(win.params.kind, ORGANISER)
        win._on_redo()
        self.assertEqual(win.params.kind, DRAWER_UNIT)

        # Verify every interactive control, group box, label, and tab has a tooltip
        from PySide6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDoubleSpinBox,
            QGroupBox,
            QLabel,
            QPushButton,
            QRadioButton,
            QSlider,
        )

        for tab_idx in range(win.tabs.count()):
            self.assertTrue(win.tabs.tabToolTip(tab_idx), f"Tab {tab_idx} missing tooltip")

        for cls in (QSlider, QDoubleSpinBox, QComboBox, QCheckBox, QRadioButton, QPushButton, QGroupBox, QLabel):
            for w in win.findChildren(cls):
                if not w.objectName().startswith("qt_"):
                    self.assertTrue(
                        bool(w.toolTip().strip()),
                        f"{cls.__name__} '{getattr(w, 'text', lambda: w.objectName())()}' is missing a tooltip",
                    )

        win.close()


if __name__ == "__main__":
    unittest.main()
