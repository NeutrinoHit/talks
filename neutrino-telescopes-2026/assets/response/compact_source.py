"""Editable causal diagram of pion production and photon reprocessing."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE.parent.parent/'media/response/compact-source.svg'


def build():
    parts=['''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="640" viewBox="0 0 1600 640">
<title>Particle production and reprocessing in a compact source</title>
<desc>Schematic causal paths, without a calculated geometry or flux.</desc>
<rect width="1600" height="640" fill="#070d16"/>
<defs>''']
    colors={'proton':'#ffb052','nu':'#67ddf7','gamma':'#ffd477','muted':'#a0b5ca','target':'#aa9bef'}
    for k,c in colors.items():
        parts.append(f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="{c}"/></marker>')
    parts.append('</defs>')
    def text(x,y,t,k='muted',size=31,anchor='middle'):
        parts.append(f'<text x="{x}" y="{y}" fill="{colors[k]}" font-family="Arial, sans-serif" font-size="{size}" text-anchor="{anchor}">{t}</text>')
    def line(path,k):
        parts.append(f'<path d="{path}" fill="none" stroke="{colors[k]}" stroke-width="4" marker-end="url(#{k})"/>')
    parts.append('<path d="M1130 90V565" stroke="#506a84" stroke-width="2" stroke-dasharray="10 10"/>')
    text(1110,63,'Source boundary',size=25)
    text(200,260,'Energetic protons','proton')
    line('M140 300H450','proton')
    text(490,110,'Gas or photons','target')
    line('M490 140V280','target')
    parts.append('<circle cx="490" cy="300" r="10" fill="#f4f5ff"/>')
    text(475,355,'Pion production',size=30,anchor='end')
    line('M505 292L650 185H850','nu')
    text(765,145,'Charged-pion and muon decays','nu',28)
    line('M875 185H1400','nu')
    text(1375,145,'Neutrinos','nu',34)
    line('M505 311L670 410H915','gamma')
    text(750,375,'Neutral-pion decay','gamma',29)
    text(950,452,'Gamma rays','gamma',31,anchor='end')
    line('M970 410V535','gamma')
    text(1000,500,'Pairs',size=29,anchor='start')
    text(730,555,'Conversion and cooling',size=28)
    line('M980 550H1430','gamma')
    text(1325,507,'Reprocessed photons','gamma',31)
    text(310,605,'Schematic production and escape paths',size=25)
    parts.append('</svg>')
    return '\n'.join(parts)+'\n'


if __name__=='__main__':
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(build())
