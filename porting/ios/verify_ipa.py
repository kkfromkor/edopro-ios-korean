#!/usr/bin/env python3
"""Validate a signed IPA's device binary and all packaged runtime files."""
import hashlib
import json
from pathlib import Path
import plistlib
import sys
import tempfile
import zipfile

from package_app import validate_binary

path = Path(sys.argv[1])
prefix = "Payload/EDOPro.app/"
with zipfile.ZipFile(path) as ipa:
    bad = ipa.testzip()
    if bad:
        raise ValueError(f"Corrupt ZIP entry: {bad}")
    info = plistlib.loads(ipa.read(prefix + "Info.plist"))
    executable = info["CFBundleExecutable"]
    with tempfile.TemporaryDirectory() as temporary:
        binary = Path(temporary) / "executable"
        binary.write_bytes(ipa.read(prefix + executable))
        binary_info = validate_binary(binary)
    if not binary_info["has_code_signature"]:
        raise ValueError("Missing Mach-O code signature")
    if not (ipa.getinfo(prefix + executable).external_attr >> 16) & 0o111:
        raise ValueError("Missing executable permissions")
    if info["MinimumOSVersion"] != binary_info["minimum_ios"]:
        raise ValueError("Plist and binary iOS deployment targets differ")
    ipa.getinfo(prefix + "_CodeSignature/CodeResources")
    resources = prefix + "EDOProResources/"
    manifest = json.loads(ipa.read(resources + "resource-manifest.json"))
    for name, expected in manifest["files"].items():
        if hashlib.sha256(ipa.read(resources + name)).hexdigest() != expected:
            raise ValueError(f"Resource hash mismatch: {name}")
    result = {"ipa": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "bytes": path.stat().st_size, "resource_files": len(manifest["files"]),
              "bundle_id": info["CFBundleIdentifier"], **binary_info}
    report = path.with_suffix(".validation.json")
    report.write_text(json.dumps(result, indent=2) + "\n", "utf-8")
    print(json.dumps(result, indent=2))
