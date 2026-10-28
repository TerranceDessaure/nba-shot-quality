"""Step 3 of the Shot Quality project: compare each player's actual points
to the points a league-average shooter would score on the same shots."""

import sqlite3

import pandas as pd

DB_PATH = "nba_shots.db"
MIN_ATTEMPTS = 300

QUERY = """
SELECT
    s.PLAYER_NAME,
    COUNT(*) AS attempts,
    SUM(s.SHOT_MADE_FLAG * CASE WHEN s.SHOT_TYPE = '3PT Field Goal' THEN 3 ELSE 2 END)
        AS actual_points,
    SUM(z.expected_points) AS expected_points
FROM shots_typed AS s
JOIN zone_expected AS z
    ON s.SHOT_ZONE_BASIC = z.SHOT_ZONE_BASIC
   AND s.SHOT_ZONE_AREA = z.SHOT_ZONE_AREA
   AND s.SHOT_CATEGORY = z.SHOT_CATEGORY
GROUP BY s.PLAYER_ID, s.PLAYER_NAME
HAVING COUNT(*) >= ?
"""


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as conn:
        players = pd.read_sql(QUERY, conn, params=(MIN_ATTEMPTS,))
        players["points_above_expected"] = players["actual_points"] - players["expected_points"]
        players["pae_per_100_shots"] = 100 * players["points_above_expected"] / players["attempts"]
        players = players.sort_values("pae_per_100_shots", ascending=False)
        players.to_sql("player_shot_quality", conn, if_exists="replace", index=False)

    print("Best shooters vs. expected:")
    print(print(players.head(10).round(1).to_string(index=False)) if False else players.head(10).round(1).to_string(index=False))
    print("\nWorst shooters vs. expected:")
    print(players.tail(10).round(1).to_string(index=False))