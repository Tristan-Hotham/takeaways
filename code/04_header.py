"""Step 4: header.png, the 1200 by 630 social card.
Run: FONT_DIR=path/to/fonts python3 code/04_header.py
"""
from figlib import *

fig = plt.figure(figsize=(6, 3.15), dpi=200)
ax = fig.add_axes([.56, .01, .43, .98]); img, br, cols = area_image("fish_chips"); mapax(ax, img, lines=False)
fig.text(.05, .89, "DATA STUDY  ·  FOOD  ·  UNITED KINGDOM 2026", family=MONO, fontsize=6.2, color=MUTED)
fig.text(.045, .83, "Chips,", fontproperties=DISP, fontsize=34, color=CHIP, va="top")
fig.text(.045, .65, "curry or", fontproperties=DISP, fontsize=34, color=KETCHUP, va="top")
fig.text(.045, .47, "kebab?", fontproperties=DISP, fontsize=34, color=VINEGAR, va="top")
H = R["headline"]
fig.text(.05, .27, f"{R['n_T']:,} takeaways and {R['n_R']:,} restaurants and cafes,\nsorted by name and counted per head for every\npostcode district. Map: chip shops per 100,000 people.",
         family=SER, fontsize=7.6, color=INK, va="top", linespacing=1.18)
fig.text(.05, .05, "Dr Tristan Hotham · Independent researcher", family=MONO, fontsize=6, color=MUTED)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=200)
print("header.png written")
