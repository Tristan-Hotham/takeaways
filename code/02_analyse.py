"""Step 2: every statistic. Writes data/results.json (every number used anywhere), the district and
county tables with per-head rates, the accuracy sample, the OpenStreetMap cross-check, the page data
(data/page.json) and the per-family point files (data/points/*.json).
"""
import os, re, json, gzip, sys, math, random
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from classify import CATS, LABEL, classify, norm
from manual_labels import LABELS

RAW = os.environ.get("RAW", "/home/claude/hist/_data18/takeaways")
DATA = os.path.join(ROOT, "data")
fh = json.load(gzip.open(os.path.join(RAW, "takeaways_fhrs.json.gz")))
B = pd.read_csv(os.path.join(DATA, "_businesses.csv.gz"), keep_default_na=False, na_values=[""], dtype={"rating": str})
DT = pd.read_csv(os.path.join(DATA, "_districts_base.csv"))
CN = pd.read_csv(os.path.join(DATA, "_counties_pop.csv"))
O = pd.read_csv(os.path.join(DATA, "osm_uk.csv.gz"), keep_default_na=False, na_values=[""])
FAM = [c for c, _ in CATS if c != "other"]
G = {7844: "T", 1: "R", 7843: "P", 7846: "M"}
B["g"] = B.typeId.map(G)
RES = {}
def r1(x): return round(float(x), 1)
def r2(x): return round(float(x), 2)
def pct(a, b): return round(100.0 * a / b, 1) if b else None

# ---------- coverage ----------
tot = {str(k): int(v) for k, v in fh["totals"].items()}
RES["retrieved"] = fh["retrieved"][:10]
RES["n_names_dash"] = int(sum(1 for r in fh["rows"] if r[0] and ("\u2013" in r[0] or "\u2014" in r[0])))  # written as hyphens in published files
RES["n_all_types"] = int(sum(tot.values()))
RES["n_by_type"] = tot
RES["n_rows"] = int(len(B))
RES["n_T"] = int((B.g == "T").sum()); RES["n_R"] = int((B.g == "R").sum()); RES["n_P"] = int((B.g == "P").sum()); RES["n_M"] = int((B.g == "M").sum())
RES["geocoded_pct"] = pct(B.lat.notna().sum(), len(B)); RES["not_geocoded_pct"] = r1(100 - RES["geocoded_pct"])
RES["county_pct"] = pct(B.county.notna().sum(), len(B))
RES["district_pct"] = pct(B.district.isin(DT.district).sum(), len(B))
cls = {}
for g in "TRM":
    s = B[B.g == g]; cls[g] = {"n": int(len(s)), "classified": int((s.cuisine != "other").sum()), "classified_pct": pct((s.cuisine != "other").sum(), len(s)),
                               "by_family": {f: int((s.cuisine == f).sum()) for f in FAM + ["other"]}}
RES["classified"] = cls
RES["pop_total"] = int(DT["pop"].sum()); RES["n_districts"] = int(len(DT)); RES["n_districts_drawn"] = int(DT.drawn.sum())
RES["pop_sources"] = DT.groupby("pop_source")["pop"].agg(["count", "sum"]).astype(int).to_dict("index")
RES["n_counties"] = int(len(CN)); RES["county_pop_year"] = str(CN.pop_year.dropna().iloc[0])

# ---------- counts by area ----------
def counts(frame, key):
    out = {}
    for g in "TRM":
        s = frame[frame.g == g]
        out[f"{g}_all"] = s.groupby(key).size()
        for f in FAM:
            out[f"{g}_{f}"] = s[s.cuisine == f].groupby(key).size()
    out["P_all"] = frame[frame.g == "P"].groupby(key).size()
    return pd.DataFrame(out).fillna(0).astype(int)

cd = counts(B, "district").reindex(DT.district).fillna(0).astype(int)
DT = DT.set_index("district").join(cd).reset_index()
cc = counts(B[B.county.notna()], "county_code").reindex(CN.code).fillna(0).astype(int)
CN = CN.set_index("code").join(cc).reset_index()
for f in FAM:
    DT[f"TR_{f}"] = DT[f"T_{f}"] + DT[f"R_{f}"]; CN[f"TR_{f}"] = CN[f"T_{f}"] + CN[f"R_{f}"]
DT["TR_all"] = DT.T_all + DT.R_all; CN["TR_all"] = CN.T_all + CN.R_all
MINPOP = 10000; MINPOP_C = 100000
RES["min_pop_rank"] = MINPOP; RES["min_pop_rank_county"] = MINPOP_C

def per10k(n, p): return n / p * 1e5   # per 100,000 people (name kept for brevity)

def ranking(T, key, col, minpop=0, k=10, namecol="name"):
    s = T[(T["pop"] >= minpop) & T["pop"].notna()].copy()
    s["rate"] = per10k(s[col], s["pop"])
    s = s.sort_values("rate", ascending=False)
    return [{"name": r[namecol], "rate": r1(r.rate), "n": int(r[col]), "pop": int(r["pop"]), **({"county": r.county} if "county" in r and isinstance(r.county, str) else {})}
            for _, r in s.head(k).iterrows()]

# national rates
NAT = {}
CN["nation"] = CN.code.str[0].map({"E": "England", "W": "Wales", "S": "Scotland", "N": "Northern Ireland"})
for nat, s in list(CN.groupby("nation")) + [("United Kingdom", CN)]:
    p = s["pop"].sum(); d = {"pop": int(p)}
    for col in ["T_all", "R_all", "P_all", "M_all", "TR_all"] + [f"TR_{f}" for f in FAM] + [f"T_{f}" for f in FAM]:
        d[col] = int(s[col].sum()); d[col + "_100k"] = r1(per10k(s[col].sum(), p))
    d["ratio_TR"] = r2(s.T_all.sum() / s.R_all.sum())
    NAT[nat] = d
RES["nations"] = NAT

STORY = {}
for f in FAM:
    STORY[f] = {"county_top": ranking(CN, "code", f"TR_{f}", MINPOP_C, 10), "district_top": ranking(DT, "district", f"TR_{f}", MINPOP, 10, "district"),
                "county_bottom": ranking(CN, "code", f"TR_{f}", MINPOP_C, 300)[-5:][::-1], "county_top_any": ranking(CN, "code", f"TR_{f}", 0, 3),
                "T_county_top": ranking(CN, "code", f"T_{f}", MINPOP_C, 10)}
    sd = DT[(DT["pop"] >= MINPOP) & (DT.TR_all >= 30)].copy(); sd["share"] = sd[f"TR_{f}"] / sd.TR_all
    sd = sd.sort_values("share", ascending=False)
    STORY[f]["district_share_top"] = [{"name": r.district, "county": r.county, "share": r1(100 * r.share), "n": int(r[f"TR_{f}"]), "of": int(r.TR_all)} for _, r in sd.head(10).iterrows()]
    # share of an area's takeaways and restaurants that are this family
    s = CN[CN["pop"] >= MINPOP_C].copy(); s["share"] = s[f"TR_{f}"] / s.TR_all
    s = s.sort_values("share", ascending=False)
    STORY[f]["county_share_top"] = [{"name": r["name"], "share": r1(100 * r.share), "n": int(r[f"TR_{f}"])} for _, r in s.head(5).iterrows()]
STORY["T_all"] = {"county_top": ranking(CN, "code", "T_all", MINPOP_C, 10), "district_top": ranking(DT, "district", "T_all", MINPOP, 10, "district"),
                  "county_bottom": ranking(CN, "code", "T_all", MINPOP_C, 300)[-5:][::-1]}
STORY["R_all"] = {"county_top": ranking(CN, "code", "R_all", MINPOP_C, 10), "county_bottom": ranking(CN, "code", "R_all", MINPOP_C, 300)[-5:][::-1]}
STORY["P_all"] = {"county_top": ranking(CN, "code", "P_all", MINPOP_C, 10)}
# takeaway to restaurant ratio
s = CN[(CN["pop"] >= MINPOP_C) & (CN.R_all > 0)].copy(); s["ratio"] = s.T_all / s.R_all
s = s.sort_values("ratio", ascending=False)
STORY["ratio"] = {"county_top": [{"name": r["name"], "ratio": r2(r.ratio), "T": int(r.T_all), "R": int(r.R_all)} for _, r in s.head(10).iterrows()],
                  "county_bottom": [{"name": r["name"], "ratio": r2(r.ratio), "T": int(r.T_all), "R": int(r.R_all)} for _, r in s.tail(10).iloc[::-1].iterrows()],
                  "uk": NAT["United Kingdom"]["ratio_TR"]}
d = DT[DT["pop"] >= MINPOP].copy(); d = d[d.R_all >= 10]; d["ratio"] = d.T_all / d.R_all
d = d.sort_values("ratio", ascending=False)
STORY["ratio"]["district_top"] = [{"name": r.district, "county": r.county, "ratio": r2(r.ratio), "T": int(r.T_all), "R": int(r.R_all)} for _, r in d.head(10).iterrows()]
STORY["ratio"]["district_bottom"] = [{"name": r.district, "county": r.county, "ratio": r2(r.ratio), "T": int(r.T_all), "R": int(r.R_all)} for _, r in d.tail(10).iloc[::-1].iterrows()]
# the leading family of each county's takeaways (excluding sandwich and cafe)
hot = ["fish_chips", "indian", "chinese", "pizza", "kebab", "chicken", "burger"]
lead = {}
for _, r in CN.iterrows():
    v = {f: r[f"T_{f}"] for f in hot}; lead[r["name"]] = max(v, key=v.get)
STORY["lead_family_counts"] = pd.Series(lead).value_counts().to_dict()
RES["stories"] = STORY
UKN = NAT["United Kingdom"]
RES["headline"] = {"people_per_T": int(round(UKN["pop"] / UKN["T_all"])), "fish_chips_TR": UKN["TR_fish_chips"], "indian_TR": UKN["TR_indian"],
                   "chinese_TR": UKN["TR_chinese"], "pizza_TR": UKN["TR_pizza"], "kebab_TR": UKN["TR_kebab"], "chicken_TR": UKN["TR_chicken"],
                   "n_counties_T_gt_R": int(((CN.T_all > CN.R_all) & (CN["pop"] >= MINPOP_C)).sum()),
                   "n_counties_T_gt_R_any": int((CN.T_all > CN.R_all).sum())}
# how even is each food across counties (coefficient of variation of per-head rates, counties of 100,000+)
cv_ = {}
big = CN[CN["pop"] >= MINPOP_C]
for f in ["fish_chips", "indian", "chinese", "pizza", "kebab", "chicken", "burger"]:
    r_ = per10k(big[f"TR_{f}"], big["pop"]); cv_[f] = r2(r_.std() / r_.mean())
RES["evenness_cv"] = cv_
# the most common named takeaway of the six big kinds in each postcode district (1,000+ residents, 3+ such takeaways)
six = ["fish_chips", "chinese", "indian", "pizza", "kebab", "chicken"]
dd = DT[(DT["pop"] >= 1000)].copy(); m6 = dd[[f"T_{f}" for f in six]].values
ok_ = m6.sum(axis=1) >= 3; lead_ = np.array(six)[m6.argmax(axis=1)]
tie = (m6 == m6.max(axis=1, keepdims=True)).sum(axis=1) > 1
RES["district_lead"] = {"n": int(ok_.sum()), "ties": int((ok_ & tie).sum()), "counts": {f: int(((lead_ == f) & ok_ & ~tie).sum()) for f in six}}
# districts named in the text and on figures, with their rates (takeaways and restaurants per 100,000)
NAMED = ["PE25", "YO15", "YO14", "FY1", "PA34", "NR29", "DN35", "TW3", "UB1", "B5", "M1", "L1"]
RES["named_districts"] = {d: {"pop": int(r["pop"]), "county": r.county, **{f: r1(per10k(r[f"TR_{f}"], r["pop"])) for f in ["fish_chips", "indian", "chinese", "pizza", "kebab", "chicken"]}}
                          for d in NAMED for _, r in DT[DT.district == d].iterrows()}
RES["chicken_top10_london"] = int(sum(1 for c in STORY["chicken"]["county_top"] if CN.loc[CN.name == c["name"], "code"].iloc[0].startswith("E09")))
RES["kebab_top3_london"] = int(sum(1 for c in STORY["kebab"]["county_top"][:3] if CN.loc[CN.name == c["name"], "code"].iloc[0].startswith("E09")))

# Spearman between the fish and chip map and the chicken or kebab map (counties): is it a north/south thing?
CN["lat"] = np.nan
cent = B[B.lat.notna()].groupby("county_code")[["lat", "lon"]].median()
CN = CN.set_index("code").join(cent, rsuffix="_c").reset_index(); CN["lat"] = CN["lat_c"]; CN = CN.drop(columns=["lat_c"])
for f in ["fish_chips", "indian", "chinese", "pizza", "kebab", "chicken"]:
    rho, p = spearmanr(CN.lat, per10k(CN[f"TR_{f}"], CN["pop"]))
    RES.setdefault("lat_rho", {})[f] = r2(rho)

# ---------- chains ----------
chain = B[B.rule.str.startswith("chain:")].copy()
chain["brand"] = chain.rule.str[6:].str.replace("'", "", regex=False).str.replace(r"\s+", " ", regex=True)
brand_norm = {"dominos": "Domino's", "domino s": "Domino's", "papa johns": "Papa John's", "papa john s": "Papa John's", "papajohns": "Papa John's", "pizza hut": "Pizza Hut", "kfc": "KFC", "kentucky fried": "KFC",
              "mcdonalds": "McDonald's", "mcdonald s": "McDonald's", "burger king": "Burger King", "subway": "Subway", "greggs": "Greggs", "costa": "Costa", "starbucks": "Starbucks", "nandos": "Nando's", "nando s": "Nando's",
              "chicken cottage": "Chicken Cottage", "dixy": "Dixy", "morleys": "Morley's", "popeyes": "Popeyes", "five guys": "Five Guys", "wingstop": "Wingstop"}
chain["brand"] = chain.brand.map(lambda b: brand_norm.get(b.strip(), None))
TAK = B[B.g.isin(["T", "R"])]
CH = {}
for f, brands in [("pizza", ["Domino's", "Papa John's", "Pizza Hut"]), ("chicken", ["KFC", "Nando's", "Chicken Cottage", "Dixy", "Morley's", "Popeyes", "Wingstop"]),
                  ("burger", ["McDonald's", "Burger King", "Five Guys"]), ("sandwich", ["Greggs", "Subway"]), ("cafe", ["Costa", "Starbucks"])]:
    n = int((TAK.cuisine == f).sum()); d = {"n_family": n}
    for b in brands:
        k = int(((chain.brand == b) & chain.g.isin(["T", "R"])).sum()); d[b] = {"n": k, "share": pct(k, n)}
    d["big_share"] = pct(sum(d[b]["n"] for b in brands), n)
    CH[f] = d
fc = TAK[TAK.cuisine == "fish_chips"]
CH["fish_chips"] = {"n_family": int(len(fc)), "chain_n": int(fc.rule.str.startswith("chain:").sum()), "chain_share": pct(fc.rule.str.startswith("chain:").sum(), len(fc))}
RES["chains"] = CH

# ---------- hygiene ----------
def hyg(s):
    r = s.rating
    num = pd.to_numeric(r, errors="coerce"); num = num[num.notna()]
    out = {"n_rated": int(len(num))}
    if len(num):
        out.update({"mean": r2(num.mean()), "pct5": pct((num == 5).sum(), len(num)), "pct_le2": pct((num <= 2).sum(), len(num)), "pct0": pct((num == 0).sum(), len(num))})
    sc = r[r.isin(["Pass", "Pass and Eat Safe", "Improvement Required"])]
    out["n_fhis"] = int(len(sc))
    if len(sc):
        out["fhis_pass_pct"] = pct(sc.isin(["Pass", "Pass and Eat Safe"]).sum(), len(sc))
    return out
HY = {"by_type_all_uk": {}}
for t, dct in fh["rdist"].items():
    num = {int(k): v for k, v in dct.items() if k in "012345"}
    n = sum(num.values())
    sc = {k: v for k, v in dct.items() if k in ("Pass", "Pass and Eat Safe", "Improvement Required")}
    m = sum(sc.values())
    HY["by_type_all_uk"][t] = {"n_rated": n, "mean": r2(sum(k * v for k, v in num.items()) / n) if n else None, "pct5": pct(num.get(5, 0), n), "pct_le2": pct(num.get(0, 0) + num.get(1, 0) + num.get(2, 0), n),
                               "n_fhis": m, "fhis_pass_pct": pct(sc.get("Pass", 0) + sc.get("Pass and Eat Safe", 0), m)}
HY["by_family_T"] = {f: hyg(B[(B.g == "T") & (B.cuisine == f)]) for f in FAM + ["other"]}
HY["by_family_TR"] = {f: hyg(B[(B.g.isin(["T", "R"])) & (B.cuisine == f)]) for f in FAM + ["other"]}
HY["by_group"] = {g: hyg(B[B.g == g]) for g in "TRPM"}
HY["chain_vs_indep_T"] = {"chain": hyg(B[(B.g == "T") & B.rule.str.startswith("chain:")]), "independent": hyg(B[(B.g == "T") & ~B.rule.str.startswith("chain:")])}
HY["by_nation_T"] = {n: hyg(B[(B.g == "T") & (B.nation == n)]) for n in ["England", "Wales", "Northern Ireland", "Scotland"]}
HY["by_nation_R"] = {n: hyg(B[(B.g == "R") & (B.nation == n)]) for n in ["England", "Wales", "Northern Ireland", "Scotland"]}
RES["hygiene"] = HY

# ---------- OpenStreetMap cross-check ----------
R_ = 6371000.0
def xy(lat, lon):
    la = np.radians(lat); return np.column_stack([R_ * np.radians(lon) * np.cos(np.radians(54.5)), R_ * la])
FB = B[B.lat.notna() & B.g.isin(["T", "R", "M"])].reset_index(drop=True)
tree = cKDTree(xy(FB.lat.values, FB.lon.values))
Ok = O[(O.name.fillna("") != "")].reset_index(drop=True)
def toks(s): return set(t for t in norm(s).replace("&", " ").split() if t not in {"the", "and", "ltd", "limited", "takeaway", "take", "away", "restaurant", "&"})
pairs = []
for i, nb in enumerate(tree.query_ball_point(xy(Ok.lat.values, Ok.lon.values), r=100)):
    if not nb: continue
    to = toks(Ok.name[i]); best = (0, None)
    for j in nb:
        tf = toks(FB.name[j]); u = to | tf
        sim = len(to & tf) / len(u) if u else 0
        if sim > best[0]: best = (sim, j)
    if best[0] >= 0.5:
        pairs.append((i, best[1], best[0]))
P = pd.DataFrame(pairs, columns=["oi", "fi", "sim"]).sort_values("sim", ascending=False).drop_duplicates("fi")
M = pd.DataFrame({"osm_name": Ok.name[P.oi].values, "osm_cuisine": Ok.cuisine[P.oi].values, "osm_family": Ok.family[P.oi].values,
                  "fsa_name": FB.name[P.fi].values, "fsa_type": FB.type[P.fi].values, "classifier": FB.cuisine[P.fi].values, "sim": P.sim.values})
M.to_csv(os.path.join(DATA, "osm_matches.csv.gz"), index=False, compression="gzip")
fam_known = M[M.osm_family.notna() & (M.osm_family != "unmapped")]
both = fam_known[fam_known.classifier != "other"]
OSMR = {"n_osm": int(len(O)), "n_osm_named": int(len(Ok)), "n_osm_cuisine": int(O.cuisine.fillna("").ne("").sum()), "pct_osm_cuisine": pct(O.cuisine.fillna("").ne("").sum(), len(O)),
        "n_matched": int(len(M)), "n_matched_family": int(len(fam_known)), "n_both": int(len(both)),
        "agree_pct": pct((both.osm_family == both.classifier).sum(), len(both)),
        "classifier_other_with_osm_family": int((fam_known.classifier == "other").sum()),
        "recall_pct": pct((fam_known.classifier == fam_known.osm_family).sum(), len(fam_known))}
per = {}
for f in FAM:
    a = both[both.classifier == f]; b = fam_known[fam_known.osm_family == f]
    per[f] = {"n_classified": int(len(a)), "precision_pct": pct((a.osm_family == f).sum(), len(a)), "n_osm": int(len(b)), "recall_pct": pct((b.classifier == f).sum(), len(b))}
OSMR["per_family"] = per
oth = fam_known[fam_known.classifier == "other"].osm_family.value_counts()
OSMR["other_breakdown"] = {k: int(v) for k, v in oth.head(8).items()}
# do the two sources draw the same map? district counts, Spearman over districts with population >= MINPOP
O["fam2"] = O.family
for f in ["fish_chips", "indian", "chinese", "pizza", "kebab", "chicken"]:
    oc = O[O.fam2 == f].groupby("district").size().reindex(DT.district).fillna(0).values
    fc_ = DT[f"TR_{f}"].values; m = DT["pop"].values >= MINPOP
    rho, _ = spearmanr(oc[m] / DT["pop"].values[m], fc_[m] / DT["pop"].values[m])
    rho_c, _ = spearmanr(O[O.fam2 == f].groupby("county").size().reindex(CN.name).fillna(0).values / CN["pop"].values, CN[f"TR_{f}"].values / CN["pop"].values)
    OSMR.setdefault("rho_district", {})[f] = r2(rho); OSMR.setdefault("rho_county", {})[f] = r2(rho_c)
RES["osm"] = OSMR

# ---------- the hand-checked samples ----------
# Sample A (450 names) was used while the rules were being written; sample B (300 names) was drawn and
# labelled afterwards and is the honest, held-out estimate reported on the page and in the paper.
def wilson(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [r1(100 * (c - h) / d), r1(100 * (c + h) / d)]
from manual_labels import LABELS_B
def score(path, labels, tag):
    S = pd.read_csv(os.path.join(DATA, path), keep_default_na=False)
    S["manual"] = S.k.map(labels)
    S["classifier"] = [classify(n)[0] for n in S.name]
    S["rule"] = [classify(n)[1] for n in S.name]
    S["ok"] = [c in m.split("|") for c, m in zip(S.classifier, S.manual)]
    S["classified"] = S.classifier != "other"; S["manual_known"] = S.manual != "unknown"
    out = {}
    for grp, s_ in [("all", S), ("T", S[S.group == "T"]), ("R", S[S.group == "R"])]:
        cl_ = s_[s_.classified]; kn = s_[s_.manual_known]
        out[grp] = {"n": int(len(s_)), "n_classified": int(len(cl_)), "classified_pct": pct(len(cl_), len(s_)), "precision_pct": pct(int(cl_.ok.sum()), len(cl_)),
                    "precision_ci": wilson(int(cl_.ok.sum()), len(cl_)), "n_known": int(len(kn)), "known_pct": pct(len(kn), len(s_)),
                    "recall_pct": pct(int(kn.ok.sum()), len(kn)), "recall_ci": wilson(int(kn.ok.sum()), len(kn)),
                    "false_other": int(((s_.classifier == "other") & s_.manual_known).sum()),
                    "wrong_family": int((s_.classified & ~s_.ok & s_.manual_known).sum()),
                    "named_unknown_but_classified": int((s_.classified & ~s_.manual_known).sum())}
    out["errors"] = [{"name": r["name"], "classifier": LABEL[r.classifier], "checked": r.manual} for _, r in S[S.classified & ~S.ok].iterrows()]
    out["missed"] = [{"name": r["name"], "checked": r.manual} for _, r in S[(S.classifier == "other") & S.manual_known].iterrows()]
    S.insert(0, "sample", tag)
    return out, S[["sample", "k", "group", "fhrsid", "name", "classifier", "rule", "manual", "ok"]]
accA, SA = score("_sample_names.csv", LABELS, "A (development)")
accB, SB = score("_sample_names_b.csv", LABELS_B, "B (held out)")
RES["accuracy"] = {"A": accA, "B": accB}
pd.concat([SB, SA]).to_csv(os.path.join(DATA, "accuracy_sample.csv"), index=False)
ACC = RES["accuracy"]

# ---------- write tables ----------
keep = ["district", "pop", "pop_source", "county", "nation", "lat", "lon", "area_km2", "T_all", "R_all", "P_all", "M_all", "TR_all"] + \
       [f"T_{f}" for f in FAM] + [f"R_{f}" for f in FAM] + [f"M_{f}" for f in FAM] + [f"n_{t}" for t in [7844, 1, 7843, 7846, 7, 7838, 5, 7842, 14, 7839, 7841, 4613, 7840, 7845]] + ["n_all"]
DT[keep].to_csv(os.path.join(DATA, "districts.csv"), index=False)
ck = ["code", "name", "nation", "pop", "pop_year", "T_all", "R_all", "P_all", "M_all", "TR_all"] + [f"T_{f}" for f in FAM] + [f"R_{f}" for f in FAM] + [f"M_{f}" for f in FAM]
CN[ck].to_csv(os.path.join(DATA, "counties.csv"), index=False)

# ---------- page data ----------
fams = FAM
def row(r, name):
    return [name, int(r["pop"]) if pd.notna(r["pop"]) else 0] + [int(r[f"T_{f}"]) for f in fams] + [int(r[f"R_{f}"]) for f in fams] + [int(r.T_all), int(r.R_all), int(r.P_all), int(r.M_all)]
CI = {c: i for i, c in enumerate(pd.read_csv(os.path.join(DATA, "_counties_index.csv")).code)}
page = {"fams": [[f, LABEL[f]] for f in fams], "cols": "name,pop,T_x16,R_x16,T_all,R_all,P_all,M_all",
        "districts": [row(r, r.district) + [CI.get(CN.code[CN.name == r.county].iloc[0], -1) if isinstance(r.county, str) and (CN.name == r.county).any() else -1,
                                            r2(r.lat) if pd.notna(r.lat) else None, r2(r.lon) if pd.notna(r.lon) else None] for _, r in DT.iterrows()],
        "counties": [None] * len(CI)}
for _, r in CN.iterrows():
    page["counties"][CI[r.code]] = row(r, r["name"]) + [r.nation, r2(r.lat) if pd.notna(r.lat) else None, r2(r.lon) if pd.notna(r.lon) else None]
json.dump(page, open(os.path.join(DATA, "page.json"), "w"), separators=(",", ":"), ensure_ascii=False)

# points per family, for the zoomed-in view: lat, lon, group (0 takeaway, 1 restaurant, 2 mobile), rating, name
os.makedirs(os.path.join(DATA, "points"), exist_ok=True)
GI = {"T": 0, "R": 1, "M": 2}
for f in fams:
    s = B[(B.cuisine == f) & B.lat.notna() & B.g.isin(["T", "R", "M"])]
    pts = [[round(a, 4), round(b, 4), GI[g], rt if isinstance(rt, str) else "", n] for a, b, g, rt, n in zip(s.lat, s.lon, s.g, s.rating, s.name)]
    json.dump(pts, open(os.path.join(DATA, "points", f + ".json"), "w"), separators=(",", ":"), ensure_ascii=False)

json.dump(RES, open(os.path.join(DATA, "results.json"), "w"), indent=1, ensure_ascii=False, default=lambda o: int(o) if isinstance(o, np.integer) else float(o))
print(json.dumps({k: RES[k] for k in ["n_rows", "geocoded_pct", "county_pct", "district_pct", "pop_total"]}, indent=0))
print("classified", {g: v["classified_pct"] for g, v in cls.items()})
print("accuracy B", {k: v for k, v in ACC["B"].items() if k not in ("errors","missed")}); print("A", {k: v for k, v in ACC["A"].items() if k not in ("errors","missed")}); print(ACC["B"]["errors"]); print(ACC["B"]["missed"])
print("osm", {k: v for k, v in OSMR.items() if k not in ("per_family",)})
for f in ["fish_chips", "indian", "chinese", "pizza", "kebab", "chicken"]:
    print(f, STORY[f]["county_top"][:3], STORY[f]["district_top"][:3])
print("ratio", STORY["ratio"]["county_top"][:3], STORY["ratio"]["county_bottom"][:3])

# published business tables (split so that no file is over 9 MB): what the FSA publishes plus the
# derived postcode district, county and the classifier's family and rule
cols = ["fhrsid", "name", "type", "postcode", "district", "lat", "lon", "rating", "ratingYear", "la_name", "county", "nation", "cuisine", "rule"]
B[B.g.isin(["T", "M"])][cols].to_csv(os.path.join(DATA, "businesses_takeaways_mobile.csv.gz"), index=False, compression="gzip")
B[B.g.isin(["R", "P"])][cols].to_csv(os.path.join(DATA, "businesses_restaurants_pubs.csv.gz"), index=False, compression="gzip")
