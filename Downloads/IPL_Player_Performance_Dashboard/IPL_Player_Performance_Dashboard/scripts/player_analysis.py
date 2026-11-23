
"""IPL Player Performance Analysis.

Generates batting, bowling and season-wise player statistics.
"""

from pathlib import Path
import pandas as pd

# --------------------------------------------------
# 1. LOAD CLEANED DATA
# --------------------------------------------------

BASE = Path(__file__).resolve().parents[1]

DATA_PATH = BASE / 'data' / 'processed' / 'ball_by_ball_clean.csv'

OUT = BASE / 'data' / 'processed'
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH, low_memory=False)

print("Dataset loaded successfully!")
print("Total delivery rows:", len(df))

# --------------------------------------------------
# 2. PREPARE DATA
# --------------------------------------------------

numeric_columns = [
    'batter_runs',
    'total_runs',
    'extra_runs',
    'wides',
    'noballs',
    'byes',
    'legbyes',
    'penalty',
    'legal_ball',
    'is_boundary_4',
    'is_boundary_6',
    'is_wicket'
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df['season'] = df['season'].astype('string')
df['wicket_kind'] = df['wicket_kind'].fillna('').str.lower().str.strip()

# Balls faced: wides do not count.
# No-balls do count as balls faced.
df['balls_faced'] = (df['wides'] == 0).astype(int)

# Runs conceded by a bowler.
# Byes, leg-byes and penalty runs are excluded.
df['bowler_runs_conceded'] = (
    df['total_runs']
    - df['byes']
    - df['legbyes']
    - df['penalty']
)

# --------------------------------------------------
# 3. IDENTIFY DISMISSALS
# --------------------------------------------------

dismissals = df[
    df['wicket_player_out'].notna()
].copy()

# Retired hurt is not counted as a batting dismissal.
dismissals = dismissals[
    dismissals['wicket_kind'] != 'retired hurt'
]

# Dismissals not credited to the bowler.
not_bowler_wickets = [
    'run out',
    'retired hurt',
    'retired out',
    'obstructing the field'
]

bowler_dismissals = dismissals[
    ~dismissals['wicket_kind'].isin(not_bowler_wickets)
    & dismissals['bowler'].notna()
].copy()

# --------------------------------------------------
# 4. BATTING ANALYSIS
# --------------------------------------------------

print("\nCalculating batting statistics...")

batting = df.groupby('batter').agg(
    runs=('batter_runs', 'sum'),
    balls_faced=('balls_faced', 'sum'),
    fours=('is_boundary_4', 'sum'),
    sixes=('is_boundary_6', 'sum'),
    matches=('match_id', 'nunique')
)

# Count actual dismissals for each batter.
dismissal_counts = dismissals.groupby(
    'wicket_player_out'
).size()

batting['dismissals'] = (
    batting.index.map(dismissal_counts)
)

batting['dismissals'] = batting['dismissals'].fillna(0)

# Batting average = Runs / Dismissals
batting['batting_average'] = (
    batting['runs'] /
    batting['dismissals'].replace(0, float('nan'))
)

# Strike rate = Runs / Balls faced * 100
batting['strike_rate'] = (
    batting['runs'] /
    batting['balls_faced'].replace(0, float('nan'))
) * 100

batting = batting.reset_index()

batting = batting.sort_values(
    by='runs', ascending=False
)

# --------------------------------------------------
# 5. BOWLING ANALYSIS
# --------------------------------------------------

print("Calculating bowling statistics...")

bowling = df.groupby('bowler').agg(
    runs_conceded=('bowler_runs_conceded', 'sum'),
    balls_bowled=('legal_ball', 'sum'),
    matches=('match_id', 'nunique')
)

# Count wickets credited to bowlers.
wicket_counts = bowler_dismissals.groupby('bowler').size()

bowling['wickets'] = bowling.index.map(wicket_counts)
bowling['wickets'] = bowling['wickets'].fillna(0)

# Overs bowled
bowling['overs_bowled'] = bowling['balls_bowled'] / 6

# Economy = Runs conceded / Overs
bowling['economy'] = (
    bowling['runs_conceded'] /
    bowling['overs_bowled'].replace(0, float('nan'))
)

# Bowling average = Runs conceded / Wickets
bowling['bowling_average'] = (
    bowling['runs_conceded'] /
    bowling['wickets'].replace(0, float('nan'))
)

# Bowling strike rate = Balls bowled / Wickets
bowling['bowling_strike_rate'] = (
    bowling['balls_bowled'] /
    bowling['wickets'].replace(0, float('nan'))
)

bowling = bowling.reset_index()

bowling = bowling.sort_values(
    by='wickets', ascending=False
)

# --------------------------------------------------
# 6. SEASON-WISE BATTING ANALYSIS
# --------------------------------------------------

print("Calculating season-wise batting statistics...")

season_batting = df.groupby(
    ['season', 'batter']
).agg(
    runs=('batter_runs', 'sum'),
    balls_faced=('balls_faced', 'sum'),
    fours=('is_boundary_4', 'sum'),
    sixes=('is_boundary_6', 'sum'),
    matches=('match_id', 'nunique')
).reset_index()

season_dismissals = dismissals.groupby(
    ['season', 'wicket_player_out']
).size()

season_batting['dismissals'] = [
    season_dismissals.get((season, player), 0)
    for season, player in zip(
        season_batting['season'],
        season_batting['batter']
    )
]

season_batting['batting_average'] = (
    season_batting['runs'] /
    season_batting['dismissals'].replace(0, float('nan'))
)

season_batting['strike_rate'] = (
    season_batting['runs'] /
    season_batting['balls_faced'].replace(0, float('nan'))
) * 100

# --------------------------------------------------
# 7. SEASON-WISE BOWLING ANALYSIS
# --------------------------------------------------

print("Calculating season-wise bowling statistics...")

season_bowling = df.groupby(
    ['season', 'bowler']
).agg(
    runs_conceded=('bowler_runs_conceded', 'sum'),
    balls_bowled=('legal_ball', 'sum'),
    matches=('match_id', 'nunique')
).reset_index()

season_wickets = bowler_dismissals.groupby(
    ['season', 'bowler']
).size()

season_bowling['wickets'] = [
    season_wickets.get((season, player), 0)
    for season, player in zip(
        season_bowling['season'],
        season_bowling['bowler']
    )
]

season_bowling['overs_bowled'] = (
    season_bowling['balls_bowled'] / 6
)

season_bowling['economy'] = (
    season_bowling['runs_conceded'] /
    season_bowling['overs_bowled'].replace(0, float('nan'))
)

# --------------------------------------------------
# 8. SAVE ANALYSIS RESULTS
# --------------------------------------------------

batting.to_csv(
    OUT / 'batting_analysis.csv',
    index=False
)

bowling.to_csv(
    OUT / 'bowling_analysis.csv',
    index=False
)

season_batting.to_csv(
    OUT / 'season_batting_analysis.csv',
    index=False
)

season_bowling.to_csv(
    OUT / 'season_bowling_analysis.csv',
    index=False
)

# --------------------------------------------------
# 9. DISPLAY TOP PERFORMERS
# --------------------------------------------------

print("\n========== TOP 10 RUN SCORERS ==========")

print(
    batting[
        ['batter', 'runs', 'matches', 'batting_average', 'strike_rate']
    ].head(10).to_string(index=False)
)

print("\n========== TOP 10 WICKET TAKERS ==========")

print(
    bowling[
        ['bowler', 'wickets', 'runs_conceded', 'economy']
    ].head(10).to_string(index=False)
)

print("\n========== ANALYSIS COMPLETED ==========")

print("\nFiles saved:")
print("- batting_analysis.csv")
print("- bowling_analysis.csv")
print("- season_batting_analysis.csv")
print("- season_bowling_analysis.csv")

print("\nOutput directory:", OUT)
