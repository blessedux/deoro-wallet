#!/usr/bin/env python3
"""Ticket 4: package shape + missing-cert refusal (no Apple certs required)."""

from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from issuer.package import (  # noqa: E402
    PKPASS_TYPE,
    REQUIRED_FILES,
    BadSerial,
    MissingCredentials,
    UnknownMember,
    build_unsigned_files,
    credentials,
    issue_response,
    issue_signed_pkpass,
    zip_package,
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def test_unsigned_package_shape() -> None:
    files = build_unsigned_files("DEORO-10001")
    for name in REQUIRED_FILES:
        if name not in files:
            fail(f"package missing {name}")
    manifest = json.loads(files["manifest.json"])
    for name, blob in files.items():
        if name == "manifest.json":
            continue
        digest = hashlib.sha1(blob).hexdigest()
        if manifest.get(name) != digest:
            fail(f"SHA-1 mismatch for {name}")
    if "signature" in files:
        fail("unsigned package must not include a signature")
    zipped = zip_package(files)
    with zipfile.ZipFile(io.BytesIO(zipped)) as zf:
        names = set(zf.namelist())
    if "pass.json" not in names or "manifest.json" not in names:
        fail("zip missing pass.json or manifest.json")
    print("unsigned package shape OK")


def test_unknown_and_bad_serial() -> None:
    try:
        build_unsigned_files("DEORO-99999")
        fail("unknown serial should raise")
    except UnknownMember:
        pass
    try:
        build_unsigned_files("HELLO")
        fail("bad serial should raise")
    except BadSerial:
        pass
    print("serial errors OK")


def test_missing_cert_refusal() -> None:
    empty = {}
    try:
        credentials(empty)
        fail("credentials() must raise without certs")
    except MissingCredentials:
        pass
    try:
        issue_signed_pkpass("DEORO-10001", empty)
        fail("issue_signed_pkpass must raise without certs")
    except MissingCredentials:
        pass

    status, content_type, body, _headers = issue_response("DEORO-10001", empty)
    if status != 503:
        fail(f"install URL without certs must be 503, got {status}")
    if content_type.startswith(PKPASS_TYPE) or body[:2] == b"PK":
        fail("must not emit a pretend-valid .pkpass without certs")
    if b"Signing credentials" not in body:
        fail("refusal must explain missing signing credentials")

    status, _ct, _body, _ = issue_response("DEORO-99999", empty)
    if status != 404:
        fail(f"unknown member must be 404, got {status}")
    print("missing-cert refusal OK")


def main() -> None:
    test_unsigned_package_shape()
    test_unknown_and_bad_serial()
    test_missing_cert_refusal()
    print("issuer tests OK")


if __name__ == "__main__":
    main()
