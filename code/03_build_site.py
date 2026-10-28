"""Step 3: build index.html from code/page_template.html.

Every number in the text is a {{path|format}} token filled from data/results.json, so the page cannot
drift from the analysis. Facts the template states in words are checked against the data first.
Run: python3 code/03_build_site.py
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from palette import FCOL
R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
GM = json.load(open(os.path.join(ROOT, "data", "grid", "meta.json")))


def get(path):
    v = R
    for k in re.split(r"\.(?![^\[]*\])", path):
        m = re.fullmatch(r'(\w+)\["(.+)"\]', k)
        if m:
            v = v[m.group(1)][m.group(2)]; continue
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(v):,}"
    if f == "f1": return f"{v:,.1f}"
    if f == "f2": return f"{v:.2f}".replace("-", "−")
    raise ValueError(f)


def sub(m):
    return fmt(get(m.group(1)), m.group(3))


def check():
    """Facts the page, paper, blog and collage state in words."""
    S = R["stories"]
    names = lambda L, k=3: [x["name"] for x in L[:k]]
    assert S["fish_chips"]["county_top"][0]["name"] == "Blackpool"
    assert names(S["fish_chips"]["district_top"], 3) == ["PE25", "YO15", "YO14"]          # Skegness, Bridlington, Filey
    assert S["indian"]["district_top"][0]["name"] == "TW3" and S["indian"]["district_top"][2]["name"] == "UB1"  # Hounslow, Southall
    assert S["indian"]["county_top"][0]["name"] == "Hounslow"
    assert names(S["chinese"]["district_top"], 3) == ["B5", "M1", "L1"]                    # Chinese Quarter and Chinatowns
    assert names(S["kebab"]["county_top"], 3) == ["Islington", "Hackney", "Enfield"]
    assert S["pizza"]["county_top"][0]["name"] == "North East Lincolnshire"
    assert R["chicken_top10_london"] == 10
    N = R["nations"]
    assert max(["England", "Wales", "Scotland", "Northern Ireland"], key=lambda n: N[n]["T_all_100k"]) == "Scotland"
    assert N["Scotland"]["TR_chinese_100k"] > N["England"]["TR_chinese_100k"]
    for f in ("TR_fish_chips_100k", "TR_kebab_100k"):
        assert max(["England", "Wales", "Scotland", "Northern Ireland"], key=lambda n: N[n][f]) == "Wales"
    for f in ("TR_kebab_100k", "TR_chicken_100k"):
        assert sorted(["England", "Wales", "Scotland", "Northern Ireland"], key=lambda n: N[n][f])[:2] == ["Northern Ireland", "Scotland"]
    assert max(["England", "Wales", "Scotland", "Northern Ireland"], key=lambda n: N[n]["TR_indian_100k"]) == "Scotland"
    assert max(["England", "Wales", "Scotland", "Northern Ireland"], key=lambda n: N[n]["TR_pizza_100k"]) == "Northern Ireland"
    assert [x["name"] for x in S["ratio"]["county_top"][:R["headline"]["n_counties_T_gt_R"]]] == ["North Lanarkshire", "Rochdale", "Caerphilly", "Sunderland"]
    big = ["fish_chips", "indian", "chinese", "pizza", "kebab", "chicken"]
    assert sorted(big, key=lambda f: R["evenness_cv"][f])[:2] in (["chinese", "indian"], ["indian", "chinese"])
    assert R["lat_rho"]["chinese"] > 0.3 and R["lat_rho"]["kebab"] < -0.3 and R["lat_rho"]["chicken"] < -0.3
    assert 0 < R["headline"]["n_counties_T_gt_R"] <= 6
    H = R["hygiene"]["by_family_T"]
    ok = [f for f in H if f != "other" and H[f]["n_rated"] >= 150]
    assert max(ok, key=lambda f: H[f]["pct5"]) == "japanese" and min(ok, key=lambda f: H[f]["pct5"]) == "indian"
    assert R["hygiene"]["chain_vs_indep_T"]["chain"]["pct5"] > R["hygiene"]["chain_vs_indep_T"]["independent"]["pct5"]
    assert {m["name"] for m in R["accuracy"]["B"]["missed"]} >= {"Erawan", "Chettinad"}
    assert list(R["osm"]["other_breakdown"])[:3] == ["chinese", "indian", "italian"]


if __name__ == "__main__":
    check()
    tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
    html = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", sub, tpl)
    slim = {k: R[k] for k in ("stories", "nations", "chains", "hygiene", "accuracy", "osm", "headline")}
    slim["accuracy"] = {"B": {k: v for k, v in R["accuracy"]["B"].items() if k in ("T", "R", "all")}}
    slim["osm"] = {k: v for k, v in R["osm"].items() if not isinstance(v, (dict, list))}
    html = html.replace("/*RESULTS*/", json.dumps(slim, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("/*GRIDMETA*/", json.dumps({k: GM[k] for k in ("W", "H", "px_m", "west", "east", "south", "north")}))
    html = html.replace("/*FCOL*/", json.dumps(FCOL))
    assert "{{" not in html and "/*" not in html.split("<script>")[1][:200]
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html))
