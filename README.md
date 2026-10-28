# Chips, curry or kebab? The UK's takeaway map

Every takeaway and restaurant on the UK's food hygiene register, sorted by what its name says it sells, and counted per head for every postcode district and every county and unitary authority. The interactive page lets you pick a kind of food, switch between takeaways, restaurants or both, between postcode districts and counties, and between places per 100,000 people and the share of an area's places; search a town, a postcode district or a postcode; and zoom in to see every place as a dot. A "Map layers" panel adds a base map, hills, place names, map labels and county borders.

**Interactive version:** https://maps.tristanhotham.com/takeaways/

**Paper and archived release:** https://doi.org/10.5281/zenodo.23748252

A data study by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349).

## Headline results

- The Food Standards Agency register held 614,680 food businesses on 2026-10-28, including 62,949 takeaways and sandwich shops (one for every 1,104 people) and 141,306 restaurants, cafes and canteens.
- Keyword rules on the names give a kind of food to 65.0% of takeaways. In a held-out sample of 300 names, each labelled individually by reading the name, as part of the AI-assisted analysis, and reviewed by the author, 96.7% of the rules' answers were right (95% interval 93.0 to 98.5%); they caught 90.3% of names that plainly say the food. Against 21,351 matched OpenStreetMap places with a cuisine tag they agree 91.7%.
- Fish and chips is the commonest named takeaway (7,358), ahead of pizza (7,055) and Chinese (6,908).
- Chip shop capital: Blackpool (34.1 per 100,000 people among council areas of 100,000 or more); by postcode district, the resorts: Skegness PE25 (129.6), Bridlington YO15 (90.4), Filey YO14 (69.7).
- Curry capital: Hounslow (29.4); by district Hounslow's TW3 (91.9) and Southall's UB1 (72.9).
- Chinese places peak in the old Chinatowns: Birmingham B5 (182.9), Manchester M1 (144.1), Liverpool L1 (112.4). Kebabs lead in Islington, Hackney and Enfield; all ten top council areas for chicken shops are London boroughs.
- Scotland has the most takeaways per head (112.4 per 100,000; England 88.0); Wales the most chip shops (17.8); Northern Ireland the most pizza places (16.1).
- UK: 0.45 takeaways per restaurant. Takeaways outnumber restaurants in only 4 council areas of 100,000 or more (North Lanarkshire 1.33, Rochdale, Caerphilly, Sunderland); Westminster has 0.08.
- Hygiene: 61.4% of rated takeaways have a 5, against 75.6% of restaurants; Japanese and sushi takeaways 85.6%, Indian 44.7%; chain takeaways 84.4% against independents 58.4%.

Every number is in `data/results.json`, which the page, paper, blog and collage are built from.

## Files

| Path | What it is |
|---|---|
| `index.html` | The interactive page (results embedded; the grid, tables, boundaries, places and dots are loaded from `data/`). |
| `header.png` | Social card (1200 by 630). |
| `data/districts.csv` | Every postcode district with residents: population and its source, county, nation, centre, drawn area, counts of takeaways (`T_`), restaurants (`R_`) and mobile caterers (`M_`) by kind of food, pubs, and counts of all fourteen FSA business types (`n_<type id>`). |
| `data/counties.csv` | The same counts for the 218 counties and unitary authorities, with ONS mid-2025 populations. |
| `data/businesses_takeaways_mobile.csv.gz`, `data/businesses_restaurants_pubs.csv.gz` | Every takeaway, mobile caterer, restaurant and pub: FSA id, name, type, postcode, district, point, rating, rating year, council, county, nation, and the classifier's family and the rule that fired. |
| `data/accuracy_sample.csv` | Both labelled samples (A development, B held out) with the rules' answer and the checked label. |
| `data/_sample_names.csv`, `data/_sample_names_b.csv` | The two random samples as drawn. |
| `data/osm_uk.csv.gz`, `data/osm_matches.csv.gz` | OpenStreetMap fast food and restaurants in the UK with cuisine and family; matches to the register (ODbL). |
| `data/grid/districts.png`, `meta.json` | The page's 750 m Web Mercator grid: approximate postcode district (R*256+G) and county (B) of every land square. |
| `data/page.json`, `data/counties.geojson`, `data/places.json`, `data/points/*.json` | Compact tables for the page, simplified county boundaries, place names for labels and search, and each kind of food as dots. |
| `data/results.json` | Every number used anywhere. |
| `code/classify.py` | The name rules, and the OpenStreetMap cuisine mapping. |
| `code/manual_labels.py` | The labels for both samples (labelled individually by reading the name, as part of the AI-assisted analysis, and reviewed by the author). |
| `code/01_prepare.py` | Reads the raw bundles, classifies names, assigns counties, draws district areas, writes the grid and tables. |
| `code/02_analyse.py` | All statistics, the accuracy and OpenStreetMap checks, page data. |
| `code/03_build_site.py` | Fills `code/page_template.html` from `results.json` and checks facts stated in words. |
| `code/04_header.py`, `code/05_figures.py`, `code/figlib.py`, `code/palette.py` | Social card and static figures (matplotlib). |
| `code/06_paper.py`, `code/paper_template.tex` | The paper (xelatex). |
| `code/07_release.py`, `code/blog_template.html` | Blog post, blog and Zenodo metadata, Zenodo folder. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `release/` | Paper PDF and source, blog post and figures, Zenodo files. |

## Method in brief

- **Register.** FSA ratings API v2, all establishments of all fourteen business types, retrieved 2026-10-28 through a browser and reduced to the fields used. Scotland's businesses are in the same register (Food Hygiene Information Scheme).
- **Names.** Chains first, then strong words, then (only if nothing strong fires) weak hints; hybrids go to the first family in a fixed order. Pubs are not sorted.
- **Checks.** Two random samples, each name labelled individually by reading the name, as part of the AI-assisted analysis, and reviewed by the author (A while writing the rules; B afterwards, reported). OpenStreetMap places matched within 100 m by shared name words.
- **People.** Census 2021 (England, Wales, Northern Ireland) and Scotland's Census 2022 counts by postcode district; ONS mid-2025 estimates for counties and unitary authorities. Each business takes its inspecting council's county.
- **Areas.** Approximate postcode district shapes on a 750 m grid from the nearest labelled points; for display only. Rankings use districts of 10,000+ and council areas of 100,000+ residents.

## Known limits

- 111 business names containing en or em dashes are written with plain hyphens in the published files.

- Every count is a floor: about a third of takeaways and over half of restaurants have names that do not say what they sell (OpenStreetMap suggests many are Chinese, Indian and Italian).
- Councils assign business types differently, so the takeaway to restaurant ratio is a broad pattern.
- The register lists inspected premises; openings and closures lag, and delivery-only kitchens and multi-brand kitchens may appear once or several times.
- City centres and resorts have high rates per resident because their places serve visitors and workers.
- Mobile caterers are registered at a base address and are left off the maps.
- District populations come from the 2021 and 2022 censuses; county populations from mid-2025 estimates.

## How to rerun

The raw bundles (gzipped JSON fetched in a browser from the FSA API, Nomis, ONS Open Geography, maps.gov.scot and Overpass, plus the NISRA district table) are read in place from `RAW` (default `/home/claude/hist/_data18/takeaways`); place names from the sun-and-rain-uk project's `places_search.json` (`PLACES`).

```
python3 code/01_prepare.py
python3 code/02_analyse.py
python3 code/03_build_site.py
FONT_DIR=path/to/fonts python3 code/04_header.py
FONT_DIR=path/to/fonts python3 code/05_figures.py
python3 code/06_paper.py
python3 code/07_release.py
```

Needs Python 3 with numpy, pandas, scipy, shapely, pyproj, Pillow and matplotlib, and xelatex with TeX Gyre Pagella and Inter for the paper.

## Sources and licences

- Food Standards Agency, Food Hygiene Rating Scheme and Food Hygiene Information Scheme open data (https://api.ratings.food.gov.uk/), Open Government Licence v3.0.
- Office for National Statistics: Census 2021 usual residents by postcode district (P004) and mid-year population estimates, via Nomis; Counties and Unitary Authorities (December 2023) boundaries, ONS Open Geography Portal (contains OS data © Crown copyright and database right). Open Government Licence v3.0.
- National Records of Scotland: Scotland's Census 2022 postcode population (maps.gov.scot). Open Government Licence v3.0.
- NISRA: Census 2021 person and household estimates for postcodes in Northern Ireland. Open Government Licence v3.0.
- © OpenStreetMap contributors, Open Database Licence 1.0, via the Overpass API.
- Place names: OS Open Names (OGL v3.0) and GeoNames (CC BY 4.0). Postcode look-ups on the page: postcodes.io. Map tiles: Esri. Map library: Leaflet.

Data files: Open Government Licence v3.0, except `osm_*` (ODbL 1.0). Text and figures: CC BY 4.0. Code: MIT (see `LICENSE`).

## Citation

Hotham, T. (2026) Chips, Curry or Kebab? The United Kingdom's Takeaways and Restaurants by Name, per Head and by Place. Zenodo. https://doi.org/10.5281/zenodo.23748252

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
