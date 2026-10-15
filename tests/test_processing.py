"""Small contract tests for the analytical rules and packaged map geometry."""

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_global_screen import district_metrics  # noqa: E402
from build_dashboard import numeric  # noqa: E402
from prepare_map_geometry import slim  # noqa: E402


class ProcessingTests(unittest.TestCase):
    def test_district_arithmetic_and_missingness(self):
        good = {"CALC_DIST_95MCV1_P": "25", "DIST_95_NUMBER_DISTRICTS_MCV1": "1", "DIST_TOTAL_NUMBER": "4"}
        self.assertEqual(district_metrics(good, "MCV1")["district_mcv1_quality"], "corroborated")
        inconsistent = {**good, "CALC_DIST_95MCV1_P": "80"}
        self.assertEqual(district_metrics(inconsistent, "MCV1")["district_mcv1_quality"], "inconsistent_count_or_denominator")
        missing = {**good, "CALC_DIST_95MCV1_P": ""}
        self.assertEqual(district_metrics(missing, "MCV1")["district_mcv1_quality"], "missing_percent")

    def test_blank_is_not_zero(self):
        self.assertIsNone(numeric(""))
        self.assertEqual(numeric("0"), 0)

    def test_who_code_aliases_in_boundary_join(self):
        features = [
            {"type": "Feature", "properties": {"ADM0_A3": "SDS", "NAME": "S. Sudan"}, "geometry": {"type": "Polygon", "coordinates": []}},
            {"type": "Feature", "properties": {"ADM0_A3": "PSX", "NAME": "Palestine"}, "geometry": {"type": "Polygon", "coordinates": []}},
        ]
        result = slim(features, "ADM0_A3", {"SSD", "PSE"}, "NAME")
        self.assertEqual({feature["properties"]["iso3"] for feature in result["features"]}, {"SSD", "PSE"})

    def test_packaged_geometry_covers_same_countries(self):
        world = json.loads((ROOT / "data/geo/world_simplified.geojson").read_text(encoding="utf-8"))["features"]
        admin1 = json.loads((ROOT / "data/geo/admin1_simplified.geojson").read_text(encoding="utf-8"))["features"]
        self.assertEqual(len(world), 195)
        self.assertEqual(len(admin1), 4386)
        self.assertEqual({f["properties"]["iso3"] for f in world}, {f["properties"]["iso3"] for f in admin1})


if __name__ == "__main__":
    unittest.main()
