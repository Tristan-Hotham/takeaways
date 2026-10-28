"""Shared drawing helpers for the header, the blog and paper figures and the Reddit collage (matplotlib).
Fonts: FONT_DIR holding Fraunces, Source Serif 4 and IBM Plex Mono (github.com/google/fonts); otherwise
matplotlib's defaults are used.
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image
from palette import FCOL, INK, PAPER, KETCHUP, CHIP, VINEGAR, MUTED, RULE

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts")
DISP = None
if os.path.isdir(FD):
    for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
        if os.path.exists(os.path.join(FD, f)): fm.fontManager.addfont(os.path.join(FD, f))
    DISP = fm.FontProperties(fname=os.path.join(FD, "FrauncesVar.ttf"), weight=900)
SER, MONO = "Source Serif 4", "IBM Plex Mono"
SEA = "#E6EAE9"; NODATA = "#E9E3D8"
plt.rcParams.update({"font.family": SER, "font.size": 12, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.facecolor": PAPER, "figure.facecolor": PAPER, "axes.facecolor": PAPER})
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
P = json.load(open(os.path.join(ROOT, "data", "page.json")))
GM = json.load(open(os.path.join(ROOT, "data", "grid", "meta.json")))
FAMS = [f for f, _ in P["fams"]]; LAB = dict(P["fams"])
NF = len(FAMS)
_im = np.array(Image.open(os.path.join(ROOT, "data", "grid", "districts.png"))).astype(np.int32)
DID = _im[:, :, 0] * 256 + _im[:, :, 1]; CID = _im[:, :, 2]
RE = 6378137.0
def mx(lon): return RE * np.radians(lon)
def my(lat): return RE * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
EXT = [mx(GM["west"]), mx(GM["east"]), my(GM["south"]), my(GM["north"])]


def hexrgb(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255


def ramp(col, n=7):
    c = hexrgb(col); pale = hexrgb("#F6EEDE"); deep = c + (np.array([20, 12, 8]) / 255 - c) * .45
    out = []
    for k in range(n):
        t = k / (n - 1)
        out.append(pale + (c - pale) * (t / .7) if t < .7 else c + (deep - c) * ((t - .7) / .3))
    return out


def area_values(fam, g="TR", level="d", measure="rate", minpop=1000):
    """Per 100,000 people (or % share of places) for every district or county row in page.json."""
    rows = P["districts"] if level == "d" else P["counties"]
    out = []
    for r in rows:
        pop = r[1]
        if fam == "all": n = (r[2 + 2 * NF] if "T" in g else 0) + (r[3 + 2 * NF] if "R" in g else 0)
        else:
            k = FAMS.index(fam); n = (r[2 + k] if "T" in g else 0) + (r[2 + NF + k] if "R" in g else 0)
        if not pop or pop < minpop: out.append(np.nan); continue
        if measure == "share":
            tot = (r[2 + 2 * NF] if "T" in g else 0) + (r[3 + 2 * NF] if "R" in g else 0)
            out.append(100 * n / tot if tot >= 5 else np.nan)
        else: out.append(n / pop * 1e5)
    return np.array(out, dtype=float)


def breaks(vals, n=7):
    v = np.sort(vals[np.isfinite(vals) & (vals > 0)])
    return [0] + [v[int(len(v) * k / (n - 1))] for k in range(1, n - 1)]


def classify(vals, br):
    c = np.full(len(vals), -1)
    ok = np.isfinite(vals)
    c[ok & (vals <= 0)] = 0
    pos = ok & (vals > 0)
    c[pos] = 1 + np.searchsorted(br[1:], vals[pos], side="right")
    return c


def area_image(fam, g="TR", level="d", col=None):
    vals = area_values(fam, g, level)
    br = breaks(vals); cl = classify(vals, br)
    cols = ramp(col or FCOL.get(fam, VINEGAR))
    lut = np.zeros((len(vals) + 1, 4))
    for k in range(len(vals)):
        lut[k + 1, :3] = cols[cl[k]] if cl[k] >= 0 else hexrgb(NODATA); lut[k + 1, 3] = 1
    ids = DID if level == "d" else CID
    return lut[ids], br, cols


def county_lines(ax, color=INK, lw=.35, alpha=.55):
    gj = json.load(open(os.path.join(ROOT, "data", "counties.geojson")))
    for f in gj["features"]:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for ring in poly:
                a = np.array(ring); ax.plot(mx(a[:, 0]), my(a[:, 1]), color=color, lw=lw, alpha=alpha, solid_joinstyle="round")


def mapax(ax, img, lat=(49.85, 58.75), lon=(-8.3, 1.85), lines=True):
    ax.set_facecolor(SEA)
    ax.imshow(img, extent=EXT, origin="upper", interpolation="nearest", zorder=1)
    if lines: county_lines(ax)
    ax.set_xlim(mx(lon[0]), mx(lon[1])); ax.set_ylim(my(lat[0]), my(lat[1]))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    for s in ax.spines.values(): s.set_visible(False)


def save(fig, path, dpi=200):
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    print("wrote", os.path.relpath(path, ROOT))
