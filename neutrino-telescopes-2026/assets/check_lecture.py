"""Check the lecture assembly, local evidence and scientific presentation labels."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent.parent


def expand(path):
    def include(m):
        target=ROOT/m[1]
        if not target.is_file():raise AssertionError(f'Missing include: {target}')
        return expand(target) if target.suffix=='.qmd' else m[0]
    return re.sub(r'\{\{< include ([^ ]+) >\}\}',include,path.read_text())


def check():
    text=expand(ROOT/'lecture.qmd')
    headings=re.findall(r'^## .*?\{#([^}]+)\}',text,re.M)
    assert len(headings)==35, f'{1+len(headings)} slides, expected 36'
    assert len(set(headings))==len(headings),'Duplicate slide ID'
    required=['detector-response','acceleration-and-confinement','pion-production',
              'energy-budget','source-populations','icecube-diffuse-flux',
              'baikal-diffuse-flux','diffuse-spectral-structure','galactic-neutrinos',
              'gamma-budget','hidden-sources','ngc-1068','txs-0506','km3-230213a',
              'source-limits','source-sensitivity','global-observatories',
              'icecube-future','b-hunt','next-questions','what-we-need','conclusions']
    positions=[headings.index(h) for h in required]
    assert positions==sorted(positions),'Physical/observational sequence changed'
    assert headings[-1]=='conclusions'
    refs=re.findall(r'(?:src|poster)="((?:media|assets)/[^"]+)"',text)
    refs+=re.findall(r'!\[[^\]]*\]\(((?:media|assets)/[^)]+)\)',text)
    for rel in refs:assert (ROOT/rel).is_file(),f'Missing media: {rel}'
    for video in re.findall(r'<video\b[^>]*>',text):
        assert 'poster=' in video,'A film needs its static poster'
    assert not re.search(r'Visual slot|Animation slot|fake hit|not yet been generated|\b(?:Claude|ChatGPT|Codex)\b',text,re.I),'Production residue in lecture'
    items=json.loads((ROOT/'assets/evidence/figures.json').read_text())
    for item in items:
        output=ROOT/'media'/item['output']
        assert hashlib.sha256(output.read_bytes()).hexdigest()==item['output_sha256'],f'Publication artwork changed: {output}'
    # Guard the mixed-date and mixed-convention comparisons against silent conflation.
    assert 'Historical comparison' in text and '2022 neutrino fit' in text
    assert 'Blue IceCube points are preliminary' in text
    assert 'Per flavour, $\\nu+\\bar\\nu$' in text
    # Journal figures on white are redrawn in the lecture style; only these stay as originals.
    white_ok={'media/propagation/rzf_2dxsCT10nlo.png','media/diffuse/icecube-2013-veto.svg',
              'media/diffuse/icecube-glashow-event-2021.jpg','media/source-results/km3-energy-calibration.png',
              'media/observatories/km3net-arca-orca.png','media/observatories/baikal-gvd-2026.jpg',
              'media/observatories/p-one-configuration.jpg','media/observatories/trident-layout.png'}
    white=set(re.findall(r'!\[[^\]]*\]\(((?:media|assets)/[^)]+)\)\{[^}]*--media-bg: #fff',text))
    assert white<=white_ok,f'White figures not redrawn: {sorted(white-white_ok)}'
    print(f'{1+len(headings)} slides; {len(refs)} local references; {len(items)} publication figures; chronology and conventions checked')


if __name__=='__main__':check()
