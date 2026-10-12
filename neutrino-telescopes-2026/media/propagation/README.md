# Earth transmission source figure

The active slide now uses the user-supplied original `rzf_2dxsCT10nlo.png`
from Downloads (8 October 2026). It is a 6400 × 4800 RGBA PNG. A read-only
pixel comparison confirmed that its RGB channels are identical to the
dissertation extraction below. Original transparency is retained; the slide's
shared media component supplies a white background. No image edits or new
transport calculation were performed. Matching PDF files were not found in
Downloads at import time.

`allakhverdyan-earth-transmission.png` is the original embedded raster image
from V. A. Allakhverdyan's publicly available 2026 dissertation, page 111,
figure 4.20. It is extracted without redrawing or changing the data or labels.

Source: https://issc.jinr.ru/files/326/f_2_5830.pdf
Defence record: https://dissertations.jinr.ru/ru/Dissertations/Announcement/326

The plotted quantity includes neutral-current regeneration. It is a
transmitted-to-incident differential flux ratio for the specified source
spectrum, not the no-interaction probability of one neutrino. The original
Russian axis labels are preserved and explained in English on the slide.
Section 4.8.2 and its preceding discussion specify a detector depth of 1 km.
The spectrum parameters include gamma = 1 and alpha = 0.5; the source definition
is equation 4.23. Do not substitute a different spectrum without recomputing.

A related published presentation of this calculation is figure 9 of
Allakhverdyan, Zavyalov and Naumov, *Physics of Particles and Nuclei Letters*
23 (2026), Russian edition pp. 140–163:
https://www1.jinr.ru/Pepan_letters/panl_2026_2/05_Allahverd_rus.pdf

The no-interaction estimate in the separate slide tab uses a different,
explicitly labelled calculation (CC + NC and a PREM diameter column).
See `../../assets/propagation_estimate.py` for the arithmetic and assumptions.

The supplied tomography figures are tracked separately in
`../tomography/README.md`; their delta-chi-squared colour maps are not
transmission probabilities.
