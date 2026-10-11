"""Source and publication checks, no cluster usage."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Volume01SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chapters = sorted((ROOT / "volumes/01-foundations").glob("[0-9][0-9]-*.md"))
        cls.labs = sorted((ROOT / "labs").glob("[0-9][0-9]-*.md"))
        cls.cases = sorted((ROOT / "case-studies/v01-banking-api").glob("[0-9][0-9]-*.md"))

    def test_thirteen_chapters_in_sequence(self):
        self.assertEqual(
            [p.name[:2] for p in self.chapters],
            [f"{i:02d}" for i in range(1, 14)],
        )

    def test_eight_labs_three_case_studies(self):
        self.assertEqual(len(self.labs), 8)
        self.assertEqual(len(self.cases), 3)

    def test_each_chapter_has_headings_and_sources(self):
        for p in self.chapters:
            s = p.read_text(encoding="utf-8")
            with self.subTest(p=p.name):
                self.assertTrue(s.startswith("# "))
                self.assertRegex(s, r"(?i)## (références|sources)")
                self.assertGreaterEqual(len(re.findall(r"(?m)^## ", s)), 3)

    def test_chapters_do_not_claim_new_crc_proof(self):
        # Each chapter distinguishes evidence status from runtime proof.
        for p in self.chapters:
            s = p.read_text(encoding="utf-8")
            with self.subTest(p=p.name):
                self.assertTrue(re.search(r"(EDITION_1_CONTENT_COMPLETE|DRAFT|édition|Statut)", s, re.I))
                self.assertTrue(re.search(r"(preuv|test|vérifi|laboratoire|source)", s, re.I))

    def test_bib_has_documentation(self):
        s = (ROOT / "docs/SOURCES.md").read_text(encoding="utf-8")
        self.assertIn("docs.redhat.com", s)
        self.assertIn("kubernetes.io", s)
        self.assertIn("opencontainers.org", s)


if __name__ == "__main__":
    unittest.main()
