"""Reddit collage (2400 by 3000 px). Run from the project folder: FONT_DIR=path/to/fonts python3 reddit/collage.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figlib import *

BG = "#FBF3DC"; FG = INK
plt.rcParams.update({"savefig.facecolor": BG, "figure.facecolor": BG, "axes.facecolor": BG})
SIX = ["fish_chips", "chinese", "pizza", "indian", "chicken", "kebab"]
NAME = {"fish_chips": "fish and chips", "chinese": "Chinese", "pizza": "pizza", "indian": "Indian", "chicken": "chicken shop", "kebab": "kebab"}
DL = R["district_lead"]

# hero: each postcode district coloured by its most common named takeaway of the six big kinds
lead = np.zeros((len(P["districts"]) + 1, 4)); lead[0] = 0
for k, r in enumerate(P["districts"]):
    t = [r[2 + FAMS.index(f)] for f in SIX]
    if r[1] >= 1000 and sum(t) >= 3 and t.count(max(t)) == 1:
        lead[k + 1, :3] = hexrgb(FCOL[SIX[int(np.argmax(t))]]); lead[k + 1, 3] = 1
    else:
        lead[k + 1, :3] = hexrgb("#E4DCC8"); lead[k + 1, 3] = 1
img = lead[DID]

fig = plt.figure(figsize=(12, 15), dpi=200)
fig.text(.045, .965, "Chips, curry or kebab?", fontproperties=DISP, fontsize=52, color=FG, va="top")
fig.text(.045, .905, f"What the UK's takeaways sell, read from their names. All {R['n_T']:,} takeaways on the Food Standards\nAgency hygiene register, sorted by name and counted for every postcode district.",
         family=SER, fontsize=15.5, color=FG, va="top", linespacing=1.35)

ax = fig.add_axes([.0, .28, .62, .585])
ax.set_facecolor(BG); ax.imshow(img, extent=EXT, origin="upper", interpolation="nearest")
ax.set_xlim(mx(-8.3), mx(1.85)); ax.set_ylim(my(49.85), my(58.75)); ax.set_aspect("equal"); ax.axis("off")
fig.text(.64, .822, "MOST COMMON NAMED TAKEAWAY\nIN EACH POSTCODE DISTRICT", family=MONO, fontsize=11.5, color=MUTED, va="bottom", linespacing=1.3)

# legend with district counts
lx, ly = .64, .80
for i, f in enumerate(SIX):
    y = ly - i * .028
    fig.text(lx, y, "\u25CF", fontsize=22, color=FCOL[f], va="center", family="DejaVu Sans")
    fig.text(lx + .025, y, f"{NAME[f]}", family=MONO, fontsize=13, color=FG, va="center")
    fig.text(lx + .29, y, f"{DL['counts'][f]:,} districts", family=MONO, fontsize=13, color=MUTED, va="center", ha="right")
fig.text(lx, ly - 6 * .028, "\u25CF", fontsize=22, color="#E4DCC8", va="center", family="DejaVu Sans")
fig.text(lx + .025, ly - 6 * .028, f"tie, or too few", family=MONO, fontsize=13, color=MUTED, va="center")

S = R["stories"]; nd = R["named_districts"]
big = [(f"{nd['PE25']['fish_chips']:.0f}", "chip shops per 100,000 residents in Skegness\n(PE25). Blackpool leads the larger councils."),
       (f"{nd['TW3']['indian']:.0f}", "curry houses per 100,000 in Hounslow's TW3. The\nChinatowns (B5, M1, L1) top the Chinese map."),
       (f"{R['headline']['n_counties_T_gt_R']}", f"council areas of 100,000+ where takeaways outnumber\nrestaurants. UK: {S['ratio']['uk']:.2f} takeaways per restaurant."),
       (f"{R['accuracy']['B']['all']['precision_pct']:.0f}%", "of the name rules' answers were right in a\nheld-out sample of 300 labelled names.")]
for i, (b, s) in enumerate(big):
    y = .59 - i * .085
    fig.text(.64, y, b, fontproperties=DISP, fontsize=40, color=KETCHUP, va="top")
    fig.text(.64, y - .042, s, family=SER, fontsize=12.5, color=FG, va="top", linespacing=1.3)

# small multiples: per head maps
fig.text(.045, .262, "PER 100,000 RESIDENTS, TAKEAWAYS AND RESTAURANTS  (palest: none)", family=MONO, fontsize=11.5, color=MUTED)
for i, f in enumerate(SIX):
    a = fig.add_axes([.01 + i * .165, .045, .16, .17])
    im, br, cols = area_image(f)
    a.imshow(im, extent=EXT, origin="upper", interpolation="nearest"); a.set_xlim(mx(-8.3), mx(1.85)); a.set_ylim(my(49.85), my(58.75)); a.set_aspect("equal"); a.axis("off")
    top = S[f]['county_top'][0]['name'].replace('North East Lincolnshire', 'NE Lincolnshire')
    fig.text(.09 + i * .165, .248, NAME[f], family=MONO, fontsize=12, color=FCOL[f], ha="center", va="top", weight="medium")
    fig.text(.09 + i * .165, .23, f"top: {top}", family=MONO, fontsize=10, color=MUTED, ha="center", va="top")

fig.text(.045, .022, f"Data: Food Standards Agency hygiene register, {R['retrieved']} (OGL v3); ONS, NRS, NISRA census populations (OGL v3); OSM (ODbL) check.",
         family=MONO, fontsize=9.3, color=MUTED)
fig.text(.045, .008, "Analysis and chart: Tristan Hotham, with Python and matplotlib. Counts are floors: a third of names do not say the food.",
         family=MONO, fontsize=9.3, color=MUTED)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chips_curry_kebab.png")
fig.savefig(out, dpi=200); print("wrote", out)
