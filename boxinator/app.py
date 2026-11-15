"""Focused PySide6 desktop interface for Boxinator."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProxyStyle,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QStatusBar,
    QStyle,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .geometry import BoxDesign, translate_mesh
from .params import (
    ACCENT_PARTS,
    BANDS,
    BUILT_IN,
    CADDY,
    COLOUR_NAMES,
    DIV_MODE_NAMES,
    DRAWER_UNIT,
    FIT_NAMES,
    HEXAGON,
    KIND_NAMES,
    LID_STYLE_NAMES,
    LIDDED_BOX,
    LOOK_NAMES,
    OCTAGON,
    ONE_COLOUR,
    ORGANISER,
    PARTS_BIN,
    PATTERN_NAMES,
    RECTANGLE,
    SHAPE_NAMES,
    SLIDE_IN,
    SMOOTH,
    SQUARE,
    BoxParams,
)
from .presets import GALLERY, PALETTES, surprise
from .report import HELP_HTML, info_html, print_steps_html
from .slicers import find_slicers, open_in_slicer
from .stl import write_binary_stl
from .threemf import write_3mf
from .tooltips import (
    COLOUR_ITEM_TIPS,
    DIV_MODE_ITEM_TIPS,
    FIT_ITEM_TIPS,
    KIND_ITEM_TIPS,
    LID_STYLE_ITEM_TIPS,
    LOOK_ITEM_TIPS,
    PATTERN_ITEM_TIPS,
    SHAPE_ITEM_TIPS,
    TIPS,
)
from .viewer import Viewer3D

DARK_QSS = """
QMainWindow, QDialog { background: #16181d; color: #e6e9ef; }
QWidget { color: #e6e9ef; font-size: 12px; }
QToolTip {
    background-color: #1b2230;
    color: #f0f4fc;
    border: 1px solid #4c8bf5;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 12px;
}
QScrollArea, QWidget#scroll_page { background: #181b21; border: none; }
QGroupBox {
    background: #1d2027; border: 1px solid #2b303c; border-radius: 6px;
    margin-top: 14px; padding: 14px 10px 10px 10px; font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    left: 10px; top: 0px; padding: 1px 7px;
    background: #1d2027; border: 1px solid #2b303c; border-radius: 3px;
    color: #8ab4f8;
}
QCheckBox { spacing: 7px; padding: 2px 0px; }
QTabWidget::pane { border: 1px solid #2b303c; background: #181b21; border-radius: 6px; }
QTabBar::tab {
    background: #1d2027; color: #aab2c0; padding: 7px 11px; margin-right: 2px;
    border-top-left-radius: 5px; border-top-right-radius: 5px; border: 1px solid #2b303c;
}
QTabBar::tab:selected { background: #263147; color: #ffffff; border-bottom-color: #8ab4f8; font-weight: 600; }
QPushButton {
    background: #282d37; border: 1px solid #383f4d; border-radius: 5px;
    padding: 6px 11px; color: #e6e9ef;
}
QPushButton:hover { background: #323946; border-color: #525c70; }
QPushButton:pressed { background: #22262f; }
QPushButton:disabled { color: #656b78; background: #1c1f26; border-color: #272b34; }
QPushButton#primary {
    background: #2b5b84; border-color: #3e7cb1; font-weight: 600; padding: 8px 14px; color: #ffffff;
}
QPushButton#primary:hover { background: #356d9c; }
QComboBox, QDoubleSpinBox, QListWidget, QTextBrowser {
    background: #14161b; border: 1px solid #323846; border-radius: 4px; padding: 4px 6px;
}
QSlider::groove:horizontal { height: 6px; background: #2b303c; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #4c8bf5; border-radius: 3px; }
QSlider::handle:horizontal {
    width: 14px; height: 14px; margin: -4px 0; background: #e6e9ef; border: 1px solid #4c8bf5; border-radius: 7px;
}
QScrollBar:vertical {
    background: #16181d; width: 10px; margin: 0px; border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #323846; min-height: 24px; border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QMenuBar { background: #1c1f26; border-bottom: 1px solid #2b303c; }
QMenuBar::item:selected { background: #2c323f; }
QMenu { background: #1d2027; border: 1px solid #323846; }
QMenu::item:selected { background: #2b5b84; }
QSplitter::handle { background: #262b36; width: 2px; }
QStatusBar { background: #14161b; color: #9aa2b1; border-top: 1px solid #2b303c; }
"""


def _app_icon() -> QIcon:
    import sys

    roots = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        roots.append(Path(sys._MEIPASS))
    roots.append(Path(__file__).resolve().parent.parent)
    for root in roots:
        for rel in ("assets/icon.png", "assets/icon.ico"):
            cand = root / rel
            if cand.exists():
                ico = QIcon(str(cand))
                if not ico.isNull():
                    return ico

    pm = QPixmap(64, 64)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor("#2b6cb0"))
    p.setPen(QColor("#90cdf4"))
    p.drawRoundedRect(6, 10, 52, 44, 8, 8)
    p.setPen(QColor("#e2e8f0"))
    p.drawLine(24, 10, 24, 54)
    p.drawLine(40, 10, 40, 54)
    p.drawLine(6, 32, 58, 32)
    p.end()
    return QIcon(pm)


class _FastTooltipStyle(QProxyStyle):
    """Pops up tooltips quickly (~140 ms) and keeps them visible while reading."""

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_ToolTip_WakeUpDelay:
            return 140
        if hint == QStyle.SH_ToolTip_FallAsleepDelay:
            return 20000
        return super().styleHint(hint, option, widget, returnData)


class _SliderSpin(QWidget):
    """Synchronized horizontal slider and spinbox for a numeric parameter."""

    valueChanged = Signal(float)

    def __init__(self, lo: float, hi: float, step: float = 1.0, decimals: int = 1, suffix: str = ""):
        super().__init__()
        self._scale = round(1.0 / max(step, 1e-4))
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(int(round(lo * self._scale)), int(round(hi * self._scale)))
        self.spin = QDoubleSpinBox()
        self.spin.setRange(lo, hi)
        self.spin.setSingleStep(step)
        self.spin.setDecimals(decimals)
        if suffix:
            self.spin.setSuffix(f" {suffix}")
        self.spin.setFixedWidth(108)
        lay.addWidget(self.slider, 1)
        lay.addWidget(self.spin)
        self.slider.valueChanged.connect(self._on_slider)
        self.spin.valueChanged.connect(self._on_spin)

    def setToolTip(self, tip: str):
        super().setToolTip(tip)
        self.slider.setToolTip(tip)
        self.spin.setToolTip(tip)

    def _on_slider(self, v: int):
        val = v / self._scale
        self.spin.blockSignals(True)
        self.spin.setValue(val)
        self.spin.blockSignals(False)
        self.valueChanged.emit(val)

    def _on_spin(self, val: float):
        self.slider.blockSignals(True)
        self.slider.setValue(int(round(val * self._scale)))
        self.slider.blockSignals(False)
        self.valueChanged.emit(float(val))

    def value(self) -> float:
        return float(self.spin.value())

    def setValue(self, val: float):
        self.spin.blockSignals(True)
        self.slider.blockSignals(True)
        self.spin.setValue(float(val))
        self.slider.setValue(int(round(float(val) * self._scale)))
        self.spin.blockSignals(False)
        self.slider.blockSignals(False)


class PresetDialog(QDialog):
    """Modal gallery dialog to pick one of the 10 curated Boxinator starter designs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose a Boxinator Preset")
        self.resize(520, 420)
        self.chosen: dict | None = None
        lay = QVBoxLayout(self)
        lbl = QLabel("Pick a starter design to load into Boxinator (double-click any item to load):")
        lay.addWidget(lbl)
        self.list = QListWidget()
        self.list.setToolTip(
            "<b>Preset Gallery:</b><br>Click a preset to select it, or double-click to load it immediately "
            "into the 3D designer."
        )
        for name, sub, d in GALLERY:
            item = QListWidgetItem(f"{name}\n   {sub}")
            item.setData(Qt.UserRole, (name, d))
            role_lbl = KIND_NAMES.get(d.get("kind", ORGANISER), "Box")
            dims = f"{d.get('length', 120)} × {d.get('width', d.get('length', 80))} × {d.get('height', 65)} mm"
            divs = f"{d.get('div_x', 1)} × {d.get('div_y', 1)} compartments"
            item.setToolTip(
                f"<b>{name}</b><br>{sub}<br>"
                f"• <b>Role:</b> {role_lbl}<br>"
                f"• <b>Outside size:</b> {dims}<br>"
                f"• <b>Interior grid:</b> {divs}"
            )
            self.list.addItem(item)
        self.list.setCurrentRow(0)
        self.list.itemDoubleClicked.connect(self._accept)
        lay.addWidget(self.list, 1)
        btns = QHBoxLayout()
        btns.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.setToolTip("Close this dialog without changing your current box design.")
        ok = QPushButton("Load Preset")
        ok.setObjectName("primary")
        ok.setToolTip("Load the selected preset into Boxinator (you can still customize every slider afterward!).")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self._accept)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        lay.addLayout(btns)

    def _accept(self):
        item = self.list.currentItem()
        if item is not None:
            name, d = item.data(Qt.UserRole)
            self.chosen = dict(d, name=name.lower().replace(" ", "_"))
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        app = QApplication.instance()
        if app is not None and not isinstance(app.style(), _FastTooltipStyle):
            app.setStyle(_FastTooltipStyle(app.style()))
        self.setWindowTitle(f"Boxinator {__version__} — Stackable, Connectable & Side-Drawer Box Designer")
        self.setWindowIcon(_app_icon())
        self.resize(1380, 860)
        self.setStyleSheet(DARK_QSS)

        self.params = BoxParams()
        self.design: BoxDesign | None = None
        self.current_path: Path | None = None
        self._updating = False
        self._camera_initialized = False

        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []
        self._last_pushed: dict = self.params.to_dict()

        self._slicers = find_slicers()

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(45)
        self._timer.timeout.connect(self._rebuild)

        self._build_menus()
        self._build_ui()
        self.setStatusBar(QStatusBar())
        self.statusBar().setToolTip(
            "<b>Live Print Check Bar:</b> Shows active box role, total compartments, accessory count, "
            "filament weight estimate, steepest overhang angle, and manifold watertight status."
        )
        self._load_params(self.params, push_undo=False, fit_camera=True)

    # ------------------------------------------------------------------ menus
    def _build_menus(self):
        mb = self.menuBar()
        fmenu = mb.addMenu("&File")
        fmenu.setToolTipsVisible(True)
        self._add_action(
            fmenu, "&New Default Box", self._on_new, QKeySequence.New,
            "Reset all parameters back to the default 2×2 Desk Organiser box.",
        )
        self._add_action(
            fmenu, "&Open Project (.box)…", self._on_open, QKeySequence.Open,
            "Load a previously saved Boxinator project file (.box or .json).",
        )
        self._add_action(
            fmenu, "&Save Project (.box)", self._on_save, QKeySequence.Save,
            "Save your current slider settings and colours to a Boxinator (.box) project file.",
        )
        self._add_action(
            fmenu, "Save Project &As…", self._on_save_as, QKeySequence("Ctrl+Shift+S"),
            "Save your current design under a new (.box) project filename.",
        )
        fmenu.addSeparator()
        self._add_action(
            fmenu, "Export &3MF for Printing…", self._on_export_3mf, QKeySequence("Ctrl+E"),
            "Export a complete, ready-to-print .3mf file containing all parts and filament colours.",
        )
        self._add_action(
            fmenu, "Export Main &Body STL…", self._on_export_body_stl, None,
            "Export only the main box body (or outer cubby shell) as a binary .stl file.",
        )
        self._add_action(
            fmenu, "Export &Accessory STL (Lid / Drawer / Dividers)…", self._on_export_acc_stl, None,
            "Export the matching lid, sliding drawer, or slide-in divider set as a binary .stl file.",
        )
        fmenu.addSeparator()
        self._add_action(
            fmenu, "Open in &Slicer", self._on_open_slicer, QKeySequence("Ctrl+P"),
            "Export the print-bed .3mf and launch it directly in your target 3D slicer.",
        )
        self._add_action(
            fmenu, "Save 3D &Picture (.png)…", self._on_screenshot, None,
            "Save a high-resolution PNG snapshot of the current 3D viewport.",
        )
        fmenu.addSeparator()
        self._add_action(fmenu, "&Quit", self.close, QKeySequence.Quit, "Close Boxinator.")

        emenu = mb.addMenu("&Edit")
        emenu.setToolTipsVisible(True)
        self.act_undo = self._add_action(
            emenu, "&Undo", self._on_undo, QKeySequence.Undo, "Undo the last parameter change."
        )
        self.act_redo = self._add_action(
            emenu, "&Redo", self._on_redo, QKeySequence.Redo, "Redo the previously undone parameter change."
        )
        emenu.addSeparator()
        self._add_action(
            emenu, "&Copy Summary Report", self._on_copy_report, None,
            "Copy the current box dimensions, compartment metrics, and print stats to the clipboard.",
        )

        pmenu = mb.addMenu("&Presets")
        pmenu.setToolTipsVisible(True)
        self._add_action(
            pmenu, "&Preset Gallery…", self._on_preset_dialog, QKeySequence("Ctrl+G"),
            "Open the visual gallery of 10 curated starter designs.",
        )
        self._add_action(
            pmenu, "&Surprise Me!", self._on_surprise, QKeySequence("Ctrl+R"),
            "Generate a random, guaranteed-printable box, drawer unit, or parts bin.",
        )
        pmenu.addSeparator()
        for name, sub, d in GALLERY:
            act = QAction(f"{name} — {sub}", self)
            act.setToolTip(f"<b>{name}:</b> {sub}")
            act.triggered.connect(lambda checked=False, nm=name, dd=d: self._apply_preset_dict(nm, dd))
            pmenu.addAction(act)

        hmenu = mb.addMenu("&Help")
        hmenu.setToolTipsVisible(True)
        self._add_action(
            hmenu, "&How to Print & Assemble…", self._on_help_print, None,
            "Show step-by-step printing and assembly instructions for the current box role.",
        )
        self._add_action(
            hmenu, "&Guide & Tips…", self._on_help_guide, QKeySequence.HelpContents,
            "Open the Boxinator quick reference guide.",
        )
        self._add_action(
            hmenu, "&About Boxinator", self._on_about, None,
            "Version and overview of Boxinator.",
        )

    def _add_action(self, menu, text, slot, shortcut=None, tip: str = "") -> QAction:
        act = QAction(text, self)
        if shortcut is not None:
            act.setShortcut(shortcut)
        if tip:
            act.setToolTip(tip)
            act.setStatusTip(tip)
        act.triggered.connect(slot)
        menu.addAction(act)
        return act

    # ------------------------------------------------------------------ UI layout
    def _build_ui(self):
        splitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(splitter)

        # ================= LEFT PANEL (Focused Controls) =================
        left = QWidget()
        left.setMinimumWidth(425)
        left.setMaximumWidth(500)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(8, 8, 8, 8)
        left_lay.setSpacing(6)

        # Top quick bar: Role + Preset + Surprise
        top_box = QGroupBox("1. What are we making?")
        top_box.setToolTip(TIPS["top_box"])
        top_lay = QVBoxLayout(top_box)
        role_row = QHBoxLayout()
        lbl_role = QLabel("Role:")
        lbl_role.setToolTip(TIPS["kind"])
        role_row.addWidget(lbl_role)
        self.cmb_kind = self._combo(KIND_NAMES, KIND_ITEM_TIPS, TIPS["kind"])
        self.cmb_kind.currentIndexChanged.connect(self._on_ui_changed)
        role_row.addWidget(self.cmb_kind, 1)
        top_lay.addLayout(role_row)

        btn_row = QHBoxLayout()
        self.btn_presets = QPushButton("Choose a Preset…")
        self.btn_presets.setToolTip(TIPS["presets"])
        self.btn_presets.clicked.connect(self._on_preset_dialog)
        self.btn_surprise = QPushButton("Surprise Me!")
        self.btn_surprise.setToolTip(TIPS["surprise"])
        self.btn_surprise.clicked.connect(self._on_surprise)
        btn_row.addWidget(self.btn_presets, 1)
        btn_row.addWidget(self.btn_surprise)
        top_lay.addLayout(btn_row)

        # Interactive Open / Pull Out slider (shown for Lidded Box & Side Drawer Unit)
        self.pull_widget = QWidget()
        pull_lay = QHBoxLayout(self.pull_widget)
        pull_lay.setContentsMargins(0, 2, 0, 0)
        self.lbl_pull = QLabel("Drawer pull-out:")
        self.sld_pull = _SliderSpin(0.0, 100.0, 1.0, 0, "%")
        self.lbl_pull.setToolTip(TIPS["pull_drawer"])
        self.sld_pull.setToolTip(TIPS["pull_drawer"])
        self.sld_pull.valueChanged.connect(self._on_ui_changed)
        pull_lay.addWidget(self.lbl_pull)
        pull_lay.addWidget(self.sld_pull, 1)
        top_lay.addWidget(self.pull_widget)
        left_lay.addWidget(top_box)

        # Focused 3-Tab Designer
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_tab_size_dividers(), "Size && Dividers")
        self.tabs.addTab(self._build_tab_modular_role(), "Stack, Connect && Role")
        self.tabs.addTab(self._build_tab_surface_printer(), "Surface && Colours")
        self.tabs.setTabToolTip(0, TIPS["tab_size"])
        self.tabs.setTabToolTip(1, TIPS["tab_modular"])
        self.tabs.setTabToolTip(2, TIPS["tab_surface"])
        left_lay.addWidget(self.tabs, 1)

        # Bottom Export & Slicer Bar
        exp_frame = QFrame()
        exp_lay = QVBoxLayout(exp_frame)
        exp_lay.setContentsMargins(0, 2, 0, 0)
        exp_lay.setSpacing(5)
        self.btn_save_3mf = QPushButton("Save for Printing (3MF)…")
        self.btn_save_3mf.setObjectName("primary")
        self.btn_save_3mf.setToolTip(TIPS["save_3mf"])
        self.btn_save_3mf.clicked.connect(self._on_export_3mf)
        exp_lay.addWidget(self.btn_save_3mf)

        sub_row = QHBoxLayout()
        self.btn_save_acc = QPushButton("Save Accessory STL…")
        self.btn_save_acc.setToolTip(TIPS["save_acc_none"])
        self.btn_save_acc.clicked.connect(self._on_export_acc_stl)
        self.btn_slicer = QPushButton("Open in Slicer")
        self.btn_slicer.setToolTip(TIPS["open_slicer"])
        self.btn_slicer.clicked.connect(self._on_open_slicer)
        sub_row.addWidget(self.btn_save_acc, 1)
        sub_row.addWidget(self.btn_slicer, 1)
        exp_lay.addLayout(sub_row)
        left_lay.addWidget(exp_frame)

        splitter.addWidget(left)

        # ================= CENTRE PANEL (3D Viewer + View Modes) =================
        center = QWidget()
        c_lay = QVBoxLayout(center)
        c_lay.setContentsMargins(4, 8, 4, 8)
        c_lay.setSpacing(6)

        bar = QHBoxLayout()
        self.view_group = QButtonGroup(self)
        self.rb_asm = QRadioButton("Assembled View")
        self.rb_asm.setToolTip(TIPS["rb_asm"])
        self.rb_cluster = QRadioButton("2×2 Connected Cluster")
        self.rb_cluster.setToolTip(TIPS["rb_cluster"])
        self.rb_section = QRadioButton("Section Cut")
        self.rb_section.setToolTip(TIPS["rb_section"])
        self.rb_overhang = QRadioButton("Overhang Check")
        self.rb_overhang.setToolTip(TIPS["rb_overhang"])
        self.rb_bed = QRadioButton("Print Bed Layout")
        self.rb_bed.setToolTip(TIPS["rb_bed"])
        self.rb_asm.setChecked(True)
        for idx, rb in enumerate((self.rb_asm, self.rb_cluster, self.rb_section, self.rb_overhang, self.rb_bed)):
            self.view_group.addButton(rb, idx)
            bar.addWidget(rb)
            rb.toggled.connect(self._on_view_mode_changed)
        bar.addStretch(1)
        self.btn_fit = QPushButton("Reset Camera")
        self.btn_fit.setToolTip(TIPS["fit_cam"])
        self.btn_fit.clicked.connect(self._fit_camera)
        bar.addWidget(self.btn_fit)
        c_lay.addLayout(bar)

        self.viewer = Viewer3D(self)
        self.viewer.setToolTip(TIPS["viewer"])
        self.viewer.reset_requested.connect(self._fit_camera)
        c_lay.addWidget(self.viewer, 1)
        splitter.addWidget(center)

        # ================= RIGHT PANEL (Live Summary & Print Guide) =================
        right = QWidget()
        right.setMinimumWidth(295)
        right.setMaximumWidth(370)
        r_lay = QVBoxLayout(right)
        r_lay.setContentsMargins(6, 8, 8, 8)
        r_lay.setSpacing(6)
        lbl_rep = QLabel("<b>Design Summary &amp; Print Check</b>")
        lbl_rep.setToolTip(TIPS["report_box"])
        r_lay.addWidget(lbl_rep)
        self.report_box = QTextBrowser()
        self.report_box.setOpenExternalLinks(False)
        self.report_box.setToolTip(TIPS["report_box"])
        r_lay.addWidget(self.report_box, 1)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

    def _combo(
        self,
        items_dict: dict | None = None,
        item_tips: dict | None = None,
        base_tip: str = "",
    ) -> QComboBox:
        cmb = QComboBox()
        cmb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        cmb.setMinimumContentsLength(12)
        if base_tip:
            cmb.setToolTip(base_tip)
        if items_dict is not None:
            for i, (k, label) in enumerate(items_dict.items()):
                cmb.addItem(label, k)
                if item_tips and k in item_tips:
                    cmb.setItemData(i, item_tips[k], Qt.ToolTipRole)
        return cmb

    def _add_row(self, form: QFormLayout, label: str | QLabel, widget: QWidget, tip: str = "") -> QLabel:
        lbl = QLabel(label) if isinstance(label, str) else label
        if tip:
            lbl.setToolTip(tip)
            widget.setToolTip(tip)
        form.addRow(lbl, widget)
        return lbl

    def _form(self, parent: QWidget) -> QFormLayout:
        f = QFormLayout(parent)
        f.setContentsMargins(6, 8, 6, 6)
        f.setHorizontalSpacing(10)
        f.setVerticalSpacing(7)
        f.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        f.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        f.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        return f

    def _scroll_page(self) -> tuple[QScrollArea, QVBoxLayout]:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        page = QWidget()
        page.setObjectName("scroll_page")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(10)
        scroll.setWidget(page)
        return scroll, lay

    def _build_tab_size_dividers(self) -> QWidget:
        scroll, lay = self._scroll_page()

        # Shape & Outer Dimensions
        g_size = QGroupBox("Shape && Outer Dimensions")
        g_size.setToolTip(TIPS["grp_size"])
        f_size = self._form(g_size)
        self.cmb_shape = self._combo(SHAPE_NAMES, SHAPE_ITEM_TIPS, TIPS["shape"])
        self.cmb_shape.currentIndexChanged.connect(self._on_ui_changed)
        self._add_row(f_size, "Footprint shape:", self.cmb_shape, TIPS["shape"])

        self.sld_length = _SliderSpin(30.0, 240.0, 1.0, 1, "mm")
        self.sld_width = _SliderSpin(30.0, 240.0, 1.0, 1, "mm")
        self.sld_height = _SliderSpin(18.0, 220.0, 1.0, 1, "mm")
        self.sld_corner = _SliderSpin(1.5, 45.0, 0.5, 1, "mm")
        self.sld_wall = _SliderSpin(1.2, 5.0, 0.2, 1, "mm")
        self.sld_floor = _SliderSpin(1.2, 6.0, 0.2, 1, "mm")

        self.lbl_length = QLabel("Length (X):")
        self.lbl_width = QLabel("Width (Y):")
        self.lbl_height = QLabel("Height (Z):")
        self._add_row(f_size, self.lbl_length, self.sld_length, TIPS["length_box"])
        self._add_row(f_size, self.lbl_width, self.sld_width, TIPS["width_box"])
        self._add_row(f_size, self.lbl_height, self.sld_height, TIPS["height_box"])
        self._add_row(f_size, "Corner rounding:", self.sld_corner, TIPS["corner_r"])
        self._add_row(f_size, "Wall thickness:", self.sld_wall, TIPS["wall"])
        self._add_row(f_size, "Floor thickness:", self.sld_floor, TIPS["floor"])
        for w in (self.sld_length, self.sld_width, self.sld_height, self.sld_corner, self.sld_wall, self.sld_floor):
            w.valueChanged.connect(self._on_ui_changed)
        lay.addWidget(g_size)

        # Dividers & Interior
        g_div = QGroupBox("Dividers && Easy-Grab Interior")
        g_div.setToolTip(TIPS["grp_div"])
        f_div = self._form(g_div)
        self.sld_div_x = _SliderSpin(1, 8, 1, 0, "")
        self.sld_div_y = _SliderSpin(1, 8, 1, 0, "")
        self.cmb_div_mode = self._combo(DIV_MODE_NAMES, DIV_MODE_ITEM_TIPS, TIPS["div_mode"])
        self.sld_div_wall = _SliderSpin(1.0, 4.0, 0.2, 1, "mm")
        self.sld_div_h = _SliderSpin(35.0, 100.0, 5.0, 0, "%")
        self.sld_div_dip = _SliderSpin(0.0, 25.0, 1.0, 1, "mm")
        self.chk_scoop = QCheckBox("Curved finger-scoop floor (for small screws && tokens)")
        self.chk_scoop.setToolTip(TIPS["scoop"])

        self._add_row(f_div, "Columns across (X):", self.sld_div_x, TIPS["div_x"])
        self._add_row(f_div, "Rows front-to-back (Y):", self.sld_div_y, TIPS["div_y"])
        self._add_row(f_div, "Divider type:", self.cmb_div_mode, TIPS["div_mode"])
        self._add_row(f_div, "Divider thickness:", self.sld_div_wall, TIPS["div_wall"])
        self._add_row(f_div, "Divider height:", self.sld_div_h, TIPS["div_h"])
        self._add_row(f_div, "Finger-dip cutout:", self.sld_div_dip, TIPS["div_dip"])
        f_div.addRow(self.chk_scoop)

        for w in (self.sld_div_x, self.sld_div_y, self.sld_div_wall, self.sld_div_h, self.sld_div_dip):
            w.valueChanged.connect(self._on_ui_changed)
        self.cmb_div_mode.currentIndexChanged.connect(self._on_ui_changed)
        self.chk_scoop.toggled.connect(self._on_ui_changed)
        lay.addWidget(g_div)

        lay.addStretch(1)
        return scroll

    def _build_tab_modular_role(self) -> QWidget:
        scroll, lay = self._scroll_page()

        # Stack & Connect
        g_mod = QGroupBox("Stackable && Connectable")
        g_mod.setToolTip(TIPS["grp_mod"])
        f_mod = self._form(g_mod)
        self.chk_stack = QCheckBox("Stackable nesting base (45° support-free foot)")
        self.chk_stack.setToolTip(TIPS["stackable"])
        self.sld_stack_h = _SliderSpin(2.0, 8.0, 0.4, 1, "mm")
        self.chk_connect = QCheckBox("Connectable sides (interlocking XY dovetails)")
        self.chk_connect.setToolTip(TIPS["connectable"])
        self.sld_dove_d = _SliderSpin(1.6, 4.0, 0.2, 1, "mm")
        self.cmb_fit = self._combo(FIT_NAMES, FIT_ITEM_TIPS, TIPS["fit"])

        f_mod.addRow(self.chk_stack)
        self._add_row(f_mod, "Stacking foot depth:", self.sld_stack_h, TIPS["stack_h"])
        f_mod.addRow(self.chk_connect)
        self._add_row(f_mod, "Dovetail lock depth:", self.sld_dove_d, TIPS["dove_d"])
        self._add_row(f_mod, "Joint && sliding fit:", self.cmb_fit, TIPS["fit"])

        self.chk_stack.toggled.connect(self._on_ui_changed)
        self.sld_stack_h.valueChanged.connect(self._on_ui_changed)
        self.chk_connect.toggled.connect(self._on_ui_changed)
        self.sld_dove_d.valueChanged.connect(self._on_ui_changed)
        self.cmb_fit.currentIndexChanged.connect(self._on_ui_changed)
        lay.addWidget(g_mod)

        # Role-specific options (shown contextually so the UI stays super clean)
        self.grp_lid = QGroupBox("Lid Options (for Lidded Box)")
        self.grp_lid.setToolTip(TIPS["grp_lid"])
        f_lid = self._form(self.grp_lid)
        self.cmb_lid_style = self._combo(LID_STYLE_NAMES, LID_STYLE_ITEM_TIPS, TIPS["lid_style"])
        self.cmb_lid_style.currentIndexChanged.connect(self._on_ui_changed)
        self._add_row(f_lid, "Lid mechanism:", self.cmb_lid_style, TIPS["lid_style"])
        lay.addWidget(self.grp_lid)

        self.grp_drawer = QGroupBox("Side-Drawer Unit Options")
        self.grp_drawer.setToolTip(TIPS["grp_drawer"])
        f_drw = QVBoxLayout(self.grp_drawer)
        f_drw.setContentsMargins(6, 8, 6, 6)
        f_drw.setSpacing(6)
        self.chk_drawer_stop = QCheckBox("Anti-tip drawer stop catch (prevents falling out)")
        self.chk_drawer_stop.setToolTip(TIPS["drawer_stop"])
        self.chk_drawer_stop.toggled.connect(self._on_ui_changed)
        f_drw.addWidget(self.chk_drawer_stop)
        drw_note = QLabel(
            "<i>Clever print trick:</i> The outer Cubby Shell prints upright on its closed back wall "
            "with zero supports. Its Right and Top walls carry Male Dovetail Tails while its Left and "
            "Bottom walls carry recessed Female Sockets—so cubbies sit flat on a desk AND lock together "
            "<b>side-by-side and stacked</b>!"
        )
        drw_note.setWordWrap(True)
        drw_note.setToolTip(TIPS["drawer_note"])
        f_drw.addWidget(drw_note)
        lay.addWidget(self.grp_drawer)

        self.grp_bin = QGroupBox("Workshop Parts Bin Options")
        self.grp_bin.setToolTip(TIPS["grp_bin"])
        f_bin = self._form(self.grp_bin)
        self.sld_bin_scoop = _SliderSpin(20.0, 65.0, 5.0, 0, "%")
        self.sld_bin_scoop.valueChanged.connect(self._on_ui_changed)
        self._add_row(f_bin, "Front mouth drop:", self.sld_bin_scoop, TIPS["bin_scoop"])
        lay.addWidget(self.grp_bin)

        self.grp_caddy = QGroupBox("Carry Caddy Options")
        self.grp_caddy.setToolTip(TIPS["grp_caddy"])
        f_cad = self._form(self.grp_caddy)
        self.sld_caddy_h = _SliderSpin(15.0, 75.0, 2.0, 0, "mm")
        self.sld_caddy_h.valueChanged.connect(self._on_ui_changed)
        self._add_row(f_cad, "Handle arch height:", self.sld_caddy_h, TIPS["caddy_h"])
        lay.addWidget(self.grp_caddy)

        self.grp_label = QGroupBox("Workshop Labelling")
        self.grp_label.setToolTip(TIPS["grp_label"])
        f_lbl = QVBoxLayout(self.grp_label)
        f_lbl.setContentsMargins(6, 8, 6, 6)
        self.chk_label = QCheckBox("Front slide-in label holder frame (45° support-free rails)")
        self.chk_label.setToolTip(TIPS["label_slot"])
        self.chk_label.toggled.connect(self._on_ui_changed)
        f_lbl.addWidget(self.chk_label)
        lay.addWidget(self.grp_label)

        lay.addStretch(1)
        return scroll

    def _build_tab_surface_printer(self) -> QWidget:
        scroll, lay = self._scroll_page()

        # Outer Surface Texture
        g_tex = QGroupBox("Outer Wall Texture")
        g_tex.setToolTip(TIPS["grp_tex"])
        f_tex = self._form(g_tex)
        self.cmb_pattern = self._combo(PATTERN_NAMES, PATTERN_ITEM_TIPS, TIPS["pattern"])
        self.sld_rib_d = _SliderSpin(0.4, 3.0, 0.2, 1, "mm")
        self.sld_rib_p = _SliderSpin(4.0, 18.0, 0.5, 1, "mm")
        self._add_row(f_tex, "Surface pattern:", self.cmb_pattern, TIPS["pattern"])
        self._add_row(f_tex, "Pattern depth:", self.sld_rib_d, TIPS["rib_d"])
        self._add_row(f_tex, "Pattern spacing:", self.sld_rib_p, TIPS["rib_p"])
        self.cmb_pattern.currentIndexChanged.connect(self._on_ui_changed)
        self.sld_rib_d.valueChanged.connect(self._on_ui_changed)
        self.sld_rib_p.valueChanged.connect(self._on_ui_changed)
        lay.addWidget(g_tex)

        # Colours & Look
        g_col = QGroupBox("Colours && Material")
        g_col.setToolTip(TIPS["grp_col"])
        f_col = self._form(g_col)
        self.cmb_col_style = self._combo(COLOUR_NAMES, COLOUR_ITEM_TIPS, TIPS["col_style"])
        self.sld_col_used = _SliderSpin(1, 4, 1, 0, "")
        self.sld_bands = _SliderSpin(2, 16, 1, 0, "")
        self.cmb_palette = self._combo(base_tip=TIPS["palette"])
        self.cmb_palette.addItem("Choose a colour palette…", None)
        for i, (name, cols) in enumerate(PALETTES, start=1):
            self.cmb_palette.addItem(name, cols)
            self.cmb_palette.setItemData(
                i,
                f"<b>{name}:</b> Sets the 4 filament swatches to {', '.join(cols)}.",
                Qt.ToolTipRole,
            )
        self.cmb_palette.currentIndexChanged.connect(self._on_palette_chosen)

        sw_widget = QWidget()
        sw_row = QHBoxLayout(sw_widget)
        sw_row.setContentsMargins(0, 0, 0, 0)
        sw_row.setSpacing(6)
        self.btn_cols: list[QPushButton] = []
        for i in range(4):
            b = QPushButton(f"#{i + 1}")
            b.setFixedHeight(26)
            b.setToolTip(TIPS["swatch"].format(idx=i + 1))
            b.clicked.connect(lambda checked=False, idx=i: self._pick_colour(idx))
            sw_row.addWidget(b)
            self.btn_cols.append(b)

        self.cmb_look = self._combo(LOOK_NAMES, LOOK_ITEM_TIPS, TIPS["look"])

        self._add_row(f_col, "Colour mode:", self.cmb_col_style, TIPS["col_style"])
        self._add_row(f_col, "Filaments used:", self.sld_col_used, TIPS["col_used"])
        self._add_row(f_col, "Height bands:", self.sld_bands, TIPS["bands"])
        self._add_row(f_col, "Quick palette:", self.cmb_palette, TIPS["palette"])
        lbl_sw = QLabel("Swatches:")
        lbl_sw.setToolTip(TIPS["swatch"].format(idx="1–4"))
        f_col.addRow(lbl_sw, sw_widget)
        self._add_row(f_col, "Material look:", self.cmb_look, TIPS["look"])

        self.cmb_col_style.currentIndexChanged.connect(self._on_ui_changed)
        self.sld_col_used.valueChanged.connect(self._on_ui_changed)
        self.sld_bands.valueChanged.connect(self._on_ui_changed)
        self.cmb_look.currentIndexChanged.connect(self._on_ui_changed)
        lay.addWidget(g_col)

        # Printer & Slicer
        g_prn = QGroupBox("Printer && Slicer")
        g_prn.setToolTip(TIPS["grp_prn"])
        f_prn = self._form(g_prn)
        self.sld_bed_x = _SliderSpin(120.0, 450.0, 5.0, 0, "mm")
        self.sld_bed_y = _SliderSpin(120.0, 450.0, 5.0, 0, "mm")
        self.sld_bed_z = _SliderSpin(120.0, 450.0, 5.0, 0, "mm")
        self.sld_overhang = _SliderSpin(35.0, 60.0, 5.0, 0, "°")
        self.cmb_slicer = self._combo(base_tip=TIPS["slicer"])
        if self._slicers:
            for name, path in self._slicers:
                self.cmb_slicer.addItem(name, path)
        else:
            self.cmb_slicer.addItem("System default (.3mf)", None)

        self._add_row(f_prn, "Bed width (X):", self.sld_bed_x, TIPS["bed_x"])
        self._add_row(f_prn, "Bed depth (Y):", self.sld_bed_y, TIPS["bed_y"])
        self._add_row(f_prn, "Max print height:", self.sld_bed_z, TIPS["bed_z"])
        self._add_row(f_prn, "Overhang limit:", self.sld_overhang, TIPS["overhang"])
        self._add_row(f_prn, "Target slicer:", self.cmb_slicer, TIPS["slicer"])
        for w in (self.sld_bed_x, self.sld_bed_y, self.sld_bed_z, self.sld_overhang):
            w.valueChanged.connect(self._on_ui_changed)
        lay.addWidget(g_prn)

        lay.addStretch(1)
        return scroll

    # ------------------------------------------------------------------ state sync
    def _update_swatch_buttons(self):
        cols = self.params.colors()
        for i, b in enumerate(self.btn_cols):
            r, g, bl = [int(round(c * 255)) for c in cols[i + 1]]
            fg = "#111111" if (0.299 * r + 0.587 * g + 0.114 * bl) > 150 else "#ffffff"
            b.setStyleSheet(f"background-color: rgb({r},{g},{bl}); color: {fg}; font-weight: 600;")

    def _update_contextual_visibility(self):
        p = self.params
        is_rect = p.shape == RECTANGLE
        self.lbl_width.setVisible(is_rect)
        self.sld_width.setVisible(is_rect)

        if p.kind == DRAWER_UNIT:
            self.lbl_length.setText("Cubby width (X):")
            self.lbl_width.setText("Cubby height (Z):")
            self.lbl_height.setText("Cubby depth (Y):")
            t_len, t_wid, t_hgt = TIPS["length_drawer"], TIPS["width_drawer"], TIPS["height_drawer"]
        else:
            self.lbl_length.setText("Length (X):" if is_rect else "Outer size (flat-to-flat):")
            self.lbl_width.setText("Width (Y):")
            self.lbl_height.setText("Height (Z):")
            t_len = TIPS["length_box"] if is_rect else TIPS["length_poly"]
            t_wid = TIPS["width_box"]
            t_hgt = TIPS["height_box"]
        self.lbl_length.setToolTip(t_len)
        self.sld_length.setToolTip(t_len)
        self.lbl_width.setToolTip(t_wid)
        self.sld_width.setToolTip(t_wid)
        self.lbl_height.setToolTip(t_hgt)
        self.sld_height.setToolTip(t_hgt)

        has_pull = p.kind in (DRAWER_UNIT, LIDDED_BOX)
        self.pull_widget.setVisible(has_pull)
        self.lbl_pull.setText("Drawer pull-out:" if p.kind == DRAWER_UNIT else "Lid lift preview:")
        t_pull = TIPS["pull_drawer"] if p.kind == DRAWER_UNIT else TIPS["pull_lid"]
        self.lbl_pull.setToolTip(t_pull)
        self.sld_pull.setToolTip(t_pull)

        self.grp_lid.setVisible(p.kind == LIDDED_BOX)
        self.grp_drawer.setVisible(p.kind == DRAWER_UNIT)
        self.grp_bin.setVisible(p.kind == PARTS_BIN)
        self.grp_caddy.setVisible(p.kind == CADDY)
        self.grp_label.setVisible(p.kind not in (DRAWER_UNIT, PARTS_BIN) and p.shape in (RECTANGLE, SQUARE))

    def _load_params(self, p: BoxParams, push_undo: bool = True, fit_camera: bool = False):
        if push_undo:
            self._undo_stack.append(self._last_pushed)
            self._redo_stack.clear()
        self.params = p.copy()
        self._last_pushed = self.params.to_dict()

        self._updating = True
        self.cmb_kind.setCurrentIndex(max(0, self.cmb_kind.findData(p.kind)))
        self.cmb_shape.setCurrentIndex(max(0, self.cmb_shape.findData(p.shape)))
        self.sld_length.setValue(p.length)
        self.sld_width.setValue(p.width)
        self.sld_height.setValue(p.height)
        self.sld_corner.setValue(p.corner_r)
        self.sld_wall.setValue(p.wall_thickness)
        self.sld_floor.setValue(p.floor_thickness)

        self.sld_div_x.setValue(p.div_x)
        self.sld_div_y.setValue(p.div_y)
        self.cmb_div_mode.setCurrentIndex(max(0, self.cmb_div_mode.findData(p.div_mode)))
        self.sld_div_wall.setValue(p.div_wall)
        self.sld_div_h.setValue(p.div_height_pct)
        self.sld_div_dip.setValue(p.div_dip)
        self.chk_scoop.setChecked(p.scoop_floor)

        self.chk_stack.setChecked(p.stackable)
        self.sld_stack_h.setValue(p.stack_height)
        self.chk_connect.setChecked(p.connectable)
        self.sld_dove_d.setValue(p.dovetail_depth)
        self.cmb_fit.setCurrentIndex(max(0, self.cmb_fit.findData(p.fit_grip)))

        self.cmb_lid_style.setCurrentIndex(max(0, self.cmb_lid_style.findData(p.lid_style)))
        self.chk_drawer_stop.setChecked(p.drawer_stop)
        self.sld_pull.setValue(p.drawer_pull_pct)
        self.sld_bin_scoop.setValue(p.bin_scoop_pct)
        self.chk_label.setChecked(p.label_slot)
        self.sld_caddy_h.setValue(p.caddy_handle_h)

        self.cmb_pattern.setCurrentIndex(max(0, self.cmb_pattern.findData(p.pattern)))
        self.sld_rib_d.setValue(p.rib_depth)
        self.sld_rib_p.setValue(p.rib_pitch)

        self.cmb_col_style.setCurrentIndex(max(0, self.cmb_col_style.findData(p.colour_style)))
        self.sld_col_used.setValue(p.colours_used)
        self.sld_bands.setValue(p.band_count)
        self.cmb_look.setCurrentIndex(max(0, self.cmb_look.findData(p.look)))
        self._update_swatch_buttons()

        self.sld_bed_x.setValue(p.bed_x)
        self.sld_bed_y.setValue(p.bed_y)
        self.sld_bed_z.setValue(p.printer_height)
        self.sld_overhang.setValue(p.max_overhang)
        self._updating = False

        self._update_contextual_visibility()
        self._rebuild(fit_camera=fit_camera)

    def _read_ui_into_params(self):
        p = self.params
        p.kind = int(self.cmb_kind.currentData())
        p.shape = int(self.cmb_shape.currentData())
        p.length = self.sld_length.value()
        p.width = self.sld_width.value() if p.shape == RECTANGLE else p.length
        p.height = self.sld_height.value()
        p.corner_r = self.sld_corner.value()
        p.wall_thickness = self.sld_wall.value()
        p.floor_thickness = self.sld_floor.value()

        p.div_x = int(round(self.sld_div_x.value()))
        p.div_y = int(round(self.sld_div_y.value()))
        p.div_mode = int(self.cmb_div_mode.currentData())
        p.div_wall = self.sld_div_wall.value()
        p.div_height_pct = self.sld_div_h.value()
        p.div_dip = self.sld_div_dip.value()
        p.scoop_floor = self.chk_scoop.isChecked()

        p.stackable = self.chk_stack.isChecked()
        p.stack_height = self.sld_stack_h.value()
        p.connectable = self.chk_connect.isChecked()
        p.dovetail_depth = self.sld_dove_d.value()
        p.fit_grip = int(self.cmb_fit.currentData())

        p.lid_style = int(self.cmb_lid_style.currentData())
        p.drawer_stop = self.chk_drawer_stop.isChecked()
        p.drawer_pull_pct = self.sld_pull.value()
        p.bin_scoop_pct = self.sld_bin_scoop.value()
        p.label_slot = self.chk_label.isChecked()
        p.caddy_handle_h = self.sld_caddy_h.value()

        p.pattern = int(self.cmb_pattern.currentData())
        p.rib_depth = self.sld_rib_d.value()
        p.rib_pitch = self.sld_rib_p.value()

        p.colour_style = int(self.cmb_col_style.currentData())
        p.colours_used = int(round(self.sld_col_used.value()))
        p.band_count = int(round(self.sld_bands.value()))
        p.look = int(self.cmb_look.currentData())

        p.bed_x = self.sld_bed_x.value()
        p.bed_y = self.sld_bed_y.value()
        p.printer_height = self.sld_bed_z.value()
        p.max_overhang = self.sld_overhang.value()

    def _on_ui_changed(self, *args):
        if self._updating:
            return
        prev = self._last_pushed
        self._read_ui_into_params()
        cur = self.params.to_dict()
        if cur != prev:
            self._undo_stack.append(prev)
            if len(self._undo_stack) > 80:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
            self._last_pushed = cur
        self._update_contextual_visibility()
        self._timer.start()

    def _on_view_mode_changed(self):
        self._sync_viewer(fit_camera=True)

    # ------------------------------------------------------------------ geometry & 3D view
    def _rebuild(self, fit_camera: bool = False):
        self.design = BoxDesign(self.params)
        d = self.design
        self.report_box.setHtml(info_html(d))
        self.btn_save_acc.setEnabled(bool(d.accessories))
        if d.accessories:
            lbl = d.accessories[0]["label"]
            self.btn_save_acc.setText(f"Save {lbl} STL…")
            self.btn_save_acc.setToolTip(TIPS["save_acc_active"].format(label=lbl))
        else:
            self.btn_save_acc.setText("Save Accessory STL…")
            self.btn_save_acc.setToolTip(TIPS["save_acc_none"])

        self._sync_viewer(fit_camera=fit_camera or not self._camera_initialized)
        self._camera_initialized = True

        if d.errors:
            self.statusBar().showMessage(f"Cannot build box: {d.errors[0]}")
        else:
            acc_txt = f" + {len(d.accessories)} accessory part(s)" if d.accessories else ""
            self.statusBar().showMessage(
                f"{KIND_NAMES[self.params.kind]} · {d.compartments} compartments{acc_txt} · "
                f"~{d.grams:.0f} g · Steepest overhang {d.worst:.1f}° · Watertight: {'Yes' if d.closed else 'No'}"
            )

    def _sync_viewer(self, fit_camera: bool = False):
        d = self.design
        if d is None or d.errors or len(d.verts) == 0:
            self.viewer.clear_meshes()
            return

        p = self.params
        v = self.viewer
        v.clear_meshes()
        v.set_bed(p.bed_x, p.bed_y, p.printer_height)
        v.limit = p.max_overhang
        v.look = p.look

        cols = p.colors()
        stops = d.band_stops()
        v.bands = [(z, cols[fil]) for z, fil in stops]

        mode = self.view_group.checkedId()
        # 0: Assembled, 1: 2x2 Connected Cluster, 2: Section, 3: Overhang Check, 4: Print Bed Layout
        v.section = mode == 2
        v.show_bed = mode == 4
        if mode == 3:
            v.colmode = 3
        elif p.colour_style == BANDS and p.colours_used > 1 and mode != 1:
            v.colmode = 1
        else:
            v.colmode = 0

        if mode in (0, 2):
            asm = d.assembled_meshes()
            for idx, (name, mv, mf, fil) in enumerate(asm):
                v.set_mesh(f"asm_{idx}_{name}", mv, mf, cols[fil], use_bands=(idx == 0 and p.kind != DRAWER_UNIT))
            if mode == 2:
                v.set_section_source(asm[0][1], asm[0][2])
            else:
                v.set_section_source([], [])
        elif mode == 1:
            # 2x2 Connected / Stacked Modular Cluster preview!
            asm = d.assembled_meshes()
            W_eff = p.width if p.shape == RECTANGLE else p.length
            if p.kind == DRAWER_UNIT:
                # 2 side-by-side x 2 stacked 4-drawer cabinet, with the 4th cubby mid-slide along the dovetail rails!
                shifts = [
                    (-0.5 * p.length, 0.0, 0.0),
                    (0.5 * p.length, 0.0, 0.0),
                    (-0.5 * p.length, 0.0, W_eff),
                    (0.5 * p.length, 22.0, W_eff),
                ]
            elif p.shape == HEXAGON:
                # Honeycomb 3-pod cluster + 1 stacked on top
                R = 0.5 * p.length
                apothem = R * 0.8660254
                shifts = [
                    (0.0, 0.0, 0.0),
                    (1.5 * R, apothem, 0.0),
                    (0.0, 2.0 * apothem, 0.0),
                    (0.0, 2.0 * apothem, p.height - (p.stack_height if p.stackable else 0.0)),
                ]
            else:
                # 2 side-by-side in front + 1 behind + 1 stacked on back-left so front dovetail joints are in full view
                shifts = [
                    (-0.5 * p.length, -0.5 * W_eff, 0.0),
                    (0.5 * p.length, -0.5 * W_eff, 0.0),
                    (-0.5 * p.length, 0.5 * W_eff, 0.0),
                    (-0.5 * p.length, 0.5 * W_eff, p.height - (p.stack_height if p.stackable else 0.0)),
                ]
            shades = (1.00, 0.84, 0.91, 0.78)
            drw_push = (0.0, 0.55, 0.92, 0.88)
            pull_dist = (p.drawer_pull_pct / 100.0) * 0.58 * max(p.height - p.floor_thickness - 2.0, 10.0)
            for c_i, (dx, dy, dz) in enumerate(shifts):
                sh = shades[c_i % len(shades)]
                for idx, (name, mv, mf, fil) in enumerate(asm):
                    base_rgb = cols.get(fil, cols[1])
                    s_fac = sh if idx == 0 else (0.94 + 0.06 * sh)
                    rgb = tuple(min(1.0, max(0.0, c * s_fac)) for c in base_rgb)
                    extra_y = (drw_push[c_i % 4] * pull_dist) if (p.kind == DRAWER_UNIT and idx == 1) else 0.0
                    v.set_mesh(
                        f"cl_{c_i}_{idx}",
                        translate_mesh(mv, dx, dy + extra_y, dz),
                        mf,
                        rgb,
                        use_bands=False,
                    )
            v.set_section_source([], [])
        elif mode == 3:
            # Overhang check in print orientation
            v.set_mesh("body_overhang", d.verts, d.faces, cols[1], face_vals=d.lean, use_bands=False)
            v.set_section_source([], [])
        else:
            # Print Bed Layout (all parts flat on bed)
            for idx, (name, mv, mf, fil, rgb) in enumerate(d.print_parts()):
                v.set_mesh(f"bed_{idx}_{name}", mv, mf, rgb, use_bands=(idx == 0))
            v.set_section_source([], [])

        if fit_camera:
            self._fit_camera()

    def _fit_camera(self):
        lo, hi = self.viewer.scene_bounds()
        self.viewer.target = 0.5 * (lo + hi)
        self.viewer.dist = self.viewer.fit_distance(lo, hi)
        self.viewer.update()

    # ------------------------------------------------------------------ actions
    def _pick_colour(self, idx: int):
        cols = self.params.colors()
        r, g, b = [int(round(c * 255)) for c in cols[idx + 1]]
        chosen = QColorDialog.getColor(QColor(r, g, b), self, f"Pick Filament Colour #{idx + 1}")
        if chosen.isValid():
            setattr(self.params, f"color{idx + 1}", chosen.name().upper())
            self._update_swatch_buttons()
            self._on_ui_changed()

    def _on_palette_chosen(self, idx: int):
        data = self.cmb_palette.itemData(idx)
        if not data:
            return
        for i, col in enumerate(data[:4]):
            setattr(self.params, f"color{i + 1}", str(col))
        self._update_swatch_buttons()
        self._on_ui_changed()

    def _on_preset_dialog(self):
        dlg = PresetDialog(self)
        if dlg.exec() == QDialog.Accepted and dlg.chosen:
            p = BoxParams.from_dict(dlg.chosen)
            self._load_params(p, push_undo=True, fit_camera=True)

    def _apply_preset_dict(self, name: str, d: dict):
        p = BoxParams.from_dict(dict(d, name=name.lower().replace(" ", "_")))
        self._load_params(p, push_undo=True, fit_camera=True)

    def _on_surprise(self):
        p = surprise(self.params)
        self._load_params(p, push_undo=True, fit_camera=True)

    def _on_new(self):
        self.current_path = None
        self._load_params(BoxParams(), push_undo=True, fit_camera=True)

    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Boxinator Project", "", "Boxinator (*.box *.json)")
        if not path:
            return
        try:
            p = BoxParams.load(path)
            self.current_path = Path(path)
            self._load_params(p, push_undo=True, fit_camera=True)
        except Exception as exc:
            QMessageBox.warning(self, "Could not open file", str(exc))

    def _on_save(self):
        if self.current_path is None:
            self._on_save_as()
            return
        self.params.save(self.current_path)
        self.statusBar().showMessage(f"Saved project to {self.current_path}")

    def _on_save_as(self):
        default_name = f"{self.params.name}.box"
        path, _ = QFileDialog.getSaveFileName(self, "Save Boxinator Project", default_name, "Boxinator (*.box)")
        if not path:
            return
        self.current_path = Path(path)
        self._on_save()

    def _on_export_3mf(self):
        if self.design is None or self.design.errors:
            return
        default_name = f"{self.params.name}.3mf"
        path, _ = QFileDialog.getSaveFileName(self, "Save 3MF for Printing", default_name, "3MF files (*.3mf)")
        if not path:
            return
        write_3mf(path, self.design, self.params)
        self.statusBar().showMessage(f"Saved 3MF to {path}")

    def _on_export_body_stl(self):
        if self.design is None or self.design.errors:
            return
        default_name = f"{self.params.name}_body.stl"
        path, _ = QFileDialog.getSaveFileName(self, "Save Main Body STL", default_name, "STL files (*.stl)")
        if not path:
            return
        write_binary_stl(path, self.design.verts, self.design.faces, header_text=f"Boxinator {self.params.name}")
        self.statusBar().showMessage(f"Saved STL to {path}")

    def _on_export_acc_stl(self):
        if self.design is None or not self.design.accessories:
            return
        acc = self.design.accessories[0]
        default_name = f"{acc['name']}.stl"
        path, _ = QFileDialog.getSaveFileName(
            self, f"Save {acc['label']} STL", default_name, "STL files (*.stl)"
        )
        if not path:
            return
        write_binary_stl(path, acc["verts_bed"], acc["faces_bed"], header_text=f"Boxinator {acc['name']}")
        self.statusBar().showMessage(f"Saved {acc['label']} STL to {path}")

    def _on_open_slicer(self):
        if self.design is None or self.design.errors:
            return
        slicer_path = self.cmb_slicer.currentData()
        try:
            out_path, used = open_in_slicer(self.design, self.params, slicer_path)
            self.statusBar().showMessage(f"Opened {out_path.name} in {used}")
        except Exception as exc:
            QMessageBox.warning(self, "Could not launch slicer", str(exc))

    def _on_screenshot(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save 3D Picture", f"{self.params.name}.png", "PNG image (*.png)"
        )
        if not path:
            return
        img = self.viewer.grabFramebuffer()
        img.save(path, "PNG")
        self.statusBar().showMessage(f"Saved screenshot to {path}")

    def _on_undo(self):
        if not self._undo_stack:
            return
        self._redo_stack.append(self.params.to_dict())
        prev = self._undo_stack.pop()
        self._load_params(BoxParams.from_dict(prev), push_undo=False)

    def _on_redo(self):
        if not self._redo_stack:
            return
        self._undo_stack.append(self.params.to_dict())
        nxt = self._redo_stack.pop()
        self._load_params(BoxParams.from_dict(nxt), push_undo=False)

    def _on_copy_report(self):
        if self.design is None:
            return
        lines = [f"{k}: {v}" for k, v in self.design.info().items()]
        QApplication.clipboard().setText("\n".join(lines))
        self.statusBar().showMessage("Copied design summary to clipboard")

    def _on_help_print(self):
        if self.design is None:
            return
        QMessageBox.information(self, "How to Print & Assemble", print_steps_html(self.design))

    def _on_help_guide(self):
        QMessageBox.information(self, "Boxinator Guide", HELP_HTML)

    def _on_about(self):
        QMessageBox.about(
            self,
            "About Boxinator",
            f"<h3>Boxinator {__version__}</h3>"
            "<p>A focused parametric designer for 3D-printable <b>stackable, connectable, divided boxes, "
            "workshop parts bins, carry caddies, and modular side-drawer units</b>.</p>"
            "<p>Every part is generated as a 100% closed, support-free manifold mesh ready for any slicer.</p>",
        )


def run() -> int:
    import ctypes
    import sys

    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Boxinator.App.1")
        except Exception:
            pass
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Boxinator")
    app.setWindowIcon(_app_icon())
    win = MainWindow()
    win.show()
    return app.exec()


main = run
