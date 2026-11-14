"""Design parameters for Boxinator, with JSON persistence (.box files)."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, fields

FILE_FORMAT = "boxinator"
FILE_VERSION = 1
FILAMENTS = (1, 2, 3, 4)

# Box roles / kinds
ORGANISER, LIDDED_BOX, DRAWER_UNIT, PARTS_BIN, CADDY = 0, 1, 2, 3, 4
KINDS = (ORGANISER, LIDDED_BOX, DRAWER_UNIT, PARTS_BIN, CADDY)
KIND_NAMES = {
    ORGANISER: "Organiser box",
    LIDDED_BOX: "Lidded box",
    DRAWER_UNIT: "Side drawer unit",
    PARTS_BIN: "Front-scoop parts bin",
    CADDY: "Carry caddy",
}

# Cross-section shapes
RECTANGLE, SQUARE, HEXAGON, OCTAGON = 0, 1, 2, 3
SHAPES = (RECTANGLE, SQUARE, HEXAGON, OCTAGON)
SHAPE_NAMES = {
    RECTANGLE: "Rectangle",
    SQUARE: "Square",
    HEXAGON: "Hexagon (Honeycomb)",
    OCTAGON: "Octagon",
}

# Divider styles
BUILT_IN, SLIDE_IN = 0, 1
DIVIDER_MODES = (BUILT_IN, SLIDE_IN)
DIV_MODE_NAMES = {
    BUILT_IN: "Built-in walls (prints as one piece)",
    SLIDE_IN: "Slide-in plates (wall slots + flat plates)",
}

# Lid styles (for LIDDED_BOX)
SLIDE_LID, TRAY_LID = 0, 1
LID_STYLES = (SLIDE_LID, TRAY_LID)
LID_STYLE_NAMES = {
    TRAY_LID: "Stackable sorting-tray lid",
    SLIDE_LID: "Slide-lock corner-rail lid",
}

# Surface textures
SMOOTH, RIBS, DIAMONDS, RINGS, HEX_WINDOWS = 0, 1, 2, 3, 4
PATTERNS = (SMOOTH, RIBS, DIAMONDS, RINGS, HEX_WINDOWS)
PATTERN_NAMES = {
    SMOOTH: "Smooth walls",
    RIBS: "Vertical fluted ribs",
    DIAMONDS: "Diamond knurl",
    RINGS: "Horizontal rings",
    HEX_WINDOWS: "Recessed hex dimples",
}

# Colour styles
ONE_COLOUR, BANDS, ACCENT_PARTS = 0, 1, 2
COLOUR_STYLES = (ONE_COLOUR, BANDS, ACCENT_PARTS)
COLOUR_NAMES = {
    ONE_COLOUR: "Single filament colour",
    BANDS: "Horizontal colour bands",
    ACCENT_PARTS: "Accent lid / drawer / dividers",
}

# Material finish in 3D view
MATTE, SILK, GLOSSY, TRANSLUCENT = 0, 1, 2, 3
LOOKS = (MATTE, SILK, GLOSSY, TRANSLUCENT)
LOOK_NAMES = {
    MATTE: "Matte PLA / PETG",
    SILK: "Silk PLA",
    GLOSSY: "Glossy PETG / ABS",
    TRANSLUCENT: "Translucent / Clear",
}

# Fit / grip presets for connectors, lids and drawers
GENTLE, SNUG, FIRM = 0, 1, 2
GRIPS = (GENTLE, SNUG, FIRM)
FIT_NAMES = {
    GENTLE: "Gentle — easy slip fit (0.28 mm)",
    SNUG: "Snug — everyday fit (0.20 mm)",
    FIRM: "Firm — tight lock (0.14 mm)",
}


@dataclass
class BoxParams:
    name: str = "desk_organiser"

    # --- What kind of box ---------------------------------------------------
    kind: int = ORGANISER             # ORGANISER, LIDDED_BOX, DRAWER_UNIT, PARTS_BIN, CADDY
    shape: int = RECTANGLE            # RECTANGLE, SQUARE, HEXAGON, OCTAGON

    # --- Outer dimensions (mm) ----------------------------------------------
    length: float = 120.0             # X size (mm); for SQUARE/HEXAGON/OCTAGON, width follows length
    width: float = 80.0               # Y size (mm)
    height: float = 65.0              # Z height (mm); for DRAWER_UNIT, the depth of the cubby/drawer
    corner_r: float = 8.0             # outer corner rounding radius (mm)
    wall_thickness: float = 1.8       # outer wall thickness (mm)
    floor_thickness: float = 1.6      # solid floor thickness (mm)

    # --- Stackable & Connectable --------------------------------------------
    stackable: bool = True            # 45-degree recessed stacking foot that nests into the rim below
    stack_height: float = 3.6         # vertical engagement depth of stacking foot (mm)
    connectable: bool = True          # integral support-free XY dovetail keys (+X/+Y) and slots (-X/-Y)
    dovetail_depth: float = 3.2       # depth of dovetail key/slot (mm)
    fit_grip: int = SNUG              # GENTLE (0.28 mm), SNUG (0.20 mm), FIRM (0.14 mm) clearance

    # --- Dividers & Interior ------------------------------------------------
    div_x: int = 2                    # compartments along length (1 = no X dividers .. 6)
    div_y: int = 2                    # compartments across width (1 = no Y dividers .. 6)
    div_mode: int = BUILT_IN          # BUILT_IN (printed as one piece) or SLIDE_IN (slots + flat plates)
    div_height_pct: float = 92.0      # divider height as % of interior depth (25..100%)
    div_dip: float = 8.0              # finger-scoop dip in the middle of each divider top (mm, 0 = flat)
    div_wall: float = 1.4             # thickness of internal divider walls (mm)
    scoop_floor: bool = True          # curved finger-sweep fillet at the bottom of compartments

    # --- Role-specific features (Lid, Drawer, Scoop, Label, Handle) ---------
    lid_style: int = TRAY_LID         # TRAY_LID (stackable tray lid) or SLIDE_LID (locking corner-rail slide)
    drawer_pull_pct: float = 35.0     # preview: how far the drawer or lid is opened in 3D view (0..100%)
    drawer_stop: bool = True          # anti-tip keeper bump at the top of the drawer/cubby
    bin_scoop_pct: float = 50.0       # PARTS_BIN: how far down the front mouth dips (% of height)
    label_slot: bool = False          # slide-in label frame on the front face (or drawer front)
    caddy_handle_h: float = 32.0      # CADDY: height of the central arched carry handle above rim (mm)

    # --- Surface pattern ----------------------------------------------------
    pattern: int = SMOOTH             # SMOOTH, RIBS, DIAMONDS, RINGS, HEX_WINDOWS
    rib_pitch: float = 6.0            # spacing of ribs / diamonds / rings (mm)
    rib_depth: float = 0.8            # depth of surface texture (mm)

    # --- Colours ------------------------------------------------------------
    color1: str = "#2A9D8F"           # primary body filament
    color2: str = "#E9C46A"           # secondary / drawer / lid / band filament
    color3: str = "#F4A261"           # tertiary / dividers / accent filament
    color4: str = "#264653"           # fourth filament
    colour_style: int = ACCENT_PARTS  # ONE_COLOUR, BANDS, ACCENT_PARTS (box=1, drawer/lid=2, dividers=3)
    colours_used: int = 2
    band_count: int = 3
    look: int = MATTE

    # --- Printer settings ---------------------------------------------------
    max_overhang: float = 45.0
    line_width: float = 0.45
    layer_height: float = 0.2
    printer_height: float = 250.0
    bed_x: float = 256.0
    bed_y: float = 256.0
    speed: float = 60.0
    max_flow: float = 14.0
    filament_d: float = 1.75
    density: float = 1.24

    def copy(self) -> "BoxParams":
        return BoxParams.from_dict(self.to_dict())

    def to_dict(self) -> dict:
        return asdict(self)

    def colors(self) -> dict[int, tuple[float, float, float]]:
        return {k: hex_to_rgb(getattr(self, f"color{k}")) for k in FILAMENTS}

    @property
    def clearance(self) -> float:
        """Clearance gap (mm) from the chosen fit_grip."""
        return {GENTLE: 0.28, SNUG: 0.20, FIRM: 0.14}.get(self.fit_grip, 0.20)

    @classmethod
    def from_dict(cls, d: dict) -> "BoxParams":
        if not isinstance(d, dict):
            raise ValueError("Design settings must be an object.")
        p = cls()
        fresh = cls()
        for f in fields(cls):
            if f.name not in d:
                continue
            cur, v = getattr(p, f.name), d[f.name]
            if isinstance(v, float) and not math.isfinite(v):
                continue
            try:
                if isinstance(cur, bool):
                    v = bool(v)
                elif isinstance(cur, int):
                    v = int(v)
                elif isinstance(cur, float):
                    v = float(v)
                else:
                    v = str(v)
            except (TypeError, ValueError, OverflowError):
                continue
            if isinstance(v, float) and not math.isfinite(v):
                continue
            setattr(p, f.name, v)

        allowed = {
            "kind": KINDS,
            "shape": SHAPES,
            "fit_grip": GRIPS,
            "div_mode": DIVIDER_MODES,
            "lid_style": LID_STYLES,
            "pattern": PATTERNS,
            "colour_style": COLOUR_STYLES,
            "colours_used": (1, 2, 3, 4),
            "look": LOOKS,
        }
        for key, values in allowed.items():
            if getattr(p, key) not in values:
                setattr(p, key, getattr(fresh, key))

        for key, lo, hi in (
            ("length", 30.0, 400.0),
            ("width", 30.0, 400.0),
            ("height", 15.0, 350.0),
            ("corner_r", 1.0, 100.0),
            ("wall_thickness", 1.0, 6.0),
            ("floor_thickness", 0.8, 8.0),
            ("stack_height", 1.5, 10.0),
            ("dovetail_depth", 1.4, 5.0),
            ("div_x", 1, 8),
            ("div_y", 1, 8),
            ("div_height_pct", 25.0, 100.0),
            ("div_dip", 0.0, 40.0),
            ("div_wall", 0.8, 4.0),
            ("drawer_pull_pct", 0.0, 100.0),
            ("bin_scoop_pct", 20.0, 80.0),
            ("caddy_handle_h", 15.0, 80.0),
            ("rib_pitch", 3.0, 25.0),
            ("rib_depth", 0.2, 2.5),
            ("band_count", 2, 20),
            ("max_overhang", 30.0, 60.0),
            ("line_width", 0.25, 1.2),
            ("layer_height", 0.08, 0.6),
            ("printer_height", 80.0, 600.0),
            ("bed_x", 80.0, 600.0),
            ("bed_y", 80.0, 600.0),
            ("speed", 10.0, 500.0),
            ("max_flow", 2.0, 60.0),
            ("filament_d", 1.0, 3.0),
            ("density", 0.8, 2.5),
        ):
            val = getattr(p, key)
            clamped = min(max(val, lo), hi)
            setattr(p, key, int(clamped) if isinstance(getattr(fresh, key), int) else float(clamped))

        for k in FILAMENTS:
            try:
                hex_to_rgb(getattr(p, f"color{k}"))
            except ValueError:
                setattr(p, f"color{k}", getattr(fresh, f"color{k}"))
        return p

    def save(self, path: str | object):
        save_design(str(path), self)

    @classmethod
    def load(cls, path: str | object) -> "BoxParams":
        return load_design(str(path))


def hex_to_rgb(text: str) -> tuple[float, float, float]:
    if isinstance(text, (tuple, list)) and len(text) == 3:
        return (float(text[0]), float(text[1]), float(text[2]))
    t = str(text).strip().lstrip("#")
    if len(t) != 6:
        raise ValueError(f"not a colour: {text!r}")
    return tuple(int(t[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{int(round(max(0.0, min(1.0, float(c))) * 255)):02X}" for c in rgb[:3])


def save_design(path: str, params: BoxParams):
    data = {"format": FILE_FORMAT, "version": FILE_VERSION, "params": params.to_dict()}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_design(path: str) -> BoxParams:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("format") != FILE_FORMAT:
        raise ValueError("Not a Boxinator design file")
    return BoxParams.from_dict(data.get("params", {}))
