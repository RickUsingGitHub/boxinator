"""HTML summary panel, printing steps, and help text for Boxinator."""

from __future__ import annotations

import os
from html import escape

from . import __version__
from .geometry import duration
from .params import DRAWER_UNIT, LIDDED_BOX, SLIDE_IN

APP_NAME = "Boxinator"


def _chip(hex_col: str) -> str:
    return f"<span style='background:{hex_col}; color:{hex_col}; border-radius:3px;'>&nbsp;■■&nbsp;</span>"


def info_html(d, errors: list[str] | None = None, warnings: list[str] | None = None) -> str:
    if errors is None and d is not None:
        errors = d.errors
    if warnings is None and d is not None:
        warnings = d.warnings
    errors = errors or []
    warnings = warnings or []
    css = (
        "<style>"
        "td{padding:3px 6px; vertical-align:top;} "
        ".k{color:#9aa3ad; white-space:nowrap; font-weight:600;} "
        ".p{color:#c5cdd9; margin:4px 0 8px 0;} "
        ".e{color:#ff6b6b;} .w{color:#f2c14e;} .ok{color:#6fdc8c;} "
        "h3{margin:8px 0 4px 0; color:#8ab4f8;}"
        "</style>"
    )
    html = [css]
    if errors:
        html.append("<h3 class='e'>Cannot build this box</h3><ul>")
        html += [f"<li class='e'>{escape(e)}</li>" for e in errors]
        html.append("</ul>")
    if d is not None and not errors:
        html.append("<h3>The box</h3><table width='100%'>")
        for k, v in d.info().items():
            cls = " class='ok'" if v.endswith("✓") else (" class='e'" if v.endswith("✗") else "")
            html.append(f"<tr><td class='k'>{escape(k)}</td><td{cls}>{escape(v)}</td></tr>")
        html.append("</table>")
        for note in d.notes:
            html.append(f"<p class='p'>ℹ {escape(note)}</p>")
    if warnings:
        html.append("<h3 class='w'>Notes & warnings</h3><ul>")
        html += [f"<li class='w'>{escape(w)}</li>" for w in warnings]
        html.append("</ul>")

    if d is not None and not errors:
        p = d.p
        html.append("<h3>How it connects & prints</h3>")
        if p.kind == DRAWER_UNIT:
            html.append(
                "<p class='p'><b>Side-Drawer Unit:</b> The outer <b>Cubby Shell</b> prints standing upright on its "
                "closed back wall (zero supports, zero bridging). Its Right and Top walls carry flared <b>Male "
                "Dovetail Tails</b>; its Left and Bottom walls carry recessed <b>Female Dovetail Sockets</b> (whose "
                "inner housings double as low-friction drawer runner rails!). Slide cubbies together front-to-back "
                "to lock them <b>side-by-side and stacked</b>.</p>"
            )
        elif p.kind == LIDDED_BOX:
            html.append(
                "<p class='p'><b>Lidded Box:</b> Both the box and its fitted lid print flat on the bed with "
                "<b>no supports</b>. The <b>Stackable Tray Lid</b> doubles as a parts-sorting tray and accepts "
                "another box stacked on top; the <b>Slide-Lock Lid</b> hooks into corner rails inside the rim.</p>"
            )
        else:
            html.append(
                "<p class='p'>Prints flat on the bed with your <b>usual slicer settings</b> (Spiral vase off, "
                f"<b>Supports off</b> — steepest overhang is {d.worst:.0f}°). "
                "To connect boxes side-by-side, slide the flared dovetail tails on the Right/Back walls vertically "
                "into the dovetail sockets on the neighbour's Left/Front walls. "
                + (
                    "Slide-in divider plates print flat on the bed and drop into the vertical wall slots."
                    if p.div_mode == SLIDE_IN and (p.div_x > 1 or p.div_y > 1)
                    else ""
                )
                + "</p>"
            )

        html.append("<h3>Filaments</h3><p>")
        parts = d.print_parts()
        seen = []
        for nm, _, _, fil, _ in parts:
            col = getattr(p, f"color{fil}").upper()
            seen.append(f"{_chip(col)} <b>{escape(nm)}</b> (Filament {fil})")
        html.append("<br>".join(seen) + "</p>")
    return "".join(html)


def print_steps(d, path: str, where: str = "your slicer") -> str:
    parts = d.print_parts()
    acc_note = ""
    if d.p.kind == DRAWER_UNIT:
        acc_note = (
            "<li>The file holds both the <b>Cubby Shell</b> (standing on its closed back) and the "
            "<b>Sliding Drawer</b> (flat on its floor). When printed, lay the Cubby Shell on its side and "
            "slide the drawer in!</li>"
        )
    elif d.accessories:
        labels = ", ".join(a["label"] for a in d.accessories)
        acc_note = f"<li>The file includes the box and its <b>{escape(labels)}</b> laid flat on the bed.</li>"

    return (
        f"<p>Saved <b>{escape(os.path.basename(path))}</b><br>in {escape(os.path.dirname(path))}</p>"
        f"<ol><li>Open it in {escape(where)} (the button below, or File ▸ Import).</li>"
        "<li>Use your <b>usual print settings</b> (2–3 walls, 15% infill, <b>Supports off</b>).</li>"
        f"{acc_note}"
        f"<li>Slice and print: about <b>{duration(d.seconds)}</b> and <b>{d.grams:.0f} g</b> of filament.</li></ol>"
    )


ABOUT_HTML = (
    f"<h3>{APP_NAME} {__version__}</h3>"
    "<p>Focused parametric designer for 3D-printable <b>stackable, connectable, divided boxes, workshop "
    "parts bins, caddies, and modular side-drawer units</b> — all engineered to print with <b>zero supports</b>.</p>"
    "<ul>"
    "<li><b>Stackable:</b> 45° recessed bottom foot nests positively into the open rim of any matching box below.</li>"
    "<li><b>Connectable:</b> Integral XY dovetail keys and slots lock boxes side-by-side (and vertically when "
    "laid on their sides as drawer cubbies) with 0° Z overhang and a built-in bottom alignment stop.</li>"
    "<li><b>Side Drawers:</b> Turn any box into a modular drawer unit — the cubby shell prints upright on its back "
    "without supports, lays on its side, and accepts a matching divided sliding drawer.</li>"
    "<li><b>Dividers & Finger Scoops:</b> Built-in dividers or fast flat-printed slide-in plates, plus curved "
    "finger-sweep floors for picking up small screws, beads, and tokens effortlessly.</li>"
    "</ul>"
)


def print_steps_html(d, path: str = "box.3mf", where: str = "your slicer") -> str:
    return print_steps(d, path, where)


HELP_HTML = ABOUT_HTML
