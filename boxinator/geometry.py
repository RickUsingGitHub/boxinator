"""Parametric 3D geometry engine for Boxinator.

Builds closed, watertight, support-free meshes for:
* Stackable & connectable organiser boxes (Rectangle, Square, Hexagon, Octagon)
* Lidded boxes (Stackable Tray Lid or Slide-Lock Lid)
* Modular Side-Drawer Units (Cubby shell printed upright on its back with 4-way
  XY dovetails so shells lock side-by-side and stacked when laid on their side,
  plus a matching divided sliding drawer with pull handle and anti-tip stop)
* Open-front stackable/connectable workshop Parts Bins
* Divided Carry Caddies with central arched handle
* Built-in or flat-printed Slide-In cross-lap dividers

Every generated solid is constructed directly as a closed manifold triangle mesh
(verified by ``edge_check``) with no external boolean libraries required.
"""

from __future__ import annotations

import math

import numpy as np

from .params import (
    ACCENT_PARTS,
    BANDS,
    BUILT_IN,
    CADDY,
    DIAMONDS,
    DRAWER_UNIT,
    HEX_WINDOWS,
    HEXAGON,
    KIND_NAMES,
    LIDDED_BOX,
    OCTAGON,
    ONE_COLOUR,
    ORGANISER,
    PARTS_BIN,
    RECTANGLE,
    RIBS,
    RINGS,
    SHAPE_NAMES,
    SLIDE_IN,
    SLIDE_LID,
    SMOOTH,
    SQUARE,
    TRAY_LID,
    BoxParams,
)

TAU = 2.0 * math.pi
TOLERANCE = 0.5


def duration(seconds: float) -> str:
    m = int(round(seconds / 60.0))
    return f"{m // 60} h {m % 60:02d} min" if m >= 60 else f"{max(m, 1)} min"


def face_normals(verts: np.ndarray, faces: np.ndarray) -> np.ndarray:
    tri = verts[faces]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    return n / ln


def lean_angles(verts: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """Overhang angle from upright (degrees) for downward-facing surfaces; -1 for flat caps."""
    n = face_normals(verts, faces)
    down = -n[:, 2]
    over = np.degrees(np.arcsin(np.clip(down, 0.0, 1.0)))
    return np.where(np.abs(n[:, 2]) > 0.995, -1.0, np.where(down > 0.0, over, 0.0))


def mesh_volume(verts: np.ndarray, faces: np.ndarray) -> float:
    tri = verts[faces]
    return float(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6.0)


def edge_check(faces: np.ndarray) -> tuple[bool, int]:
    """Whether every directed edge in ``faces`` is paired once with its reverse."""
    f = np.asarray(faces, dtype=np.int64)
    if len(f) == 0:
        return False, 1
    a = f.ravel()
    b = np.roll(f, -1, axis=1).ravel()
    n = int(f.max()) + 1
    fwd = np.sort(a * n + b)
    rev = np.sort(b * n + a)
    twice = int((np.diff(fwd) == 0).sum())
    unmatched = int((fwd != rev).sum())
    return twice == 0 and unmatched == 0, twice + unmatched


def orient_outward(verts: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    v = np.asarray(verts, dtype=np.float64)
    f = np.asarray(faces, dtype=np.int64)
    if mesh_volume(v, f) < 0.0:
        f = f[:, ::-1].copy()
    return v, f


def combine_meshes(parts: list[tuple[np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
    vs, fs, offset = [], [], 0
    for v, f in parts:
        if len(v) == 0 or len(f) == 0:
            continue
        v, f = orient_outward(v, f)
        vs.append(v)
        fs.append(f + offset)
        offset += len(v)
    if not vs:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64)
    return np.concatenate(vs, axis=0), np.concatenate(fs, axis=0)


def translate_mesh(verts: np.ndarray, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> np.ndarray:
    return verts + np.array([dx, dy, dz], dtype=np.float64)


def rotate_x_90(verts: np.ndarray) -> np.ndarray:
    """Rotate mesh so upright print Z becomes horizontal -Y (for laying a cubby shell on its side)."""
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]
    return np.column_stack([x, -z, y])


# ===================================================================== 2D loops & primitives


def _anticlockwise(loop: np.ndarray) -> np.ndarray:
    x, y = loop[:, 0], loop[:, 1]
    area = 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))
    return loop if area >= 0 else loop[::-1].copy()


def base_polygon(shape: int, length: float, width: float, corner_r: float, n: int = 256) -> np.ndarray:
    """Closed anticlockwise 2D loop (n, 2) centred on the origin, sampled evenly by angle."""
    angles = np.arange(n) * (TAU / n)
    c, s = np.cos(angles), np.sin(angles)

    if shape == SQUARE:
        width = length
        shape = RECTANGLE

    if shape == RECTANGLE:
        hx = 0.5 * length
        hy = 0.5 * width
        r = min(max(corner_r, 1.0), min(hx, hy) - 1.0)
        ax, ay = max(hx - r, 0.5), max(hy - r, 0.5)
        # Ray intersection from origin at angle theta to rounded rectangle of half-size (hx, hy) and corner r
        pts = np.zeros((n, 2), dtype=np.float64)
        for i, (ci, si) in enumerate(zip(c, s)):
            ac, as_ = abs(ci), abs(si)
            # Check straight horizontal/vertical flanks first
            tx = hx / max(ac, 1e-12)
            ty = hy / max(as_, 1e-12)
            if tx <= ty and tx * as_ <= ay:
                rad = tx
            elif ty < tx and ty * ac <= ax:
                rad = ty
            else:
                # Corner circle centred at (ax, ay) with radius r: (t*ac - ax)^2 + (t*as - ay)^2 = r^2
                b_proj = ac * ax + as_ * ay
                disc = max(r * r - (ax * ax + ay * ay - b_proj * b_proj), 0.0)
                rad = b_proj + math.sqrt(disc)
            pts[i] = (rad * ci, rad * si)
        return pts

    sides = 6 if shape == HEXAGON else 8
    R = 0.5 * length
    r_c = min(max(corner_r, 1.0), 0.35 * R)
    sector = TAU / sides
    half_sec = 0.5 * sector
    # Exact C1-continuous rounded regular polygon with corner circle radius r_c at distance cx_c = R - r_c
    cx_c = max(R - r_c, 1.0)
    apothem = cx_c * math.cos(half_sec) + r_c
    rel_tan = math.atan2(cx_c * math.sin(half_sec), apothem)
    pts = np.zeros((n, 2), dtype=np.float64)
    for i, ang in enumerate(angles):
        rel = abs((ang + half_sec) % sector - half_sec)
        if rel <= rel_tan:
            rad = apothem / max(math.cos(rel), 1e-6)
        else:
            b_proj = cx_c * math.cos(half_sec - rel)
            disc = max(r_c * r_c - (cx_c * math.sin(half_sec - rel)) ** 2, 0.0)
            rad = b_proj + math.sqrt(disc)
        pts[i] = (rad * math.cos(ang), rad * math.sin(ang))
    return pts


def loop_normals(loop: np.ndarray) -> np.ndarray:
    """Outward unit normals (N, 2) of an anticlockwise 2D loop."""
    tang = np.roll(loop, -1, axis=0) - np.roll(loop, 1, axis=0)
    n = np.column_stack([tang[:, 1], -tang[:, 0]])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    return n / ln


def inset_loop(loop: np.ndarray, amount: float) -> np.ndarray:
    """Move an anticlockwise loop inward by ``amount`` along its outward normal, keeping it simple."""
    n = loop_normals(loop)
    moved = loop - n * amount
    # Ensure radii stay positive
    r_orig = np.hypot(loop[:, 0], loop[:, 1])
    r_new = np.hypot(moved[:, 0], moved[:, 1])
    scale = np.maximum(r_new, 2.0) / np.maximum(r_new, 1e-9)
    return moved * scale[:, None]


def _fillet_polyline_2d(
    pts: list[tuple[float, float]],
    radii: list[float],
    arc_steps: int = 4,
    seg_step: float = 1.6,
) -> list[tuple[float, float]]:
    """Round interior corners of a 2D (t, n) polyline with exact tangent circular arcs.

    Eliminates sharp acute tips on dovetails so FDM nozzles print clean, predictable
    clearances without corner bulging or root stress concentrations.
    """
    m = len(pts)
    if m < 3:
        return list(pts)

    p = [np.array(pt, dtype=np.float64) for pt in pts]
    trims: list[tuple[np.ndarray, np.ndarray, np.ndarray, float] | None] = [None] * m

    for i in range(1, m - 1):
        r = float(radii[i])
        if r <= 1e-4:
            continue
        v_in = p[i - 1] - p[i]
        v_out = p[i + 1] - p[i]
        l_in = float(np.linalg.norm(v_in))
        l_out = float(np.linalg.norm(v_out))
        if l_in < 1e-6 or l_out < 1e-6:
            continue
        u_in = v_in / l_in
        u_out = v_out / l_out
        cos_a = float(np.clip(np.dot(u_in, u_out), -0.9999, 0.9999))
        ang = math.acos(cos_a)
        if ang > math.pi - 1e-3 or ang < 1e-3:
            continue
        half_a = 0.5 * ang
        tan_half = math.tan(half_a)
        if tan_half < 1e-4:
            continue
        d_tan = r / tan_half
        max_d = 0.44 * min(l_in, l_out)
        if d_tan > max_d:
            d_tan = max_d
            r_eff = d_tan * tan_half
        else:
            r_eff = r
        t1 = p[i] + u_in * d_tan
        t2 = p[i] + u_out * d_tan
        bis = u_in + u_out
        bis_len = float(np.linalg.norm(bis))
        if bis_len < 1e-6:
            continue
        bis /= bis_len
        dist_c = r_eff / max(math.sin(half_a), 1e-6)
        center = p[i] + bis * dist_c
        trims[i] = (t1, t2, center, r_eff)

    out: list[tuple[float, float]] = []

    def _emit_line(a: np.ndarray, b: np.ndarray):
        dist = float(np.linalg.norm(b - a))
        n_seg = max(int(math.ceil(dist / seg_step)), 1)
        for k in range(n_seg):
            u = k / float(n_seg)
            pt = a + u * (b - a)
            out.append((float(pt[0]), float(pt[1])))

    cur = p[0]
    for i in range(1, m - 1):
        tr = trims[i]
        if tr is None:
            _emit_line(cur, p[i])
            cur = p[i]
        else:
            t1, t2, center, r_eff = tr
            _emit_line(cur, t1)
            a1 = math.atan2(t1[1] - center[1], t1[0] - center[0])
            a2 = math.atan2(t2[1] - center[1], t2[0] - center[0])
            da = (a2 - a1 + math.pi) % (2.0 * math.pi) - math.pi
            for s in range(arc_steps):
                u = s / float(arc_steps)
                ang = a1 + u * da
                pt = center + r_eff * np.array([math.cos(ang), math.sin(ang)], dtype=np.float64)
                out.append((float(pt[0]), float(pt[1])))
            cur = t2
    _emit_line(cur, p[-1])
    out.append((float(p[-1][0]), float(p[-1][1])))
    return out


def build_dovetail_loops(
    shape: int,
    length: float,
    width: float,
    corner_r: float,
    wall: float,
    depth: float,
    clearance: float,
    connectable: bool,
    is_drawer_shell: bool = False,
    has_front_opening: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build matched vertex-correspondent 2D loops for plain and dovetailed walls.

    Returns ``(base_out, dove_out, key_mask, slot_mask, base_in, dove_in)``, each of shape ``(N, 2)``
    (or ``(N,)`` for the masks), ordered anticlockwise around the perimeter.
    * Male dovetail tails (``key_mask == 1``) have a narrow neck (``W_neck``) at the wall that flares
      outward to a wide locking head (``W_head > W_neck``) at distance ``+depth``.
    * Female dovetail sockets (``slot_mask == 1``) have a narrow opening at the outer wall that flares
      inward to a wide locking chamber at depth ``-(depth + clearance)``, while ``dove_in`` forms a
      solid internal backing boss around the socket so the wall is never thinned or punctured.
    """
    if shape == SQUARE:
        width = length
        eff_shape = RECTANGLE
    else:
        eff_shape = shape

    if eff_shape == RECTANGLE:
        hx, hy = 0.5 * length, 0.5 * width
        r_c = min(max(corner_r, 1.5), min(hx, hy) - 2.0)
        # 4 sides: (apothem, half_flat, normal_angle)
        sides_spec = [
            (hx, max(hy - r_c, 1.0), 0.0),            # Side 0: Right (+X)
            (hy, max(hx - r_c, 1.0), 0.5 * math.pi),  # Side 1: Back / Cubby Top (+Y)
            (hx, max(hy - r_c, 1.0), math.pi),        # Side 2: Left (-X)
            (hy, max(hx - r_c, 1.0), 1.5 * math.pi),  # Side 3: Front / Cubby Bottom (-Y)
        ]
        # Side roles: +1 = Male Dovetail Tail, -1 = Female Dovetail Socket, 0 = Plain
        if not connectable:
            roles = [0, 0, 0, 0]
        elif is_drawer_shell:
            # Laid on side: +X=Right(Tail), +Y=Top(Tail), -X=Left(Socket), -Y=Bottom(Socket -> sits flat on desk!)
            roles = [+1, +1, -1, -1]
        else:
            roles = [+1, +1, -1, 0 if has_front_opening else -1]
    else:
        n_sides = 6 if eff_shape == HEXAGON else 8
        R = 0.5 * length
        r_c = min(max(corner_r, 1.5), 0.30 * R)
        sector = TAU / n_sides
        half_sec = 0.5 * sector
        cx_c = max(R - r_c, 1.0)
        apothem = cx_c * math.cos(half_sec) + r_c
        half_flat = max(cx_c * math.sin(half_sec), 1.0)
        sides_spec = [(apothem, half_flat, k * sector) for k in range(n_sides)]
        roles = []
        for k in range(n_sides):
            if not connectable:
                roles.append(0)
            elif k < n_sides // 2:
                roles.append(+1)
            else:
                ang = k * sector
                if has_front_opening and abs(math.sin(ang) + 1.0) < 0.35:
                    roles.append(0)
                else:
                    roles.append(-1)

    D = max(float(depth), 2.8)
    flare = 0.90 * D
    w_neck_base = 8.4
    w_head_base = w_neck_base + 2.0 * flare
    boss_wall = max(wall, 1.6)
    w_win = 0.5 * w_head_base + clearance + 2.0 * boss_wall + 0.6

    b_out_list, d_out_list = [], []
    b_in_list, d_in_list = [], []
    k_mask_list, s_mask_list = [], []

    n_sides = len(sides_spec)
    arc_span = TAU / n_sides
    r_in = max(r_c - wall, 0.8)

    def _add_segment(
        t0_bo, n0_bo, t0_do, n0_do, t0_bi, n0_bi, t0_di, n0_di,
        t1_bo, n1_bo, t1_do, n1_do, t1_bi, n1_bi, t1_di, n1_di,
        steps, km, sm, ap, nv, tv,
    ):
        for s_i in range(steps):
            u = s_i / float(steps)
            tbo = t0_bo + u * (t1_bo - t0_bo)
            nbo = n0_bo + u * (n1_bo - n0_bo)
            tdo = t0_do + u * (t1_do - t0_do)
            ndo = n0_do + u * (n1_do - n0_do)
            tbi = t0_bi + u * (t1_bi - t0_bi)
            nbi = n0_bi + u * (n1_bi - n0_bi)
            tdi = t0_di + u * (t1_di - t0_di)
            ndi = n0_di + u * (n1_di - n0_di)
            b_out_list.append((ap + nbo) * nv + tbo * tv)
            d_out_list.append((ap + ndo) * nv + tdo * tv)
            b_in_list.append((ap + nbi) * nv + tbi * tv)
            d_in_list.append((ap + ndi) * nv + tdi * tv)
            k_mask_list.append(km)
            s_mask_list.append(sm)

    for idx, (ap, h_flat, ang_n) in enumerate(sides_spec):
        role = roles[idx]
        nv = np.array([math.cos(ang_n), math.sin(ang_n)], dtype=np.float64)
        tv = np.array([-math.sin(ang_n), math.cos(ang_n)], dtype=np.float64)

        # Determine dovetail centres along t in [-h_flat, +h_flat]
        if role == 0 or h_flat < w_win + 0.8:
            centres = []
        elif h_flat >= 2.0 * w_win + 2.5:
            off = min(max(0.46 * h_flat, w_win + 0.6), h_flat - w_win - 0.4)
            centres = [-off, +off]
        else:
            centres = [0.0]

        cursor = -h_flat
        for tc in centres:
            t_start = tc - w_win
            t_end = tc + w_win
            if t_start > cursor + 0.2:
                n_plain = max(int(round((t_start - cursor) / 2.5)), 2)
                _add_segment(
                    cursor, 0.0, cursor, 0.0, cursor, -wall, cursor, -wall,
                    t_start, 0.0, t_start, 0.0, t_start, -wall, t_start, -wall,
                    n_plain, 0.0, 0.0, ap, nv, tv,
                )

            if role > 0:
                # MALE DOVETAIL TENON: flat inner wall, rounded-corner keystone tenon on outer wall
                wn = 0.5 * w_neck_base
                wh = 0.5 * w_head_base
                r_neck = min(0.95, 0.30 * D)
                r_head = min(0.85, 0.28 * D)
                tenon_pts = [
                    (t_start, 0.0),
                    (tc - wn, 0.0),
                    (tc - wh, +D),
                    (tc + wh, +D),
                    (tc + wn, 0.0),
                    (t_end, 0.0),
                ]
                tenon_r = [0.0, r_neck, r_head, r_head, r_neck, 0.0]
                fil_out = _fillet_polyline_2d(tenon_pts, tenon_r, arc_steps=5, seg_step=1.5)
                pts_arr = np.array(fil_out, dtype=np.float64)
                ds = np.linalg.norm(np.diff(pts_arr, axis=0), axis=1)
                s_cum = np.concatenate([[0.0], np.cumsum(ds)])
                s_tot = max(float(s_cum[-1]), 1e-6)
                for p_i in range(len(fil_out) - 1):
                    t_do, n_do = fil_out[p_i]
                    t_base = t_start + (s_cum[p_i] / s_tot) * (t_end - t_start)
                    b_out_list.append(ap * nv + t_base * tv)
                    d_out_list.append((ap + n_do) * nv + t_do * tv)
                    b_in_list.append((ap - wall) * nv + t_base * tv)
                    d_in_list.append((ap - wall) * nv + t_base * tv)
                    k_mask_list.append(1.0)
                    s_mask_list.append(0.0)
            else:
                # FEMALE DOVETAIL MORTISE SOCKET: rounded-corner narrow mouth + wide locking chamber,
                # housed inside a smooth trapezoidal internal boss
                wn = 0.5 * w_neck_base + clearance
                wh = 0.5 * w_head_base + clearance
                d_eff = -(D + clearance + 0.15)
                n_boss = d_eff - boss_wall
                t_boss = wh + boss_wall
                r_mouth = min(0.95, 0.30 * D) + clearance
                r_pocket = min(0.85, 0.28 * D) + clearance
                mortise_pts = [
                    (t_start, 0.0),
                    (tc - wn, 0.0),
                    (tc - wh, d_eff),
                    (tc + wh, d_eff),
                    (tc + wn, 0.0),
                    (t_end, 0.0),
                ]
                mortise_r = [0.0, r_mouth, r_pocket, r_pocket, r_mouth, 0.0]
                fil_out = _fillet_polyline_2d(mortise_pts, mortise_r, arc_steps=5, seg_step=1.5)

                boss_pts = [
                    (t_start, -wall),
                    (tc - t_boss, n_boss),
                    (tc + t_boss, n_boss),
                    (t_end, -wall),
                ]
                boss_fil = _fillet_polyline_2d(boss_pts, [0.0, 1.2, 1.2, 0.0], arc_steps=3, seg_step=2.0)
                boss_arr = np.array(boss_fil, dtype=np.float64)
                b_ds = np.linalg.norm(np.diff(boss_arr, axis=0), axis=1)
                b_cum = np.concatenate([[0.0], np.cumsum(b_ds)])
                b_tot = max(float(b_cum[-1]), 1e-6)
                b_u = b_cum / b_tot

                pts_arr = np.array(fil_out, dtype=np.float64)
                ds = np.linalg.norm(np.diff(pts_arr, axis=0), axis=1)
                s_cum = np.concatenate([[0.0], np.cumsum(ds)])
                s_tot = max(float(s_cum[-1]), 1e-6)
                for p_i in range(len(fil_out) - 1):
                    u_i = float(s_cum[p_i] / s_tot)
                    t_do, n_do = fil_out[p_i]
                    t_base = t_start + u_i * (t_end - t_start)
                    t_di = float(np.interp(u_i, b_u, boss_arr[:, 0]))
                    n_di = float(np.interp(u_i, b_u, boss_arr[:, 1]))
                    b_out_list.append(ap * nv + t_base * tv)
                    d_out_list.append((ap + n_do) * nv + t_do * tv)
                    b_in_list.append((ap - wall) * nv + t_base * tv)
                    d_in_list.append((ap + n_di) * nv + t_di * tv)
                    k_mask_list.append(0.0)
                    s_mask_list.append(1.0)
            cursor = t_end

        if h_flat > cursor + 0.2:
            n_rem = max(int(round((h_flat - cursor) / 2.5)), 2)
            _add_segment(
                cursor, 0.0, cursor, 0.0, cursor, -wall, cursor, -wall,
                h_flat, 0.0, h_flat, 0.0, h_flat, -wall, h_flat, -wall,
                n_rem, 0.0, 0.0, ap, nv, tv,
            )

        # Rounded corner arc to next side
        c_center = (ap - r_c) * nv + h_flat * tv
        n_arc = 10
        for a_i in range(n_arc):
            th = ang_n + (a_i / float(n_arc)) * arc_span
            dir_v = np.array([math.cos(th), math.sin(th)], dtype=np.float64)
            pt_out = c_center + r_c * dir_v
            pt_in = c_center + r_in * dir_v
            b_out_list.append(pt_out)
            d_out_list.append(pt_out)
            b_in_list.append(pt_in)
            d_in_list.append(pt_in)
            k_mask_list.append(0.0)
            s_mask_list.append(0.0)

    return (
        np.array(b_out_list, dtype=np.float64),
        np.array(d_out_list, dtype=np.float64),
        np.array(k_mask_list, dtype=np.float64),
        np.array(s_mask_list, dtype=np.float64),
        np.array(b_in_list, dtype=np.float64),
        np.array(d_in_list, dtype=np.float64),
    )


def extrude_box_prism(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> tuple[np.ndarray, np.ndarray]:
    """Closed axis-aligned rectangular prism from (x0,y0,z0) to (x1,y1,z1)."""
    verts = np.array(
        [
            [x0, y0, z0],
            [x1, y0, z0],
            [x1, y1, z0],
            [x0, y1, z0],
            [x0, y0, z1],
            [x1, y0, z1],
            [x1, y1, z1],
            [x0, y1, z1],
        ],
        dtype=np.float64,
    )
    faces = np.array(
        [
            [0, 2, 1],
            [0, 3, 2],  # bottom
            [4, 5, 6],
            [4, 6, 7],  # top
            [0, 1, 5],
            [0, 5, 4],  # front (-Y)
            [2, 3, 7],
            [2, 7, 6],  # back (+Y)
            [1, 2, 6],
            [1, 6, 5],  # right (+X)
            [3, 0, 4],
            [3, 4, 7],  # left (-X)
        ],
        dtype=np.int64,
    )
    return orient_outward(verts, faces)


def extrude_profile_along_axis(
    profile_yz: np.ndarray, x0: float, x1: float, swap_xy: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    """Extrude a 2D closed polygon ``profile_yz`` (M, 2) of (u, z) from v=x0 to v=x1.
    If ``swap_xy`` is False: u is X, extrusion is along Y (from y=x0 to y=x1).
    If ``swap_xy`` is True: u is Y, extrusion is along X (from x=x0 to x=x1).
    """
    prof = _anticlockwise(np.asarray(profile_yz, dtype=np.float64))
    m = len(prof)
    u, z = prof[:, 0], prof[:, 1]
    # True 2D polygon area centroid so non-uniform vertex density never biases the fan center
    u_nxt, z_nxt = np.roll(u, -1), np.roll(z, -1)
    cross = u * z_nxt - u_nxt * z
    area6 = 3.0 * float(cross.sum())
    if abs(area6) > 1e-6:
        c_u = float(((u + u_nxt) * cross).sum() / area6)
        c_z = float(((z + z_nxt) * cross).sum() / area6)
    else:
        c_u, c_z = float(u.mean()), float(z.mean())
    if not swap_xy:
        v0 = np.column_stack([u, np.full(m, x0), z])
        v1 = np.column_stack([u, np.full(m, x1), z])
        centers = np.array([[c_u, x0, c_z], [c_u, x1, c_z]], dtype=np.float64)
    else:
        v0 = np.column_stack([np.full(m, x0), u, z])
        v1 = np.column_stack([np.full(m, x1), u, z])
        centers = np.array([[x0, c_u, c_z], [x1, c_u, c_z]], dtype=np.float64)

    verts = np.concatenate([v0, v1, centers], axis=0)
    k = np.arange(m)
    nxt = (k + 1) % m
    cap0 = np.stack([np.full(m, 2 * m), nxt, k], axis=1)
    cap1 = np.stack([np.full(m, 2 * m + 1), m + k, m + nxt], axis=1)
    side1 = np.stack([k, nxt, m + nxt], axis=1)
    side2 = np.stack([k, m + nxt, m + k], axis=1)
    faces = np.concatenate([cap0, cap1, side1, side2], axis=0)
    return orient_outward(verts, faces)


def extrude_wall_strip(
    us: np.ndarray, z_bot: float, zs_top: np.ndarray, v0: float, v1: float, swap_xy: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    """Build a closed manifold wall from horizontal stations ``us`` (M,), flat bottom ``z_bot``,
    and top height profile ``zs_top`` (M,), extruded across thickness ``[v0, v1]``.
    Triangulates each vertical strip ``[u_k, u_{k+1}]`` as a quad so deep finger-dips never fold over.
    """
    us = np.asarray(us, dtype=np.float64)
    zt = np.asarray(zs_top, dtype=np.float64)
    zb = np.full_like(us, float(z_bot))
    m = len(us)

    def _pts(u_arr, v_val, z_arr):
        if not swap_xy:
            return np.column_stack([u_arr, np.full(len(u_arr), v_val), z_arr])
        return np.column_stack([np.full(len(u_arr), v_val), u_arr, z_arr])

    # 4 rails of M vertices each: (0: bot at v0, 1: top at v0, 2: bot at v1, 3: top at v1)
    verts = np.concatenate(
        [
            _pts(us, v0, zb),
            _pts(us, v0, zt),
            _pts(us, v1, zb),
            _pts(us, v1, zt),
        ],
        axis=0,
    )
    k = np.arange(m - 1)
    b0, t0, b1, t1 = k, m + k, 2 * m + k, 3 * m + k

    faces = np.concatenate(
        [
            # Side v0 (outward normal -v)
            np.stack([b0, t0, t0 + 1], axis=1),
            np.stack([b0, t0 + 1, b0 + 1], axis=1),
            # Side v1 (outward normal +v)
            np.stack([b1, b1 + 1, t1 + 1], axis=1),
            np.stack([b1, t1 + 1, t1], axis=1),
            # Top ridge (outward normal +z)
            np.stack([t0, t1, t1 + 1], axis=1),
            np.stack([t0, t1 + 1, t0 + 1], axis=1),
            # Bottom base (outward normal -z)
            np.stack([b0, b0 + 1, b1 + 1], axis=1),
            np.stack([b0, b1 + 1, b1], axis=1),
            # Left end cap (k = 0) and Right end cap (k = m - 1)
            np.array(
                [
                    [0, 2 * m, 3 * m],
                    [0, 3 * m, m],
                    [m - 1, 2 * m - 1, 4 * m - 1],
                    [m - 1, 4 * m - 1, 3 * m - 1],
                ],
                dtype=np.int64,
            ),
        ],
        axis=0,
    )
    return orient_outward(verts, faces)


def hollow_pot_from_rings(
    zs: np.ndarray,
    O: np.ndarray,
    I: np.ndarray,
    kb: int,
    rim_z: np.ndarray | None = None,
    z_rim_base: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Build a closed, watertight hollow pot from outer rings ``O`` (K, N, 2) and inner rings ``I`` (K, N, 2)
    at heights ``zs`` (K,), with solid floor up to row ``kb``.

    If ``rim_z`` (N,) is given (e.g. for an angled front scoop on a parts bin), the rows above ``z_rim_base``
    are scaled in Z per column so the rim smoothly dips down to ``rim_z[col]`` while keeping all lower
    features (foot steps and dovetail ramps) at constant horizontal Z.
    """
    K, N = O.shape[:2]
    H = float(zs[-1])
    z_floor = float(zs[kb])
    z_base = float(z_rim_base) if z_rim_base is not None else z_floor

    # Per-vertex Z coordinates for outer and inner walls
    Z_out = np.broadcast_to(zs[:, None], (K, N)).copy()
    if rim_z is not None:
        above = zs >= z_base
        frac = (zs[above, None] - z_base) / max(H - z_base, 1e-6)
        Z_out[above] = z_base + frac * ( np.maximum(rim_z[None, :], z_base + 2.0) - z_base )

    Z_in = Z_out[kb:].copy()
    Ki = K - kb

    pts_out = np.concatenate([O, Z_out[:, :, None]], axis=2).reshape(-1, 3)
    pts_in = np.concatenate([I[kb:], Z_in[:, :, None]], axis=2).reshape(-1, 3)
    c_bot = np.array([[0.0, 0.0, float(zs[0])]], dtype=np.float64)
    c_flr = np.array([[0.0, 0.0, z_floor]], dtype=np.float64)
    verts = np.concatenate([pts_out, pts_in, c_bot, c_flr], axis=0)

    vo = np.arange(K * N).reshape(K, N)
    vi = (K * N) + np.arange(Ki * N).reshape(Ki, N)
    idx_bot = K * N + Ki * N
    idx_flr = idx_bot + 1

    faces = []
    # Outer wall
    for r_arr, flip in ((vo, False), (vi, True)):
        a = r_arr[:-1]
        b = np.roll(r_arr, -1, axis=1)[:-1]
        c = np.roll(r_arr, -1, axis=1)[1:]
        d = r_arr[1:]
        t1 = np.stack([a, b, c], axis=-1).reshape(-1, 3)
        t2 = np.stack([a, c, d], axis=-1).reshape(-1, 3)
        tris = np.concatenate([t1, t2], axis=0)
        if flip:
            tris = tris[:, ::-1]
        faces.append(tris)

    # Rim connecting vo[-1] and vi[-1]
    o_top = vo[-1]
    i_top = vi[-1]
    o_nxt = np.roll(o_top, -1)
    i_nxt = np.roll(i_top, -1)
    rim_tris = np.concatenate(
        [np.stack([o_top, o_nxt, i_nxt], axis=1), np.stack([o_top, i_nxt, i_top], axis=1)], axis=0
    )
    faces.append(rim_tris)

    # Bottom cap (z = 0) and Inner floor cap (z = z_floor)
    o_bot = vo[0]
    o_bot_nxt = np.roll(o_bot, -1)
    bot_cap = np.stack([np.full(N, idx_bot), o_bot_nxt, o_bot], axis=1)

    i_flr = vi[0]
    i_flr_nxt = np.roll(i_flr, -1)
    flr_cap = np.stack([np.full(N, idx_flr), i_flr, i_flr_nxt], axis=1)

    faces.append(bot_cap)
    faces.append(flr_cap)
    return orient_outward(verts, np.concatenate(faces, axis=0))


# ===================================================================== BoxDesign


class BoxDesign:
    """A complete parametric Boxinator design: main body, dividers, and optional lid / drawer / slide-in plates."""

    def __init__(self, p: BoxParams):
        self.p = p = p.copy()
        if p.shape in (SQUARE, HEXAGON, OCTAGON):
            p.width = p.length
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

        self.verts = np.zeros((0, 3))
        self.faces = np.zeros((0, 3), dtype=np.int64)
        self.lean = np.zeros(0)
        self.worst = 0.0
        self.closed = False
        self.accessories: list[dict] = []  # each: {name, verts_bed, faces_bed, verts_asm, faces_asm, fil}

        if not self._check():
            return

        self._build()

    def _check(self) -> bool:
        p = self.p
        min_dim = min(p.length, p.width)
        if min_dim < 28.0:
            self.errors.append("Length and width must each be at least 28 mm.")
        if p.height < 15.0:
            self.errors.append("Height must be at least 15 mm.")
        if 2.0 * p.wall_thickness >= min_dim - 10.0:
            self.errors.append("The walls are too thick for a box this narrow.")
        if p.floor_thickness >= 0.5 * p.height:
            self.errors.append("The floor thickness must be less than half the box height.")
        return not self.errors

    def _surface_delta(self, loop: np.ndarray, z: float, z_lo: float, z_hi: float) -> np.ndarray:
        """Surface texture offset (mm) at height z around ``loop``, faded cleanly at z_lo and z_hi."""
        p = self.p
        N = len(loop)
        if p.pattern == SMOOTH or z <= z_lo or z >= z_hi or p.rib_depth <= 0.0:
            return np.zeros(N, dtype=np.float64)

        fade = 3.0
        env = min((z - z_lo) / fade, (z_hi - z) / fade, 1.0)
        env = max(0.0, env)
        env = env * env * (3.0 - 2.0 * env)

        # Distance along perimeter
        seg = np.linalg.norm(np.roll(loop, -1, axis=0) - loop, axis=1)
        along = np.concatenate([[0.0], np.cumsum(seg[:-1])])
        perim = float(seg.sum())
        pitch = max(p.rib_pitch, 3.0)
        n_ribs = max(int(round(perim / pitch)), 6)
        phase = TAU * n_ribs * (along / max(perim, 1e-6))

        if p.pattern == RIBS:
            wave = 0.5 * (1.0 + np.cos(phase))
            return env * p.rib_depth * (wave**1.6)
        if p.pattern == RINGS:
            wave_z = 0.5 * (1.0 - np.cos(TAU * (z - z_lo) / pitch))
            return np.full(N, env * p.rib_depth * (wave_z**1.6))
        if p.pattern == DIAMONDS:
            lean_z = TAU * (z - z_lo) / (2.2 * pitch)
            w1 = 0.5 * (1.0 + np.cos(phase - lean_z))
            w2 = 0.5 * (1.0 + np.cos(phase + lean_z))
            return env * p.rib_depth * (np.maximum(w1, w2) ** 2.0)
        if p.pattern == HEX_WINDOWS:
            # Recessed hex-lattice dimples that never breach water-tightness or overhangs
            row_h = pitch * 0.866
            row = (z - z_lo) / max(row_h, 1.0)
            stagger = (math.floor(row) % 2) * 0.5
            u = ((along / pitch) + stagger) % 1.0 - 0.5
            v = (row % 1.0) - 0.5
            d = np.hypot(u, v)
            dimple = np.clip(1.0 - (d / 0.38) ** 2, 0.0, 1.0)
            return -env * min(p.rib_depth, 0.45 * p.wall_thickness) * dimple
        return np.zeros(N, dtype=np.float64)

    def _build(self):
        p = self.p
        H = float(p.height)
        wall = float(p.wall_thickness)
        flr = float(p.floor_thickness)
        clr = p.clearance

        is_drawer = p.kind == DRAWER_UNIT
        has_scoop_mouth = p.kind == PARTS_BIN

        # Build vertex-correspondent plain and dovetailed 2D loops
        base_out, dove_out, key_mask, slot_mask, base_in, dove_in = build_dovetail_loops(
            p.shape,
            p.length,
            p.width,
            p.corner_r,
            wall,
            p.dovetail_depth,
            clr,
            p.connectable,
            is_drawer_shell=is_drawer,
            has_front_opening=has_scoop_mouth or p.label_slot,
        )
        N = len(base_out)

        # Height grid
        n_z = max(int(round(H / 1.0)), 48)
        zs = np.linspace(0.0, H, n_z + 1)

        # Ensure exact Z stations for floor, stacking step, scoop top, etc.
        stack_in = wall + clr if (p.stackable and not is_drawer) else 0.0
        z_stack1 = min(p.stack_height, 0.25 * H) if stack_in > 0 else 0.0
        z_stack2 = min(z_stack1 + stack_in * 1.15, 0.45 * H) if stack_in > 0 else 0.0
        z_scoop = min(flr + (7.0 if p.scoop_floor else 0.0), 0.6 * H)

        # On a drawer shell (or non-stackable box), dovetails can start right at the print bed (z = 0 -> 0 deg overhang!)
        # On a stackable upright box, male dovetail tails ramp out cleanly above the stacking foot at z_stack2 + 0.8,
        # while female dovetail sockets (recessed inward) run straight from z = 0 with zero overhang!
        z_conn_start = (z_stack2 + 0.8) if stack_in > 0 else 0.0
        ramp_h = max(p.dovetail_depth * 2.1, 5.0) if z_conn_start > 0 else 0.0
        z_rim_base = min(max(z_conn_start + ramp_h + 1.5, flr + 10.0), 0.48 * H)

        special_z = {0.0, flr, H}
        if stack_in > 0:
            special_z |= {z_stack1, z_stack2}
        if p.connectable and z_conn_start > 0:
            special_z |= {
                min(z_conn_start, H),
                min(z_conn_start + 0.5 * ramp_h, H),
                min(z_conn_start + ramp_h, H),
            }
        if has_scoop_mouth:
            special_z.add(z_rim_base)
        if p.scoop_floor:
            special_z.add(z_scoop)
        if p.kind == LIDDED_BOX and p.lid_style == SLIDE_LID:
            special_z |= {H - 6.8, H - 4.2, H - 3.0, H - 2.9}

        zs = np.array(sorted(set(np.round(zs, 4).tolist()) | {round(v, 4) for v in special_z}), dtype=np.float64)
        K = len(zs)
        kb = int(np.argmin(np.abs(zs - flr)))

        connector_mask = (key_mask > 0.01) | (slot_mask > 0.01)
        z_tex_lo = max(z_conn_start + ramp_h, 4.0)
        z_tex_hi = H - 4.0

        O = np.zeros((K, N, 2), dtype=np.float64)
        I = np.zeros((K, N, 2), dtype=np.float64)
        normals = loop_normals(base_out)

        # Slide-in divider V-rib slots on the inner wall (for RECTANGLE / SQUARE)
        slot_rib = np.zeros(N, dtype=np.float64)
        if p.div_mode == SLIDE_IN and not is_drawer and p.shape in (RECTANGLE, SQUARE):
            slot_rib = self._wall_slot_ribs(base_in)

        # Slide-lid rails inside rim (for LIDDED_BOX with SLIDE_LID)
        lid_rail_stations = p.kind == LIDDED_BOX and p.lid_style == SLIDE_LID and p.shape in (RECTANGLE, SQUARE)

        for k, z in enumerate(zs):
            # 1) Outer foot inset for stackability (45 deg support-free step)
            if stack_in > 0 and z < z_stack2:
                if z <= z_stack1:
                    foot_inset = stack_in
                else:
                    foot_inset = stack_in * (1.0 - (z - z_stack1) / max(z_stack2 - z_stack1, 1e-6))
            else:
                foot_inset = 0.0

            # 2) True interlocking XY dovetail tails & sockets
            if not p.connectable:
                ramp_k = 0.0
                ramp_s = 0.0
            else:
                ramp_s = 1.0  # Female sockets are recessed inward and run full height with 0 deg overhang
                if z_conn_start <= 0.0:
                    ramp_k = 1.0
                elif z <= z_conn_start:
                    ramp_k = 0.0
                else:
                    ramp_k = min((z - z_conn_start) / max(ramp_h, 1e-6), 1.0)
            ramp_vec = ramp_k * key_mask + ramp_s * slot_mask

            # 3) Surface texture where clear of connectors
            tex_delta = self._surface_delta(base_out, z, z_tex_lo, z_tex_hi)
            tex_delta = np.where(connector_mask, 0.0, tex_delta)

            # Apply outer profile (interpolating from plain base_out to dovetailed dove_out)
            row_out = (
                base_out
                + (dove_out - base_out) * ramp_vec[:, None]
                - normals * foot_inset
                + normals * tex_delta[:, None]
            )
            O[k] = row_out

            # 4) Inner profile: dovetail socket housing boss + scoop floor + slide-in divider ribs + slide-lid rails
            in_inset = foot_inset * 0.65
            if p.scoop_floor and not is_drawer and flr <= z < z_scoop:
                u = (z - flr) / max(z_scoop - flr, 1e-6)
                scoop_add = 3.2 * (1.0 - math.sin(0.5 * math.pi * u))
                in_inset += scoop_add

            rib_in = np.zeros(N, dtype=np.float64)
            if np.any(slot_rib > 0) and z >= flr:
                taper = min((H - z) / 1.5, 1.0) if H - z < 1.5 else 1.0
                rib_in = np.maximum(rib_in, slot_rib * max(taper, 0.0))
            if lid_rail_stations:
                rib_in = np.maximum(rib_in, self._lid_rail_offset(base_in, H - z))

            row_in = base_in + (dove_in - base_in) * ramp_vec[:, None] - normals * (in_inset + rib_in)[:, None]
            I[k] = row_in

        # Optional angled front scoop rim for PARTS_BIN
        rim_z = None
        if has_scoop_mouth:
            rim_z = self._parts_bin_rim(base_out, H, z_rim_base)

        pot_verts, pot_faces = hollow_pot_from_rings(zs, O, I, kb, rim_z=rim_z, z_rim_base=z_rim_base)
        parts = [(pot_verts, pot_faces)]

        # Optional front label frame (on upright boxes when not a drawer shell)
        if p.label_slot and not is_drawer and not has_scoop_mouth and p.shape in (RECTANGLE, SQUARE):
            parts.extend(self._build_label_frame(p.length, p.width if p.shape == RECTANGLE else p.length, H, z_stack2))

        # Built-in dividers (for non-drawer boxes; for DRAWER_UNIT, dividers go inside the sliding drawer!)
        if not is_drawer and p.div_mode == BUILT_IN and (p.div_x > 1 or p.div_y > 1):
            parts.extend(self._build_internal_dividers(dove_in, flr, H, rim_z))

        # Caddy central handle (if kind == CADDY)
        if p.kind == CADDY:
            parts.extend(self._build_caddy_handle(dove_in, flr, H))

        # Drawer Shell keeper bump at top of front opening (when laid on its side, +Y rim at z = H)
        if is_drawer and p.drawer_stop and p.shape in (RECTANGLE, SQUARE):
            parts.extend(self._build_shell_keeper(dove_in, H))

        self.verts, self.faces = combine_meshes(parts)

        # Build accessories (Lid, Sliding Drawer, or Slide-In Divider Plates)
        if is_drawer:
            self._build_sliding_drawer(base_in, dove_in, flr, H)
        elif p.kind == LIDDED_BOX:
            self._build_box_lid(base_out, dove_in, H)

        if not is_drawer and p.div_mode == SLIDE_IN and (p.div_x > 1 or p.div_y > 1):
            self._build_slide_in_divider_plates(dove_in, flr, H)

        # Compute metrics
        self.closed = edge_check(self.faces)[0] and all(
            edge_check(acc["faces_bed"])[0] for acc in self.accessories
        )
        self.lean = lean_angles(self.verts, self.faces)
        self.worst = float(max(self.lean.max(), 0.0)) if len(self.lean) else 0.0
        self.triangles = int(len(self.faces) + sum(len(a["faces_bed"]) for a in self.accessories))
        self.size = self.verts.max(axis=0) - self.verts.min(axis=0)
        vol = mesh_volume(self.verts, self.faces) + sum(
            mesh_volume(a["verts_bed"], a["faces_bed"]) for a in self.accessories
        )
        self.grams = max(vol / 1000.0 * p.density, 1.0)
        eff_speed = min(p.speed, p.max_flow / max(p.line_width * p.layer_height, 1e-6))
        self.seconds = vol / (p.line_width * p.layer_height) / max(eff_speed, 1.0) + 90.0

        # Compartment dimensions
        W_eff = p.width if p.shape == RECTANGLE else p.length
        in_x = max(p.length - 2.0 * wall, 4.0)
        in_y = max(W_eff - 2.0 * wall, 4.0)
        in_z = max(H - flr, 4.0)
        dx_count = max(int(p.div_x), 1)
        dy_count = max(int(p.div_y), 1)
        self.cell_x = (in_x - (dx_count - 1) * p.div_wall) / dx_count
        self.cell_y = (in_y - (dy_count - 1) * p.div_wall) / dy_count
        self.cell_z = in_z
        self.compartments = dx_count * dy_count

        if self.size[0] > p.bed_x or self.size[1] > p.bed_y:
            self.warnings.append(
                f"Footprint ({self.size[0]:.0f} × {self.size[1]:.0f} mm) exceeds the print bed "
                f"({p.bed_x:.0f} × {p.bed_y:.0f} mm)."
            )
        if H > p.printer_height:
            self.warnings.append(f"Height ({H:.0f} mm) exceeds printer height ({p.printer_height:.0f} mm).")

    # -------------------------------------------------------- wall features

    def _wall_slot_ribs(self, base_in: np.ndarray) -> np.ndarray:
        """Vertical pair of 45-degree guide ribs on the inner wall for slide-in dividers."""
        p = self.p
        x, y = base_in[:, 0], base_in[:, 1]
        hx = float(np.abs(x).max())
        hy = float(np.abs(y).max())
        rib = np.zeros(len(base_in), dtype=np.float64)
        half_slot = 0.5 * (p.div_wall + p.clearance + 0.15)
        rib_w = 1.4
        rib_h = 1.3

        # X stations (dividers running along Y, slots on +Y and -Y walls)
        if p.div_x > 1:
            span_x = 2.0 * hx
            for i in range(1, p.div_x):
                xc = -hx + i * span_x / p.div_x
                on_y_wall = np.abs(y) > hy - 1.2
                d_pair = np.abs(np.abs(x - xc) - (half_slot + 0.5 * rib_w))
                prof = np.clip(1.0 - d_pair / (0.65 * rib_w), 0.0, 1.0) * rib_h
                rib = np.where(on_y_wall, np.maximum(rib, prof), rib)

        # Y stations (dividers running along X, slots on +X and -X walls)
        if p.div_y > 1:
            span_y = 2.0 * hy
            for j in range(1, p.div_y):
                yc = -hy + j * span_y / p.div_y
                on_x_wall = np.abs(x) > hx - 1.2
                d_pair = np.abs(np.abs(y - yc) - (half_slot + 0.5 * rib_w))
                prof = np.clip(1.0 - d_pair / (0.65 * rib_w), 0.0, 1.0) * rib_h
                rib = np.where(on_x_wall, np.maximum(rib, prof), rib)

        return rib

    def _drawer_shell_runners(self, base_in: np.ndarray) -> np.ndarray:
        """Two smooth guide rails along the bottom wall (-Y) of a drawer cubby shell."""
        x, y = base_in[:, 0], base_in[:, 1]
        hx = float(np.abs(x).max())
        hy = float(np.abs(y).max())
        on_floor = y < -hy + 1.2
        r_pos = 0.52 * hx
        d = np.minimum(np.abs(x - r_pos), np.abs(x + r_pos))
        prof = np.clip(1.0 - d / 2.2, 0.0, 1.0) * 1.4
        return np.where(on_floor, prof, 0.0)

    def _lid_rail_offset(self, base_in: np.ndarray, h_from_rim: float) -> np.ndarray:
        """Corner slide-lock rails inside the rim of a LIDDED_BOX (when lid_style == SLIDE_LID)."""
        if h_from_rim < 2.8 or h_from_rim > 7.2:
            return np.zeros(len(base_in), dtype=np.float64)
        x, y = base_in[:, 0], base_in[:, 1]
        hx = float(np.abs(x).max())
        hy = float(np.abs(y).max())
        on_long = np.abs(y) > hy - 1.2
        # Rails sit near the corners along X
        u = np.abs(x)
        to = max(hx - max(self.p.corner_r, 4.0) - 6.0, 10.0)
        start = max(to - 9.0, 2.0)
        along = np.clip(np.minimum(u - (start - 1.0), (to + 1.0) - u), 0.0, 1.0)
        if h_from_rim <= 3.0:
            depth = (h_from_rim - 2.8) / 0.2 * 1.8
        elif h_from_rim <= 4.4:
            depth = 1.8
        else:
            depth = max(1.8 - (h_from_rim - 4.4) * math.tan(math.radians(38.0)), 0.0)
        return np.where(on_long, depth * along, 0.0)

    def _parts_bin_rim(self, base_out: np.ndarray, H: float, flr: float) -> np.ndarray:
        """Front scoop profile for an open-front workshop parts bin (no overhangs: faces upward!)."""
        p = self.p
        y = base_out[:, 1]
        hy = float(np.abs(y).max())
        # Front is -Y: slope down in the front zone y in [-0.92*hy, -0.62*hy], clear of the side dovetails
        dip_z = max(flr + 8.0, H * (1.0 - 0.01 * p.bin_scoop_pct))
        y_start = -0.62 * hy
        y_flat = -0.92 * hy
        t = np.clip((y_start - y) / max(y_start - y_flat, 1e-6), 0.0, 1.0)
        smooth = t * t * (3.0 - 2.0 * t)
        return H - smooth * (H - dip_z)

    def _build_label_frame(
        self, length: float, width: float, H: float, z_base: float
    ) -> list[tuple[np.ndarray, np.ndarray]]:
        """Support-free 45-degree slide-in label holder on the front (-Y) face."""
        hy = 0.5 * width
        lw = min(max(0.55 * length, 24.0), 64.0)
        lh = min(max(0.35 * (H - z_base), 12.0), 22.0)
        zc = 0.5 * (z_base + H)
        z0, z1 = zc - 0.5 * lh, zc + 0.5 * lh
        if z0 < z_base + 2.0 or lw < 18.0:
            return []
        # Bottom retaining rail with 45-deg underside, and two side stops
        bot_prof = np.array(
            [
                [-hy + 0.2, z0 - 1.6],
                [-hy - 1.4, z0],
                [-hy - 1.4, z0 + 1.8],
                [-hy - 0.6, z0 + 1.8],
                [-hy - 0.6, z0 + 0.6],
                [-hy + 0.2, z0 + 0.6],
            ]
        )
        top_prof = np.array(
            [
                [-hy + 0.2, z1 - 0.6],
                [-hy - 0.6, z1 - 0.6],
                [-hy - 0.6, z1 - 1.6],
                [-hy - 1.4, z1 - 1.6],
                [-hy - 1.4, z1],
                [-hy + 0.2, z1 + 1.4],
            ]
        )
        return [
            extrude_profile_along_axis(bot_prof, -0.5 * lw, 0.5 * lw, swap_xy=True),
            extrude_profile_along_axis(top_prof, -0.5 * lw, 0.5 * lw, swap_xy=True),
        ]

    def _build_shell_keeper(self, base_in: np.ndarray, H: float) -> list[tuple[np.ndarray, np.ndarray]]:
        """Small 45-degree keeper bump inside the top wall (+Y) of a drawer shell near the open front (z=H)."""
        hy = float(np.abs(base_in[:, 1]).max())
        hx = float(np.abs(base_in[:, 0]).max())
        w = min(18.0, 0.4 * hx)
        z_top = H - 1.2
        z_bot = H - 5.2
        prof = np.array(
            [
                [hy + 0.2, z_bot],
                [hy - 1.4, z_bot + 1.6],
                [hy - 1.4, z_top - 1.0],
                [hy + 0.2, z_top],
            ]
        )
        return [extrude_profile_along_axis(prof, -w, w, swap_xy=True)]

    # -------------------------------------------------------- internal dividers & caddy handle

    def _divider_wall(
        self,
        u0: float,
        u1: float,
        z_flr: float,
        z_top: float,
        n_cells: int,
        dip: float,
        v0: float,
        v1: float,
        swap_xy: bool,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Build a closed divider wall from u0 to u1 with curved finger-dip cutouts in each cell."""
        n_pts = 48 * max(n_cells, 1)
        us = np.linspace(u0, u1, n_pts + 1)
        cell_w = (u1 - u0) / max(n_cells, 1)
        eff_dip = min(dip, 0.45 * (z_top - z_flr), 0.35 * cell_w)
        zs_top = np.full_like(us, z_top)
        if eff_dip > 0.2:
            rel = ((us - u0) / max(cell_w, 1e-6)) % 1.0
            in_dip = np.clip((0.325 - np.abs(rel - 0.5)) / 0.325, 0.0, 1.0)
            zs_top -= eff_dip * (0.5 * (1.0 - np.cos(math.pi * in_dip)))
        return extrude_wall_strip(us, z_flr, zs_top, v0, v1, swap_xy=swap_xy)

    def _build_internal_dividers(
        self, base_in: np.ndarray, flr: float, H: float, rim_z: np.ndarray | None
    ) -> list[tuple[np.ndarray, np.ndarray]]:
        """Closed internal divider walls for BUILT_IN mode."""
        p = self.p
        x, y = base_in[:, 0], base_in[:, 1]
        hx = float(np.abs(x).max()) - 0.1
        hy = float(np.abs(y).max()) - 0.1
        z_top = flr + (H - flr) * (0.01 * p.div_height_pct)
        if rim_z is not None:
            z_top = min(z_top, float(rim_z.min()) + 0.35 * (H - float(rim_z.min())))
        z_top = max(z_top, flr + 4.0)
        dw = p.div_wall
        out = []

        # X dividers (walls running along Y from -hy to +hy)
        if p.div_x > 1:
            for i in range(1, p.div_x):
                xc = -hx + i * (2.0 * hx) / p.div_x
                # Reach out to the actual polygon wall at xc
                y_lim = self._wall_reach(base_in, xc, axis=0) - 0.05
                if y_lim > 3.0:
                    out.append(
                        self._divider_wall(
                            -y_lim, y_lim, flr, z_top, p.div_y, p.div_dip, xc - 0.5 * dw, xc + 0.5 * dw, True
                        )
                    )

        # Y dividers (walls running along X, segmented between X dividers so there is zero 3D self-intersection!)
        if p.div_y > 1:
            x_cuts = [-hx + i * (2.0 * hx) / p.div_x for i in range(p.div_x + 1)]
            for j in range(1, p.div_y):
                yc = -hy + j * (2.0 * hy) / p.div_y
                x_lim = self._wall_reach(base_in, yc, axis=1) - 0.05
                if x_lim <= 3.0:
                    continue
                for c_idx in range(p.div_x):
                    xa = max(x_cuts[c_idx] + (0.5 * dw if c_idx > 0 else 0.0), -x_lim)
                    xb = min(x_cuts[c_idx + 1] - (0.5 * dw if c_idx + 1 < p.div_x else 0.0), x_lim)
                    if xb - xa > 2.0:
                        out.append(
                            self._divider_wall(
                                xa, xb, flr, z_top, 1, p.div_dip, yc - 0.5 * dw, yc + 0.5 * dw, False
                            )
                        )
        return out

    def _build_caddy_handle(
        self, base_in: np.ndarray, flr: float, H: float
    ) -> list[tuple[np.ndarray, np.ndarray]]:
        """Central arched carry handle."""
        p = self.p
        hx = float(np.abs(base_in[:, 0]).max()) - 0.1
        dw = max(p.div_wall, 2.4)
        n = 36
        xs = np.linspace(-hx, hx, 2 * n + 1)
        arch = H + p.caddy_handle_h * np.clip(1.0 - (xs / max(0.85 * hx, 1.0)) ** 2, 0.0, 1.0) ** 1.4
        arch = np.maximum(arch, H * 0.92)
        return [extrude_wall_strip(xs, flr, arch, -0.5 * dw, 0.5 * dw, swap_xy=False)]

    @staticmethod
    def _wall_reach(loop: np.ndarray, coord: float, axis: int) -> float:
        """Furthest positive coordinate on ``1 - axis`` where ``loop`` crosses ``coord`` along ``axis``."""
        a = loop[:, axis]
        b = np.roll(a, -1)
        va = loop[:, 1 - axis]
        vb = np.roll(va, -1)
        cross = (np.minimum(a, b) <= coord) & (np.maximum(a, b) >= coord) & (a != b)
        if not np.any(cross):
            return float(np.abs(va).max()) * 0.85
        t = (coord - a[cross]) / (b[cross] - a[cross])
        vals = np.abs(va[cross] + t * (vb[cross] - va[cross]))
        return float(vals.max())

    # -------------------------------------------------------- accessories (Drawer, Lid, Slide-in Dividers)

    def _build_sliding_drawer(self, base_in: np.ndarray, dove_in: np.ndarray, flr: float, H: float):
        """Build the matching Sliding Drawer for a DRAWER_UNIT.

        When the Cubby Shell is laid on its side (via rotate_x_90 + translate dz=+0.5*W_eff):
        - Shell's X stays X (width of cubby = p.length)
        - Shell's Y (-0.5*W_eff .. +0.5*W_eff) becomes Z (0 .. W_eff)
        - Shell's Z (0..H) becomes -Y (depth of cubby = -H .. 0, opening at y = -H)
        The longitudinal internal bosses of the Female Dovetail Sockets along -Y and -X act as
        built-in low-friction drawer runner rails!
        """
        p = self.p
        clr = p.clearance
        W_eff = p.width if p.shape == RECTANGLE else p.length
        hx = 0.5 * p.length
        hy = 0.5 * W_eff

        # Clear interior bounds inside the cubby shell (accounting for internal socket runner bosses)
        left_pts = dove_in[base_in[:, 0] < -hx + p.wall_thickness + 0.5, 0]
        right_pts = dove_in[base_in[:, 0] > hx - p.wall_thickness - 0.5, 0]
        bot_pts = dove_in[base_in[:, 1] < -hy + p.wall_thickness + 0.5, 1]
        top_pts = dove_in[base_in[:, 1] > hy - p.wall_thickness - 0.5, 1]

        x_min_in = float(left_pts.max()) if len(left_pts) else (-hx + p.wall_thickness)
        x_max_in = float(right_pts.min()) if len(right_pts) else (hx - p.wall_thickness)
        y_min_in = float(bot_pts.max()) if len(bot_pts) else (-hy + p.wall_thickness)
        y_max_in = float(top_pts.min()) if len(top_pts) else (hy - p.wall_thickness)

        drw_x = max((x_max_in - x_min_in) - 2.0 * clr - 0.2, 20.0)
        drw_y = max(H - flr - clr - 0.5, 20.0)
        drw_z = max((y_max_in - y_min_in) - 2.0 * clr - 1.4, 12.0)
        wall = max(p.wall_thickness - 0.2, 1.2)
        d_flr = max(p.floor_thickness - 0.2, 1.2)
        cr = max(p.corner_r - p.wall_thickness - clr, 2.0)

        N = 192
        loop_out = base_polygon(RECTANGLE, drw_x, drw_y, cr, N)
        loop_in = inset_loop(loop_out, wall)
        zs = np.array([0.0, d_flr, d_flr + 5.0, drw_z], dtype=np.float64)
        K = len(zs)
        O = np.broadcast_to(loop_out[None, :, :], (K, N, 2)).copy()
        I = np.broadcast_to(loop_in[None, :, :], (K, N, 2)).copy()
        if p.scoop_floor:
            I[1] = inset_loop(loop_in, 2.4)

        body_v, body_f = hollow_pot_from_rings(zs, O, I, 1)
        parts = [(body_v, body_f)]

        # Front pull handle on -Y face of drawer (printable without supports: 45-degree underside chamfer)
        hw = min(max(0.42 * drw_x, 22.0), 64.0)
        hy_d = 0.5 * drw_y
        hz_top = min(0.68 * drw_z, drw_z - 2.0)
        hz_bot = max(hz_top - 12.0, 2.5)
        h_prof = np.array(
            [
                [-hy_d + 0.1, hz_bot],
                [-hy_d - 8.5, hz_bot + 8.5],
                [-hy_d - 8.5, hz_top],
                [-hy_d - 6.0, hz_top],
                [-hy_d - 6.0, hz_bot + 9.2],
                [-hy_d + 0.1, hz_bot + 9.2],
            ]
        )
        parts.append(extrude_profile_along_axis(h_prof, -0.5 * hw, 0.5 * hw, swap_xy=True))

        # Optional anti-tip stop catch at the back (+Y) top of the drawer
        if p.drawer_stop:
            sw = min(14.0, 0.35 * drw_x)
            parts.append(extrude_box_prism(-sw, sw, hy_d - wall, hy_d + 0.8, drw_z, drw_z + 1.3))

        # Internal dividers inside the drawer
        if p.div_x > 1 or p.div_y > 1:
            z_top = d_flr + (drw_z - d_flr) * (0.01 * p.div_height_pct)
            in_hx = 0.5 * drw_x - wall - 0.05
            in_hy = 0.5 * drw_y - wall - 0.05
            dw = p.div_wall
            if p.div_x > 1:
                for i in range(1, p.div_x):
                    xc = -in_hx + i * (2.0 * in_hx) / p.div_x
                    parts.append(
                        self._divider_wall(
                            -in_hy, in_hy, d_flr, z_top, p.div_y, p.div_dip, xc - 0.5 * dw, xc + 0.5 * dw, True
                        )
                    )
            if p.div_y > 1:
                x_cuts = [-in_hx + i * (2.0 * in_hx) / p.div_x for i in range(p.div_x + 1)]
                for j in range(1, p.div_y):
                    yc = -in_hy + j * (2.0 * in_hy) / p.div_y
                    for c_idx in range(p.div_x):
                        xa = x_cuts[c_idx] + (0.5 * dw if c_idx > 0 else 0.0)
                        xb = x_cuts[c_idx + 1] - (0.5 * dw if c_idx + 1 < p.div_x else 0.0)
                        if xb - xa > 2.0:
                            parts.append(
                                self._divider_wall(
                                    xa, xb, d_flr, z_top, 1, p.div_dip, yc - 0.5 * dw, yc + 0.5 * dw, False
                                )
                            )

        v_raw, f_raw = combine_meshes(parts)
        # On print bed: place drawer beside the upright cubby shell
        bed_offset_x = 0.5 * p.length + 0.5 * drw_x + 16.0
        v_bed = translate_mesh(v_raw, dx=bed_offset_x, dy=0.0, dz=0.0)

        # In assembled 3D view: cubby shell spans Y in [-H, 0] and Z in [0, W_eff]
        pull_dist = (0.01 * p.drawer_pull_pct) * 0.65 * drw_y
        drw_cx = 0.5 * (x_min_in + x_max_in)
        drw_dy = -flr - clr - 0.5 * drw_y - pull_dist
        drw_dz = (y_min_in + 0.5 * W_eff) + clr
        v_asm = translate_mesh(v_raw, dx=drw_cx, dy=drw_dy, dz=drw_dz)
        fil = 2 if (p.colour_style == ACCENT_PARTS and p.colours_used >= 2) else 1
        self.accessories.append(
            {
                "name": f"{p.name}_drawer",
                "label": "Sliding drawer",
                "verts_raw": v_raw,
                "faces_raw": f_raw,
                "verts_bed": v_bed,
                "faces_bed": f_raw,
                "verts_asm": v_asm,
                "faces_asm": f_raw,
                "filament": fil,
            }
        )

    def _build_box_lid(self, base_out: np.ndarray, base_in: np.ndarray, H: float):
        """Build a Stackable Tray Lid or Slide-Lock Lid for LIDDED_BOX."""
        p = self.p
        clr = p.clearance
        N = len(base_out)
        plate_h = 2.0
        skirt_in = inset_loop(base_in, clr)
        skirt_inner = inset_loop(skirt_in, 1.8)

        if p.lid_style == TRAY_LID:
            # Printed upside-down or flat: flat base plate + inner locator ring + raised stacking rim!
            # Built as a clean stepped hollow pot so it is 100% manifold and support-free:
            # Bottom (z=0..3.0) is the locator plug that drops into the box rim;
            # At z=3.0..4.8 it steps out at 45 deg to base_out;
            # From z=4.8..8.0 it forms a shallow parts-sorting tray on top that also accepts a stacked box!
            z_plug = 3.0
            step = p.wall_thickness + clr
            z_step = z_plug + step
            z_top = z_step + 3.2
            zs = np.array([0.0, plate_h, z_plug, z_step, z_top], dtype=np.float64)
            O = np.stack([skirt_in, skirt_in, skirt_in, base_out, base_out], axis=0)
            I = np.stack([skirt_inner, skirt_inner, skirt_inner, base_in, base_in], axis=0)
            v_raw, f_raw = hollow_pot_from_rings(zs, O, I, 1)
            label = "Stackable tray lid"
        else:
            # Slide-Lock Lid with corner hooks
            zs = np.array([0.0, plate_h, plate_h + 2.8], dtype=np.float64)
            O = np.stack([base_out, base_out, skirt_in], axis=0)
            I = np.stack([skirt_inner, skirt_inner, skirt_inner], axis=0)
            v_raw, f_raw = hollow_pot_from_rings(zs, O, I, 1)
            label = "Slide-lock lid"

        W_eff = p.width if p.shape == RECTANGLE else p.length
        bed_offset_y = 0.5 * W_eff + 0.5 * W_eff + 14.0
        v_bed = translate_mesh(v_raw, dx=0.0, dy=bed_offset_y, dz=0.0)
        lift = 0.35 * H * (0.01 * p.drawer_pull_pct)
        v_asm = translate_mesh(v_raw, dx=0.0, dy=0.0, dz=H - 2.8 + lift)
        fil = 2 if (p.colour_style == ACCENT_PARTS and p.colours_used >= 2) else 1
        self.accessories.append(
            {
                "name": f"{p.name}_lid",
                "label": label,
                "verts_raw": v_raw,
                "faces_raw": f_raw,
                "verts_bed": v_bed,
                "faces_bed": f_raw,
                "verts_asm": v_asm,
                "faces_asm": f_raw,
                "filament": fil,
            }
        )

    def _build_slide_in_divider_plates(self, base_in: np.ndarray, flr: float, H: float):
        """Flat-printed slide-in divider plates (with cross-lap slots when both div_x > 1 and div_y > 1)."""
        p = self.p
        clr = p.clearance
        hx = float(np.abs(base_in[:, 0]).max()) - clr
        hy = float(np.abs(base_in[:, 1]).max()) - clr
        div_h = max((H - flr) * (0.01 * p.div_height_pct) - 0.5, 8.0)
        thick = max(p.div_wall - 0.15, 0.8)

        plates_bed = []
        plates_asm = []
        cursor_y = -0.5 * (p.width if p.shape == RECTANGLE else p.length) - 10.0

        # X divider plates (length = 2*hy, height = div_h, printed flat on bed in XY)
        for i in range(1, p.div_x):
            xc = -hx + i * (2.0 * hx) / p.div_x
            # Flat on bed: (u -> X, z -> Y, thickness -> Z)
            v_flat, f_flat = self._divider_wall(-hy, hy, 0.0, div_h, p.div_y, p.div_dip, 0.0, thick, False)
            # Rotate flat onto XY bed: (x, z, -y) -> orient_outward
            v_bed_i, f_bed_i = orient_outward(
                np.column_stack([v_flat[:, 0], v_flat[:, 2] + cursor_y - div_h, v_flat[:, 1]]), f_flat
            )
            cursor_y -= div_h + 6.0
            plates_bed.append((v_bed_i, f_bed_i))

            v_asm_i, f_asm_i = self._divider_wall(
                -hy, hy, flr, flr + div_h, p.div_y, p.div_dip, xc - 0.5 * thick, xc + 0.5 * thick, True
            )
            plates_asm.append((v_asm_i, f_asm_i))

        # Y divider plates (length = 2*hx, height = div_h)
        for j in range(1, p.div_y):
            yc = -hy + j * (2.0 * hy) / p.div_y
            v_flat, f_flat = self._divider_wall(-hx, hx, 0.0, div_h, p.div_x, p.div_dip, 0.0, thick, False)
            v_bed_j, f_bed_j = orient_outward(
                np.column_stack([v_flat[:, 0], v_flat[:, 2] + cursor_y - div_h, v_flat[:, 1]]), f_flat
            )
            cursor_y -= div_h + 6.0
            plates_bed.append((v_bed_j, f_bed_j))

            v_asm_j, f_asm_j = self._divider_wall(
                -hx, hx, flr, flr + div_h, p.div_x, p.div_dip, yc - 0.5 * thick, yc + 0.5 * thick, False
            )
            plates_asm.append((v_asm_j, f_asm_j))

        if plates_bed:
            vb, fb = combine_meshes(plates_bed)
            va, fa = combine_meshes(plates_asm)
            fil = min(3, p.colours_used) if p.colour_style == ACCENT_PARTS else 1
            self.accessories.append(
                {
                    "name": f"{p.name}_dividers",
                    "label": f"{len(plates_bed)} slide-in divider plate(s)",
                    "verts_raw": vb,
                    "faces_raw": fb,
                    "verts_bed": vb,
                    "faces_bed": fb,
                    "verts_asm": va,
                    "faces_asm": fa,
                    "filament": fil,
                }
            )

    # -------------------------------------------------------- views & exports

    def assembled_meshes(self) -> list[tuple[str, np.ndarray, np.ndarray, int]]:
        """Meshes positioned as used (for DRAWER_UNIT, shell laid on its side with drawer sliding out)."""
        p = self.p
        if p.kind == DRAWER_UNIT:
            W_eff = p.width if p.shape == RECTANGLE else p.length
            v_shell = rotate_x_90(self.verts)
            # Shift Z by +0.5 * W_eff so the flat bottom wall (-Y before rotation) rests at z = 0.0
            v_shell = translate_mesh(v_shell, dz=0.5 * W_eff)
            out = [(p.name, v_shell, self.faces, 1)]
        else:
            out = [(p.name, self.verts, self.faces, 1)]
        for acc in self.accessories:
            out.append((acc["name"], acc["verts_asm"], acc["faces_asm"], acc["filament"]))
        return out

    def print_parts(self) -> list[tuple[str, np.ndarray, np.ndarray, int, tuple[float, float, float]]]:
        """All parts arranged flat on the print bed for 3MF export: (name, verts, faces, filament, rgb)."""
        p = self.p
        cols = p.colors()
        out = [(p.name, self.verts, self.faces, 1, cols[1])]
        for acc in self.accessories:
            fil = acc["filament"]
            out.append((acc["name"], acc["verts_bed"], acc["faces_bed"], fil, cols[fil]))
        return out

    def band_stops(self) -> list[tuple[float, int]]:
        """Height band stops [(z_start, filament_1_to_4)] for the 3D shader."""
        p = self.p
        if p.colour_style != BANDS or p.colours_used <= 1:
            return [(0.0, 1)]
        nb = max(int(p.band_count), 2)
        used = max(int(p.colours_used), 2)
        return [(p.height * k / nb, (k % used) + 1) for k in range(nb)]

    def info(self) -> dict[str, str]:
        p = self.p
        W_eff = p.width if p.shape == RECTANGLE else p.length
        lean_ok = "✓" if self.worst <= p.max_overhang + TOLERANCE else "✗"
        mesh_str = f"{self.triangles:,} triangles" + (", closed & watertight ✓" if self.closed else " ✗")

        features = []
        if p.stackable and p.kind != DRAWER_UNIT:
            features.append(f"stackable ({p.stack_height:g} mm foot)")
        if p.connectable:
            features.append(
                "4-way connectable (side-by-side & stacked on side)"
                if p.kind == DRAWER_UNIT
                else "side-connectable (XY dovetails)"
            )
        if p.scoop_floor:
            features.append("finger-scoop floor")
        if p.label_slot:
            features.append("front label slot")

        d = {
            "Role": KIND_NAMES.get(p.kind, "Box"),
            "Shape": SHAPE_NAMES.get(p.shape, "Rectangle"),
            "Outer size": (
                f"{p.length:.0f} W × {p.height:.0f} D × {W_eff:.0f} H mm (laid on side as cubby)"
                if p.kind == DRAWER_UNIT
                else f"{p.length:.0f} × {W_eff:.0f} × {p.height:.0f} mm"
            ),
            "Compartments": (
                f"{p.div_x} × {p.div_y} ({self.compartments} cells of ~{self.cell_x:.0f} × {self.cell_y:.0f} mm)"
                + (" — slide-in plates" if p.div_mode == SLIDE_IN and p.kind != DRAWER_UNIT else " — built-in walls")
            ),
            "Modular features": ", ".join(features).capitalize() if features else "Standalone",
            "Accessories": (
                ", ".join(a["label"] for a in self.accessories) if self.accessories else "None (single piece)"
            ),
            "Steepest overhang": f"{self.worst:.1f}° (limit {p.max_overhang:g}°) {lean_ok}",
            "Filament & time": f"~{self.grams:.0f} g · about {duration(self.seconds)}",
            "Mesh": mesh_str,
        }
        return d
