"""Data Valiadation Step"""

import sqlite3

import pandas as pd

DB_PATH = "nba_shots.db"

with sqlite3.connect(DB_PATH) as conn:
    # 1. Total number of shots in the table
    total = pd.read_sql("SELECT COUNT(*) AS total_shots FROM shots", conn)

    # 2. Number of different games in the table
    games = pd.read_sql("SELECT count(distinct game_id) AS games FROM shots", conn)

    # 3. Luka's shots and the number of games he appears in
    luka = pd.read_sql(
        """
        SELECT COUNT(*) AS shots, COUNT(DISTINCT game_id) AS games
        FROM shots
        WHERE PLAYER_NAME LIKE 'Luka Dončić%'
        """,
        conn,
    )

print(total)
print(games)
print(luka)
