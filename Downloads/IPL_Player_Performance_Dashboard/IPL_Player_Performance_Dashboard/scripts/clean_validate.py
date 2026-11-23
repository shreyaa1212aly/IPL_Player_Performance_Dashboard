
"""IPL ball-by-ball and match data validation/cleaning."""

from pathlib import Path
import sys
import pandas as pd

# --------------------------------------------------
# 1. PATH CONFIGURATION
# --------------------------------------------------

BASE = Path(__file__).resolve().parents[1]

BALL_PATH = (
    Path(sys.argv[1]) if len(sys.argv) > 1
    else BASE / 'data' / 'ipl_ball_by_ball_clean.csv'
)

MATCH_PATH = (
    Path(sys.argv[2]) if len(sys.argv) > 2
    else BASE / 'data' / 'ipl_matches_clean.csv'
)

OUT = BASE / 'data' / 'processed'
OUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

ball = pd.read_csv(BALL_PATH, low_memory=False)
match = pd.read_csv(MATCH_PATH, low_memory=False)

original_ball_rows = len(ball)
original_match_rows = len(match)

# --------------------------------------------------
# 3. STANDARDIZE COLUMN NAMES AND TEXT
# --------------------------------------------------

ball.columns = ball.columns.str.strip().str.lower()
match.columns = match.columns.str.strip().str.lower()

for df in (ball, match):
    for col in df.columns:
        if (
            pd.api.types.is_object_dtype(df[col].dtype)
            or pd.api.types.is_string_dtype(df[col].dtype)
        ):
            df[col] = df[col].astype('string').str.strip()

# Keep seasons as strings
ball['season'] = ball['season'].astype('string')
match['season'] = match['season'].astype('string')

# --------------------------------------------------
# 4. STANDARDIZE DATES
# --------------------------------------------------

ball['date'] = pd.to_datetime(ball['date'], errors='coerce')
match['date'] = pd.to_datetime(match['date'], errors='coerce')

# --------------------------------------------------
# 5. CONVERT NUMERIC COLUMNS
# --------------------------------------------------

numeric_columns = [
    'innings', 'over', 'ball_in_over',
    'legal_ball', 'legal_ball_number',
    'batter_runs', 'extra_runs', 'total_runs',
    'wides', 'noballs', 'byes', 'legbyes',
    'penalty', 'is_boundary_4', 'is_boundary_6',
    'is_dot_ball', 'is_wicket', 'wicket_count'
]

for col in numeric_columns:
    if col in ball.columns:
        ball[col] = pd.to_numeric(ball[col], errors='coerce')

# --------------------------------------------------
# 6. REMOVE DUPLICATES
# --------------------------------------------------

ball = ball.drop_duplicates()
match = match.drop_duplicates()

duplicate_ball_rows = original_ball_rows - len(ball)
duplicate_match_rows = original_match_rows - len(match)

# --------------------------------------------------
# 7. RESTORE MISSING SEASONS
# --------------------------------------------------

print("\n========== SEASON CORRECTION ==========")

missing_before = ball['season'].isna().sum()

season_lookup = (
    match.drop_duplicates(subset='match_id')
    .set_index('match_id')['season']
)

mapped_seasons = ball['match_id'].map(season_lookup)

ball['season'] = ball['season'].fillna(mapped_seasons)

missing_after = ball['season'].isna().sum()
recovered = missing_before - missing_after

print(f"Missing seasons before: {missing_before:,}")
print(f"Seasons recovered: {recovered:,}")
print(f"Missing seasons remaining: {missing_after:,}")

# --------------------------------------------------
# 8. VERIFY SEASON CONSISTENCY
# --------------------------------------------------

season_check = ball.merge(
    match[['match_id', 'season']],
    on='match_id',
    how='left',
    suffixes=('_delivery', '_match')
)

mismatches = season_check[
    season_check['season_delivery'] != season_check['season_match']
]

missing_match_mappings = season_check['season_match'].isna().sum()

print("\n========== SEASON CONSISTENCY CHECK ==========")
print("Total mismatched delivery rows:", len(mismatches))
print("Total missing match mappings:", missing_match_mappings)

# --------------------------------------------------
# 9. GENERATE DATA QUALITY REPORT
# --------------------------------------------------

season_values = sorted(
    ball['season'].dropna().unique().tolist()
)

report = [
    '# Data Quality Report',
    '',
    '## Dataset Overview',
    '',
    f'- Ball-by-ball rows after duplicate removal: {len(ball):,}',
    f'- Match rows after duplicate removal: {len(match):,}',
    f'- Duplicate ball rows removed: {duplicate_ball_rows:,}',
    f'- Duplicate match rows removed: {duplicate_match_rows:,}',
    '',
    '## Missing Values',
    '',
    f'- Ball-by-ball missing date rows: {ball["date"].isna().sum():,}',
    f'- Ball-by-ball missing batter rows: {ball["batter"].isna().sum():,}',
    f'- Ball-by-ball missing bowler rows: {ball["bowler"].isna().sum():,}',
    f'- Match missing winner rows: {match["winner"].isna().sum():,}',
    '',
    '## Season Correction',
    '',
    f'- Missing seasons before correction: {missing_before:,}',
    f'- Seasons recovered: {recovered:,}',
    f'- Missing seasons remaining: {missing_after:,}',
    f'- Available seasons: {season_values}',
    '',
    '## Season Consistency',
    '',
    f'- Mismatched delivery rows: {len(mismatches):,}',
    f'- Missing match mappings: {missing_match_mappings:,}',
    '',
    '## Notes',
    '',
    '- Null wicket fields are expected for deliveries without wickets; do not replace with zero or an artificial wicket type.',
    '- Balls faced for batting exclude wides. No-balls count as balls faced; verify against the selected data source convention before final reporting.',
    '- Bowling conceded runs exclude byes, leg-byes and penalty runs; wides and no-balls are included.',
    '- Retired hurt, obstructing the field, and run-outs are excluded from bowler wickets.',
]

# --------------------------------------------------
# 10. SAVE CLEANED DATASETS
# --------------------------------------------------

ball.to_csv(OUT / 'ball_by_ball_clean.csv', index=False)
match.to_csv(OUT / 'matches_clean.csv', index=False)

# --------------------------------------------------
# 11. SAVE VALIDATION REPORT
# --------------------------------------------------

DOCS = BASE / 'docs'
DOCS.mkdir(parents=True, exist_ok=True)

(DOCS / 'data_quality_report.md').write_text(
    '\n'.join(report),
    encoding='utf-8'
)

# --------------------------------------------------
# 12. FINAL OUTPUT
# --------------------------------------------------

print("\n========== DATA QUALITY REPORT ==========\n")
print('\n'.join(report))

print(f"\nCleaned files saved to: {OUT}")
print(f"Validation report saved to: {DOCS}")

print("\n========== CLEANING COMPLETED ==========")
