#!/usr/bin/env python3
"""Generate QR PNGs for demo equipment assets."""
import json
from pathlib import Path

import qrcode

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "backend" / "app" / "data" / "equipment.json"
OUT = ROOT / "frontend" / "public" / "qr"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with open(DATA) as f:
        equipment = json.load(f)
    for eq in equipment:
        img = qrcode.make(eq["qr_payload"])
        path = OUT / f"{eq['id']}.png"
        img.save(path)
        print(f"Wrote {path} -> {eq['qr_payload']}")


if __name__ == "__main__":
    main()
