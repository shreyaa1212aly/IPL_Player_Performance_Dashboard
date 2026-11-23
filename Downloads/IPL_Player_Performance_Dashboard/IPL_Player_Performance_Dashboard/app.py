"""
IPL Player Performance Dashboard
Pages: Season Overview | Batting Leaders | Bowling Analysis | Player Comparison
Run:   streamlit run app.py
Needs: pip install streamlit pandas numpy plotly
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(page_title="IPL Analytics Dashboard", page_icon="🏏", layout="wide")

DATA = Path(__file__).parent / "data" / "processed"

ORANGE, BLUE, PURPLE = "#FF9F1C", "#3A86FF", "#8338EC"
GREEN, CYAN, PINK = "#2EC4B6", "#4CC9F0", "#F72585"
TEXT = "#E6EDF7"
NON_BOWLER_WICKETS = ["run out", "retired hurt", "retired out", "obstructing the field"]

st.markdown(
    """
<style>
.stApp {background: radial-gradient(circle at 15% 0%, #14213d 0%, #0b1220 45%, #070b14 100%);}
[data-testid="stSidebar"] {background: #0a101d; border-right: 1px solid rgba(255,255,255,.07);}
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 4.5rem; padding-bottom: 2rem;}
h1, h2, h3, h4, label, p, span, div {color: #E6EDF7;}
.page-title {font-size: 1.7rem; font-weight: 800; letter-spacing: .5px; margin: 0 0 .6rem 0;}
.page-title span {color: #FF9F1C;}
.kpi {border-radius: 14px; padding: 16px 18px; border: 1px solid rgba(255,255,255,.10);
      box-shadow: 0 6px 18px rgba(0,0,0,.35); min-height: 108px;}
.kpi.orange {background: linear-gradient(135deg, #e8590c 0%, #ff9f1c 100%);}
.kpi.blue   {background: linear-gradient(135deg, #1d3fbf 0%, #3a86ff 100%);}
.kpi.purple {background: linear-gradient(135deg, #5a189a 0%, #8338ec 100%);}
.kpi.green  {background: linear-gradient(135deg, #0b6e63 0%, #2ec4b6 100%);}
.kpi.dark   {background: linear-gradient(135deg, #16213a 0%, #1f2d4d 100%);}
.kpi-label {font-size: .78rem; text-transform: uppercase; letter-spacing: 1px; opacity: .9; color: #fff;}
.kpi-value {font-size: 2.1rem; font-weight: 800; line-height: 1.15; color: #fff;}
.kpi-sub   {font-size: .8rem; opacity: .85; color: #fff;}
.player-card {border-radius: 14px; padding: 14px 18px; background: #101a30;
              border: 1px solid rgba(255,255,255,.08);}
.player-card .name {font-size: 1.25rem; font-weight: 800; color: #fff;}
.player-card .tag  {font-size: .72rem; color: #FF9F1C; text-transform: uppercase; letter-spacing: 1px;}
.player-card .stat {font-size: .9rem; color: #b8c4dc;}
.panel-title {font-size: 1rem; font-weight: 700; margin: 4px 0 6px 0; color: #FF9F1C;}
[data-testid="stVerticalBlockBorderWrapper"] {background: rgba(16,26,48,.55); border-radius: 14px;}
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading IPL data...")
def load_data():
    cols = [
        "match_id", "season", "venue", "batting_team", "bowling_team", "innings", "over",
        "batter", "bowler", "batter_runs", "extra_runs", "total_runs", "wides", "noballs",
        "byes", "legbyes", "penalty", "is_boundary_4", "is_boundary_6", "is_wicket",
        "wicket_player_out", "wicket_kind", "phase",
    ]
    ball = pd.read_csv(DATA / "ball_by_ball_clean.csv", usecols=cols)
    matches = pd.read_csv(DATA / "matches_clean.csv")

    ball["season"] = ball["season"].astype(str)
    matches["season"] = matches["season"].astype(str)
    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")

    num_cols = ["batter_runs", "extra_runs", "total_runs", "wides", "noballs", "byes",
                "legbyes", "penalty", "is_boundary_4", "is_boundary_6", "is_wicket"]
    for c in num_cols:
        ball[c] = pd.to_numeric(ball[c], errors="coerce").fillna(0).astype(int)

    ball["over_no"] = ball["over"] + 1 if ball["over"].min() == 0 else ball["over"]
    ball["faced"] = (ball["wides"] == 0).astype(int)
    ball["is_legal"] = ((ball["wides"] == 0) & (ball["noballs"] == 0)).astype(int)
    ball["runs_conceded"] = ball["total_runs"] - ball["byes"] - ball["legbyes"] - ball["penalty"]
    ball["is_dot"] = ((ball["is_legal"] == 1) & (ball["runs_conceded"] == 0)).astype(int)
    kind = ball["wicket_kind"].astype(str).str.lower()
    ball["is_bowler_wicket"] = ((ball["is_wicket"] == 1) & ~kind.isin(NON_BOWLER_WICKETS)).astype(int)
    ball["is_dismissal"] = ((ball["is_wicket"] == 1) & ~kind.isin(["retired hurt"])).astype(int)
    return ball, matches


def filt(df, season, team=None, team_col="batting_team"):
    if season != "All Seasons":
        df = df[df["season"] == season]
    if team and team != "All Teams":
        df = df[df[team_col] == team]
    return df


def batting_table(d):
    g = d.groupby("batter").agg(
        runs=("batter_runs", "sum"), balls=("faced", "sum"),
        fours=("is_boundary_4", "sum"), sixes=("is_boundary_6", "sum"),
        matches=("match_id", "nunique"),
    )
    dism = d[d["is_dismissal"] == 1].groupby("wicket_player_out").size()
    g["dismissals"] = dism.reindex(g.index).fillna(0).astype(int)
    g["average"] = g["runs"] / g["dismissals"].replace(0, np.nan)
    g["strike_rate"] = g["runs"] / g["balls"].replace(0, np.nan) * 100
    g["boundary_pct"] = (g["fours"] * 4 + g["sixes"] * 6) / g["runs"].replace(0, np.nan) * 100
    return g


def bowling_table(d):
    g = d.groupby("bowler").agg(
        runs=("runs_conceded", "sum"), balls=("is_legal", "sum"),
        wickets=("is_bowler_wicket", "sum"), dots=("is_dot", "sum"),
        matches=("match_id", "nunique"),
    )
    g["economy"] = g["runs"] / (g["balls"] / 6).replace(0, np.nan)
    g["average"] = g["runs"] / g["wickets"].replace(0, np.nan)
    g["strike_rate"] = g["balls"] / g["wickets"].replace(0, np.nan)
    g["dot_pct"] = g["dots"] / g["balls"].replace(0, np.nan) * 100
    return g


# ----------------------------------------------------------------------------
# UI HELPERS
# ----------------------------------------------------------------------------
def kpi(label, value, color="orange", sub=""):
    st.markdown(
        f'<div class="kpi {color}"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-sub">{sub}&nbsp;</div></div>',
        unsafe_allow_html=True,
    )


def player_card(tag, name, stats):
    st.markdown(
        f'<div class="player-card"><div class="tag">{tag}</div>'
        f'<div class="name">{name}</div><div class="stat">{stats}</div></div>',
        unsafe_allow_html=True,
    )


def title(text):
    st.markdown(f'<div class="panel-title">{text}</div>', unsafe_allow_html=True)


def style(fig, h=340):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=h, margin=dict(l=8, r=8, t=8, b=8), font=dict(color=TEXT),
        legend=dict(orientation="h", y=-0.2, title=None),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.06)", title=None)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.06)", title=None)
    return fig


def show(fig, h=340):
    st.plotly_chart(style(fig, h), width="stretch")


def hbar(df, x, y, color=ORANGE, h=340, scale=None):
    fig = px.bar(df, x=x, y=y, orientation="h", text=x)
    if scale:
        fig.update_traces(marker=dict(color=df[x], colorscale=scale))
    else:
        fig.update_traces(marker_color=color)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="total ascending")
    show(fig, h)


def fmt(x, d=0):
    return "-" if pd.isna(x) else f"{x:,.{d}f}"


# ----------------------------------------------------------------------------
# PAGE 1 - SEASON OVERVIEW
# ----------------------------------------------------------------------------
def page_overview(ball, matches, seasons, teams):
    st.markdown('<div class="page-title">🏏 IPL <span>Season Overview</span></div>', unsafe_allow_html=True)
    f1, f2, _ = st.columns([1, 1, 2])
    season = f1.selectbox("Season", ["All Seasons"] + seasons[::-1], key="ov_s")
    team = f2.selectbox("Team", ["All Teams"] + teams, key="ov_t")

    bat = filt(ball, season, team, "batting_team")
    bowl = filt(ball, season, team, "bowling_team")
    m = matches if season == "All Seasons" else matches[matches["season"] == season]
    if team != "All Teams":
        m = m[(m["team1"] == team) | (m["team2"] == team)]
    if bat.empty:
        st.warning("No data for this selection.")
        return

    bt, bw = batting_table(bat), bowling_table(bowl)

    c = st.columns(5)
    with c[0]: kpi("Seasons", bat["season"].nunique(), "dark")
    with c[1]: kpi("Matches", fmt(m["match_id"].nunique()), "blue")
    with c[2]: kpi("Total Runs", fmt(bat["batter_runs"].sum()), "orange", "batter runs")
    with c[3]: kpi("Total Wickets", fmt(bowl["is_bowler_wicket"].sum()), "purple", "bowler-credited")
    with c[4]: kpi("Players", fmt(bat["batter"].nunique()), "green", "batters")

    st.write("")
    p1, p2, p3 = st.columns(3)
    top_b = bt.sort_values("runs", ascending=False).iloc[0]
    top_w = bw.sort_values("wickets", ascending=False).iloc[0]
    with p1:
        player_card("Most Runs", bt["runs"].idxmax(),
                    f"{fmt(top_b['runs'])} runs | SR {fmt(top_b['strike_rate'], 1)} | Avg {fmt(top_b['average'], 1)}")
    with p2:
        player_card("Most Wickets", bw["wickets"].idxmax(),
                    f"{fmt(top_w['wickets'])} wkts | Econ {fmt(top_w['economy'], 2)} | Avg {fmt(top_w['average'], 1)}")
    with p3:
        player_card("Boundaries", f"{fmt(bat['is_boundary_4'].sum())} fours | {fmt(bat['is_boundary_6'].sum())} sixes",
                    "all selected matches")

    st.write("")
    left, right = st.columns(2)
    with left, st.container(border=True):
        title("🏆 Top 10 Run Scorers")
        hbar(bt.nlargest(10, "runs").reset_index(), "runs", "batter", scale=[[0, "#e8590c"], [1, ORANGE]])
    with right, st.container(border=True):
        title("🎯 Top 10 Wicket Takers")
        hbar(bw.nlargest(10, "wickets").reset_index(), "wickets", "bowler", scale=[[0, PURPLE], [1, PINK]])

    # season totals (respect team filter, ignore season filter)
    all_bat = filt(ball, "All Seasons", team, "batting_team")
    all_bowl = filt(ball, "All Seasons", team, "bowling_team")
    runs_s = all_bat.groupby("season")["batter_runs"].sum().reindex(seasons).reset_index()
    wk_s = all_bowl.groupby("season")["is_bowler_wicket"].sum().reindex(seasons).reset_index()

    a, b = st.columns(2)
    with a, st.container(border=True):
        title("📈 Season-wise Total Runs")
        fig = px.bar(runs_s, x="season", y="batter_runs")
        fig.update_traces(marker_color=ORANGE)
        show(fig, 300)
    with b, st.container(border=True):
        title("📉 Season-wise Total Wickets")
        fig = px.line(wk_s, x="season", y="is_bowler_wicket", markers=True)
        fig.update_traces(line_color=CYAN, marker_size=9)
        show(fig, 300)

    # champions (winner of the last match of each season = final)
    fin = matches.sort_values("date").groupby("season").tail(1)[["season", "winner"]].dropna()
    c1, c2 = st.columns([1, 1])
    with c1, st.container(border=True):
        title("🏆 Season Champions (winner of final match)")
        show_fin = fin if season == "All Seasons" else fin[fin["season"] == season]
        st.dataframe(show_fin.rename(columns={"season": "Season", "winner": "Champion"}),
                     hide_index=True, width="stretch", height=300)
    with c2, st.container(border=True):
        title("🥇 Titles by Team")
        titles = fin.groupby("winner").size().reset_index(name="titles")
        hbar(titles, "titles", "winner", color=GREEN, h=300)


# ----------------------------------------------------------------------------
# PAGE 2 - BATTING LEADERS
# ----------------------------------------------------------------------------
def page_batting(ball, seasons, teams):
    st.markdown('<div class="page-title">🏏 IPL <span>Batting Leaders</span></div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    season = f1.selectbox("Season", ["All Seasons"] + seasons[::-1], key="bt_s")
    team = f2.selectbox("Team", ["All Teams"] + teams, key="bt_t")
    min_balls = f3.slider("Min balls faced (scatter / leaderboard)", 0, 500,
                          100 if season == "All Seasons" else 30, 10)

    d = filt(ball, season, team, "batting_team")
    if d.empty:
        st.warning("No data for this selection.")
        return
    bt = batting_table(d)
    sr = d["batter_runs"].sum() / max(d["faced"].sum(), 1) * 100

    k1, k2, k3, k4 = st.columns([1, 1, 1, 1.2])
    with k1: kpi("Total Runs", fmt(d["batter_runs"].sum()), "orange")
    with k2: kpi("Total 4s", fmt(d["is_boundary_4"].sum()), "blue")
    with k3: kpi("Total 6s", fmt(d["is_boundary_6"].sum()), "purple")
    with k4:
        g = go.Figure(go.Indicator(
            mode="gauge+number", value=sr, number=dict(font=dict(size=34, color="#fff"), valueformat=".2f"),
            title=dict(text="Avg Strike Rate", font=dict(size=13)),
            gauge=dict(axis=dict(range=[0, 200]), bar=dict(color=GREEN),
                       bgcolor="#16213a", borderwidth=0)))
        g.update_layout(height=130, margin=dict(l=10, r=10, t=30, b=0),
                        paper_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT))
        st.plotly_chart(g, width="stretch")

    top10 = bt.nlargest(10, "runs").reset_index()
    a, b = st.columns(2)
    with a, st.container(border=True):
        title("Sum of Runs by Player")
        hbar(top10, "runs", "batter", scale=[[0, "#e8590c"], [1, ORANGE]])
    with b, st.container(border=True):
        title("Runs vs Strike Rate")
        sc = bt[bt["balls"] >= min_balls].reset_index()
        if sc.empty:
            st.info("No players meet the minimum balls filter.")
        else:
            fig = px.scatter(sc, x="strike_rate", y="runs", hover_name="batter",
                             size="sixes", size_max=22, hover_data=["balls", "fours", "sixes", "average"])
            fig.update_traces(marker=dict(color=CYAN, opacity=.75, line=dict(width=0)))
            show(fig)

    c, e = st.columns(2)
    with c, st.container(border=True):
        title("Sum of 4s and 6s by Player (Top 10 run scorers)")
        long = top10.melt(id_vars="batter", value_vars=["fours", "sixes"], var_name="type", value_name="count")
        fig = px.bar(long, x="batter", y="count", color="type", barmode="stack",
                     color_discrete_map={"fours": BLUE, "sixes": ORANGE})
        show(fig)
    with e, st.container(border=True):
        title("Runs by Team")
        by_team = d.groupby("batting_team")["batter_runs"].sum().reset_index()
        fig = px.pie(by_team, names="batting_team", values="batter_runs", hole=.62,
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textinfo="percent")
        fig.add_annotation(text=f"<b>{d['batter_runs'].sum():,}</b><br>Total Runs", showarrow=False,
                           font=dict(size=15, color="#fff"))
        show(fig)

    g1, g2 = st.columns(2)
    with g1, st.container(border=True):
        title("Runs by Match Phase")
        ph = d.groupby("phase")["batter_runs"].sum().reset_index()
        fig = px.bar(ph, x="phase", y="batter_runs", color="phase",
                     color_discrete_sequence=[BLUE, ORANGE, PURPLE, GREEN])
        fig.update_layout(showlegend=False)
        show(fig, 280)
    with g2, st.container(border=True):
        title("Player Performance Trend (runs per season)")
        default = ball.groupby("batter")["batter_runs"].sum().nlargest(3).index.tolist()
        players = st.multiselect("Batters", sorted(ball["batter"].unique()), default=default, key="bt_trend")
        if players:
            tr = (ball[ball["batter"].isin(players)].groupby(["season", "batter"])["batter_runs"]
                  .sum().reset_index())
            fig = px.line(tr, x="season", y="batter_runs", color="batter", markers=True,
                          category_orders={"season": seasons})
            show(fig, 240)

    with st.container(border=True):
        title("Batting Leaderboard")
        lb = bt[bt["balls"] >= min_balls].sort_values("runs", ascending=False).head(50).round(2).reset_index()
        st.dataframe(lb, hide_index=True, width="stretch", height=340)


# ----------------------------------------------------------------------------
# PAGE 3 - BOWLING ANALYSIS
# ----------------------------------------------------------------------------
def page_bowling(ball, seasons, teams):
    st.markdown('<div class="page-title">🎯 IPL <span>Bowler Analysis</span></div>', unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    season = f1.selectbox("Select season", ["All Seasons"] + seasons[::-1], key="bw_s")
    d = filt(ball, season)
    bw = bowling_table(d)
    bw = bw[bw["balls"] > 0].sort_values("wickets", ascending=False)
    bowler = f2.selectbox("Select bowler", bw.index.tolist(), key="bw_p")

    bd = d[d["bowler"] == bowler]
    r = bw.loc[bowler]

    k = st.columns(5)
    with k[0]: kpi("Wickets", fmt(r["wickets"]), "orange")
    with k[1]: kpi("Economy", fmt(r["economy"], 2), "blue")
    with k[2]: kpi("Average", fmt(r["average"], 2), "purple")
    with k[3]: kpi("Strike Rate", fmt(r["strike_rate"], 2), "green")
    with k[4]: kpi("Matches", fmt(r["matches"]), "dark", f"dot ball {fmt(r['dot_pct'], 1)}%")

    st.write("")
    a, b, c = st.columns(3)
    with a, st.container(border=True):
        title("Who hits more runs (off this bowler)")
        x = bd.groupby("batter")["batter_runs"].sum().nlargest(8).reset_index()
        hbar(x, "batter_runs", "batter", color=CYAN, h=300)
    with b, st.container(border=True):
        title("Dismissal type")
        x = (bd[bd["is_bowler_wicket"] == 1].groupby("wicket_kind").size().reset_index(name="wickets"))
        if x.empty:
            st.info("No wickets in this selection.")
        else:
            fig = px.bar(x.sort_values("wickets", ascending=False), x="wicket_kind", y="wickets")
            fig.update_traces(marker_color=PURPLE)
            show(fig, 300)
    with c, st.container(border=True):
        title("Wickets per over")
        x = bd.groupby("over_no")["is_bowler_wicket"].sum().reset_index()
        fig = px.bar(x, x="over_no", y="is_bowler_wicket")
        fig.update_traces(marker_color=ORANGE)
        show(fig, 300)

    e, f, g = st.columns(3)
    with e, st.container(border=True):
        title("Wickets taken at venue")
        x = (bd[bd["is_bowler_wicket"] == 1].groupby("venue").size().nlargest(8).reset_index(name="wickets"))
        if x.empty:
            st.info("No wickets in this selection.")
        else:
            hbar(x, "wickets", "venue", color=GREEN, h=300)
    with f, st.container(border=True):
        title("Runs given per over")
        x = bd.groupby("over_no")["runs_conceded"].sum().reset_index()
        fig = px.bar(x, x="over_no", y="runs_conceded")
        fig.update_traces(marker_color=BLUE)
        show(fig, 300)
    with g, st.container(border=True):
        title("Wickets taken - innings wise")
        x = bd[bd["is_bowler_wicket"] == 1].groupby("innings").size().reset_index(name="wickets")
        if x.empty:
            st.info("No wickets in this selection.")
        else:
            x["innings"] = x["innings"].astype(str)
            fig = px.pie(x, names="innings", values="wickets", hole=.6,
                         color_discrete_sequence=[BLUE, ORANGE, PURPLE])
            show(fig, 300)

    h1, h2 = st.columns(2)
    with h1, st.container(border=True):
        title(f"Top 10 Wicket Takers ({season})")
        hbar(bw.head(10).reset_index(), "wickets", "bowler", scale=[[0, PURPLE], [1, PINK]], h=320)
    with h2, st.container(border=True):
        title(f"{bowler} - wickets per season")
        tr = (ball[ball["bowler"] == bowler].groupby("season")["is_bowler_wicket"].sum()
              .reindex(seasons).fillna(0).reset_index())
        fig = px.line(tr, x="season", y="is_bowler_wicket", markers=True)
        fig.update_traces(line_color=ORANGE, marker_size=9)
        show(fig, 320)


# ----------------------------------------------------------------------------
# PAGE 4 - PLAYER COMPARISON
# ----------------------------------------------------------------------------
def radar(names, rows, cats):
    fig = go.Figure()
    for n, color in zip(names, [GREEN, BLUE]):
        fig.add_trace(go.Scatterpolar(r=rows[n] + [rows[n][0]], theta=cats + [cats[0]], fill="toself",
                                      name=n, line=dict(color=color), opacity=.65))
    fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                 radialaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,.12)"),
                                 angularaxis=dict(gridcolor="rgba(255,255,255,.12)")))
    return fig


def page_compare(ball, seasons):
    st.markdown('<div class="page-title">⚔️ IPL <span>Player Comparison</span></div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    mode = f1.radio("Compare", ["Batters", "Bowlers"], horizontal=True)
    season = f2.selectbox("Season", ["All Seasons"] + seasons[::-1], key="cp_s")
    d = filt(ball, season)

    if mode == "Batters":
        min_balls = f3.slider("Min balls faced", 0, 500, 100 if season == "All Seasons" else 30, 10)
        t = batting_table(d)
        t = t[t["balls"] >= min_balls].sort_values("runs", ascending=False)
        metrics = {"runs": "Runs", "average": "Average", "strike_rate": "Strike Rate",
                   "boundary_pct": "Boundary %", "sixes": "Sixes", "matches": "Matches"}
        invert = []
    else:
        min_balls = f3.slider("Min balls bowled", 0, 600, 120 if season == "All Seasons" else 24, 6)
        t = bowling_table(d)
        t = t[t["balls"] >= min_balls].sort_values("wickets", ascending=False)
        t = t.fillna({"average": t["average"].max(), "strike_rate": t["strike_rate"].max()})
        metrics = {"wickets": "Wickets", "economy": "Economy (lower=better)",
                   "average": "Average (lower=better)", "strike_rate": "Strike Rate (lower=better)",
                   "dot_pct": "Dot Ball %", "matches": "Matches"}
        invert = ["economy", "average", "strike_rate"]

    if len(t) < 2:
        st.warning("Not enough players meet the filter. Lower the minimum.")
        return

    names = t.index.tolist()
    p1, p2 = st.columns(2)
    a = p1.selectbox("Player A", names, index=0, key="cp_a")
    b = p2.selectbox("Player B", names, index=1, key="cp_b")

    # scale each metric to 0-100 against all qualified players
    scaled = {}
    for n in (a, b):
        row = []
        for col in metrics:
            lo, hi = t[col].min(), t[col].max()
            span = (hi - lo) or 1
            v = (t.loc[n, col] - lo) / span * 100
            row.append(round(100 - v if col in invert else v, 1))
        scaled[n] = row

    left, right = st.columns([1.2, 1])
    with left, st.container(border=True):
        title("Performance Index - Player Comparison")
        show(radar([a, b], scaled, list(metrics.values())), 480)
    with right, st.container(border=True):
        title("Key Performance Indicators")
        tbl = t.loc[[a, b], list(metrics)].T.round(2)
        tbl.index = list(metrics.values())
        st.dataframe(tbl, width="stretch", height=300)
        st.caption("Radar axes are scaled 0-100 against all players who meet the minimum filter.")


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    try:
        ball, matches = load_data()
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Run this app from the project root so 'data/processed' is found.")
        st.stop()

    seasons = sorted(ball["season"].unique())
    teams = sorted(set(ball["batting_team"].dropna().unique()))

    st.sidebar.markdown("## 🏏 IPL Analytics")
    st.sidebar.caption("Explore player statistics and performance.")
    page = st.sidebar.radio("Dashboard", ["Season Overview", "Batting Leaders",
                                          "Bowling Analysis", "Player Comparison"])
    st.sidebar.divider()
    st.sidebar.caption(f"Seasons: {seasons[0]} - {seasons[-1]}")
    st.sidebar.caption(f"Matches: {matches['match_id'].nunique():,}")

    if page == "Season Overview":
        page_overview(ball, matches, seasons, teams)
    elif page == "Batting Leaders":
        page_batting(ball, seasons, teams)
    elif page == "Bowling Analysis":
        page_bowling(ball, seasons, teams)
    else:
        page_compare(ball, seasons)

    st.caption("IPL Player Performance Dashboard | Built using Python, Pandas, Plotly and Streamlit")


main()