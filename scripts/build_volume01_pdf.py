"""Build the self-contained French Volume 01 PDF directly from versioned Markdown.

Deps: pip install mistune==3.2.0 weasyprint==68.0 pypdf==6.3.0
No network access; does not read Kubernetes credentials or touch CRC.
"""
from __future__ import annotations

import argparse
import html
import posixpath
import re
from pathlib import Path
from urllib.parse import quote

import mistune
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/blob/main/"
CHAPTERS = sorted((ROOT / "volumes/01-foundations").glob("[0-9][0-9]-*.md"))
LABS = sorted((ROOT / "labs").glob("[0-9][0-9]-*.md"))
CASES = sorted((ROOT / "case-studies/v01-banking-api").glob("[0-9][0-9]-*.md"))
GLOSSARY = ROOT / "volumes/01-foundations/GLOSSARY.md"
CSS = r"""
@page { size: A4; margin: 18mm 17.5mm 18mm 18.5mm;
    @bottom-center { content: "OPENSHIFT MASTERBOOK  •  VOLUME 01  |  " counter(page);
        color: #617883; font-size: 7.3pt; }
    @top-right { content: string(chapter-title); font-size: 7pt; color: #84959d; }
}
@page cover { margin: 0; @top-right { content: none; } @bottom-center { content: none; } }
html { font-family: "DejaVu Sans", "Noto Sans", sans-serif; color: #203745; }
body { font-size: 9.35pt; line-height: 1.5; }
.cover { page: cover; page-break-after: always; padding: 58mm 24mm 20mm;
    min-height: 190mm; background: #102e40; color: white; }
.cover .kicker { color: #6ad0c7; font-size: 12pt; letter-spacing: .08em; }
.cover h1 { font-size: 35pt; line-height: 1.17; color: #fff; margin: 13mm 0 8mm; }
.cover .subtitle { font-size: 15pt; color: #d5e4ea; }
.cover .copyright { margin-top: 42mm; font-size: 9pt; color: #c7dce4; }
.front { page-break-after: always; }
.front h2 { font-size: 22pt; margin: 0 0 6mm; color: #123a4b; }
.toc-list { list-style: none; margin: 4mm 0; padding: 0; }
.toc-list li { border-bottom: 1px solid #e4ebee; padding: 2.5mm 0; break-inside: avoid; }
.toc-list .num { display:inline-block; width:14mm; color:#127d83; font-weight:700; }
a { color: #14768a; text-decoration:none; }
h1 { color: #123e4e; font-size: 20.5pt; line-height: 1.2; string-set: chapter-title content(text); }
h2 { color: #19727a; font-size: 13.5pt; margin: 7mm 0 3mm; break-after: avoid; }
h3 { color: #315563; font-size: 11.1pt; margin: 5mm 0 2mm; break-after: avoid; }
h4 { color: #57707b; font-size: 10pt; margin: 4mm 0 2mm; break-after: avoid; }
.chapter { page-break-before:always; }
.chapter > h1 { border-bottom: 2px solid #62bdb6; padding-bottom:5mm; margin-top:0; }
.chapter > p:first-of-type { color: #728b96; font-size: 8.4pt; }
.section-annex > h1 { color: #445e6c; border-color: #b8cbd1; }
p { margin: 2.2mm 0 3.1mm; }
li { margin-bottom:1.3mm; }
ul,ol { padding-left: 7mm; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: .84em; overflow-wrap:anywhere; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; word-break:break-word; border-radius:4pt;
    background: #f0f4f6; padding:9pt 10pt; line-height:1.34; font-size:7.05pt;
    border-left:2.5pt solid #58a5a6; }
pre code { font-size: 7.05pt; }
pre.mermaid-source { border-color:#be9f5d; background:#faf8f1; }
pre.mermaid-source::before { content:"Schéma source Mermaid"; display:block;
    color:#8d7241; font-size:7.4pt; margin-bottom:4pt; }
table { width:100%; border-collapse:collapse; font-size:7.8pt; margin:3.5mm 0 5mm; }
thead { display:table-header-group; background:#e5eff1; }
tr { break-inside:avoid; }
th,td { border:.5pt solid #d5e0e4; padding:5pt 5.5pt; vertical-align:top;
    text-align:left; overflow-wrap:anywhere; }
th { color:#315c6b; font-weight:700; }
blockquote { margin:4mm 0; border-left:3pt solid #55adaa;
    background:#f1f8f8; padding:7pt 11pt; }
hr { border:0; border-bottom:.5pt solid #d4e0e3; margin:7mm 0; }
strong { color:#123d4b; }
.legal { padding:5mm; border:1px solid #d4e0e3; color:#4e6b75; background:#f5f8f9; font-size:8.3pt; }
.annex-divider { page-break-before:always; }
"""


def source_link_rewrite(markdown: str, path: Path) -> str:
    """Use canonical GitHub source URLs instead of broken relative PDF file targets."""
    parent = path.relative_to(ROOT).parent.as_posix()

    def convert(m: re.Match[str]) -> str:
        label, target = m.group(1), m.group(2)
        if target.startswith(("https://", "http://", "mailto:", "#")):
            return m.group(0)
        rel = posixpath.normpath(posixpath.join(parent, target))
        return "[" + label + "](" + BASE + quote(rel, safe="/#-._") + ")"

    return re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", convert, markdown)


def chapter_title(path: Path) -> str:
    match = re.search(r"^#\s+(.+)$", path.read_text(encoding="utf-8"), re.M)
    if not match:
        raise ValueError("No H1 in " + str(path))
    return match.group(1).strip()


def render_source(path: Path, section_id: str, md: mistune.Markdown, annex: bool) -> str:
    source = source_link_rewrite(path.read_text(encoding="utf-8"), path)
    fragment = md(source)
    fragment = re.sub(r'<pre><code class="language-mermaid">',
                      '<pre class="mermaid-source"><code>', fragment)
    class_name = "chapter section-annex" if annex else "chapter"
    return '<section id="' + section_id + '" class="' + class_name + '">' + fragment + '</section>'


def make_pdf(out: Path) -> Path:
    if len(CHAPTERS) != 13 or len(LABS) != 8 or len(CASES) != 3 or not GLOSSARY.exists():
        raise ValueError("Volume 01 coverage incomplete: need 13 chapters, 8 labs, 3 studies and glossary")
    md = mistune.create_markdown(plugins=["table", "strikethrough", "url"])
    sections = (
        [("CHAPITRES", i, f"chapter-{i:02d}", p, False) for i, p in enumerate(CHAPTERS, 1)]
        + [("ÉTUDES DE CAS", i, f"case-{i:02d}", p, True) for i, p in enumerate(CASES, 1)]
        + [("LABORATOIRES", i, f"lab-{i:02d}", p, True) for i, p in enumerate(LABS, 1)]
        + [("GLOSSAIRE", 1, "glossary", GLOSSARY, True)]
    )
    toc_rows = []
    for kind, number, section_id, path, _ in sections:
        title = html.escape(chapter_title(path))
        toc_rows.append(
            f'<li><span class="num">{number:02d}</span>'
            f'<a href="#{section_id}">{title}</a></li>'
        )
    cover = """<section class="cover">
      <div class="kicker">OPENSHIFT MASTERBOOK · VOLUME 01</div>
      <h1>Des fondations Linux<br>à l'architecture<br>OpenShift</h1>
      <div class="subtitle">Kubernetes · Conteneurs · Sécurité<br>
      Exploitation · Architecture d'entreprise</div>
      <div class="copyright">Zidane Djamal<br>
      Édition 1.0 · 11 octobre 2026<br>
      Référence pédagogique indépendante de Red Hat</div>
    </section>"""
    front = """<section class="front">
      <h2>Avant-propos et périmètre</h2>
      <p>Une édition originale, indépendante, reposant sur une base documentaire OpenShift Container Platform 4.22 et les concepts officiels Kubernetes/OCI.</p>
      <p>13 chapitres, 3 études d'architecture, 8 laboratoires et un glossaire. Les laboratoires documentés non exécutés restent explicitement distincts des tests hors cluster.</p>
      <div class="legal"><b>Copyright et marques.</b> © 2026 Zidane Djamal pour ses textes et exemples originaux, sous réserve des droits des tiers. Tous droits réservés tant qu'aucune licence définitive n'est accordée. OpenShift, Red Hat et les marques associées appartiennent à leurs titulaires respectifs. Ce document n'est pas une publication officielle Red Hat.</div>
      <p><b>Important :</b> les exemples utilisant des domaines <code>.invalid</code> ou des digests fictifs ne sont pas déployables. Ne pas appliquer des NetworkPolicies ou manifests à un cluster partagé sans autorisation et validation.</p>
      <p><b>Validation :</b> la vérification automatisée du contenu ne prouve ni compatibilité sur tous les clusters, ni disponibilité, ni conformité réglementaire, ni tests de haute disponibilité ou PRA.</p>
    </section>"""
    toc = '<section class="front"><h2>Table des matières</h2><ol class="toc-list">' + "".join(toc_rows) + '</ol></section>'
    body = "".join(render_source(path, section_id, md, annex) for _,_,section_id,path,annex in sections)
    full = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>OpenShift Masterbook - Volume 01</title><style>' + CSS + '</style></head><body>' + cover + front + toc + body + '</body></html>'
    out.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=full, base_url=ROOT.as_uri() + "/").write_pdf(out)
    if out.stat().st_size < 30000:
        raise ValueError("Suspiciously small PDF file")
    print(f"PDF: {out} ({out.stat().st_size:,} bytes)")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="dist/OpenShift_Masterbook_Volume_01_Zidane_Djamal_2026.pdf")
    args = parser.parse_args()
    make_pdf(ROOT / args.out)
