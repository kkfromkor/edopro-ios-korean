import json
from pathlib import Path
import sqlite3
import ssl
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_resources import OUTPUT, KOREAN, FONT, sha256
from package_app import validate_binary


class KoreanResourceIntegrationTests(unittest.TestCase):
    """Validate the real assembled runtime, not placeholder fixtures."""

    def test_every_packaged_file_matches_manifest(self):
        manifest = json.loads((OUTPUT / "resource-manifest.json").read_text("utf-8"))
        self.assertGreater(len(manifest["files"]), 1000)
        for name, expected in manifest["files"].items():
            with self.subTest(file=name):
                self.assertEqual(sha256(OUTPUT / name), expected)
        self.assertFalse(any(p.name == ".git" for p in OUTPUT.rglob("*")))

    def test_korean_card_and_ui_are_available_offline(self):
        language = OUTPUT / "config/languages/Korean"
        with sqlite3.connect((language / "cards.cdb").resolve().as_uri() + "?mode=ro", uri=True) as db:
            name = db.execute("SELECT name FROM texts WHERE id = 89631139").fetchone()[0]
            self.assertIn("푸른", name)
        self.assertIn("일반 소환", (language / "strings.conf").read_text("utf-8-sig"))
        for db in KOREAN.glob("*.cdb"):
            self.assertEqual(sha256(db), sha256(language / db.name))

    def test_configuration_keeps_translation_separate_from_gameplay(self):
        config = OUTPUT / "config"
        settings = (config / "system.conf").read_text("utf-8")
        self.assertIn("language = Korean\n", settings)
        self.assertIn("dpi_scale = 2\n", settings)
        self.assertIn("ios_layout_version = 1\n", settings)
        self.assertIn(f"textfont = fonts/{FONT} 12\n", settings)
        self.assertTrue((OUTPUT / "fonts" / FONT).is_file())
        user = json.loads((config / "user_configs.json").read_text("utf-8"))
        repo = next(r for r in user["repos"] if r.get("language") == "Korean")
        self.assertTrue(repo["is_language"])
        self.assertEqual(repo["data_path"], ".")
        self.assertTrue((OUTPUT / "script/utility.lua").is_file())
        self.assertTrue((OUTPUT / "expansions/cards.cdb").is_file())

    def test_https_and_image_sources_are_configured(self):
        context = ssl.create_default_context(cafile=str(OUTPUT / "cacert.pem"))
        self.assertGreater(context.cert_store_stats()["x509_ca"], 50)
        user = json.loads((OUTPUT / "config/user_configs.json").read_text("utf-8"))
        picture = next(source["url"] for source in user["urls"] if source["type"] == "pic")
        self.assertEqual(picture.format(89631139), "https://pics.projectignis.org:2096/pics/89631139.jpg")

    def test_packager_rejects_non_executable_input(self):
        with self.assertRaises(ValueError):
            validate_binary(OUTPUT / "fonts" / FONT)


if __name__ == "__main__":
    unittest.main()
