#!/usr/bin/env python3
"""Validate pass source, preview seam, and counter lookup (no Apple certs)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS_DIR = ROOT / "pass" / "Deoro Loyalty.pass"
PASS_JSON = PASS_DIR / "pass.json"
PREVIEW = ROOT / "preview" / "index.html"
QR_LIB = ROOT / "preview" / "vendor" / "qrcode.js"
COUNTER = ROOT / "counter" / "index.html"
COUNTER_LIB = ROOT / "counter" / "vendor" / "html5-qrcode.min.js"

REQUIRED_IMAGES = [
    "icon.png",
    "icon@2x.png",
    "icon@3x.png",
    "logo.png",
    "logo@2x.png",
    "logo@3x.png",
    "strip.png",
    "strip@2x.png",
    "strip@3x.png",
]

BACK_KEYS = ("how", "hours", "terms", "contact")


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not PASS_JSON.is_file():
        fail(f"missing {PASS_JSON}")
    pass_data = json.loads(PASS_JSON.read_text(encoding="utf-8"))

    for key in (
        "formatVersion",
        "passTypeIdentifier",
        "teamIdentifier",
        "serialNumber",
        "organizationName",
        "description",
        "foregroundColor",
        "backgroundColor",
        "labelColor",
        "storeCard",
        "barcodes",
    ):
        if key not in pass_data:
            fail(f"pass.json missing {key}")

    if pass_data["formatVersion"] != 1:
        fail("formatVersion must be 1")
    if pass_data["passTypeIdentifier"] != "pass.com.deoro.loyalty":
        fail("passTypeIdentifier must be pass.com.deoro.loyalty")
    if pass_data["serialNumber"] != "DEORO-10001":
        fail("demo serialNumber must be DEORO-10001")
    if pass_data["backgroundColor"] != "rgb(42, 28, 20)":
        fail("backgroundColor must be espresso rgb(42, 28, 20)")
    if pass_data["foregroundColor"] != "rgb(245, 230, 196)":
        fail("foregroundColor must be cream rgb(245, 230, 196)")
    if pass_data["labelColor"] != "rgb(212, 175, 106)":
        fail("labelColor must be gold rgb(212, 175, 106)")

    card = pass_data["storeCard"]
    stamps = next((f for f in card.get("primaryFields", []) if f.get("key") == "stamps"), None)
    member = next((f for f in card.get("headerFields", []) if f.get("key") == "member"), None)
    if not stamps:
        fail("storeCard.primaryFields must include stamps")
    if not member:
        fail("storeCard.headerFields must include member")
    if "/" not in str(stamps.get("value", "")):
        fail("stamps value should look like '7 / 10'")

    barcode = pass_data["barcodes"][0]
    if barcode.get("format") != "PKBarcodeFormatQR":
        fail("barcode format must be PKBarcodeFormatQR")
    if barcode.get("message") != pass_data["serialNumber"]:
        fail("QR message must equal serialNumber")

    back_keys = {f.get("key") for f in card.get("backFields", [])}
    missing_back = [k for k in BACK_KEYS if k not in back_keys]
    if missing_back:
        fail(f"backFields missing {missing_back}")

    for name in REQUIRED_IMAGES:
        path = PASS_DIR / name
        if not path.is_file() or path.stat().st_size < 50:
            fail(f"missing or empty PassKit image {name}")

    preview = PREVIEW.read_text(encoding="utf-8")
    if "pass.json" not in preview:
        fail("preview must load pass.json")
    if "qrcode.js" not in preview:
        fail("preview must encode QR locally from pass.json")
    if "Flip card" not in preview:
        fail("preview must flip to back fields")
    if not QR_LIB.is_file():
        fail("missing preview/vendor/qrcode.js")

    if COUNTER.is_file():
        counter = COUNTER.read_text(encoding="utf-8")
        if "pass.json" not in counter:
            fail("counter must look up the same pass.json")
        if "DEORO-" not in counter:
            fail("counter must accept DEORO-<id> serials")
        if "No member found" not in counter:
            fail("counter must show a clear miss for unknown serials")
        if "preview" not in counter:
            fail("counter must document the preview QR as the happy path")
        if "Start camera" not in counter or "paste-form" not in counter:
            fail("counter must support camera or paste")
        if not COUNTER_LIB.is_file() or COUNTER_LIB.stat().st_size < 1000:
            fail("missing counter/vendor/html5-qrcode.min.js")
        print("counter OK")

    print("pass source OK")
    print(f"  serial {pass_data['serialNumber']}")
    print(f"  stamps {stamps['value']}")
    print(f"  member {member['value']}")
    print(f"  images {len(REQUIRED_IMAGES)}")


if __name__ == "__main__":
    main()
