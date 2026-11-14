"""Finding the slicer programs on this computer, to open a saved box in one."""

from __future__ import annotations

import glob
import os

from PySide6.QtCore import QProcess

KNOWN = [
    ("Flash Studio", r"Flashforge\Flash Studio*\flash studio.exe"),
    ("Orca Slicer", r"OrcaSlicer\orca-slicer.exe"),
    ("Bambu Studio", r"Bambu Studio\bambu-studio.exe"),
    ("PrusaSlicer", r"Prusa3D\PrusaSlicer\prusa-slicer.exe"),
    ("UltiMaker Cura", r"UltiMaker Cura *\UltiMaker-Cura.exe"),
    ("Creality Print", r"Creality\Creality Print*\CrealityPrint.exe"),
    ("Elegoo Slicer", r"ElegooSlicer\elegoo-slicer.exe"),
    ("Anycubic Slicer Next", r"AnycubicSlicerNext\AnycubicSlicerNext.exe"),
]


def _roots():
    for var in ("ProgramFiles", "ProgramFiles(x86)", "ProgramW6432"):
        if os.environ.get(var):
            yield os.environ[var]
    if os.environ.get("LOCALAPPDATA"):
        yield os.path.join(os.environ["LOCALAPPDATA"], "Programs")


def find_slicers() -> list[tuple[str, str]]:
    found, seen = [], set()
    for name, pattern in KNOWN:
        for root in _roots():
            for path in sorted(glob.glob(os.path.join(root, pattern)), reverse=True):
                key = os.path.normcase(os.path.abspath(path))
                if key not in seen:
                    seen.add(key)
                    found.append((name, path))
                    break
    return found


def slicer_name(path: str) -> str:
    for name, pattern in KNOWN:
        if os.path.basename(path).lower() == os.path.basename(pattern).lower():
            return name
    return os.path.splitext(os.path.basename(path))[0]


def open_in(program: str, file: str) -> bool:
    return bool(
        program
        and os.path.exists(program)
        and QProcess.startDetached(program, [os.path.abspath(file)], os.path.dirname(program))[0]
    )


def open_in_slicer(design, params, slicer_path: str | None = None):
    import tempfile
    from pathlib import Path
    from .threemf import write_3mf

    out_dir = Path(tempfile.gettempdir()) / "boxinator_exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{params.name}.3mf"
    write_3mf(out_path, design, params)
    if slicer_path and os.path.exists(slicer_path):
        open_in(slicer_path, str(out_path))
        return out_path, slicer_name(slicer_path)
    if hasattr(os, "startfile"):
        os.startfile(str(out_path))  # type: ignore[attr-defined]
    return out_path, "system default slicer"
