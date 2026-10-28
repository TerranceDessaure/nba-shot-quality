"""Step 2 of the Shot Quality project: calculate how many points a shot from
each zone is worth on average across the whole league (the "expected points"
baseline), and save it back to the database."""

import sqlite3

import pandas as pd

DB_PATH = "nba_shots.db"

QUERY = """
SELECT
    SHOT_ZONE_BASIC,
    SHOT_ZONE_AREA,
    COUNT(*) AS attempts,
    AVG(SHOT_MADE_FLAG) AS fg_pct,
    AVG(SHOT_MADE_FLAG * CASE WHEN SHOT_TYPE = '3PT Field Goal' THEN 3 ELSE 2 END)
        AS expected_points
FROM shots
GROUP BY SHOT_ZONE_BASIC, SHOT_ZONE_AREA
HAVING COUNT(*) >= 100
ORDER BY expected_points DESC
"""


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as conn:
        zones = pd.read_sql(QUERY, conn)
        zones.to_sql("zone_expected", conn, if_exists="replace", index=False)

    print(zones.round(3).to_string(index=False))
    print(f"\nSaved {len(zones)} zones to the zone_expected table in {DB_PATH}")