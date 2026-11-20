#!/usr/bin/env python3
"""Assemble and validate the Korean iOS runtime using pinned local sources."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "build/ios-korean/EDOProResources"
KOREAN = ROOT / "localization/korean"
DISTRIBUTION = ROOT / "porting/ios/distribution"
FONTS = ROOT / "porting/ios/fonts"
CACERT = ROOT / "porting/ios/certificates/cacert.pem"
FONT = "NotoSansCJKkr-Regular.otf"
FONT_COMMIT = "165c01b46ea533872e002e0785ff17e44f6d97d8"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def revision(path):
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def inspect_database(path):
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError(f"Corrupt database: {path}")
        names = [row[0] for row in db.execute("SELECT name FROM texts")]
        # Language packs are loaded by LoadLocaleDB, never as gameplay rules.
        return {
            "cards": len(names),
            "korean_names": sum(bool(re.search(r"[가-힣]", name)) for name in names),
            "sha256": sha256(path),
        }


def font_codepoints(path):
    """Read Unicode cmap format 4/12 without a third-party Python dependency."""
    data = path.read_bytes()
    if data[:4] not in (b"OTTO", b"\x00\x01\x00\x00"):
        raise ValueError("Expected an OpenType or TrueType font")
    u16 = lambda offset: struct.unpack_from(">H", data, offset)[0]
    u32 = lambda offset: struct.unpack_from(">I", data, offset)[0]
    cmap = None
    for i in range(u16(4)):
        pos = 12 + 16 * i
        if data[pos:pos + 4] == b"cmap":
            cmap = u32(pos + 8)
            break
    if cmap is None:
        raise ValueError("Missing font cmap")
    points = set()
    for i in range(u16(cmap + 2)):
        pos = cmap + 4 + 8 * i
        platform, encoding = u16(pos), u16(pos + 2)
        if platform != 0 and (platform != 3 or encoding not in (1, 10)):
            continue
        table = cmap + u32(pos + 4)
        kind = u16(table)
        if kind == 12:
            for j in range(u32(table + 12)):
                start, end, glyph = struct.unpack_from(">III", data, table + 16 + j * 12)
                points.update(range(start + (glyph == 0), end + 1))
        elif kind == 4:
            count = u16(table + 6) // 2
            ends = table + 14
            starts = ends + count * 2 + 2
            deltas = starts + count * 2
            offsets = deltas + count * 2
            for j in range(count):
                start, end = u16(starts + j * 2), u16(ends + j * 2)
                delta, offset = u16(deltas + j * 2), u16(offsets + j * 2)
                for point in range(start, min(end + 1, 0xFFFF)):
                    if offset:
                        glyph = u16(offsets + j * 2 + offset + 2 * (point - start))
                        glyph = (glyph + delta) & 0xFFFF if glyph else 0
                    else:
                        glyph = (point + delta) & 0xFFFF
                    if glyph:
                        points.add(point)
    return points


def ignored_files(directory, names):
    return [name for name in names if name.startswith(".git")]


def prepare():
    required = [DISTRIBUTION / "config/configs.json",
                DISTRIBUTION / "script/utility.lua",
                DISTRIBUTION / "expansions/cards.cdb",
                KOREAN / "cards.cdb", KOREAN / "strings.conf",
                FONTS / FONT, FONTS / "LICENSE", CACERT]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(f"Missing source: {path}. Initialize recursive submodules first.")
    databases = {p.name: inspect_database(p) for p in sorted(KOREAN.glob("*.cdb"))}
    if databases["cards.cdb"]["korean_names"] < 1000:
        raise ValueError("Korean card text is missing")
    if not re.search(r"!system \d+ .*?[가-힣]", (KOREAN / "strings.conf").read_text("utf-8-sig")):
        raise ValueError("Korean UI translation is missing")
    missing = set(range(0xAC00, 0xD7A4)) - font_codepoints(FONTS / FONT)
    if missing:
        raise ValueError(f"Font is missing {len(missing)} modern Hangul syllables")
    print("Korean databases, UI text and all 11,172 Hangul glyphs validated.", flush=True)

    # Only this generated directory may be replaced. Never remove source trees.
    expected = (ROOT / "build/ios-korean/EDOProResources").resolve()
    if OUTPUT.resolve() != expected or not expected.is_relative_to(ROOT.resolve() / "build"):
        raise ValueError("Unexpected output path")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    for name in ("config", "deck", "expansions", "fonts", "lflists", "puzzles", "script", "skin", "sound", "textures"):
        print(f"Copying {name}...", flush=True)
        shutil.copytree(DISTRIBUTION / name, OUTPUT / name, ignore=ignored_files)
    for name in ("pics", "replay"):
        (OUTPUT / name).mkdir(exist_ok=True)

    language = OUTPUT / "config/languages/Korean"
    language.mkdir(parents=True, exist_ok=True)
    for path in [*KOREAN.glob("*.cdb"), KOREAN / "strings.conf", KOREAN / "LICENSE"]:
        shutil.copy2(path, language / path.name)
    shutil.copy2(FONTS / FONT, OUTPUT / "fonts" / FONT)
    shutil.copy2(FONTS / "LICENSE", OUTPUT / "fonts/NotoSansCJKkr-OFL.txt")
    shutil.copy2(DISTRIBUTION / "LICENSE", OUTPUT / "LICENSE-Distribution.txt")
    shutil.copy2(ROOT / "COPYING", OUTPUT / "LICENSE-EDOPro.txt")
    shutil.copy2(CACERT, OUTPUT / "cacert.pem")

    config = OUTPUT / "config/system.conf"
    settings = {"language": "Korean", "textfont": f"fonts/{FONT} 12", "numfont": f"fonts/{FONT}"}
    lines = config.read_text("utf-8-sig").splitlines()
    lines = [line for line in lines if line.split("=", 1)[0].strip() not in settings]
    config.write_text("\n".join(lines + [f"{key} = {value}" for key, value in settings.items()]) + "\n", "utf-8")
    config = OUTPUT / "config/user_configs.json"
    user = json.loads(config.read_text("utf-8-sig"))
    # Same public image endpoints embedded in the official desktop client.
    # EDOPro caches downloaded files in Documents/pics.
    user["urls"] = [
        {"url": "https://pics.projectignis.org:2096/pics/{}.jpg", "type": "pic"},
        {"url": "https://pics.projectignis.org:2096/field/{}.png", "type": "field"},
        {"url": "https://pics.projectignis.org:2096/pics/cover/{}.jpg", "type": "cover"},
    ]
    user.setdefault("repos", []).append({
        "url": "https://github.com/Team-AllYGOPro/edopro-korean.git",
        "repo_name": "Korean translation (Team-AllYGOPro)",
        "repo_path": "./repositories/korean",
        "data_path": ".", "is_language": True, "language": "Korean",
        "should_read": True, "should_update": True,
    })
    config.write_text(json.dumps(user, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print("Recording source revisions and packaged file hashes...", flush=True)
    manifest = {
        "edopro": revision(ROOT), "korean": revision(KOREAN),
        "distribution": revision(DISTRIBUTION),
        "scripts": revision(DISTRIBUTION / "script"),
        "base_database": revision(DISTRIBUTION / "expansions"),
        "font": {"source": "https://github.com/notofonts/noto-cjk", "commit": FONT_COMMIT,
                 "sha256": sha256(FONTS / FONT), "hangul_syllables": 11172},
        "korean_databases": databases,
        "files": {str(p.relative_to(OUTPUT)).replace("\\", "/"): sha256(p)
                  for p in sorted(OUTPUT.rglob("*")) if p.is_file()},
    }
    (OUTPUT / "resource-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(f"Prepared {len(manifest['files'])} files in {OUTPUT}")
    print(json.dumps({"databases": databases, "font_hangul_syllables": 11172}, ensure_ascii=False, indent=2))
    return OUTPUT


if __name__ == "__main__":
    prepare()
