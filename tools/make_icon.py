"""Generate high-DPI PNG and multi-resolution Windows ICO icons for Boxinator."""

from __future__ import annotations

import os
import struct
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QBuffer, QIODevice, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QGuiApplication,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
)
from PySide6.QtGui import QImage


def _draw_boxinator_icon(size: int) -> QImage:
    img = QImage(size, size, QImage.Format_RGBA8888)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.SmoothPixmapTransform, True)

    s = size / 256.0
    p.scale(s, s)

    # 1) Rounded studio badge background
    badge_rect = QRectF(10, 10, 236, 236)
    bg = QLinearGradient(10, 10, 246, 246)
    bg.setColorAt(0.0, QColor("#1f2b3e"))
    bg.setColorAt(1.0, QColor("#111722"))
    p.setBrush(bg)
    p.setPen(QPen(QColor("#3c5a82"), 5.0))
    p.drawRoundedRect(badge_rect, 46, 46)

    # Subtle top-left glow
    glow = QRadialGradient(84, 72, 160)
    glow.setColorAt(0.0, QColor(76, 139, 245, 42))
    glow.setColorAt(1.0, QColor(76, 139, 245, 0))
    p.setBrush(glow)
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(badge_rect, 46, 46)

    # Isometric origin centered inside the rounded square
    # X axis goes down-right (+46, +24)
    # Y axis (front-to-back) goes up-right (+36, -22)
    # Z axis goes straight up (0, -46)
    ox, oy = 126.0, 134.0

    def iso(x: float, y: float, z: float) -> QPointF:
        return QPointF(
            ox + x * 46.0 + y * 36.0,
            oy + x * 24.0 - y * 22.0 - z * 46.0,
        )

    def poly(pts: list[tuple[float, float, float]]) -> QPolygonF:
        return QPolygonF([iso(x, y, z) for x, y, z in pts])

    # Drop shadow under the cubby
    p.setBrush(QColor(0, 0, 0, 95))
    p.setPen(Qt.NoPen)
    p.drawPolygon(poly([(-1.05, -0.82, -0.88), (1.05, -0.82, -0.88), (1.05, 0.95, -0.88), (-1.05, 0.95, -0.88)]))

    # 2) Outer Cubby Shell (Teal: #2ea89c top, #1f8077 left/front, #155c55 right)
    # Back-to-front painter order:
    # Inner floor + back wall dark recess
    p.setPen(QPen(QColor("#0f3f3a"), 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    # Right side wall (+X face: x = +1.0)
    right_grad = QLinearGradient(iso(1, -0.6, 0.8), iso(1, 0.8, -0.8))
    right_grad.setColorAt(0.0, QColor("#1b6f67"))
    right_grad.setColorAt(1.0, QColor("#114b45"))
    p.setBrush(right_grad)
    p.drawPolygon(poly([(1.0, -0.70, -0.78), (1.0, 0.82, -0.78), (1.0, 0.82, 0.78), (1.0, -0.70, 0.78)]))

    # Rounded Keystone Dovetail Tenon on the Right wall (+X, protruding outward)
    p.setBrush(QColor("#29968b"))
    p.setPen(QPen(QColor("#0f3f3a"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPolygon(
        poly(
            [
                (1.16, -0.18, -0.76),
                (1.16, 0.22, -0.76),
                (1.16, 0.22, 0.76),
                (1.16, -0.18, 0.76),
            ]
        )
    )
    # Top cap of the right-side dovetail tenon
    p.setBrush(QColor("#47cfc2"))
    p.drawPolygon(
        poly(
            [
                (1.00, -0.11, 0.78),
                (1.16, -0.18, 0.76),
                (1.16, 0.22, 0.76),
                (1.00, 0.15, 0.78),
            ]
        )
    )

    # Top face of Cubby Shell (z = +0.78)
    top_grad = QLinearGradient(iso(-1, 0.8, 0.78), iso(1, -0.7, 0.78))
    top_grad.setColorAt(0.0, QColor("#45cfc1"))
    top_grad.setColorAt(1.0, QColor("#289c90"))
    p.setBrush(top_grad)
    p.setPen(QPen(QColor("#145952"), 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPolygon(poly([(-1.0, -0.70, 0.78), (1.0, -0.70, 0.78), (1.0, 0.82, 0.78), (-1.0, 0.82, 0.78)]))

    # Two interlocking top dovetail rails (raised keystone ribs on z = +0.78)
    for x0, x1 in ((-0.62, -0.22), (0.22, 0.62)):
        p.setBrush(QColor("#5ce0d3"))
        p.drawPolygon(poly([(x0 - 0.06, -0.68, 0.90), (x1 + 0.06, -0.68, 0.90), (x1 + 0.06, 0.80, 0.90), (x0 - 0.06, 0.80, 0.90)]))
        p.setBrush(QColor("#20837a"))
        p.drawPolygon(poly([(x0, -0.68, 0.78), (x0 - 0.06, -0.68, 0.90), (x1 + 0.06, -0.68, 0.90), (x1, -0.68, 0.78)]))

    # Left/front opening rim of the Cubby Shell (-Y face at y = -0.70)
    p.setBrush(QColor("#1d7a71"))
    p.setPen(QPen(QColor("#104540"), 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPolygon(poly([(-1.0, -0.70, -0.78), (1.0, -0.70, -0.78), (1.0, -0.70, 0.78), (-1.0, -0.70, 0.78)]))

    # Dark interior cavity of the cubby shell
    p.setBrush(QColor("#0c2426"))
    p.setPen(Qt.NoPen)
    p.drawPolygon(poly([(-0.84, -0.70, -0.64), (0.84, -0.70, -0.64), (0.84, -0.70, 0.64), (-0.84, -0.70, 0.64)]))

    # 3) Sliding Drawer (Warm Gold/Amber) pulled half-way forward (y in [-1.25, -0.45])
    dy = -0.58  # pull-out distance toward -Y
    # Drawer right side (-Y..+Y on x = +0.80)
    p.setPen(QPen(QColor("#6b4a11"), 2.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(QColor("#b88428"))
    p.drawPolygon(
        poly(
            [
                (0.80, -0.70 + dy, -0.60),
                (0.80, -0.68, -0.60),
                (0.80, -0.68, 0.56),
                (0.80, -0.70 + dy, 0.56),
            ]
        )
    )

    # Drawer dark interior + crisp 2x2 divider walls visible from above!
    p.setBrush(QColor("#805916"))
    p.drawPolygon(
        poly(
            [
                (-0.80, -0.70 + dy, 0.56),
                (0.80, -0.70 + dy, 0.56),
                (0.80, -0.68, 0.56),
                (-0.80, -0.68, 0.56),
            ]
        )
    )
    # Cross divider bar inside the open drawer
    p.setBrush(QColor("#e8b95b"))
    p.drawPolygon(
        poly(
            [
                (-0.07, -0.70 + dy, 0.52),
                (0.07, -0.70 + dy, 0.52),
                (0.07, -0.68, 0.52),
                (-0.07, -0.68, 0.52),
            ]
        )
    )
    # Rim highlight around top edge of drawer
    p.setPen(QPen(QColor("#fae19c"), 3.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPolyline(poly([(-0.80, -0.68, 0.56), (-0.80, -0.70 + dy, 0.56), (0.80, -0.70 + dy, 0.56), (0.80, -0.68, 0.56)]))

    # Drawer Front Face (y = -0.70 + dy)
    front_grad = QLinearGradient(iso(-0.80, -0.70 + dy, 0.56), iso(0.80, -0.70 + dy, -0.60))
    front_grad.setColorAt(0.0, QColor("#f2c86b"))
    front_grad.setColorAt(1.0, QColor("#d49e38"))
    p.setBrush(front_grad)
    p.setPen(QPen(QColor("#6b4a11"), 2.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPolygon(
        poly(
            [
                (-0.80, -0.70 + dy, -0.60),
                (0.80, -0.70 + dy, -0.60),
                (0.80, -0.70 + dy, 0.56),
                (-0.80, -0.70 + dy, 0.56),
            ]
        )
    )

    # Drawer Pull Handle (raised horizontal bar on front face)
    hy = -0.78 + dy
    p.setBrush(QColor("#ffe6a3"))
    p.setPen(QPen(QColor("#6b4a11"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPolygon(poly([(-0.34, hy, 0.08), (0.34, hy, 0.08), (0.34, -0.70 + dy, 0.08), (-0.34, -0.70 + dy, 0.08)]))
    p.setBrush(QColor("#e5b14a"))
    p.drawPolygon(poly([(-0.34, hy, -0.06), (0.34, hy, -0.06), (0.34, hy, 0.08), (-0.34, hy, 0.08)]))

    p.end()
    return img


def _image_to_png_bytes(img: QImage) -> bytes:
    buf = QBuffer()
    buf.open(QIODevice.WriteOnly)
    img.save(buf, "PNG")
    return bytes(buf.data())


def _write_ico(path: Path, sizes: tuple[int, ...] = (16, 24, 32, 48, 64, 128, 256)) -> None:
    frames = []
    for sz in sizes:
        img = _draw_boxinator_icon(sz)
        frames.append((sz, _image_to_png_bytes(img)))

    n = len(frames)
    header = struct.pack("<HHH", 0, 1, n)
    offset = 6 + 16 * n
    entries = []
    payloads = []
    for sz, png in frames:
        w_byte = 0 if sz >= 256 else sz
        h_byte = 0 if sz >= 256 else sz
        entries.append(struct.pack("<BBBBHHII", w_byte, h_byte, 0, 0, 1, 32, len(png), offset))
        payloads.append(png)
        offset += len(png)

    path.write_bytes(header + b"".join(entries) + b"".join(payloads))


def main() -> None:
    app = QGuiApplication.instance() or QGuiApplication([])
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    img256 = _draw_boxinator_icon(256)
    (assets_dir / "icon.png").write_bytes(_image_to_png_bytes(img256))
    _write_ico(assets_dir / "icon.ico")
    print(f"Wrote {assets_dir / 'icon.png'} and {assets_dir / 'icon.ico'}")


if __name__ == "__main__":
    main()
