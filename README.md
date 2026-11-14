# Boxinator

**Boxinator** is a focused desktop designer for 3D-printable **stackable, connectable, divided boxes, workshop parts bins, carry caddies, and modular side-drawer units** — all engineered to print with **zero supports**.

## Key Features

1. **5 Focused Box Roles**
   - **Organiser Box:** Open-top divided desk, drawer, or craft organiser.
   - **Lidded Box:** Divided box with either a **Stackable Sorting-Tray Lid** (doubles as a shallow parts tray and accepts another box stacked on top) or a **Slide-Lock Corner-Rail Lid**.
   - **Side Drawer Unit:** Turns a box on its side into a **modular drawer cubby**! The outer **Cubby Shell** prints upright on its closed back wall (zero supports, zero bridging) with **4-way XY dovetails** on all four outer walls. When laid on its side, those walls become the Left, Right, Top, and Bottom faces—so cubby shells lock together **side-by-side AND stacked vertically** into a rigid multi-drawer cabinet. Includes a matching divided **Sliding Drawer** with pull handle, runner guides, and an anti-tip stop catch.
   - **Front-Scoop Parts Bin:** Classic open-front workshop bin with a smooth angled mouth that prints upright without supports.
   - **Carry Caddy:** Divided tote with a central arched carry handle.

2. **Stackable & Connectable (Zero-Support Geometry)**
   - **Stackable Foot:** 45° recessed bottom foot nests positively inside the rim (or tray lid) of any matching box below.
   - **XY Dovetail Keys & Slots:** Interlocking dovetail keys and slots run vertically along the outer walls (`0°` Z overhang) with a built-in bottom alignment ledge so connected boxes sit flush.
   - **4 Footprint Shapes:** Rectangle, Square, Hexagon (for honeycomb desk clusters), and Octagon.

3. **Clever Interior & Workshop Details**
   - **Built-in vs. Slide-in Dividers:** Print internal dividers as one solid piece with the box, or print vertical wall slots inside the box alongside fast, flat-printed slide-in divider plates.
   - **Curved Finger-Scoop Floors:** Concave bottom fillet lets you slide tiny M2/M3 screws, SMD parts, or board-game tokens right up the wall with one finger.
   - **Finger-Dip Cutouts:** Smooth cosine dips in the top of each divider wall for easy pinching.
   - **Front Slide-in Label Holder:** Support-free 45° retaining rails on the front face for paper or thin printed labels.

4. **Focused UI & Live 3D Views**
   - **Assembled View** with interactive **Drawer Pull-Out / Lid Lift** slider.
   - **2×2 Connected Cluster View** to preview boxes/drawers linked side-by-side and stacked together.
   - **Section Cut View**, **Overhang Heat-Map Check**, and **Print Bed Layout**.
   - **Multi-colour 3MF & Binary STL Export** with one-click **Open in Slicer**.

## Running Boxinator

Double-click `run.bat` on Windows, or run from a Python 3.10+ environment:

```powershell
pip install -r requirements.txt
python main.py
```

## Running the Tests

```powershell
python -m unittest discover -s tests
```
