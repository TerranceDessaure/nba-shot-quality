"""Step 2 of the Shot Quality project: calculate how many points a shot from
each zone is worth on average across the whole league (the "expected points"
baseline), and save it back to the database.

Shots are grouped by zone AND shot type, so a dunk isn't compared to a
contested layup from the same spot."""

import sqlite3

import pandas as pd

DB_PATH = "nba_shots.db"

SHOT_TYPES_VIEW = """
DROP VIEW IF EXISTS shots_typed;
CREATE VIEW shots_typed AS
SELECT *,
    CASE
        WHEN ACTION_TYPE LIKE '%Dunk%' THEN 'Dunk'
        WHEN ACTION_TYPE LIKE '%Tip%' OR ACTION_TYPE LIKE '%Putback%' THEN 'Tip/Putback'
        WHEN ACTION_TYPE LIKE '%Layup%' OR ACTION_TYPE LIKE '%Finger Roll%' THEN 'Layup'
        WHEN ACTION_TYPE LIKE '%Hook%' THEN 'Hook'
        ELSE 'Jump Shot'
    END AS SHOT_CATEGORY
FROM shots;
"""

QUERY = """
SELECT
    SHOT_ZONE_BASIC,
    SHOT_ZONE_AREA,
    SHOT_CATEGORY,
    COUNT(*) AS attempts,
    AVG(SHOT_MADE_FLAG) AS fg_pct,
    AVG(SHOT_MADE_FLAG * CASE WHEN SHOT_TYPE = '3PT Field Goal' THEN 3 ELSE 2 END)
        AS expected_points
FROM shots_typed
GROUP BY SHOT_ZONE_BASIC, SHOT_ZONE_AREA, SHOT_CATEGORY
HAVING COUNT(*) >= 100
ORDER BY expected_points DESC
"""


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SHOT_TYPES_VIEW)
        zones = pd.read_sql(QUERY, conn)
        zones.to_sql("zone_expected", conn, if_exists="replace", index=False)

    print(zones.round(3).to_string(index=False))
    print(f"\nSaved {len(zones)} zones to the zone_expected table in {DB_PATH}")