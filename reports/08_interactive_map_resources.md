# Interactive map: resources and data contract

**Implemented:** 15 October 2026 in `../dashboard.html`.

## Selected stack

| Need | Resource | Why it fits |
| --- | --- | --- |
| Pan, wheel zoom, hover, click, fit to country, keyboard zoom | [Leaflet 1.9.4](https://leafletjs.com/examples/choropleth/) | Lightweight GeoJSON choropleth and interaction controls. Vendored JS, CSS, and BSD license are in `../app/vendor/`; the report runs offline. |
| World country outlines | [Natural Earth 1:50m Admin 0](https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/) | Public-domain general-reference boundaries, joined to WHO ISO3 country codes. |
| Province/state outlines | [Natural Earth 1:10m Admin 1](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/) | First-order boundaries for the country drilldown. 4,386 shapes cover all 195 WHO-screen countries after known code aliases for Palestine and South Sudan. |
| Smaller offline geometry | [Mapshaper](https://mapshaper.org/docs/essentials/command-line.html) | Topology-aware simplification reduces the boundary payload to about 3.2 MB without dropping selected features. Rebuilt by `../scripts/prepare_map_geometry.py`. |
| National vaccine values | [WHO/UNICEF estimates](https://www.who.int/news-room/questions-and-answers/item/who-unicef-estimates-of-national-immunization-coverage) | MCV1 and MCV2 estimates for the map color and country tooltip. |

No paid mapping service, map API key, or additional Codex plugin is required for this feature. The data visualization and geospatial skill guidance informed the design; Leaflet is the runtime mapping library.

## Meaning of the two map levels

The world map colors countries by **national 2025 coverage**. The tooltip shows national MCV1 and MCV2. Clicking a country displays **province/state outlines and names** plus the national evidence in a separate panel. The outlines have no WHO vaccination value. A public country-level district summary cannot be assigned to an individual province or district.

WHO reports subnational data from some countries at Admin 1 or Admin 2, and the detailed named-area extract has a [data request process](https://immunizationdata.who.int/docs/librariesprovider21/additional-datasets/how-to-access-more-data.pdf?sfvrsn=ee878941_1). When that extract is obtained, the next step is to validate its area identifiers, administrative level, reporting year, and denominator before joining it to polygons. Some WHO reported areas may not match Natural Earth's province names or boundaries. [WHO subnational coverage](https://www.who.int/teams/immunization-vaccines-and-biologicals/Immunization-data-and-decision-making/global-monitoring/immunization-coverage/subnational-immunization-coverage-data)

## Alternative for the later subnational join

[geoBoundaries](https://github.com/wmgeolab/geoBoundaries/blob/main/README.md) provides simplified, country-specific Admin 1 and Admin 2 geometry through an API. It may match some named-area datasets more closely than Natural Earth, but its area naming, source year, license metadata, and boundary interpretation must be checked country by country before using it for coverage. The current dashboard avoids remote calls and keeps Natural Earth as a neutral reference layer.

**Boundary note:** Natural Earth represents de facto boundaries; its geography may differ from WHO or national boundary conventions. The polygons are visual reference only. [Natural Earth terms](https://www.naturalearthdata.com/about/terms-of-use/)
