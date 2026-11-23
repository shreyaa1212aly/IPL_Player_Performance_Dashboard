import pandas as pd

balls = pd.read_csv("data/processed/ball_by_ball_clean.csv")
matches = pd.read_csv("data/processed/matches_clean.csv")

# Find deliveries where season is missing
missing_season = balls[balls["season"].isna()]

print("Missing season delivery rows:", len(missing_season))
print("Unique matches affected:", missing_season["match_id"].nunique())

# Check whether those match IDs exist in matches dataset
check = missing_season[["match_id"]].drop_duplicates()

check = check.merge(
    matches[["match_id", "season"]],
    on="match_id",
    how="left"
)

print("\nMissing season match IDs and their match-table seasons:")
print(check.head(20).to_string(index=False))

print("\nMissing match-table seasons for affected matches:")
print(check["season"].isna().sum())

print("\nSeasons available in matches dataset:")
print(sorted(matches["season"].unique()))