# NBA Shot Quality: Who Makes Their Shots, and Who's Just Taking Good Ones?

**Live app:** [[View Interactive Dashboard]](https://nba-shot-quality-fdmcevshncauprbyrrn4gc.streamlit.app/)

Raw field goal percentage hides context. A corner three and a contested pull-up are not the same shot, and a center who dunks all game will always out-shoot a guard who creates his own looks. This project separates two skills that box scores mix together:

- **Shot selection:** how valuable are the spots and shot types a player chooses?
- **Shot making:** how many more (or fewer) points does he score than a league-average shooter would on those exact same shots?

## What the app does

Pick any player from the 2025-26 regular season to see:
- Their shot chart on a half court (made vs. missed, hover for zone and distance)
- **Shot selection:** the average value of their shots, compared to the league
- **Points above expected:** total points scored beyond a league-average shooter
- **Per 100 shots:** the same number, scaled so high- and low-volume players compare fairly
- A league leaderboard of the best shot makers (minimum 300 attempts)

## How it works

| Step | Script | What it does |
|---|---|---|
| Collect | `fetch_shots.py` | Downloads every 2025-26 shot from the NBA stats API, one team at a time |
| Store | `fetch_shots.py` | Saves the shots to a SQLite database (`nba_shots.db`) |
| Validate | `check_data.py` | Confirms the data is complete against published totals |
| Baseline | `expected_points.py` | SQL: league-average points per shot for each zone and shot type |
| Score players | `player_vs_expected.py` | SQL join: each player's actual points vs. expected on the same shots |
| Deliver | `app.py` | Interactive Streamlit web app |

**Expected points** for a shot = league field goal percentage for that zone and shot type × the shot's point value. For example, a corner three goes in about 39% of the time, so it's worth about 1.17 points, close to a shot at the rim and far more than a mid-range jumper.

## Data validation

My first download silently returned only about half the season: 102,400 shots from 573 games. A validation script caught it. Requesting one team at a time fixed it, and the final dataset has **219,160 shots from all 1,230 games**. As a spot check, Luka Dončić's totals in the database (64 games, 1,457 field goal attempts) match his published 2025-26 stats exactly.

## Key findings

- **Top 5 shot makers (per 100 shots):** Luke Kennard, DeAndre Ayton, Jakob Poeltl, Kevin Durant, Cam Spencer
- **The first model overrated big men.** It compared every rim attempt to the same average, so a dunk counted the same as a contested layup. After I added shot type (dunk, layup, putback, hook, jump shot) to the baseline, **DeAndre Ayton dropped from #2 to #8**, so a large part of his edge came from the easy shots he gets. **Jakob Poeltl only dropped from #3 to #5**, meaning his finishing holds up even against the right comparison.
- **A player can be good at one skill and poor at the other.** A high shot selection score with negative points above expected means a player gets to good spots but doesn't finish. The coaching takeaway is to keep his shot diet and work on finishing.

## Limitations

- The free NBA data doesn't include defender distance, so a wide-open shot and a heavily contested one from the same spot and of the same type are treated as equal.
- Shots from zone and type combinations with fewer than 100 league-wide attempts (mostly heaves) are left out of the baseline.
- Free throws are not included.
- One season only. Shot making is noisy year to year, so a multi-season version would be more reliable.

## Run it yourself

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python fetch_shots.py
python expected_points.py
python player_vs_expected.py
streamlit run app.py
```

## Built with

Python, pandas, SQLite, SQL, Altair, Streamlit, nba_api

*By Terrance Dessaure, Information Science and Technology, University of South Carolina Beaufort*
