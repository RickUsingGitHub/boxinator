"""Rich, plain-English tooltips for every control, dropdown item, tab, and button in Boxinator."""

from __future__ import annotations

from .params import (
    ACCENT_PARTS,
    BANDS,
    BUILT_IN,
    CADDY,
    DIAMONDS,
    DRAWER_UNIT,
    FIRM,
    GENTLE,
    GLOSSY,
    HEX_WINDOWS,
    HEXAGON,
    LIDDED_BOX,
    MATTE,
    OCTAGON,
    ONE_COLOUR,
    ORGANISER,
    PARTS_BIN,
    RECTANGLE,
    RIBS,
    RINGS,
    SILK,
    SLIDE_IN,
    SLIDE_LID,
    SMOOTH,
    SNUG,
    SQUARE,
    TRANSLUCENT,
    TRAY_LID,
)

# ---------------------------------------------------------------------------
# Per-item tooltips for ComboBoxes (shown when hovering options in dropdowns)
# ---------------------------------------------------------------------------

KIND_ITEM_TIPS = {
    ORGANISER: (
        "<b>Organiser box:</b> Open-top desk or drawer organiser with custom compartment dividers, "
        "optional stackable nesting foot, and side-locking dovetails. Prints flat in one piece."
    ),
    LIDDED_BOX: (
        "<b>Lidded box:</b> Divided storage box with a matching printable lid (choose a Stackable "
        "Sorting-Tray Lid or a Slide-Lock Rail Lid in the <i>Stack, Connect &amp; Role</i> tab)."
    ),
    DRAWER_UNIT: (
        "<b>Side drawer unit:</b> Modular cubby shell that lays on its side + a pull-out divided "
        "drawer. The outer shell prints upright on its back wall with <b>zero supports</b>, and "
        "locks to neighbour cubbies both side-by-side AND stacked!"
    ),
    PARTS_BIN: (
        "<b>Front-scoop parts bin:</b> Workshop hardware bin with an angled open front mouth so you "
        "can see and grab screws/parts even when bins are stacked high."
    ),
    CADDY: (
        "<b>Carry caddy:</b> Portable divided tool/craft tote with a sturdy central bridge handle "
        "that rises at a support-free 45° arch out of the internal dividers."
    ),
}

SHAPE_ITEM_TIPS = {
    RECTANGLE: (
        "<b>Rectangle:</b> Independent Length (X) and Width (Y). Best for desk drawers, shelves, "
        "and modular side-drawer cabinets."
    ),
    SQUARE: (
        "<b>Square:</b> Equal Length and Width on all 4 sides—so boxes can rotate 90° and still "
        "stack and lock together."
    ),
    HEXAGON: (
        "<b>Hexagon (Honeycomb):</b> 6-sided honeycomb pod. Connects in 6 directions to build "
        "organic desktop or wall honeycomb clusters."
    ),
    OCTAGON: (
        "<b>Octagon:</b> 8-sided chamfered pod with dovetail connectors on its flat cardinal faces."
    ),
}

DIV_MODE_ITEM_TIPS = {
    BUILT_IN: (
        "<b>Built-in walls:</b> Divider walls are fused directly into the box (or sliding drawer) "
        "and print as a single rigid piece. Best when you want maximum strength and zero assembly."
    ),
    SLIDE_IN: (
        "<b>Slide-in plates:</b> Moulds vertical V-slot guide ribs onto the inside walls of the box "
        "and generates separate flat-printed divider plates. Slide them in or pull them out "
        "anytime to create double-wide compartments!"
    ),
}

LID_STYLE_ITEM_TIPS = {
    TRAY_LID: (
        "<b>Stackable sorting-tray lid:</b> Drops onto the rim with a 45° self-centring plug and "
        "snap detent, side finger-pry notches, and a recessed top dish that holds small screws "
        "while you work (or nests the stacking foot of another box on top)."
    ),
    SLIDE_LID: (
        "<b>Slide-lock corner-rail lid:</b> Slides in from the front along 45° internal dovetail "
        "rails moulded inside the top rim, with a raised front thumb grip bar so the lid cannot "
        "pop off if the box is tipped."
    ),
}

FIT_ITEM_TIPS = {
    GENTLE: (
        "<b>Gentle (0.28 mm gap):</b> Easy, low-friction slip fit. Best for printers with slightly "
        "rough walls, PETG filament, or boxes you want to separate and rearrange frequently."
    ),
    SNUG: (
        "<b>Snug (0.20 mm gap):</b> Balanced everyday tolerance for modern printers (Bambu, Prusa, "
        "Voron, etc.). Dovetails lock firmly without play and drawers slide smoothly."
    ),
    FIRM: (
        "<b>Firm (0.14 mm gap):</b> Tight friction lock for well-calibrated printers. Great when "
        "building a permanent multi-drawer cabinet bank that stays locked together."
    ),
}

PATTERN_ITEM_TIPS = {
    SMOOTH: "<b>Smooth walls:</b> Clean, flat outer walls—fastest to print and easiest to wipe clean.",
    RIBS: (
        "<b>Vertical fluted ribs:</b> Architectural vertical flutes around the outer wall. Adds "
        "stiffness against wall bowing and hides vertical seam lines."
    ),
    DIAMONDS: (
        "<b>Diamond knurl:</b> Cross-hatched 45° diamond texture for a tactile workshop grip and "
        "matte-looking surface."
    ),
    RINGS: (
        "<b>Horizontal rings:</b> Evenly spaced horizontal grip bands that accentuate layer lines "
        "intentionally and stiffen tall walls."
    ),
    HEX_WINDOWS: (
        "<b>Recessed hex dimples:</b> Shallow honeycomb reliefs across the outer walls (automatically "
        "kept ≤ 45° so they print with zero supports)."
    ),
}

COLOUR_ITEM_TIPS = {
    ONE_COLOUR: (
        "<b>Single filament colour:</b> Prints the box and any accessories in Filament #1. "
        "Simple single-spool print."
    ),
    BANDS: (
        "<b>Horizontal colour bands:</b> Alternates your chosen filaments in horizontal stripes up "
        "the height of the box. Works with AMS/MMU multi-colour printers OR simple pause-at-height "
        "manual filament swaps on any single-extruder printer!"
    ),
    ACCENT_PARTS: (
        "<b>Accent lid / drawer / dividers:</b> Prints the main box or cubby shell in Filament #1 "
        "and the lid, sliding drawer, or slide-in divider plates in Filament #2 for a two-tone look."
    ),
}

LOOK_ITEM_TIPS = {
    MATTE: "<b>Matte PLA / PETG:</b> Soft, low-glare studio shading—great for inspecting wall geometry.",
    SILK: "<b>Silk PLA:</b> Metallic dual-highlight sheen that previews shiny silk/co-extrusion filaments.",
    GLOSSY: "<b>Glossy PETG / ABS:</b> Crisp specular highlights like glossy PETG or smoothed ABS.",
    TRANSLUCENT: (
        "<b>Translucent / Clear:</b> Semi-transparent preview so you can see internal dividers, "
        "drawers, and dovetail sockets right through the outer walls."
    ),
}


# ---------------------------------------------------------------------------
# Control & Widget Tooltips
# ---------------------------------------------------------------------------

TIPS = {
    # Top Quick Bar
    "top_box": (
        "<b>1. What are we making?</b><br>"
        "Pick the overall functional role of your box, load a curated starter preset, "
        "or roll a random printable design."
    ),
    "kind": (
        "<b>Box Role (What kind of container to build):</b><br>"
        "• <b>Organiser box:</b> Open-top divided tray for desks, drawers, or shelves.<br>"
        "• <b>Lidded box:</b> Divided storage box with a snap-fit or slide-lock lid.<br>"
        "• <b>Side drawer unit:</b> Modular cubby shell (laid on its side) + sliding divided drawer.<br>"
        "• <b>Front-scoop parts bin:</b> Stackable workshop screw bin with an open front pick-mouth.<br>"
        "• <b>Carry caddy:</b> Portable divided tote with a central 45° bridge handle."
    ),
    "presets": (
        "<b>Choose a Preset (Ctrl+G):</b><br>"
        "Browse 10 ready-made starter designs—including a 4-Drawer Modular Cabinet, "
        "SMD Screw Bin, Honeycomb Desk Pod, Board-Game Token Box, and Carry Tool Caddy."
    ),
    "surprise": (
        "<b>Surprise Me! (Ctrl+R):</b><br>"
        "Generates a fresh, randomized box, drawer unit, or parts bin with harmonious "
        "dimensions, compartments, and colour palette—guaranteed 100% support-free and printable."
    ),
    "pull_drawer": (
        "<b>Drawer Pull-Out Preview (0–100%):</b><br>"
        "Slides the drawer in and out in the 3D viewport so you can inspect how it fits inside "
        "the cubby shell and see its internal dividers.<br>"
        "<i>Note:</i> This is for 3D inspection only—exported print files (.3mf / .stl) always "
        "place the drawer flat on the print bed."
    ),
    "pull_lid": (
        "<b>Lid Lift / Open Preview (0–100%):</b><br>"
        "Lifts or slides the lid open in the 3D viewport so you can see inside the compartments "
        "and inspect the lid locking rim.<br>"
        "<i>Note:</i> This is for 3D inspection only—exported print files (.3mf / .stl) always "
        "place the lid flat on the print bed."
    ),

    # Tabs
    "tab_size": (
        "<b>Size &amp; Dividers Tab:</b><br>"
        "Set the outer footprint shape, outside dimensions (mm), wall &amp; floor thicknesses, "
        "internal compartment grid (Columns × Rows), and finger-scoop floor."
    ),
    "tab_modular": (
        "<b>Stack, Connect &amp; Role Tab:</b><br>"
        "Configure vertical stacking feet, side-to-side interlocking keystone dovetails, "
        "joint clearance fit, and role-specific options (lids, drawers, front scoop, caddy handle, labels)."
    ),
    "tab_surface": (
        "<b>Surface &amp; Colours Tab:</b><br>"
        "Add structural/decorative outer wall textures, choose filament colours &amp; palettes, "
        "change the 3D material finish, and set your 3D printer's bed size."
    ),

    # Tab 1: Shape & Outer Dimensions
    "grp_size": (
        "<b>Shape &amp; Outer Dimensions:</b><br>"
        "Controls the outside footprint and overall millimetre size of a single box or cubby unit."
    ),
    "shape": (
        "<b>Footprint Shape:</b><br>"
        "• <b>Rectangle:</b> Custom Length (X) and Width (Y). Required for Side-Drawer Units and Slide Lids.<br>"
        "• <b>Square:</b> Equal X and Y sides—can stack and connect rotated 90°.<br>"
        "• <b>Hexagon (Honeycomb):</b> 6-sided pod that locks to neighbours in 6 directions.<br>"
        "• <b>Octagon:</b> 8-sided chamfered pod."
    ),
    "length_box": (
        "<b>Length (X) — Left-to-Right Outside Width (30–240 mm):</b><br>"
        "Total outside left-to-right dimension of the box in millimetres (excluding protruding "
        "dovetail tails)."
    ),
    "length_poly": (
        "<b>Outer Size — Flat-to-Flat Width (30–240 mm):</b><br>"
        "Outside width across the polygon footprint in millimetres."
    ),
    "length_drawer": (
        "<b>Cubby Width (X) — Left-to-Right Cabinet Width (30–240 mm):</b><br>"
        "Total outside left-to-right width of one drawer cubby unit when laid on its side."
    ),
    "width_box": (
        "<b>Width (Y) — Front-to-Back Outside Depth (30–240 mm):</b><br>"
        "Total outside front-to-back depth of the box in millimetres."
    ),
    "width_drawer": (
        "<b>Cubby Height (Z) — Vertical Cabinet Height (30–240 mm):</b><br>"
        "Outside top-to-bottom height of one drawer cubby unit when laid on its side on your desk."
    ),
    "height_box": (
        "<b>Height (Z) — Total Box Height (18–220 mm):</b><br>"
        "Outside vertical height from the print bed to the top rim of the box."
    ),
    "height_drawer": (
        "<b>Cubby Depth (Y) — Front-to-Back Drawer Depth (18–220 mm):</b><br>"
        "How deep the cubby shell and sliding drawer run from front to back.<br>"
        "<i>Print note:</i> Because the cubby shell prints standing upright on its closed back wall, "
        "this depth is the vertical Z height on your print bed."
    ),
    "corner_r": (
        "<b>Corner Rounding Radius (1.5–45 mm):</b><br>"
        "Rounds the vertical outer and inner corners of the box.<br>"
        "• <b>6–12 mm</b> is ideal: it prevents sharp corners from lifting/warping off the print bed "
        "and lets your printer extrude smooth, fast corner arcs without ringing."
    ),
    "wall": (
        "<b>Outer Wall Thickness (1.2–5.0 mm):</b><br>"
        "Thickness of the outer perimeter walls.<br>"
        "• <b>1.6–2.0 mm</b> (4–5 perimeters with a standard 0.4 mm nozzle) gives a strong, rigid box.<br>"
        "• Increase to <b>2.4–3.0 mm</b> for large heavy-duty workshop bins or tool caddies."
    ),
    "floor": (
        "<b>Floor Thickness (1.2–6.0 mm):</b><br>"
        "Solid thickness of the bottom base (or the closed back wall of a side-drawer cubby).<br>"
        "• <b>1.6–2.0 mm</b> (8–10 layers at 0.2 mm layer height) prevents bottom flexing."
    ),

    # Tab 1: Dividers & Easy-Grab Interior
    "grp_div": (
        "<b>Dividers &amp; Easy-Grab Interior:</b><br>"
        "Subdivide the interior into a grid of compartments (or inside the sliding drawer for a "
        "Side-Drawer Unit) and add ergonomic scoops for picking out tiny parts."
    ),
    "div_x": (
        "<b>Columns Across (X) (1–8):</b><br>"
        "Number of compartments from left to right.<br>"
        "• Set to <b>1</b> for no left-to-right dividers (full-width span).<br>"
        "• Set to <b>2–8</b> to add internal vertical divider walls running front-to-back."
    ),
    "div_y": (
        "<b>Rows Front-to-Back (Y) (1–8):</b><br>"
        "Number of compartments from front to back.<br>"
        "• Set to <b>1</b> for no front-to-back dividers.<br>"
        "• Total compartments = <b>Columns × Rows</b>."
    ),
    "div_mode": (
        "<b>Divider Type:</b><br>"
        "• <b>Built-in walls:</b> Printed as one solid piece with the box or drawer—stiffest and "
        "zero assembly.<br>"
        "• <b>Slide-in plates:</b> Moulds vertical V-slot guide rails onto the inner box walls and "
        "exports separate flat divider plates so you can remove or rearrange compartments anytime."
    ),
    "div_wall": (
        "<b>Divider Thickness (1.0–4.0 mm):</b><br>"
        "Thickness of the internal partition walls between compartments.<br>"
        "• <b>1.2–1.6 mm</b> (3–4 nozzle perimeters) prints fast and stays plenty stiff."
    ),
    "div_h": (
        "<b>Divider Height (35–100% of interior depth):</b><br>"
        "How tall the internal dividers stand relative to the full interior height.<br>"
        "• <b>85–95%</b> keeps parts separated while leaving clearance underneath a recessed lid.<br>"
        "• Lower to <b>50–75%</b> if you want extra finger room to reach over dividers."
    ),
    "div_dip": (
        "<b>Finger-Dip Cutout Depth (0–25 mm):</b><br>"
        "Carves a smooth curved saddle dip into the top centre of each divider wall so your thumb "
        "and index finger can easily pinch items inside narrow compartments.<br>"
        "• Set to <b>0 mm</b> for flat-topped dividers."
    ),
    "scoop": (
        "<b>Curved Finger-Scoop Floor:</b><br>"
        "Adds a smooth curved fillet ramp around the bottom perimeter where the floor meets the walls.<br>"
        "• Instead of tiny screws, beads, or board-game tokens getting trapped in a sharp 90° bottom "
        "corner, you can slide them straight up the curved wall onto your fingertip!"
    ),

    # Tab 2: Stackable & Connectable
    "grp_mod": (
        "<b>Stackable &amp; Connectable:</b><br>"
        "Turn single boxes or drawer cubbies into a modular interlocking storage system with "
        "zero extra hardware or connector clips."
    ),
    "stackable": (
        "<b>Stackable Nesting Base (45° Support-Free Foot):</b><br>"
        "Steps the bottom foot of the box inward along a 45° support-free chamfer so it drops "
        "neatly inside the open top rim (or recessed lid tray) of an identical box below it.<br>"
        "• Prevents stacked boxes from sliding off each other."
    ),
    "stack_h": (
        "<b>Stacking Foot Depth (2.0–8.0 mm):</b><br>"
        "How deep the stepped bottom foot drops into the box below.<br>"
        "• <b>3.2–4.5 mm</b> engages positively without stealing interior height."
    ),
    "connectable": (
        "<b>Connectable Sides (Interlocking XY Dovetails):</b><br>"
        "Moulds flared, rounded-corner <b>Male Dovetail Tenons (⏢)</b> on the Right &amp; Back walls "
        "and matching recessed <b>Female Dovetail Mortises (⏢)</b> on the Left &amp; Front walls.<br>"
        "• Rounded corners eliminate sharp nozzle-ooze interference and root stress notches for "
        "cleaner printer margins.<br>"
        "• Slide two boxes (or two side-drawer cubbies) together to lock them into a rigid "
        "side-by-side or stacked bank with <b>zero extra clips</b>!<br>"
        "• On a <b>Side-Drawer Unit</b>, the bottom wall uses recessed Female Mortises so bottom-row "
        "cubbies sit 100% flat on your desk while upper cubbies lock onto the top Male Tails."
    ),
    "dove_d": (
        "<b>Dovetail Lock Depth (1.6–4.0 mm):</b><br>"
        "How far the keystone dovetail tenons protrude and flare outward.<br>"
        "• <b>3.0–3.4 mm</b> gives a wide ~1.7:1 keystone flare that locks neighbours solidly.<br>"
        "• Reduce to <b>2.0–2.4 mm</b> on very small boxes with thin walls."
    ),
    "fit": (
        "<b>Joint &amp; Sliding Fit (Clearance Gap):</b><br>"
        "Sets the exact XY tolerance gap between all mating parts (dovetail connectors, sliding "
        "drawers, lids, and slide-in dividers):<br>"
        "• <b>Gentle (0.28 mm):</b> Easy slip fit—best for frequent disassembly or textured filaments.<br>"
        "• <b>Snug (0.20 mm):</b> Everyday standard fit—smooth drawers and play-free dovetails.<br>"
        "• <b>Firm (0.14 mm):</b> Tight friction lock for permanent multi-drawer cabinets."
    ),

    # Tab 2: Role-specific groups
    "grp_lid": (
        "<b>Lid Options (for Lidded Box):</b><br>"
        "Choose how the separate printable lid closes and locks onto the box rim."
    ),
    "lid_style": (
        "<b>Lid Mechanism:</b><br>"
        "• <b>Stackable sorting-tray lid:</b> Drops in with a 45° self-centring plug + snap detent, "
        "side finger-pry notches, and a recessed top dish for sorting parts or stacking another box.<br>"
        "• <b>Slide-lock corner-rail lid:</b> Slides in from the front along 45° internal dovetail "
        "rails with a raised thumb grip bar—won't pop open if knocked over!"
    ),
    "grp_drawer": (
        "<b>Side-Drawer Unit Options:</b><br>"
        "Configure the pull-out drawer and cubby shell behaviour."
    ),
    "drawer_stop": (
        "<b>Anti-Tip Drawer Stop Catch:</b><br>"
        "Adds a small 45° keeper nub inside the top front rim of the cubby shell and a matching "
        "catch tab at the top back of the sliding drawer.<br>"
        "• Stops the drawer from accidentally falling out and spilling parts when pulled open.<br>"
        "• Simply tilt the drawer slightly upward at the end of its travel to remove it completely."
    ),
    "drawer_note": (
        "<b>How Side-Drawer Units Print &amp; Connect:</b><br>"
        "1. <b>Cubby Shell:</b> Prints standing upright on its closed back wall—zero supports, zero bridging!<br>"
        "2. <b>Sliding Drawer:</b> Prints flat on its base right beside the shell.<br>"
        "3. <b>Flat Bottom + 4-Way Lock:</b> Lay the shell on its side. Its bottom face has recessed "
        "Female Dovetail Sockets so it sits flat on your desk, while its Right and Top faces carry "
        "Male Dovetail Tails to lock into neighbours side-by-side and stacked!"
    ),
    "grp_bin": (
        "<b>Workshop Parts Bin Options:</b><br>"
        "Adjust the angled front pick-mouth opening so you can reach inside even when bins are stacked."
    ),
    "bin_scoop": (
        "<b>Front Mouth Drop (20–65%):</b><br>"
        "How far down the front wall dips to form the open reach-in mouth.<br>"
        "• <b>40–50%</b> gives a generous opening for fingers while keeping deep storage in the back."
    ),
    "grp_caddy": (
        "<b>Carry Caddy Options:</b><br>"
        "Adjust the central overhead carry handle."
    ),
    "caddy_h": (
        "<b>Handle Arch Height (15–75 mm):</b><br>"
        "How high the central carry handle rises above the top rim of the box.<br>"
        "• The handle grows out of the centre divider wall as a 45° arch, so it prints with "
        "<b>zero supports</b>!"
    ),
    "grp_label": (
        "<b>Workshop Labelling:</b><br>"
        "Add a built-in front frame for paper, cardstock, or 3D-printed labels."
    ),
    "label_slot": (
        "<b>Front Slide-In Label Holder Frame:</b><br>"
        "Moulds a support-free 45° label pocket onto the front wall of the box.<br>"
        "• Drop in a standard <b>48 × 15 mm</b> paper/cardstock slip or a thin 3D-printed tag."
    ),

    # Tab 3: Surface, Colours & Printer
    "grp_tex": (
        "<b>Outer Wall Texture:</b><br>"
        "Add structural ribs, flutes, or knurling to the outer walls. Boxinator automatically "
        "keeps dovetail joints and label frames smooth so parts always fit cleanly."
    ),
    "pattern": (
        "<b>Surface Pattern:</b><br>"
        "• <b>Smooth walls:</b> Clean, flat walls (fastest print).<br>"
        "• <b>Vertical fluted ribs:</b> Architectural flutes that stiffen walls and hide seams.<br>"
        "• <b>Diamond knurl:</b> Tactile cross-hatched workshop grip.<br>"
        "• <b>Horizontal rings:</b> Even horizontal grip ribs.<br>"
        "• <b>Recessed hex dimples:</b> Support-free honeycomb relief pattern."
    ),
    "rib_d": (
        "<b>Pattern Depth (0.4–3.0 mm):</b><br>"
        "How far the surface texture ribs/flutes/dimples project from the wall.<br>"
        "• <b>0.8–1.4 mm</b> gives a crisp shadow line without slowing down print speed."
    ),
    "rib_p": (
        "<b>Pattern Spacing / Pitch (4.0–18.0 mm):</b><br>"
        "Distance from one rib/flute/dimple to the next around the perimeter.<br>"
        "• Smaller values = finer, denser texture; larger values = bold, wide flutes."
    ),
    "grp_col": (
        "<b>Colours &amp; Material:</b><br>"
        "Configure multi-colour filament assignments (baked directly into exported 3MF files) "
        "and preview different filament surface finishes."
    ),
    "col_style": (
        "<b>Colour Mode:</b><br>"
        "• <b>Single filament colour:</b> Everything uses Filament #1.<br>"
        "• <b>Horizontal colour bands:</b> Stripes the box by height across Filaments #1..#N.<br>"
        "• <b>Accent lid / drawer / dividers:</b> Main body in Filament #1, accessory part in Filament #2."
    ),
    "col_used": (
        "<b>Filaments Used (1–4):</b><br>"
        "How many filament colours to cycle through when using Horizontal Colour Bands or "
        "multi-colour 3MF export."
    ),
    "bands": (
        "<b>Height Bands (2–16):</b><br>"
        "Number of horizontal colour stripes from bottom to top when <i>Colour Mode</i> is set to "
        "<b>Horizontal colour bands</b>."
    ),
    "palette": (
        "<b>Quick Colour Palette:</b><br>"
        "Pick a curated 4-colour theme (Workshop Teal &amp; Amber, Bambu Carbon, Cyberpunk, "
        "Pastel Desk, etc.) to update all 4 filament swatches at once."
    ),
    "swatch": (
        "<b>Filament Swatch #{idx}:</b><br>"
        "Click to pick a custom colour for <b>Filament #{idx}</b>.<br>"
        "• <b>#1:</b> Main box body / cubby shell.<br>"
        "• <b>#2:</b> Lid, sliding drawer, or slide-in dividers (plus Band #2).<br>"
        "• <b>#3 &amp; #4:</b> Additional horizontal stripe bands."
    ),
    "look": (
        "<b>Material Look (3D Shader Preview):</b><br>"
        "Preview how the geometry catches light in <b>Matte PLA</b>, shiny <b>Silk PLA</b>, "
        "<b>Glossy PETG</b>, or see-through <b>Translucent</b> filament."
    ),
    "grp_prn": (
        "<b>Printer &amp; Slicer:</b><br>"
        "Set your 3D printer's build volume and overhang limit so Boxinator can verify that "
        "every part fits on your bed and prints without supports."
    ),
    "bed_x": (
        "<b>Bed Width X (120–450 mm):</b><br>"
        "Left-to-right build plate width of your 3D printer (e.g. 256 mm for Bambu X1/P1/A1, "
        "250 mm for Prusa MK4, 180 mm for A1 Mini / Prusa Mini)."
    ),
    "bed_y": (
        "<b>Bed Depth Y (120–450 mm):</b><br>"
        "Front-to-back build plate depth of your 3D printer."
    ),
    "bed_z": (
        "<b>Max Print Height Z (120–450 mm):</b><br>"
        "Maximum vertical print height of your 3D printer."
    ),
    "overhang": (
        "<b>Support-Free Overhang Limit (35–60°):</b><br>"
        "Maximum overhang angle (measured from vertical) your printer handles cleanly without supports.<br>"
        "• Standard FDM printers handle <b>45°</b> effortlessly. Boxinator designs all chamfers, "
        "dovetails, and handles to stay within 45°."
    ),
    "slicer": (
        "<b>Target Slicer Application:</b><br>"
        "Select which installed slicer (Bambu Studio, OrcaSlicer, PrusaSlicer, Cura, etc.) "
        "launches when you click <b>Open in Slicer</b>."
    ),

    # Bottom Export Bar
    "save_3mf": (
        "<b>Save for Printing (.3MF) — Recommended (Ctrl+E):</b><br>"
        "Exports a complete, ready-to-slice <b>.3mf</b> project containing the main box body AND "
        "any lid, sliding drawer, or slide-in dividers already oriented flat on the print bed "
        "with multi-colour filament assignments included."
    ),
    "save_acc_none": (
        "<b>Save Accessory STL:</b><br>"
        "Currently disabled because this design prints as a single piece.<br>"
        "Switch Role to <i>Lidded box</i> or <i>Side drawer unit</i>, or set Divider Type to "
        "<i>Slide-in plates</i>, to generate a separate accessory part."
    ),
    "save_acc_active": (
        "<b>Save {label} (.STL):</b><br>"
        "Exports just the <b>{label}</b> as a standalone binary STL file, already rotated flat "
        "in its optimal support-free print orientation."
    ),
    "open_slicer": (
        "<b>Open in Slicer (Ctrl+P):</b><br>"
        "Builds a ready-to-print <b>.3mf</b> file with all parts laid out on the print bed and "
        "launches it directly in your selected slicer."
    ),

    # Centre 3D View Mode Bar & Viewport
    "rb_asm": (
        "<b>Assembled View:</b><br>"
        "Shows a single finished unit with its lid, sliding drawer, or dividers in their working "
        "position. Use the top <i>Drawer pull-out / Lid lift</i> slider to open and close it!"
    ),
    "rb_cluster": (
        "<b>2×2 Connected Cluster Preview:</b><br>"
        "Shows 4 units locked together via their interlocking XY dovetails and stacking feet "
        "(with the 4th unit shown mid-slide along the dovetail rails so you can see how the "
        "male tenons and female mortises engage)."
    ),
    "rb_section": (
        "<b>Section Cut View:</b><br>"
        "Slices the box open down the middle so you can inspect internal wall thickness, "
        "compartment dividers, finger-scoop floor ramps, and lid/dovetail lock profiles."
    ),
    "rb_overhang": (
        "<b>Overhang Check (Print Orientation):</b><br>"
        "Shows the main body in its printing orientation and colours every surface by overhang angle:<br>"
        "• <b>Green:</b> Safe, support-free angle.<br>"
        "• <b>Amber:</b> Approaching your overhang limit.<br>"
        "• <b>Red:</b> Steeper than your overhang limit (would require supports)."
    ),
    "rb_bed": (
        "<b>Print Bed Layout View:</b><br>"
        "Shows all parts (box/cubby shell + lid, drawer, or divider plates) arranged flat on your "
        "printer's 10 mm grid build plate, exactly as they will be exported to your slicer."
    ),
    "fit_cam": (
        "<b>Reset Camera:</b><br>"
        "Re-centres and zooms the 3D view to fit the current model.<br>"
        "<i>Tip:</i> You can also <b>double-click</b> anywhere in the 3D viewport to reset the camera."
    ),
    "viewer": (
        "<b>Interactive 3D Viewport:</b><br>"
        "• <b>Left-drag:</b> Orbit / rotate camera<br>"
        "• <b>Right-drag</b> (or <b>Shift + Left-drag</b>): Pan camera<br>"
        "• <b>Mouse wheel:</b> Zoom in / out<br>"
        "• <b>Double-click:</b> Reset camera to fit"
    ),
    "report_box": (
        "<b>Live Design Summary &amp; Print Check:</b><br>"
        "Updates automatically as you drag sliders: shows exact compartment inner dimensions, "
        "steepest overhang angle, estimated filament weight (g) &amp; print time, and "
        "step-by-step printing/assembly notes."
    ),
}
