"""Compile Volume 02 PDF from committed Markdown, no Kubernetes access.

Requires the exact dependencies from the Volume 01 publisher:
mistune 3.2.0, weasyprint 68.0, pypdf 6.3.0 (inspection).
"""
from __future__ import annotations

import argparse
import html
import os
from pathlib import Path

import mistune
from weasyprint import HTML

# Import only pure typesetting helpers from the already-reviewed Volume 01 builder.
import build_volume01_pdf as original_book
from build_volume01_pdf import CSS, chapter_title, render_source as base_render_source
# Pin source links to the exact GitHub commit of a released edition.
SOURCE_REF = os.getenv("GITHUB_SHA", "main")
original_book.BASE = (
    "https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/"
    f"blob/{SOURCE_REF}/"
)
import re
from urllib.parse import urljoin


def render_source(path: Path, identifier: str, markdown: mistune.Markdown, annex: bool) -> str:
    """Resolve authored Markdown vector images relative to their source files."""
    rendered = base_render_source(path, identifier, markdown, annex)
    directory = path.parent.resolve().as_uri() + "/"
    def resolve(match: re.Match[str]) -> str:
        src = match.group(1)
        if src.startswith(("http://", "https://", "file://", "data:")):
            return match.group(0)
        absolute = urljoin(directory, src)
        return 'src="' + absolute + '"'
    return re.sub(r'src="([^"]+)"', resolve, rendered)


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = sorted((ROOT / "volumes/02-platform-internals").glob("[0-9][0-9]-*.md"))
LABS = sorted((ROOT / "labs").glob("v02-[0-9][0-9]-*.md"))
CASES = sorted((ROOT / "case-studies/v02-control-plane").glob("[0-9][0-9]-*.md"))
GLOSSARY = ROOT / "volumes/02-platform-internals/GLOSSARY.md"
READER_NOTICE = ROOT / "docs/V02_1_2_READER_NOTICE.md"
ERRATUM = ROOT / "docs/ERRATA_V01_V02_20261011.md"


def make_pdf(out: Path) -> Path:
    if len(CHAPTERS) != 12 or len(LABS) != 6 or len(CASES) != 1 or not GLOSSARY.exists() or not READER_NOTICE.exists() or not ERRATUM.exists():
        raise RuntimeError("Expected 12 chapters, 6 labs, 1 case study and glossary")
    markdown = mistune.create_markdown(plugins=["table", "strikethrough", "url"])
    sections = (
        [("Chapitre", i, f"chapter-{i:02d}", p, False) for i, p in enumerate(CHAPTERS, 1)]
        + [("Étude de cas", i, f"case-{i:02d}", p, True) for i, p in enumerate(CASES, 1)]
        + [("Atelier", i, f"lab-{i:02d}", p, True) for i, p in enumerate(LABS, 1)]
        + [("Avis au lecteur", 1, "reader-notice", READER_NOTICE, True)]
        + [("Erratum", 1, "erratum", ERRATUM, True)]
        + [("Glossaire", 1, "glossary", GLOSSARY, True)]
    )
    toc = []
    for typ, number, identifier, path, annex in sections:
        title = html.escape(chapter_title(path))
        toc.append(f'<li><span class="num">{number:02d}</span><a href="#{identifier}">{title}</a></li>')

    cover = """<section class="cover">
      <div class="kicker">OPENSHIFT MASTERBOOK · VOLUME 02</div>
      <h1>Architecture interne<br>du control plane<br>OpenShift</h1>
      <div class="subtitle">etcd · Scheduler · CVO · MCO<br>
      RHCOS · CRI-O · Admission · N3</div>
      <div class="copyright">Zidane Djamal<br>
      Édition documentaire 1.2 · 12 octobre 2026<br>
      Étude indépendante, non affiliée à Red Hat</div>
    </section>"""
    front = """<section class="front">
      <h2>Avant-propos</h2>
      <p>Ce livre décrit les composants internes du plan de contrôle d'OpenShift Container Platform 4.22, sur Kubernetes 1.35, et leurs implications pour l'architecture de plateforme et le support N3.</p>
      <p>Douze chapitres, six laboratoires, un dossier d'architecture et un glossaire. Il s'agit d'une édition pédagogique consolidée, dont les cas et procédures de résolution restent documentaires.</p>
      <div class="legal"><b>Propriété intellectuelle.</b> © 2026 Zidane Djamal pour les contenus originaux, sous réserve des droits des tiers. Tous droits réservés en l'absence d'une licence explicite. Red Hat et OpenShift sont des marques de leurs propriétaires. Ce document n'est pas un produit officiel Red Hat.</div>
      <p><b>Sécurité :</b> aucune procédure de restauration, suppression de membre etcd, panne forcée, modification SCC/CVO/MCO ou upgrade n'a été exécutée sur un cluster.</p>
      <p><b>Preuve :</b> les tests Python valident des modèles pédagogiques hors cluster (quorum, filtrage du scheduler et contrat de conversion CRD). Ils ne démontrent ni consensus Raft réel, ni scheduling par kube-scheduler, ni admission/conversion Kubernetes effective, ni haute disponibilité ou PRA.</p>
      <p><b>Mise en page :</b> quatre schémas SVG originaux sont rendus; les autres schémas Mermaid restent en source lisible lorsqu'une conversion graphique n'est pas disponible; le Markdown versionné reste la source de référence.</p>
    </section>"""
    toc_html = '<section class="front"><h2>Sommaire du Volume 02</h2><ol class="toc-list">' + "".join(toc) + '</ol></section>'
    body = "".join(render_source(p, ident, markdown, annex)
                   for _, _, ident, p, annex in sections)
    style = CSS.replace("VOLUME 01", "VOLUME 02") + "\n.chapter img { display:block; width:100%; height:auto; max-height:195px; margin:6mm auto; }"
    doc = ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
           '<title>OpenShift Masterbook Volume 02 - Edition 1.2</title><style>' + style +
           '</style></head><body>' + cover + front + toc_html + body + '</body></html>')
    out.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=doc, base_url=ROOT.as_uri() + "/").write_pdf(out)
    if out.stat().st_size < 100000:
        raise RuntimeError("PDF size unexpectedly small")
    print(f"PDF: {out}, {out.stat().st_size:,} bytes")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the OpenShift V02 PDF")
    parser.add_argument("--out", default="dist/OpenShift_Masterbook_Volume_02_Edition_1_2_Zidane_Djamal_2026.pdf")
    opts = parser.parse_args()
    make_pdf(ROOT / opts.out)
