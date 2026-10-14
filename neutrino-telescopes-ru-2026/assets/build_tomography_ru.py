"""Russian version of the tomography-contrast figure: the generator of the English lecture with Russian labels.

Physics, numbers and limitations are those of ../neutrino-telescopes-2026/assets/earth-transmission/build_tomography.py.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "neutrino-telescopes-2026" / "assets" / "earth-transmission"))
import build_tomography as tg  # noqa: E402

LABELS = {
    "energy": "{e:g} ТэВ · PREM",
    "homogeneous": "однородная Земля, {rho:.2f} г/см³",
    "core": "пути через\nядро",
    "zenith": "Зенитный угол, градусы",
    "survival": "Вероятность пройти (поглощение CC)",
    "log_energy": r"$\lg\,E_\nu$, ГэВ",
    "contrast": "(PREM − однородная) / однородная",
}

if __name__ == "__main__":
    tg.plot(labels=LABELS, out=HERE.parent / "media" / "figures", name="earth-tomography-contrast-ru", decimal_comma=True)
