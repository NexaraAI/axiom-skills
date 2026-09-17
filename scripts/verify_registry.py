#!/usr/bin/env python3
"""Verify that every sha256 pin in registry.json matches the bytes on disk.

The engine hashes the exact bytes it reads at install time, so a pin that
describes different bytes than the working tree (a stale re-pin after an
edit, or a CRLF file committed over an LF one) breaks installs for every
client that fetches it. This script fails the build on any such drift.

Also checks coverage in both directions: a manifest or bundle that exists
on disk without a registry entry is an installable artifact no client can
verify, so it is reported too.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry.json"

failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


def pin_mismatch(kind: str, entry_id: str, path: Path, expected: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if b"\r\n" in path.read_bytes():
        fail(
            f"{kind} {entry_id}: {path.relative_to(ROOT)} contains CRLF line endings; "
            f"pins are computed over LF content (expected {expected[:12]}..., got {actual[:12]}...)"
        )
    else:
        fail(
            f"{kind} {entry_id}: sha256 mismatch for {path.relative_to(ROOT)} "
            f"(registry {expected[:12]}..., actual {actual[:12]}...); "
            f"re-pin it or revert the file"
        )


def main() -> int:
    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: registry.json is unreadable or invalid JSON: {error}")
        return 1

    pinned_manifests: set[str] = set()
    for skill in registry.get("skills", []):
        skill_id = skill.get("id", "<missing id>")
        manifest_url = skill.get("manifest_url", "")
        manifest = ROOT / manifest_url
        if not manifest_url or not manifest.is_file():
            fail(f"skill {skill_id}: manifest_url {manifest_url!r} does not exist on disk")
            continue
        pinned_manifests.add(manifest_url.replace("\\", "/"))
        expected = skill.get("sha256", "")
        if not expected:
            fail(f"skill {skill_id}: missing sha256 pin")
            continue
        actual = hashlib.sha256(manifest.read_bytes()).hexdigest()
        if actual != expected:
            pin_mismatch("skill", skill_id, manifest, expected)

    pinned_bundles: set[str] = set()
    for bundle in registry.get("bundles", []):
        bundle_id = bundle.get("id", "<missing id>")
        bundle_url = bundle.get("bundle_url", "")
        bundle_path = ROOT / bundle_url
        if not bundle_url or not bundle_path.is_file():
            fail(f"bundle {bundle_id}: bundle_url {bundle_url!r} does not exist on disk")
            continue
        pinned_bundles.add(bundle_url.replace("\\", "/"))
        expected = bundle.get("sha256", "")
        if not expected:
            fail(f"bundle {bundle_id}: missing sha256 pin")
            continue
        actual = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
        if actual != expected:
            pin_mismatch("bundle", bundle_id, bundle_path, expected)

    for manifest in sorted(ROOT.glob("skills/*/skill.toml")):
        rel = manifest.relative_to(ROOT).as_posix()
        if rel not in pinned_manifests:
            fail(f"unpinned manifest on disk: {rel} has no entry in registry.json")

    for bundle in sorted(ROOT.glob("bundles/*.toml")):
        rel = bundle.relative_to(ROOT).as_posix()
        if rel not in pinned_bundles:
            fail(f"unpinned bundle on disk: {rel} has no entry in registry.json")

    if failures:
        print(f"registry verification FAILED with {len(failures)} problem(s):")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    skill_count = len(registry.get("skills", []))
    bundle_count = len(registry.get("bundles", []))
    print(f"registry verification passed: {skill_count} skill pins and "
          f"{bundle_count} bundle pins match on-disk bytes; no unpinned artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
