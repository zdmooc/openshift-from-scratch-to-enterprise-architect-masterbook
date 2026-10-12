"""Editorial coverage tests for Volume 02, without external services."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOLUME = ROOT / "volumes/02-platform-internals"


class Volume02SourceTests(unittest.TestCase):
    def test_chapter_names_are_sequential(self):
        paths = sorted(VOLUME.glob("[0-9][0-9]-*.md"))
        self.assertEqual([p.name[:2] for p in paths],
                         [f"{i:02d}" for i in range(1, 13)])

    def test_chapters_cover_multiple_mechanisms_and_cite_sources(self):
        for path in sorted(VOLUME.glob("[0-9][0-9]-*.md")):
            s = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertGreaterEqual(len(re.findall(r"(?m)^## ", s)), 4)
                self.assertRegex(s, r"(?m)^# 0?[0-9]+")
                self.assertTrue(re.search(r"^## (Sources|Références)", s, re.M))
                self.assertIn("docs.redhat.com", s)
                self.assertIn("4.22", s)

    def test_editorial_status_is_not_draft(self):
        for path in sorted(VOLUME.glob("[0-9][0-9]-*.md")):
            s = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("ÉDITION 1.2", s.splitlines()[2])
                self.assertNotIn(" · DRAFT · ", s[:300])

    def test_glossary_has_no_detached_markdown_table_rows(self):
        source = (VOLUME / "GLOSSARY.md").read_text(encoding="utf-8")
        self.assertNotIn("\\n\\n| Machine API |", source)
        self.assertIn("| ClusterExtension |", source)
        self.assertIn("| Machine API |", source)

    def test_reader_notice_and_erratum_exist(self):
        self.assertTrue((ROOT / "docs/V02_1_2_READER_NOTICE.md").exists())
        self.assertTrue((ROOT / "docs/ERRATA_V01_V02_20261011.md").exists())

    def test_glossary_and_case_study(self):
        glossary = (VOLUME / "GLOSSARY.md").read_text(encoding="utf-8")
        self.assertIn("MachineConfigPool", glossary)
        case = ROOT / "case-studies/v02-control-plane/01-architecture-review-ha-upgrade.md"
        self.assertTrue(case.exists())

    def test_labs_have_explicit_proof_limits(self):
        for path in sorted((ROOT / "labs").glob("v02-*.md")):
            s = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertTrue(any(x in s for x in ("DOCUMENTED_NOT_RUN", "OFFLINE_TEST")))
        self.assertEqual(len(list((ROOT / "labs").glob("v02-*.md"))), 6)

    def test_quorum_code_does_not_shell_out(self):
        code = (ROOT / "examples/v02/quorum_model.py").read_text(encoding="utf-8")
        for forbidden in ("subprocess", "requests.", "os.system(", "kubectl", "oc apply", "etcdctl"):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()
