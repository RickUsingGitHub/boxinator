"""Curated ready-made functional box presets and 'Surprise me' generator for Boxinator."""

from __future__ import annotations

import random

from .params import (
    ACCENT_PARTS,
    BANDS,
    BUILT_IN,
    CADDY,
    DIAMONDS,
    DRAWER_UNIT,
    HEX_WINDOWS,
    HEXAGON,
    LIDDED_BOX,
    OCTAGON,
    ONE_COLOUR,
    ORGANISER,
    PARTS_BIN,
    RECTANGLE,
    RIBS,
    RINGS,
    SLIDE_IN,
    SLIDE_LID,
    SMOOTH,
    SQUARE,
    TRAY_LID,
    BoxParams,
)

PALETTES = [
    ("Teal & Amber", ("#2A9D8F", "#E9C46A", "#F4A261", "#264653")),
    ("Workshop Slate", ("#3D5A80", "#EE6C4D", "#98C1D9", "#293241")),
    ("Forest & Birch", ("#386641", "#F2E8CF", "#A7C957", "#BC4749")),
    ("Charcoal & Lime", ("#2B2D42", "#80B918", "#EDF2F4", "#EF233C")),
    ("Nordic Sand", ("#457B9D", "#F1FAEE", "#E63946", "#1D3557")),
    ("Plum & Gold", ("#5F0F40", "#FB8B24", "#E36414", "#9A031E")),
]

# (Title, Subtitle, BoxParams dict)
GALLERY: list[tuple[str, str, dict]] = [
    (
        "Desk Organiser",
        "2×2 divided desk box · stackable, connectable & finger-scoop floor",
        dict(
            name="desk_organiser",
            kind=ORGANISER,
            shape=RECTANGLE,
            length=130.0,
            width=85.0,
            height=65.0,
            corner_r=10.0,
            stackable=True,
            connectable=True,
            div_x=2,
            div_y=2,
            div_mode=BUILT_IN,
            scoop_floor=True,
            pattern=RIBS,
            rib_pitch=6.0,
            rib_depth=0.7,
            color1="#2A9D8F",
            color2="#E9C46A",
        ),
    ),
    (
        "Modular Side Drawer",
        "Cubby shell + sliding divided drawer · connect shells side-by-side & stacked!",
        dict(
            name="modular_side_drawer",
            kind=DRAWER_UNIT,
            shape=RECTANGLE,
            length=120.0,
            width=68.0,
            height=115.0,
            corner_r=8.0,
            stackable=True,
            connectable=True,
            div_x=2,
            div_y=2,
            drawer_pull_pct=40.0,
            drawer_stop=True,
            scoop_floor=True,
            pattern=SMOOTH,
            color1="#3D5A80",
            color2="#EE6C4D",
            colour_style=ACCENT_PARTS,
            colours_used=2,
        ),
    ),
    (
        "Workshop Parts Bin",
        "Front-scoop open mouth · stackable, connectable & front label slot",
        dict(
            name="workshop_parts_bin",
            kind=PARTS_BIN,
            shape=RECTANGLE,
            length=110.0,
            width=140.0,
            height=75.0,
            corner_r=8.0,
            stackable=True,
            connectable=True,
            div_x=2,
            div_y=1,
            bin_scoop_pct=48.0,
            scoop_floor=True,
            pattern=SMOOTH,
            color1="#EE6C4D",
            color2="#293241",
        ),
    ),
    (
        "Honeycomb Hex Cluster",
        "6-sided connectable hex cup · link several into a custom desk honeycomb",
        dict(
            name="honeycomb_hex_cup",
            kind=ORGANISER,
            shape=HEXAGON,
            length=96.0,
            width=96.0,
            height=85.0,
            corner_r=6.0,
            stackable=True,
            connectable=True,
            div_x=1,
            div_y=1,
            scoop_floor=False,
            pattern=RIBS,
            rib_pitch=5.5,
            rib_depth=0.6,
            color1="#FB8B24",
            color2="#5F0F40",
        ),
    ),
    (
        "Lidded Storage Box",
        "Divided box with stackable sorting-tray lid · slide-in removable dividers",
        dict(
            name="lidded_storage_box",
            kind=LIDDED_BOX,
            shape=RECTANGLE,
            length=145.0,
            width=100.0,
            height=60.0,
            corner_r=10.0,
            stackable=True,
            connectable=True,
            div_x=3,
            div_y=2,
            div_mode=SLIDE_IN,
            lid_style=TRAY_LID,
            drawer_pull_pct=35.0,
            scoop_floor=True,
            pattern=DIAMONDS,
            rib_pitch=7.0,
            rib_depth=0.6,
            color1="#386641",
            color2="#F2E8CF",
            color3="#A7C957",
            colour_style=ACCENT_PARTS,
            colours_used=3,
        ),
    ),
    (
        "Divided Tool Caddy",
        "4-compartment tote with central arched carry handle",
        dict(
            name="divided_tool_caddy",
            kind=CADDY,
            shape=RECTANGLE,
            length=165.0,
            width=115.0,
            height=70.0,
            corner_r=12.0,
            stackable=False,
            connectable=True,
            div_x=2,
            div_y=2,
            div_mode=BUILT_IN,
            caddy_handle_h=34.0,
            scoop_floor=True,
            pattern=RIBS,
            rib_pitch=6.5,
            rib_depth=0.7,
            color1="#2B2D42",
            color2="#80B918",
        ),
    ),
    (
        "SMD & Screw Sorter",
        "Low-profile 4×3 tray with finger-scoop floors for tiny screws & components",
        dict(
            name="smd_screw_sorter",
            kind=LIDDED_BOX,
            shape=RECTANGLE,
            length=150.0,
            width=110.0,
            height=34.0,
            corner_r=8.0,
            stackable=True,
            connectable=True,
            div_x=4,
            div_y=3,
            div_mode=BUILT_IN,
            div_dip=4.0,
            lid_style=TRAY_LID,
            scoop_floor=True,
            pattern=SMOOTH,
            color1="#457B9D",
            color2="#F1FAEE",
        ),
    ),
    (
        "Board Game Token Bank",
        "Square stackable token & card tray with slide-lock travel lid",
        dict(
            name="game_token_bank",
            kind=LIDDED_BOX,
            shape=SQUARE,
            length=115.0,
            width=115.0,
            height=45.0,
            corner_r=10.0,
            stackable=True,
            connectable=True,
            div_x=2,
            div_y=2,
            div_mode=BUILT_IN,
            lid_style=SLIDE_LID,
            scoop_floor=True,
            pattern=RINGS,
            rib_pitch=6.0,
            rib_depth=0.6,
            color1="#5F0F40",
            color2="#FB8B24",
        ),
    ),
    (
        "Deep Drawer Cabinet Cube",
        "Square cubby + 3-slot drawer for cables, batteries or stationery",
        dict(
            name="cube_drawer_unit",
            kind=DRAWER_UNIT,
            shape=SQUARE,
            length=105.0,
            width=105.0,
            height=110.0,
            corner_r=8.0,
            stackable=True,
            connectable=True,
            div_x=1,
            div_y=3,
            drawer_pull_pct=45.0,
            drawer_stop=True,
            scoop_floor=True,
            pattern=RIBS,
            rib_pitch=6.0,
            rib_depth=0.6,
            color1="#264653",
            color2="#2A9D8F",
        ),
    ),
    (
        "Octagon Bit & Craft Cup",
        "8-sided connectable organiser with knurled diamond grip",
        dict(
            name="octagon_craft_cup",
            kind=ORGANISER,
            shape=OCTAGON,
            length=95.0,
            width=95.0,
            height=60.0,
            corner_r=5.0,
            stackable=True,
            connectable=True,
            div_x=2,
            div_y=2,
            scoop_floor=True,
            pattern=DIAMONDS,
            rib_pitch=6.5,
            rib_depth=0.7,
            color1="#BC4749",
            color2="#F2E8CF",
        ),
    ),
]


def gallery_design(title: str, keep: BoxParams | None = None) -> BoxParams:
    for name, _, spec in GALLERY:
        if name.lower() == title.lower():
            base = keep.to_dict() if keep is not None else BoxParams().to_dict()
            # Keep printer settings from `keep`, reset design fields to defaults then overlay `spec`
            fresh = BoxParams().to_dict()
            for k in (
                "max_overhang",
                "line_width",
                "layer_height",
                "printer_height",
                "bed_x",
                "bed_y",
                "speed",
                "max_flow",
                "filament_d",
                "density",
            ):
                fresh[k] = base[k]
            fresh.update(spec)
            return BoxParams.from_dict(fresh)
    return BoxParams()


def surprise(keep: BoxParams | None = None, seed: int | None = None) -> BoxParams:
    rng = random.Random(seed)
    p = keep.copy() if keep is not None else BoxParams()
    p.kind = rng.choice([ORGANISER, LIDDED_BOX, DRAWER_UNIT, PARTS_BIN, CADDY])
    if p.kind in (DRAWER_UNIT, PARTS_BIN, CADDY):
        p.shape = rng.choice([RECTANGLE, SQUARE])
    else:
        p.shape = rng.choice([RECTANGLE, SQUARE, HEXAGON, OCTAGON])

    max_xy = min(p.bed_x, p.bed_y) * 0.55
    p.length = round(rng.uniform(75.0, min(160.0, max_xy)), 0)
    p.width = p.length if p.shape != RECTANGLE else round(rng.uniform(65.0, min(130.0, max_xy)), 0)
    p.height = round(rng.uniform(45.0, min(110.0, p.printer_height * 0.6)), 0)
    p.corner_r = round(rng.uniform(5.0, 14.0), 1)
    p.stackable = p.kind != CADDY
    p.connectable = True
    p.div_x = rng.randint(1, 3)
    p.div_y = rng.randint(1, 3)
    p.div_mode = SLIDE_IN if (p.kind in (ORGANISER, LIDDED_BOX) and p.shape in (RECTANGLE, SQUARE) and rng.random() < 0.35) else BUILT_IN
    p.scoop_floor = rng.random() < 0.8
    p.pattern = rng.choice([SMOOTH, RIBS, DIAMONDS, RINGS, HEX_WINDOWS])
    pal = rng.choice(PALETTES)[1]
    p.color1, p.color2, p.color3, p.color4 = pal
    p.colour_style = rng.choice([ACCENT_PARTS, BANDS, ONE_COLOUR])
    p.colours_used = 2 if p.colour_style != ONE_COLOUR else 1
    p.name = f"surprise_box_{rng.randint(10, 99)}"
    return p
