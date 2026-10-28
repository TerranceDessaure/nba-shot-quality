"""Step 1 of the Shot Quality project: download every shot from one NBA season
and save it to a local SQLite database.

Shots are downloaded one team at a time. Asking for the whole league in a
single request came back incomplete (102,400 shots, 573 games), so smaller
requests keep each response well under any size limit."""

import sqlite3
import time

import pandas as pd
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import teams

SEASON = "2025-26"
DB_PATH = "nba_shots.db"


def fetch_team_shots(team_id, season):
    response = shotchartdetail.ShotChartDetail(
        team_id=team_id,
        player_id=0,
        season_nullable=season,
        season_type_all_star="Regular Season",
        context_measure_simple="FGA",
        timeout=120,
    )
    return response.get_data_frames()[0]


def fetch_shots(season):
    frames = []
    for team in teams.get_teams():
        df = fetch_team_shots(team["id"], season)
        print(f"{team['full_name']}: {len(df):,} shots")
        frames.append(df)
        time.sleep(1)  # be polite to the NBA's servers
    shots = pd.concat(frames, ignore_index=True)
    return shots.drop_duplicates(subset=["GAME_ID", "GAME_EVENT_ID"])


def save_shots(df, db_path):
    with sqlite3.connect(db_path) as conn:
        df.to_sql("shots", conn, if_exists="replace", index=False)


if __name__ == "__main__":
    shots = fetch_shots(SEASON)
    print(f"\nDownloaded {len(shots):,} shots from {shots['GAME_ID'].nunique():,} games")
    save_shots(shots, DB_PATH)
    print(f"Saved to {DB_PATH}")