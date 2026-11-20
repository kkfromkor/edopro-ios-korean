#!/usr/bin/env python3
"""Stage an ARM64 app for signing. This does not sign or install an IPA."""
import argparse
from pathlib import Path
import plistlib
import shutil
import struct

from prepare_resources import ROOT, OUTPUT


def validate_binary(binary):
    data = binary.read_bytes()
    header = data[:32]
    if len(header) < 32:
        raise ValueError("Missing Mach-O header")
    magic, cpu, _, kind = struct.unpack_from("<IIII", header)
    if (magic, cpu, kind) != (0xFEEDFACF, 0x0100000C, 2):
        raise ValueError("Expected a compiled ARM64 Mach-O executable")
    ncmds, sizeofcmds = struct.unpack_from("<II", header, 16)
    if not ncmds or 32 + sizeofcmds > len(data):
        raise ValueError("Invalid Mach-O load commands")
    minimum = None
    signed = False
    libraries = []
    offset = 32
    for _ in range(ncmds):
        command, size = struct.unpack_from("<II", data, offset)
        if size < 8 or offset + size > 32 + sizeofcmds:
            raise ValueError("Truncated Mach-O load command")
        if command == 0x32:  # LC_BUILD_VERSION
            platform, minimum = struct.unpack_from("<II", data, offset + 8)
            if platform != 2:
                raise ValueError("Expected iPhoneOS device platform")
        elif command == 0x25:  # LC_VERSION_MIN_IPHONEOS
            minimum = struct.unpack_from("<I", data, offset + 8)[0]
        elif command == 0x1D:  # LC_CODE_SIGNATURE
            start, length = struct.unpack_from("<II", data, offset + 8)
            signed = length > 0 and start + length <= len(data)
        elif command in (0xC, 0x80000018, 0x8000001F):
            name_offset = struct.unpack_from("<I", data, offset + 8)[0]
            library = data[offset + name_offset:offset + size].split(b"\0", 1)[0].decode()
            if not library.startswith(("/System/Library/", "/usr/lib/")):
                raise ValueError(f"Non-system dynamic dependency must be bundled: {library}")
            libraries.append(library)
        offset += size
    if minimum is None:
        raise ValueError("Missing iPhoneOS deployment target")
    return {"minimum_ios": f"{minimum >> 16}.{(minimum >> 8) & 255}.{minimum & 255}",
            "has_code_signature": signed, "system_libraries": libraries}


def package(binary, bundle_id):
    binary_info = validate_binary(binary)
    if not (OUTPUT / "resource-manifest.json").is_file():
        raise FileNotFoundError("Run prepare_resources.py before packaging")
    app = ROOT / "build/ios-korean/Payload/EDOPro.app"
    if not app.resolve().is_relative_to(ROOT.resolve() / "build"):
        raise ValueError("App output must remain inside build/")
    if app.exists():
        shutil.rmtree(app)
    shutil.copytree(ROOT / "ios-assets", app, ignore=shutil.ignore_patterns("_CodeSignature"))
    shutil.copy2(binary, app / "ygopro")
    (app / "ygopro").chmod(0o755)
    shutil.copytree(OUTPUT, app / "EDOProResources")
    info = plistlib.loads((ROOT / "gframe/ios-Info.plist").read_bytes())
    info.update({
        "CFBundleExecutable": "ygopro",
        "CFBundleIdentifier": bundle_id,
        "CFBundleDisplayName": "EDOPro 한국어",
        "CFBundleDevelopmentRegion": "ko",
        "NSLocalNetworkUsageDescription": "같은 네트워크의 EDOPro 게임에 연결합니다.",
        "MinimumOSVersion": binary_info["minimum_ios"],
    })
    # The inherited plist contains Xcode/SDK labels unrelated to this compiler.
    for key in list(info):
        if key.startswith("DT"):
            del info[key]
    if not (app / "LaunchScreen.storyboardc").exists():
        info.pop("UILaunchStoryboardName", None)
        info["UILaunchScreen"] = {}
    (app / "Info.plist").write_bytes(plistlib.dumps(info))
    print(f"Staged app (signing still required): {app}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--bundle-id", default="dev.local.edopro.korean")
    args = parser.parse_args()
    package(args.binary, args.bundle_id)
