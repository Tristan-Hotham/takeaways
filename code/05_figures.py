"""Step 5: static figures for the blog (release/blog/b_*.png, 1520 px wide) and the paper (release/paper/fig*.png).
Run: FONT_DIR=path/to/fonts python3 code/05_figures.py
"""
from figlib import *

BLOG = os.path.join(ROOT, "release", "blog"); PAPERD = os.path.join(ROOT, "release", "paper")
os.makedirs(BLOG, exist_ok=True); os.makedirs(PAPERD, exist_ok=True)
SHORT = {"asian_other": "Other Asian", "sandwich": "Sandwich and bakery", "cafe": "Cafe and sweet things", "greek_med": "Greek and Middle Eastern", "caribbean": "Caribbean and African", "japanese": "Japanese and sushi", "asian_other": "Other Asian"}
SL = lambda f: SHORT.get(f, LAB[f])
SIX = ["fish_chips", "indian", "chinese", "pizza", "kebab", "chicken"]
TITLE = {"fish_chips": "Fish and chips", "indian": "Indian and curry", "chinese": "Chinese", "pizza": "Pizza", "kebab": "Kebab and Turkish", "chicken": "Chicken shops"}
S = R["stories"]


def six_maps(path, w=7.6, h=8.6, fs=1.0):
    fig, axs = plt.subplots(2, 3, figsize=(w, h))
    fig.subplots_adjust(left=.01, right=.99, top=.95, bottom=.03, wspace=.02, hspace=.12)
    for ax, f in zip(axs.flat, SIX):
        img, br, cols = area_image(f)
        mapax(ax, img)
        ax.set_title(TITLE[f], family=SER, fontsize=13 * fs, color=FCOL[f], fontweight="semibold", pad=3)
        # small key in the North Sea corner: palest = none, then six classes
        for k, c in enumerate(cols):
            ax.add_patch(plt.Rectangle((0.66 + k * .045, .935), .045, .03, transform=ax.transAxes, color=c, zorder=5, ec="none"))
        ax.text(.66, .905, f"top sixth:\n{br[-1]:.0f}+ per 100k", transform=ax.transAxes, family=MONO, fontsize=7.6 * fs, color=INK, zorder=5, va="top", linespacing=1.1)
    save(fig, path)


def chip_map(path, w=7.6, h=8.96):
    img, br, cols = area_image("fish_chips")
    fig = plt.figure(figsize=(w, h)); ax = fig.add_axes([0, 0, 1, 1]); mapax(ax, img, lon=(-9.0, 4.0))
    lab = {"PE25": ("Skegness", (170000, 10000)), "YO15": ("Bridlington", (150000, 15000)), "YO14": ("Filey", (120000, 110000)), "FY1": ("Blackpool", (-250000, 60000)),
           "PA34": ("Oban", (-150000, 40000)), "NR29": ("Hemsby", (50000, -150000)), "DN35": ("Cleethorpes", (130000, 30000))}
    D = {r[0]: r for r in P["districts"]}
    for d, (name, (dx, dy)) in lab.items():
        r = D[d]; x, y = mx(r[2 + 2 * NF + 6]), my(r[2 + 2 * NF + 5]); v = (r[2 + FAMS.index("fish_chips")] + r[2 + NF + FAMS.index("fish_chips")]) / r[1] * 1e5
        ax.annotate(f"{name} ({d})\n{v:.0f} per 100,000", xy=(x, y), xytext=(x + dx, y + dy), family=MONO, fontsize=9.5, color=INK,
                    ha="left" if dx > 0 else "right", va="center", arrowprops=dict(arrowstyle="-", color=INK, lw=.8, shrinkB=2), zorder=6,
                    bbox=dict(boxstyle="round,pad=0.25", fc=PAPER, ec="none", alpha=.9))
    for k, c in enumerate(cols):
        ax.add_patch(plt.Rectangle((0.63 + k * .045, .93), .045, .018, transform=ax.transAxes, color=c, zorder=5))
    ax.text(.63, .965, "Chip shops per 100,000 residents,\nby postcode district", transform=ax.transAxes, family=MONO, fontsize=9, color=INK, va="bottom")
    ax.text(.63, .915, f"palest: none\ndarkest sixth: {br[-1]:.0f} or more", transform=ax.transAxes, family=MONO, fontsize=8.5, color=MUTED, va="top")
    save(fig, path)


def capitals(path, w=7.6, h=8.4, fs=1.0):
    fig, axs = plt.subplots(3, 2, figsize=(w, h)); fig.subplots_adjust(left=.27, right=.96, top=.96, bottom=.08, hspace=.5, wspace=1.05)
    for ax, f in zip(axs.flat, SIX):
        top = S[f]["county_top"][:8][::-1]
        ax.barh(range(len(top)), [t["rate"] for t in top], color=FCOL[f], height=.72)
        ax.set_yticks(range(len(top))); ax.set_yticklabels([t["name"] for t in top], fontsize=9 * fs, family=MONO, color=INK)
        ax.tick_params(axis="x", labelsize=8.5 * fs); ax.tick_params(axis="y", length=0)
        ax.set_title(TITLE[f], loc="left", family=SER, fontsize=12.5 * fs, color=FCOL[f], fontweight="semibold")
        for i, t in enumerate(top): ax.text(t["rate"], i, f" {t['rate']:.1f}", va="center", family=MONO, fontsize=8.5 * fs, color=MUTED)
        ax.set_xlim(0, max(t["rate"] for t in top) * 1.25)
    fig.text(.01, .005, "Takeaways and restaurants per 100,000 people; council areas of 100,000 or more", family=MONO, fontsize=8.5 * fs, color=MUTED)
    save(fig, path)


def nations(path, w=7.6, h=4.6, fs=1.0):
    N = R["nations"]; nats = ["England", "Wales", "Scotland", "Northern Ireland"]
    fams = ["fish_chips", "chinese", "indian", "pizza", "chicken", "kebab"]
    fig, ax = plt.subplots(figsize=(w, h)); fig.subplots_adjust(left=.08, right=.99, top=.9, bottom=.14)
    bw = .2
    for j, n in enumerate(nats):
        vals = [N[n][f"TR_{f}_100k"] for f in fams]
        ax.bar(np.arange(len(fams)) + (j - 1.5) * bw, vals, bw * .92, color=[FCOL[f] for f in fams], alpha=[1, .75, .5, .3][j], label=n)
        for i, v in enumerate(vals): ax.text(i + (j - 1.5) * bw, v + .3, ["E", "W", "S", "NI"][j], ha="center", family=MONO, fontsize=7.5 * fs, color=MUTED)
    ax.set_xticks(range(len(fams))); ax.set_xticklabels([TITLE[f] for f in fams], fontsize=10 * fs)
    ax.set_ylabel("per 100,000 people", fontsize=10 * fs)
    ax.text(0, 1.04, "Bars left to right: E England, W Wales, S Scotland, NI Northern Ireland", transform=ax.transAxes, family=MONO, fontsize=8.5 * fs, color=MUTED)
    save(fig, path)


def ratio(path, w=7.6, h=6.6, fs=1.0):
    top = S["ratio"]["county_top"][:10]; bot = S["ratio"]["county_bottom"][:10]
    items = top + [None] + bot[::-1]
    fig, ax = plt.subplots(figsize=(w, h)); fig.subplots_adjust(left=.34, right=.95, top=.97, bottom=.12)
    ys = np.arange(len(items))[::-1]
    for y, it in zip(ys, items):
        if it is None: continue
        ax.barh(y, it["ratio"], color=VINEGAR if it in top else CHIP, height=.72)
        ax.text(it["ratio"], y, f" {it['ratio']:.2f}", va="center", family=MONO, fontsize=8.5 * fs, color=MUTED)
    ax.set_yticks([y for y, it in zip(ys, items) if it]); ax.set_yticklabels([it["name"] for it in items if it], family=MONO, fontsize=9 * fs, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.axvline(S["ratio"]["uk"], color=INK, ls=(0, (3, 3)), lw=1); ax.text(S["ratio"]["uk"], ys[0] + .9, f" UK {S['ratio']['uk']:.2f}", family=MONO, fontsize=8.5 * fs)
    ax.axvline(1, color=KETCHUP, lw=1, alpha=.6); ax.text(1, ys[-1] - 1.2, "one to one ", family=MONO, fontsize=8 * fs, color=KETCHUP, ha="right")
    ax.set_xlabel("takeaways per restaurant or cafe", fontsize=10 * fs); ax.set_ylim(-1.8, len(items))
    save(fig, path)


def hygiene(path, w=7.6, h=5.6, fs=1.0):
    H = R["hygiene"]["by_family_T"]
    fams = sorted([f for f in H if f != "other" and H[f]["n_rated"] >= 150], key=lambda f: H[f]["pct5"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(w, h), sharey=True, gridspec_kw={"width_ratios": [2, 1.15]}); fig.subplots_adjust(left=.3, right=.95, top=.9, bottom=.1, wspace=.12)
    y = np.arange(len(fams))
    a1.barh(y, [H[f]["pct5"] for f in fams], color=[FCOL[f] for f in fams], height=.72)
    a2.barh(y, [H[f]["pct_le2"] for f in fams], color=KETCHUP, alpha=.8, height=.72)
    for i, f in enumerate(fams):
        a1.text(H[f]["pct5"], i, f" {H[f]['pct5']:.0f}%", va="center", family=MONO, fontsize=8.5 * fs, color=MUTED)
        a2.text(H[f]["pct_le2"], i, f" {H[f]['pct_le2']:.1f}%", va="center", family=MONO, fontsize=8.5 * fs, color=MUTED)
    a1.set_yticks(y); a1.set_yticklabels([SL(f) for f in fams], family=MONO, fontsize=9 * fs, color=INK); a1.tick_params(axis="y", length=0)
    a1.set_xlim(0, 100); a1.set_xticks([0, 25, 50, 75]); a2.set_xlim(0, max(H[f]["pct_le2"] for f in fams) * 1.45)
    a1.set_title("% of rated takeaways with a 5", loc="left", family=MONO, fontsize=9.5 * fs, color=INK)
    a2.set_title("% rated 0, 1 or 2", loc="left", family=MONO, fontsize=9.5 * fs, color=INK)
    save(fig, path)


def chains(path, w=7.6, h=4.8, fs=1.0):
    C = R["chains"]
    items = [("burger", "McDonald's"), ("burger", "Burger King"), ("chicken", "KFC"), ("chicken", "Nando's"), ("sandwich", "Subway"), ("pizza", "Domino's"), ("sandwich", "Greggs"),
             ("pizza", "Papa John's"), ("pizza", "Pizza Hut"), ("cafe", "Costa")]
    fig, ax = plt.subplots(figsize=(w, h)); fig.subplots_adjust(left=.37, right=.95, top=.97, bottom=.12)
    vals = [C[f][b]["share"] for f, b in items] + [C["fish_chips"]["chain_share"]]
    labs = [f"{b} ({LAB[f].split(',')[0].split(' and ')[0].lower()})" for f, b in items] + ["Any chip shop chain"]
    cols = [FCOL[f] for f, _ in items] + [FCOL["fish_chips"]]
    y = np.arange(len(vals))[::-1]
    ax.barh(y, vals, color=cols, height=.72)
    for yy, v in zip(y, vals): ax.text(v, yy, f" {v:.1f}%", va="center", family=MONO, fontsize=8.5 * fs, color=MUTED)
    ax.set_yticks(y); ax.set_yticklabels(labs, family=MONO, fontsize=9 * fs, color=INK); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("share of takeaways and restaurants of that kind", fontsize=10 * fs); ax.set_xlim(0, 50)
    save(fig, path)


def osm_check(path, w=6.5, h=4.4):
    PF = R["osm"]["per_family"]; fams = [f for f in ["fish_chips", "indian", "chinese", "pizza", "kebab", "chicken", "burger", "thai", "sandwich", "japanese", "italian"] if PF[f]["n_classified"] >= 100]
    fig, ax = plt.subplots(figsize=(w, h)); fig.subplots_adjust(left=.3, right=.97, top=.9, bottom=.16)
    y = np.arange(len(fams))[::-1]
    ax.barh(y + .18, [PF[f]["precision_pct"] for f in fams], .34, color=[FCOL[f] for f in fams], label="rules' family confirmed by OpenStreetMap")
    ax.barh(y - .18, [PF[f]["recall_pct"] for f in fams], .34, color=[FCOL[f] for f in fams], alpha=.4, label="OpenStreetMap family found by the rules")
    ax.set_yticks(y); ax.set_yticklabels([SL(f) for f in fams], family=MONO, fontsize=8.5, color=INK); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 100); ax.set_xlabel("% of matched places")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=8, frameon=False, ncol=1)
    save(fig, path)


if __name__ == "__main__":
    six_maps(os.path.join(BLOG, "b_six_maps.png"))
    chip_map(os.path.join(BLOG, "b_chip_map.png"))
    capitals(os.path.join(BLOG, "b_capitals.png"))
    nations(os.path.join(BLOG, "b_nations.png"))
    ratio(os.path.join(BLOG, "b_ratio.png"))
    hygiene(os.path.join(BLOG, "b_hygiene.png"))
    chains(os.path.join(BLOG, "b_chains.png"))
    six_maps(os.path.join(PAPERD, "fig1_six_maps.png"), w=6.5, h=7.4, fs=.85)
    capitals(os.path.join(PAPERD, "fig2_capitals.png"), w=6.5, h=7.6, fs=.85)
    nations(os.path.join(PAPERD, "fig3_nations.png"), w=6.5, h=3.9, fs=.85)
    ratio(os.path.join(PAPERD, "fig4_ratio.png"), w=6.5, h=5.6, fs=.85)
    hygiene(os.path.join(PAPERD, "fig5_hygiene.png"), w=6.5, h=4.8, fs=.85)
    osm_check(os.path.join(PAPERD, "fig6_osm_check.png"))
