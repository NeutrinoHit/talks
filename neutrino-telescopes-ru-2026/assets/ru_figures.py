"""Russian versions of the map and prospects figures of the lecture neutrino-telescopes-2026.

The English generators stay the single source of the numbers and the geometry: this script reads their source,
replaces the visible English labels with Russian ones and writes the figures into media/figures of this lecture.
A label that is not found in the generator is an error, so a changed generator cannot silently produce English text.
"""
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
EN = HERE.parents[1] / "neutrino-telescopes-2026" / "assets"
OUT = HERE.parent / "media" / "figures"

PROSPECTS = {
    '"First HUNT prototype string in Lake Baikal"': '"Первая прототипная гирлянда HUNT на Байкале"',
    '"12 modules with 20-inch photomultipliers"': '"12 модулей с 20-дюймовыми ФЭУ"',
    '"Lake Baikal: full-scale string with 20-inch modules"': '"Байкал: полноразмерная гирлянда с 20-дюймовыми модулями"',
    '"South China Sea: 4 prototype detector units"': '"Южно-Китайское море: 4 прототипа детекторных узлов"',
    '"+ LED calibration unit, 1600 m"': '"+ светодиодный калибратор, 1600 м"',
    '"Baikal-GVD: 16 clusters"': '"Baikal-GVD: 16 кластеров"',
    '"effective volume ≈ 0.8 km³"': '"эффективный объём ≈ 0,8 км³"',
    '"Baikal-GVD: ≈ 1 km³"': '"Baikal-GVD: ≈ 1 км³"',
    '"B-HUNT: ≈ 30 km³ in Lake Baikal"': '"B-HUNT: ≈ 30 км³ в Байкале"',
    '"Baikal-GVD Collaboration with IHEP (Beijing)"': '"коллаборация Baikal-GVD и IHEP (Пекин)"',
    '"1 km³", "Baikal-GVD goal"': '"1 км³", "цель Baikal-GVD"',
    '"30 km³", "B-HUNT · Russia + China"': '"30 км³", "B-HUNT · Россия + Китай"',
    '"Cubes drawn to volume scale"': '"Объёмы кубов в масштабе"',
    '("Programme", "hunt", ["ФНАФЧ: neutrino physics", "and particle astrophysics", "courses · seminars", "Baikal school"])':
        '("Программа", "hunt", ["ФНАФЧ: физика нейтрино", "и астрофизика частиц", "курсы · семинары", "Байкальская школа", "Баксанская школа"])',
    '("People", "gvd", ["students become", "researchers", "and lecturers"])':
        '("Люди", "gvd", ["студенты становятся", "исследователями", "и преподавателями"])',
    '("Results", "nu", ["data analysis", "e.g. the Milky Way", "in Baikal-GVD data;", "first author: a graduate", "of the programme"])':
        '("Результаты", "nu", ["анализ данных:", "например, Млечный Путь", "в данных Baikal-GVD;", "первый автор —", "выпускник программы"])',
    '("Next experiment", "cr", ["B-HUNT", "next-generation", "telescope", "Russia + China"])':
        '("Следующий эксперимент", "cr", ["B-HUNT", "телескоп", "нового поколения", "Россия + Китай"])',
    r'"Measured cosmic\nneutrino spectrum"': r'"Измеренный спектр\nкосмических нейтрино"',
    '"Seyfert galaxies beyond NGC 1068"': '"Другие сейфертовские галактики"',
    '"Break: pp or pγ?"': '"Излом: pp или pγ?"',
    '"Milky Way and PeVatrons"': '"Млечный Путь и певатроны"',
    r'"Glashow resonance:\nflavour and pp/pγ"': r'"Резонанс Глэшоу:\nаромат и pp/pγ"',
    '"Cross section from Earth absorption"': '"Сечение по поглощению в Земле"',
    r'"KM3-230213A:\nsource or cosmogenic?"': r'"KM3-230213A:\nисточник или космогенное?"',
    '"Any energy: transients through alerts · new physics"': '"Любые энергии: вспышки · новая физика"',
    '["1 TeV", "10 TeV", "100 TeV", "1 PeV", "10 PeV", "100 PeV", "1 EeV"]':
        '["1 ТэВ", "10 ТэВ", "100 ТэВ", "1 ПэВ", "10 ПэВ", "100 ПэВ", "1 ЭэВ"]',
    '"Neutrino energy"': '"Энергия нейтрино"',
    '"Galactic Centre"': '"Центр Галактики"',
    r'"Milky Way:\ndiffuse neutrinos"': r'"Млечный Путь:\nдиффузные нейтрино"',
    r'"NGC 1068\nSeyfert galaxies"': r'"NGC 1068\nсейфертовские\nгалактики"',
    r'"TXS 0506+056\nblazars"': r'"TXS 0506+056\nблазары"',
    r'"KM3-230213A\norigin open"': r'"KM3-230213A\nпроисхождение неясно"',
    '"Most of the flux: many faint sources, not yet resolved"': '"Большая часть потока: множество слабых источников, пока не разрешённых"',
}

GLOBAL_SKY = {
    'label="Operating arrays"': 'label="Работающие телескопы"',
    'label="Next-generation projects"': 'label="Проекты нового поколения"',
}

BUDGET = {
    '"Waxman–Bahcall bound"': '"Предел Ваксмана — Бакала"',
    r'r"$\gamma$ rays"': r'r"$\gamma$-кванты"',
    '"Fermi-LAT, isotropic background"': '"Fermi-LAT, изотропный фон"',
    r'r"$\nu$ per flavour"': r'r"$\nu$, один аромат"',
    '"Cosmic rays"': '"Космические лучи"',
    '"Pierre Auger Observatory"': '"Обсерватория Пьера Оже"',
    '["1 GeV", "1 TeV", "1 PeV", "1 EeV"]': '["1 ГэВ", "1 ТэВ", "1 ПэВ", "1 ЭэВ"]',
    '"Particle energy"': '"Энергия частицы"',
    r'r"$E^2\Phi$  [GeV cm$^{-2}$ s$^{-1}$ sr$^{-1}$]"': r'r"$E^2\Phi$, ГэВ см$^{-2}$ с$^{-1}$ ср$^{-1}$"',
}


def load(path: Path, mapping: dict, name: str) -> types.ModuleType:
    src = path.read_text()
    for en, ru in mapping.items():
        if en not in src:
            raise SystemExit(f"{path.name}: label not found: {en}")
        src = src.replace(en, ru)
    mod = types.ModuleType(name)
    mod.__file__ = str(path)                      # data, configs and imports resolve next to the English generator
    sys.modules[name] = mod
    exec(compile(src, str(path), "exec"), mod.__dict__)
    mod.OUT = OUT
    return mod


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pr = load(EN / "prospects" / "build_prospects.py", PROSPECTS, "ru_prospects")
    (OUT / "gvd-to-bhunt.svg").write_text(pr.gvd_to_bhunt())
    (OUT / "people-chain.svg").write_text(pr.people_chain())
    pr.discovery_map()
    pr.sources_sky()
    gs = load(EN / "global-sky" / "build_figures.py", GLOBAL_SKY, "ru_global_sky")
    gs.world_map(gs.setup())
    eb = load(EN / "theory" / "build_energy_budget.py", BUDGET, "ru_energy_budget")
    eb.build()
    for extra in ("energy-budget.csv",):
        (OUT / extra).unlink(missing_ok=True)
    for name in ("discovery-map", "sources-sky", "global-sites", "energy-budget"):
        (OUT / f"{name}.png").unlink(missing_ok=True)   # the lecture uses the SVG files; other figures stay
    print("\n".join(str(p.relative_to(HERE.parent)) for p in sorted(OUT.iterdir())))


if __name__ == "__main__":
    build()
