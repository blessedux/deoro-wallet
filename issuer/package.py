"""PassKit package builder.

Unsigned packages are for tests and inspection only. A production download
is a signed .pkpass. Without signing credentials this module refuses to
emit a pretend-valid Wallet file.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS_DIR = ROOT / "pass" / "Deoro Loyalty.pass"
SERIAL_RE = r"^DEORO-\d+$"

REQUIRED_FILES = (
    "pass.json",
    "icon.png",
    "icon@2x.png",
    "icon@3x.png",
    "logo.png",
    "logo@2x.png",
    "logo@3x.png",
    "strip.png",
    "strip@2x.png",
    "strip@3x.png",
)

PKPASS_TYPE = "application/vnd.apple.pkpass"

CREDENTIAL_KEYS = (
    "APPLE_PASS_CERT_PEM",
    "APPLE_PASS_PRIVATE_KEY_PEM",
    "APPLE_WWDR_CERT_PEM",
)


class UnknownMember(Exception):
    def __init__(self, serial: str) -> None:
        super().__init__(f"No member for {serial}.")
        self.serial = serial


class BadSerial(Exception):
    def __init__(self, serial: str) -> None:
        super().__init__("Serial should look like DEORO-10001.")
        self.serial = serial


class MissingCredentials(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Signing credentials are not configured. "
            "Deoro will not serve an unsigned file as a Wallet pass. "
            "Ticket 5 wires Pass Type ID certs as secrets."
        )


def normalize_serial(raw: str | None) -> str:
    return str(raw or "").strip().upper()


def validate_serial_format(serial: str) -> None:
    import re

    if not re.match(SERIAL_RE, serial):
        raise BadSerial(serial)


def load_source_pass() -> dict:
    return json.loads(PASS_DIR.joinpath("pass.json").read_text(encoding="utf-8"))


def known_serial() -> str:
    return load_source_pass()["serialNumber"]


def resolve_member(serial: str) -> dict:
    serial = normalize_serial(serial)
    validate_serial_format(serial)
    source = load_source_pass()
    if source["serialNumber"] != serial:
        raise UnknownMember(serial)
    return source


def signing_configured(env: dict | None = None) -> bool:
    env = env if env is not None else os.environ
    if all(env.get(k) for k in CREDENTIAL_KEYS):
        return True
    paths = (
        env.get("APPLE_PASS_CERT_PATH"),
        env.get("APPLE_PASS_KEY_PATH"),
        env.get("APPLE_WWDR_CERT_PATH"),
    )
    return all(paths) and all(Path(p).is_file() for p in paths)


def _pem(env: dict, pem_key: str, path_key: str) -> str:
    if env.get(pem_key):
        return env[pem_key]
    path = env.get(path_key)
    if path and Path(path).is_file():
        return Path(path).read_text(encoding="utf-8")
    raise MissingCredentials()


def credentials(env: dict | None = None) -> dict[str, str]:
    env = env if env is not None else os.environ
    if not signing_configured(env):
        raise MissingCredentials()
    return {
        "cert": _pem(env, "APPLE_PASS_CERT_PEM", "APPLE_PASS_CERT_PATH"),
        "key": _pem(env, "APPLE_PASS_PRIVATE_KEY_PEM", "APPLE_PASS_KEY_PATH"),
        "wwdr": _pem(env, "APPLE_WWDR_CERT_PEM", "APPLE_WWDR_CERT_PATH"),
        "passphrase": env.get("APPLE_PASS_KEY_PASSPHRASE") or "",
        "team": env.get("APPLE_TEAM_IDENTIFIER") or "",
    }


def pass_json_bytes(source: dict, team_id: str | None = None) -> bytes:
    data = json.loads(json.dumps(source))
    if team_id:
        data["teamIdentifier"] = team_id
        return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return PASS_DIR.joinpath("pass.json").read_bytes()


def build_unsigned_files(serial: str, team_id: str | None = None) -> dict[str, bytes]:
    source = resolve_member(serial)
    files: dict[str, bytes] = {"pass.json": pass_json_bytes(source, team_id)}
    for name in REQUIRED_FILES:
        if name == "pass.json":
            continue
        path = PASS_DIR / name
        if not path.is_file():
            raise FileNotFoundError(name)
        files[name] = path.read_bytes()
    manifest = {name: hashlib.sha1(blob).hexdigest() for name, blob in files.items()}
    files["manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return files


def zip_package(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, blob in files.items():
            zf.writestr(name, blob)
    return buf.getvalue()


def sign_manifest(manifest: bytes, creds: dict[str, str]) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "cert.pem").write_text(creds["cert"], encoding="utf-8")
        (t / "key.pem").write_text(creds["key"], encoding="utf-8")
        (t / "wwdr.pem").write_text(creds["wwdr"], encoding="utf-8")
        (t / "manifest.json").write_bytes(manifest)
        cmd = [
            "openssl",
            "smime",
            "-binary",
            "-sign",
            "-certfile",
            str(t / "wwdr.pem"),
            "-signer",
            str(t / "cert.pem"),
            "-inkey",
            str(t / "key.pem"),
            "-in",
            str(t / "manifest.json"),
            "-outform",
            "DER",
            "-out",
            str(t / "signature"),
        ]
        if creds["passphrase"]:
            cmd.extend(["-passin", f"pass:{creds['passphrase']}"])
        subprocess.run(cmd, check=True, capture_output=True)
        return (t / "signature").read_bytes()


def issue_signed_pkpass(serial: str, env: dict | None = None) -> bytes:
    """Production file. Raises MissingCredentials if certs are absent."""
    creds = credentials(env)
    files = build_unsigned_files(serial, team_id=creds["team"] or None)
    files["signature"] = sign_manifest(files["manifest.json"], creds)
    return zip_package(files)


def issue_response(serial: str, env: dict | None = None) -> tuple[int, str, bytes, dict[str, str]]:
    """Return (status, content_type, body, headers) for the install URL."""
    env = env if env is not None else os.environ
    serial = normalize_serial(serial)
    try:
        validate_serial_format(serial)
        resolve_member(serial)
    except BadSerial as e:
        return 400, "text/plain; charset=utf-8", str(e).encode("utf-8"), {}
    except UnknownMember as e:
        return 404, "text/plain; charset=utf-8", str(e).encode("utf-8"), {}

    if not signing_configured(env):
        body = (
            "Signing credentials are not configured.\n\n"
            "Deoro will not serve an unsigned file as application/vnd.apple.pkpass.\n"
            "Wallet would reject it. Ticket 5 adds the Pass Type ID certificate as a secret.\n"
        ).encode("utf-8")
        return 503, "text/plain; charset=utf-8", body, {}

    try:
        pkpass = issue_signed_pkpass(serial, env)
    except (MissingCredentials, subprocess.CalledProcessError) as e:
        return 503, "text/plain; charset=utf-8", str(e).encode("utf-8"), {}

    headers = {
        "Content-Disposition": f'attachment; filename="{serial}.pkpass"',
    }
    return 200, PKPASS_TYPE, pkpass, headers
