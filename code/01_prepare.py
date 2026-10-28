"""Step 1: read the raw bundles, classify every business name, build postcode district areas.

Inputs (read in place, gathered through a browser and saved as gzipped JSON):
  RAW/takeaways_fhrs.json.gz    Food Standards Agency FHRS/FHIS API: takeaways, restaurants, pubs and
                                mobile caterers as rows; counts by postcode district and type for all
                                fourteen business types; rating counts by type; 1 km cell counts of all
                                other food businesses (used only to draw district areas).
  RAW/takeaways_ref.json.gz     Census 2021 postcode district populations (England and Wales, Nomis P004),
                                NRS Scotland's Census 2022 postcode populations (with grid references),
                                ONS mid-2025 population estimates (counties and unitary authorities,
                                and districts), ONS Counties and Unitary Authorities (December 2023)
                                generalised boundaries, OpenStreetMap fast food and restaurants.
  RAW/ni_pcd_pop2021.csv        NISRA Census 2021 usual residents by postcode district (Northern Ireland).

Outputs in data/: businesses.csv.gz, districts.csv, counties.csv, grid/districts.png (+ meta),
counties.geojson, osm_uk.csv.gz, and a few intermediate tables used by step 2.
"""
import os, io, re, csv, gzip, json, sys
import numpy as np, pandas as pd
from matplotlib.path import Path
from pyproj import Transformer
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from classify import classify, CATS, osm_family

RAW = os.environ.get("RAW", "/home/claude/hist/_data18/takeaways")
DATA = os.path.join(ROOT, "data"); os.makedirs(os.path.join(DATA, "grid"), exist_ok=True)

TYPES = {7844: "Takeaway/sandwich shop", 1: "Restaurant/Cafe/Canteen", 7843: "Pub/bar/nightclub", 7846: "Mobile caterer",
         7: "Distributors/Transporters", 7838: "Farmers/growers", 5: "Hospitals/Childcare/Caring Premises",
         7842: "Hotel/bed & breakfast/guest house", 14: "Importers/Exporters", 7839: "Manufacturers/packers",
         7841: "Other catering premises", 4613: "Retailers - other", 7840: "Retailers - supermarkets/hypermarkets",
         7845: "School/college/university"}

fh = json.load(gzip.open(os.path.join(RAW, "takeaways_fhrs.json.gz")))
ref = json.load(gzip.open(os.path.join(RAW, "takeaways_ref.json.gz")))
print("FHRS retrieved", fh["retrieved"], "ref retrieved", ref.get("retrieved"))


def district_of(pc):
    pc = re.sub(r"\s+", " ", (pc or "").upper().strip())
    if " " in pc:
        d = pc.split(" ")[0]
    else:
        c = pc.replace(" ", ""); d = c[:-3] if len(c) >= 5 else ""
    return d if re.fullmatch(r"[A-Z]{1,2}[0-9][0-9A-Z]?", d) else ""


# ---------- populations by postcode district ----------
pop = {}
src = {}
pcdd = pd.read_csv(io.StringIO(ref["pcdd"]))
for d, n in zip(pcdd.iloc[:, 0], pcdd.iloc[:, 1]):
    pop[d.strip()] = int(n); src[d.strip()] = "Census 2021 (England and Wales)"
sco = pd.DataFrame(ref["sco"], columns=["pc", "pop", "hh", "e", "n"])
sco["d"] = sco.pc.map(district_of)
for d, n in sco.groupby("d")["pop"].sum().items():
    if d:
        pop[d] = pop.get(d, 0) + int(n); src[d] = "Scotland's Census 2022"
ni = pd.read_csv(os.path.join(RAW, "ni_pcd_pop2021.csv"))
for d, n in zip(ni.district, ni["pop"]):
    pop[d.strip()] = int(n); src[d.strip()] = "Census 2021 (Northern Ireland)"
print("districts with population", len(pop), "total", sum(pop.values()))

# ---------- the grid: Web Mercator, 1.5 km pixels (about 0.9 km on the ground at these latitudes) ----------
R = 6378137.0
def mx(lon): return R * np.radians(lon)
def my(lat): return R * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
LON0, LON1, LAT0, LAT1 = -8.75, 1.85, 49.8, 60.95
PX = 750.0
X0, X1, Y0, Y1 = mx(LON0), mx(LON1), my(LAT0), my(LAT1)
W = int(np.ceil((X1 - X0) / PX)); H = int(np.ceil((Y1 - Y0) / PX))
X1 = X0 + W * PX; Y1 = Y0 + H * PX
def lon_of(x): return np.degrees(x / R)
def lat_of(y): return np.degrees(2 * np.arctan(np.exp(y / R)) - np.pi / 2)
GRID = {"W": W, "H": H, "px_m": PX, "west": float(lon_of(X0)), "east": float(lon_of(X1)), "south": float(lat_of(Y0)), "north": float(lat_of(Y1))}
print("grid", W, H)


def pix(lat, lon):
    i = np.floor((mx(lon) - X0) / PX).astype(int); j = np.floor((Y1 - my(lat)) / PX).astype(int)
    ok = (i >= 0) & (i < W) & (j >= 0) & (j < H)
    return np.where(ok, j * W + i, -1)


# ---------- counties: rasterise the ONS generalised boundaries ----------
cty = ref["cty"]["features"]
CCODE = [k for k in cty[0]["properties"] if re.fullmatch(r"CTYUA\d\dCD", k)][0]; CNAME = CCODE[:-2] + "NM"
counties = []
cgrid = np.zeros(H * W, dtype=np.int16)            # 0 = sea, else county index + 1
jj, ii = np.mgrid[0:H, 0:W]
cx = X0 + (ii + .5) * PX; cy = Y1 - (jj + .5) * PX
for f in cty:
    p = f["properties"]; counties.append({"code": p[CCODE], "name": p[CNAME]})
def bbox_area(f):
    c = np.array([pt for poly in (f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" else [f["geometry"]["coordinates"]]) for pt in poly[0]])
    return (c[:, 0].max() - c[:, 0].min()) * (c[:, 1].max() - c[:, 1].min())
# paint big areas first and small ones last, so an enclosed unitary authority (Nottingham inside
# Nottinghamshire) is never painted over if a generalised outer ring has lost its hole
for k in sorted(range(len(cty)), key=lambda k: -bbox_area(cty[k])):
    f = cty[k]
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        rings = [np.column_stack([mx(np.array(r)[:, 0]), my(np.array(r)[:, 1])]) for r in poly]
        ext = rings[0]; xa, xb, ya, yb = ext[:, 0].min(), ext[:, 0].max(), ext[:, 1].min(), ext[:, 1].max()
        sel = (cx >= xa) & (cx <= xb) & (cy >= ya) & (cy <= yb)
        if not sel.any():
            # tiny island: mark the pixel that holds its centre
            q = pix(np.array([lat_of(ext[:, 1].mean())]), np.array([lon_of(ext[:, 0].mean())]))[0]
            if q >= 0 and cgrid[q] == 0: cgrid[q] = k + 1
            continue
        pts = np.column_stack([cx[sel], cy[sel]])
        inside = Path(ext).contains_points(pts)
        for hole in rings[1:]:
            inside &= ~Path(hole).contains_points(pts)
        idx = np.flatnonzero(sel.ravel())[inside]
        cgrid[idx] = k + 1
land = cgrid > 0
print("counties", len(counties), "land pixels", land.sum())
CN = pd.DataFrame(counties)
CN["nation"] = CN.code.str[0].map({"E": "England", "W": "Wales", "S": "Scotland", "N": "Northern Ireland"})

# ---------- businesses ----------
B = pd.DataFrame(fh["rows"], columns=fh["rowCols"])
# en and em dashes in trading names are written as plain hyphens, to keep every published file free of them
B["name"] = B.name.fillna("").str.replace("\u2013", "-").str.replace("\u2014", "-")
B["district"] = B.postcode.map(district_of)
B["la_name"] = B.laCode.astype(str).map({str(k): v for k, v in fh["la"].items()})
cl = [classify(n) if t != 7843 else ("pub", "pub") for n, t in zip(B.name, B.typeId)]
B["cuisine"] = [c[0] for c in cl]; B["rule"] = [c[1] for c in cl]
ok = B.lat.notna() & B.lon.notna() & (B.lat > 49) & (B.lat < 61.5) & (B.lon > -9) & (B.lon < 2.5)
B.loc[~ok, ["lat", "lon"]] = np.nan
B["pix"] = -1
B.loc[ok, "pix"] = pix(B.loc[ok, "lat"].values, B.loc[ok, "lon"].values)
# county of each geocoded business; snap points just off the generalised coast to the nearest land pixel
dist_to_land, (ni_, nj_) = ndimage.distance_transform_edt(~land.reshape(H, W), return_indices=True)
near = (ni_ * W + nj_).ravel()
pp = B.pix.values.copy(); has = pp >= 0
pp[has] = np.where(dist_to_land.ravel()[pp[has]] <= 4, near[pp[has]], -1)
B["cty_pt"] = np.where(pp >= 0, cgrid[np.maximum(pp, 0)] - 1, -1)
# the inspecting council (local authority) nests inside one county or unitary authority: take the
# majority county of each council's geocoded businesses, then give every business its council's county
la_cty = B[B.cty_pt >= 0].groupby("laCode").cty_pt.agg(lambda s: s.value_counts().index[0])
la_share = B[B.cty_pt >= 0].groupby("laCode").cty_pt.agg(lambda s: s.value_counts(normalize=True).iloc[0])
B["cty"] = B.laCode.map(la_cty).fillna(-1).astype(int)
print("council to county agreement (median share)", round(la_share.median(), 4), "min", round(la_share.min(), 3))
print("businesses", len(B), "geocoded", ok.sum(), "with county", (B.cty >= 0).sum())

# ---------- district areas: each land pixel takes the most common district among its nearest
# labelled points (geocoded takeaways, restaurants, pubs and mobile caterers; 1 km cell centres of all
# other food businesses; and Scotland's census postcode points) ----------
D = sorted(pop)
DI = {d: k for k, d in enumerate(D)}
plat, plon, plab = [], [], []
m = B.lat.notna() & B.district.isin(DI)
plat += list(B.lat[m]); plon += list(B.lon[m]); plab += [DI[d] for d in B.district[m]]
for k, n in fh["cells"].items():
    d, a, b = k.split("|")
    if d in DI:
        for _ in range(min(n, 5)):
            plat.append(int(a) * 0.01); plon.append(int(b) * 0.016); plab.append(DI[d])
tr = Transformer.from_crs(27700, 4326, always_xy=True)
slon, slat = tr.transform(sco.e.values, sco.n.values)
ms = sco.d.isin(DI).values
plat += list(slat[ms]); plon += list(slon[ms]); plab += [DI[d] for d in sco.d.values[ms]]
plat, plon, plab = np.array(plat), np.array(plon), np.array(plab)
print("labelled points", len(plab))
from scipy.spatial import cKDTree
kt = cKDTree(np.column_stack([mx(plon), my(plat)]))
LP = np.flatnonzero(land)
K = 9
dd, nn = kt.query(np.column_stack([cx.ravel()[LP], cy.ravel()[LP]]), k=K, workers=-1)
lab = plab[nn]
# majority vote, nearer points weigh more
w = 1.0 / (dd + PX)
best = np.full(len(LP), -1); bw = np.zeros(len(LP))
for c in range(K):
    cand = lab[:, c]
    sc = (w * (lab == cand[:, None])).sum(axis=1)
    upd = sc > bw; best[upd] = cand[upd]; bw[upd] = sc[upd]
dgrid = np.full(H * W, -1, dtype=np.int32); dgrid[LP] = best
present = np.unique(dgrid[dgrid >= 0])
print("districts drawn", len(present), "of", len(D))

# district table
area_km2 = (PX * np.cos(np.radians(lat_of(cy.ravel())))) ** 2 / 1e6
rows = []
for k, d in enumerate(D):
    m = dgrid == k
    r = {"district": d, "pop": pop[d], "pop_source": src[d], "drawn": bool(m.any())}
    if m.any():
        r["area_km2"] = round(float(area_km2[m].sum()), 1)
        r["lat"] = round(float(lat_of(cy.ravel()[m].mean())), 4); r["lon"] = round(float(lon_of(cx.ravel()[m].mean())), 4)
        cc = cgrid[m]; cc = cc[cc > 0]
        r["cty"] = int(np.bincount(cc).argmax() - 1) if len(cc) else -1
    rows.append(r)
DT = pd.DataFrame(rows)
# businesses without a geocode keep their district by postcode; county of district for the record
DT["county"] = DT.cty.map(lambda c: CN.name[int(c)] if pd.notna(c) and c >= 0 else "")
DT["nation"] = DT.cty.map(lambda c: CN.nation[int(c)] if pd.notna(c) and c >= 0 else "")

# all fourteen business types by district (from the API aggregation)
allc = {d: v for d, v in fh["dist"].items()}
for t in TYPES:
    DT[f"n_{t}"] = DT.district.map(lambda d: allc.get(d, {}).get(str(t), 0))
DT["n_all"] = DT[[f"n_{t}" for t in TYPES]].sum(axis=1)

# ---------- write ----------
B["county_code"] = B.cty.map(lambda c: CN.code[c] if c >= 0 else "")
B["county"] = B.cty.map(lambda c: CN.name[c] if c >= 0 else "")
B["nation"] = B.cty.map(lambda c: CN.nation[c] if c >= 0 else "")
B["type"] = B.typeId.map(TYPES)
out = B[["fhrsid", "name", "type", "typeId", "postcode", "district", "lat", "lon", "rating", "ratingYear", "la_name", "county", "county_code", "nation", "cuisine", "rule"]]
out.to_csv(os.path.join(DATA, "_businesses.csv.gz"), index=False, compression="gzip")
DT.to_csv(os.path.join(DATA, "_districts_base.csv"), index=False)
CN.to_csv(os.path.join(DATA, "_counties_index.csv"), index=False)

# counties population (ONS mid-year estimates via Nomis)
pc = pd.read_csv(io.StringIO(ref["popCty"]))
pc.columns = [c.lower() for c in pc.columns]
CN = CN.merge(pc.rename(columns={"geography_code": "code", "obs_value": "pop", "date_name": "pop_year"})[["code", "pop", "pop_year"]], on="code", how="left")
print("counties without population", CN[CN["pop"].isna()].name.tolist())
CN.to_csv(os.path.join(DATA, "_counties_pop.csv"), index=False)

# district raster as PNG: R,G = district index + 1 (16 bit), B = county index + 1
ids = (dgrid + 1).astype(np.int64)
img = np.zeros((H * W, 3), dtype=np.uint8)
img[:, 0] = ids // 256; img[:, 1] = ids % 256; img[:, 2] = np.where(land, cgrid, 0)
Image.fromarray(img.reshape(H, W, 3), "RGB").save(os.path.join(DATA, "grid", "districts.png"), optimize=True)
json.dump({**GRID, "encoding": "R*256+G = row of districts list + 1 (0 = sea); B = county index + 1"},
          open(os.path.join(DATA, "grid", "meta.json"), "w"), indent=1)

# counties geojson for the page: simplified further, coordinates rounded
from shapely.geometry import shape, mapping
feats = []
for k, f in enumerate(cty):
    g = shape(f["geometry"]).simplify(0.004, preserve_topology=True)
    gm = json.loads(json.dumps(mapping(g)), parse_float=lambda x: round(float(x), 4))
    feats.append({"type": "Feature", "properties": {"i": k}, "geometry": gm})
json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DATA, "counties.geojson"), "w"), separators=(",", ":"))

# OpenStreetMap, deduplicated, with the same family mapping
# OpenStreetMap came in two parts: chunks 0 to 9 and 39 to 41 (in the reference bundle) and 10 to 38
osm2 = json.load(gzip.open(os.path.join(RAW, "takeaways_osm2.json.gz")))
assert sorted(set(range(ref["osmChunksForward"])) | set(ref["osmChunksReverse"]) | set(osm2["chunks"])) == list(range(42))
O = pd.DataFrame(ref["osm"] + osm2["osm"], columns=["lat", "lon", "fast_food", "name", "cuisine", "brand", "osm_id"]).drop_duplicates("osm_id")
O = O[O.lat.notna()]
O["pix"] = pix(O.lat.values, O.lon.values)
O = O[(O.pix >= 0)]
O = O[land[O.pix.values]]
O["family"] = O.cuisine.map(osm_family)
O["cls"] = [classify(n)[0] for n in O.name]
O["district"] = [D[k] if k >= 0 else "" for k in dgrid[O.pix.values]]
O["county"] = [CN.name[c - 1] if c > 0 else "" for c in cgrid[O.pix.values]]
O.drop(columns=["pix"]).to_csv(os.path.join(DATA, "osm_uk.csv.gz"), index=False, compression="gzip")
print("OSM UK points", len(O), "with cuisine", O.cuisine.ne("").sum())

# place names for the map labels and the search box: OS Open Names cities, towns and villages (GB)
# and GeoNames towns (Northern Ireland), as compiled for the sun-and-rain-uk project (read in place)
PLACES = os.environ.get("PLACES", "/home/claude/hist/sun-and-rain-uk/data/places_search.json")
pl = json.load(open(PLACES))
trp = Transformer.from_crs(27700, 4326, always_xy=True)
e = np.array([p[2] for p in pl]) * 1000; n = np.array([p[3] for p in pl]) * 1000
lo, la = trp.transform(e, n)
json.dump([[p[0], p[1], round(float(a), 4), round(float(b), 4), p[4]] for p, a, b in zip(pl, la, lo)],
          open(os.path.join(DATA, "places.json"), "w"), separators=(",", ":"), ensure_ascii=False)
print("places", len(pl))
