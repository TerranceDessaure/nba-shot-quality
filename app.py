"""Step 4 of the Shot Quality project: the interactive web app recruiters and
coaches can use. Run it with:  streamlit run app.py"""

import sqlite3

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

DB_PATH = "nba_shots.db"


@st.cache_data
def load(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(query, conn, params=params)


def court_lines():
    """Half-court lines in the NBA API's units (tenths of a foot, hoop at 0,0)."""
    pieces = []

    def add(name, xs, ys):
        pieces.append(pd.DataFrame({"x": xs, "y": ys, "piece": name, "i": range(len(xs))}))

    def arc(name, radius, center_y=0, start=0, end=360):
        t = np.radians(np.linspace(start, end, 100))
        add(name, radius * np.cos(t), center_y + radius * np.sin(t))

    add("court", [-250, -250, 250, 250, -250], [422.5, -47.5, -47.5, 422.5, 422.5])
    add("backboard", [-30, 30], [-7.5, -7.5])
    arc("hoop", 7.5)
    add("paint", [-80, -80, 80, 80], [-47.5, 142.5, 142.5, -47.5])
    arc("free throw circle", 60, 142.5, 0, 180)
    arc("restricted area", 40, 0, 0, 180)
    add("left corner 3", [-220, -220], [-47.5, 89.5])
    add("right corner 3", [220, 220], [-47.5, 89.5])
    arc("three point line", 237.5, 0, 22, 158)
    return pd.concat(pieces)


def shot_chart(shots):
    x = alt.X("x:Q", scale=alt.Scale(domain=[-250, 250]), axis=None)
    y = alt.Y("y:Q", scale=alt.Scale(domain=[-47.5, 422.5]), axis=None)
    court = alt.Chart(court_lines()).mark_line(color="gray").encode(
        x=x, y=y, detail="piece", order="i"
    )
    dots = alt.Chart(shots.rename(columns={"LOC_X": "x", "LOC_Y": "y"})).mark_circle(
        size=30, opacity=0.6, clip=True
    ).encode(
        x=x,
        y=y,
        color=alt.Color(
            "result:N",
            scale=alt.Scale(domain=["Made", "Missed"], range=["#2a9d8f", "#e76f51"]),
            title=None,
        ),
        tooltip=["SHOT_ZONE_BASIC", "SHOT_DISTANCE", "result"],
    )
    return (court + dots).properties(width=500, height=470)


st.title("NBA Shot Quality, 2025-26")
st.caption(
    "Points above expected = points a player scored minus the points a "
    "league-average shooter would have scored on the same shots."
)

leaders = load("SELECT * FROM player_shot_quality")
league_selection = leaders["expected_points"].sum() / leaders["attempts"].sum()

player = st.selectbox("Pick a player", leaders["PLAYER_NAME"])
row = leaders[leaders["PLAYER_NAME"] == player].iloc[0]
selection = row["expected_points"] / row["attempts"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Shot attempts", f"{row['attempts']:,}")
c2.metric(
    "Shot selection",
    f"{selection:.2f}",
    delta=f"{selection - league_selection:+.2f} vs. league",
    help="Average value of the spots he shoots from, in points per shot. "
    "Higher means he takes better shots (rim and corner threes).",
)
c3.metric(
    "Points above expected",
    f"{row['points_above_expected']:+.0f}",
    help="Total points scored beyond what a league-average shooter would score "
    "on the same shots. Measures shot making.",
)
c4.metric(
    "Per 100 shots",
    f"{row['pae_per_100_shots']:+.1f}",
    help="Points above expected for every 100 shots, so high- and low-volume "
    "shooters can be compared fairly.",
)

shots = load(
    "SELECT LOC_X, LOC_Y, SHOT_ZONE_BASIC, SHOT_DISTANCE, SHOT_MADE_FLAG "
    "FROM shots WHERE PLAYER_NAME = ?",
    (player,),
)
shots["result"] = shots["SHOT_MADE_FLAG"].map({1: "Made", 0: "Missed"})
st.subheader(f"{player}: every shot")
st.altair_chart(shot_chart(shots), use_container_width=False)

st.subheader("League leaderboard: best shot makers")
st.dataframe(leaders.round(1), hide_index=True)