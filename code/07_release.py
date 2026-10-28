"""Step 7: blog post (release/blog/post.html, meta.json) and the Zenodo folder (release/zenodo/).
Run: python3 code/07_release.py
"""
import json, os, re, shutil, zipfile, glob

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
REL = os.path.join(ROOT, "release"); BLOG = os.path.join(REL, "blog"); ZEN = os.path.join(REL, "zenodo")
DOI = "10.5281/zenodo.23748252"; SLUG = "takeaways"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"; GH = f"https://github.com/Tristan-Hotham/{SLUG}"


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f in (None, "", "raw"): return str(v)
    if f == "int": return f"{round(v):,}"
    if f == "f1": return f"{v:,.1f}"
    if f == "f2": return f"{v:.2f}"
    raise ValueError(f)


def fill(t):
    return re.sub(r"\{\{(?!IMG\|)([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(m.group(1)), m.group(3)), t)


post = fill(open(os.path.join(HERE, "blog_template.html")).read())
for name in re.findall(r"\{\{IMG\|([^|]+)\|", post):
    assert os.path.exists(os.path.join(BLOG, name)), name
open(os.path.join(BLOG, "post.html"), "w").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG[^}]*\}\}", " ", post).split())
print("blog words", words)

json.dump({"title": "Chips, curry or kebab? The UK's takeaway map", "slug": SLUG,
           "excerpt": f"I sorted all {R['n_T']:,} takeaways and {R['n_R']:,} restaurants on the UK's food hygiene register by what their names say they sell. The chip shop capital is the seaside, the curry capital is Hounslow, and the old Chinatowns still show.",
           "seo_description": "Every UK takeaway sorted by name and mapped per head: chip shop capitals, curry capitals, Chinatowns, kebabs and chicken shops.",
           "tags": ["takeaways", "fish and chips", "food", "maps", "Food Standards Agency", "open data", "UK", "data"],
           "header_alt": "Title card reading 'Chips, curry or kebab?' in gold, red and brown on pale paper, beside a map of the UK coloured in shades of blue by chip shops per 100,000 residents in each postcode district. Text: 62,949 takeaways and 141,306 restaurants and cafes, sorted by name and counted per head for every postcode district."},
          open(os.path.join(BLOG, "meta.json"), "w"), indent=2, ensure_ascii=False)

# Zenodo
os.makedirs(ZEN, exist_ok=True)
for f in glob.glob(os.path.join(ZEN, "*")): os.remove(f)
shutil.copy(os.path.join(REL, "Hotham_Takeaways.pdf"), ZEN)
for f in ["districts.csv", "counties.csv", "accuracy_sample.csv", "businesses_takeaways_mobile.csv.gz", "businesses_restaurants_pubs.csv.gz", "results.json"]:
    shutil.copy(os.path.join(ROOT, "data", f), ZEN)
with zipfile.ZipFile(os.path.join(ZEN, f"{SLUG}_code_and_data.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for f in ["README.md", "LICENSE"]: z.write(os.path.join(ROOT, f), f)
    for d in ["code", "data"]:
        for p in glob.glob(os.path.join(ROOT, d, "**", "*"), recursive=True):
            if os.path.isfile(p) and "__pycache__" not in p and not os.path.basename(p).startswith(("_businesses", "businesses_")) and not p.endswith("_districts_base.csv"):
                z.write(p, os.path.relpath(p, ROOT))
abstract = open(os.path.join(ROOT, "release", "paper", "Hotham_Takeaways.tex")).read()
abstract = abstract.split("\\begin{center}\\textbf{Abstract}\\end{center}")[1].split("\\textbf{Keywords:}")[0].strip()
abstract = abstract.replace("\\%", "%").replace("\\textit{", "").replace("}", "").replace("\\&", "&")
json.dump({"title": "Chips, Curry or Kebab? The United Kingdom's Takeaways and Restaurants by Name, per Head and by Place",
           "description_html": f"<p>{abstract}</p><p>Interactive version: {PAGE}. Data and code: {GH}. Blog post: to follow.</p>",
           "keywords": ["takeaways", "restaurants", "food hygiene ratings", "Food Standards Agency", "name classification", "OpenStreetMap", "postcode districts", "food geography", "United Kingdom", "open data"],
           "licence": "cc-by-4.0",
           "related": [{"identifier": GH, "relation": "issupplementedby", "resource_type": "software"},
                       {"identifier": PAGE, "relation": "issupplementedby", "resource_type": "other"},
                       {"identifier": "https://api.ratings.food.gov.uk/", "relation": "isderivedfrom", "resource_type": "dataset"},
                       {"identifier": "https://www.nomisweb.co.uk/output/census/2021/pcdd_p004.csv", "relation": "isderivedfrom", "resource_type": "dataset"},
                       {"identifier": "https://www.nomisweb.co.uk/api/v01/dataset/NM_2002_1", "relation": "isderivedfrom", "resource_type": "dataset"},
                       {"identifier": "https://www.nisra.gov.uk/publications/census-2021-person-and-household-estimates-postcodes-northern-ireland", "relation": "isderivedfrom", "resource_type": "dataset"},
                       {"identifier": "https://maps.gov.scot/server/rest/services/NRS/Census2022/MapServer", "relation": "isderivedfrom", "resource_type": "dataset"},
                       {"identifier": "https://geoportal.statistics.gov.uk/", "relation": "isderivedfrom", "resource_type": "dataset"},
                       {"identifier": "https://www.openstreetmap.org/", "relation": "isderivedfrom", "resource_type": "dataset"}]},
          open(os.path.join(ZEN, "meta.json"), "w"), indent=2, ensure_ascii=False)
for f in sorted(os.listdir(ZEN)): print(f, os.path.getsize(os.path.join(ZEN, f)))
