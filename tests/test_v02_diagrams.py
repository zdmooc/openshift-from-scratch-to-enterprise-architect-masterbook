"""Check authored vector figures as editable SVG and Markdown references.

No graphics rendering or network access. Rendering is independently verified in PDF CI.
"""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
VOLUME = ROOT / "volumes/02-platform-internals"
DIAGRAMS = {
    "api-control-plane-flow.svg",
    "etcd-quorum-zones.svg",
    "mco-rollout.svg",
    "crd-conversion.svg",
}


class DiagramsV02Tests(unittest.TestCase):
    def test_four_original_figures_present(self):
        found = {p.name for p in (VOLUME / "figures").glob("*.svg")}
        self.assertEqual(found, DIAGRAMS)

    def test_svg_parseable(self):
        for p in sorted((VOLUME / "figures").glob("*.svg")):
            with self.subTest(p=p.name):
                root = ET.parse(p).getroot()
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertTrue(root.attrib.get("viewBox"))
                self.assertTrue(root.attrib.get("role") == "img")

    def test_each_svg_has_text_and_shapes(self):
        for p in sorted((VOLUME / "figures").glob("*.svg")):
            with self.subTest(p=p.name):
                src = p.read_text(encoding="utf-8")
                self.assertGreaterEqual(src.count("<text "), 3)
                self.assertGreaterEqual(src.count("<rect "), 2)
                self.assertIn("<title>", src)

    def test_svg_has_no_external_assets_or_scripts(self):
        for p in sorted((VOLUME / "figures").glob("*.svg")):
            src = p.read_text(encoding="utf-8")
            with self.subTest(p=p.name):
                self.assertNotIn("<script", src)
                self.assertNotIn("<foreignObject", src)
                self.assertNotIn("http://www.w3.org/1999/xlink", src)
                self.assertNotIn("data:image/", src)

    def test_authored_markdown_figure_links_exist(self):
        links = []
        for path in sorted(VOLUME.glob("[0-9][0-9]-*.md")):
            source = path.read_text(encoding="utf-8")
            for match in re.finditer(r"!\[[^\]]+\]\((figures/[^)]+\.svg)\)", source):
                target = path.parent / match.group(1)
                self.assertTrue(target.is_file(), f"Broken figure: {path} -> {target}")
                links.append(target.name)
        self.assertEqual(set(links), DIAGRAMS)

    def test_pdf_builder_resolves_svg_from_chapter_dir(self):
        code = (ROOT / "scripts/build_volume02_pdf.py").read_text(encoding="utf-8")
        self.assertIn("path.parent.resolve().as_uri()", code)
        self.assertIn("urljoin(directory, src)", code)


if __name__ == "__main__":
    unittest.main()
