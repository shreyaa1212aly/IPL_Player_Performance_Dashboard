import pandas as pd

balls = pd.read_csv("data/processed/ball_by_ball_clean.csv")
matches = pd.read_csv("data/processed/matches_clean.csv")

print("\n========== BALL DATA ==========")

print("\nFirst 5 rows:")
print(balls.head())

print("\nDataset information:")
balls.info()

print("\nMissing values:")
print(balls.isnull().sum().sort_values(ascending=False).head(15))

print("\nDuplicate rows:", balls.duplicated().sum())

print("\n========== MATCH DATA ==========")

print("\nFirst 5 matches:")
print(matches.head())

print("\nDataset information:")
matches.info()

print("\nMissing values:")
print(matches.isnull().sum().sort_values(ascending=False))

print("\nDuplicate matches:", matches.duplicated().sum())