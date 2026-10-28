# Reddit post

## Title

[OC] Chips, curry or kebab? I sorted all 62,949 UK takeaways on the food hygiene register by what their names say they sell. This is the most common named takeaway in each postcode district, plus six per head maps

## Body

The Food Standards Agency publishes every inspected food business in the UK, but not what food it sells. So I sorted the names (Jubilee Fish Bar, Simla Tandoori, Happy Garden) into kinds of food with simple keyword rules. Fish and chips is the most common named takeaway in 556 postcode districts, pizza in 423, Chinese in 390. Per head, the chip shop capital is the seaside (Skegness, 130 per 100,000 residents) and the curry capital is Hounslow (TW3, 92). In a held-out sample of 300 names, each labelled individually by reading the name (as part of the AI-assisted analysis, reviewed by me), 96.7% of the rules' answers were right. Caveat: about a third of takeaways have names that do not say what they sell (Tasty Bite, Munchies), so every count is a floor.

Interactive map: https://maps.tristanhotham.com/takeaways/

## Source comment

Source: Food Standards Agency food hygiene ratings open data (FHRS and FHIS API, all 614,680 establishments, retrieved 2026-10-28), Open Government Licence v3.0. Populations: ONS Census 2021 postcode district counts (Nomis) and mid-2025 estimates; National Records of Scotland, Scotland's Census 2022 postcode counts; NISRA Census 2021 postcode district counts; all OGL v3.0. Boundaries: ONS Open Geography Portal, Counties and Unitary Authorities December 2023 (OGL v3.0). Cuisine cross-check: OpenStreetMap contributors via the Overpass API, ODbL.

Tools: Python (pandas, numpy, scipy, shapely, pyproj, matplotlib) for the analysis and the chart; Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/takeaways/
Blog post: https://blog.tristanhotham.com/2026/10/28/takeaways/
Paper and data: https://doi.org/10.5281/zenodo.23748252
