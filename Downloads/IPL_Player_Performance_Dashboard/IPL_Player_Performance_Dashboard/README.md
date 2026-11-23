# IPL Player Performance Dashboard (Python + Oracle SQL + Power BI)

A reproducible analytics project for exploring IPL batting and bowling performance by season, player, team and match. The supplied dataset files are included in `data/`.


## What this project contains
- `data/ipl_ball_by_ball_clean.csv` — ball-by-ball IPL records with player/team context and derived fields.
- `data/ipl_matches_clean.csv` — match-level information.
- `scripts/clean_validate.py` — repeatable cleaning, duplicate removal and data-quality report generator.
- `sql/` — Oracle table DDL, batting/bowling aggregate views, season rankings and comparison query.
- `powerbi/` — dashboard blueprint, KPI definitions and report page plan.
- `docs/` — data quality report, project/problem statement, schema notes and verification checklist.

## Setup
1. Python 3.9+ recommended.
2. Create an environment and install dependencies:
   ```bash
   python -m venv .venv
   # Windows: .venv\\Scripts\\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run cleaning/validation:
   ```bash
   python scripts/clean_validate.py
   ```
   Processed outputs are written to `data/processed/`.
4. Oracle SQL: create the schema using `sql/01_schema.sql`, then load the CSVs into the two tables using Oracle SQL Developer's Import Data wizard. Map `match_id` to `MATCH_ID`, `date` to `MATCH_DATE`, `over` to `OVER_NO`, and the remaining columns to their matching fields. The SQL files are designed for the analytics subset. Import full files into staging first, or use the documented mapping to load only the columns listed in DDL.
5. Run `sql/02_batting_bowling_queries.sql` to create season-level views and ranking outputs.
6. Connect Power BI Desktop to Oracle Database. Select `VW_IPL_BATTER_STATS`, `VW_IPL_BOWLER_STATS`, `IPL_MATCHES` and `IPL_BALL_BY_BALL` for visuals and drill-through.

## Metric definitions (document these on the dashboard)
- **Runs:** sum of `batter_runs` credited to the batter.
- **Balls faced:** deliveries where `wides = 0` (no-balls are counted as balls faced in this project definition).
- **Batting average:** batter runs divided by dismissal count; null/blank when not dismissed.
- **Strike rate:** 100 × runs ÷ balls faced; blank when balls faced is zero.
- **4s / 6s:** sums of the dataset's boundary flags.
- **Bowling wickets:** wicket events excluding run out, retired hurt and obstructing the field.
- **Runs conceded:** total runs minus byes, leg-byes and penalty runs; wides and no-balls remain included.
- **Economy:** runs conceded × 6 ÷ legal balls bowled (legal balls exclude wides and no-balls).
- **Bowling average:** runs conceded ÷ bowler-credited wickets.
- **Bowling strike rate:** legal balls ÷ bowler-credited wickets.
- **Rank:** use `DENSE_RANK` so tied players share a rank and the next rank is not skipped.

Metric definitions are project conventions; compare sample calculations with official IPL/scorecard stats and document any source differences before presenting.


## Dashboard pages
1. **Season Overview** — season slicer, matches, aggregate runs, wickets, leading batter, leading bowler; top-10 charts.
2. **Batting Leaders** — runs, average, strike rate, balls faced, 4s/6s; sortable table and season/team filters.
3. **Bowling Leaders** — wickets, economy, average, strike rate, legal balls; sortable table and season/team filters.
4. **Player Comparison** — select two to four players; batting and/or bowling comparison cards, season and team filters.
5. **Match/Team Drill-down** — select match, teams and venue; innings and player contributions.

Recommended slicers: Season, Team, Player, Venue, Match Type. Enable drill-through from leader tables to player comparison. Use clear labels for blank averages and show the metric definition tooltip.


## Validation plan
- Reconcile five sample players' totals against official IPL/scorecard stats for a chosen season and overall range.
- Include at least one player with not-out innings in the average check.
- Validate a season with a rank tie to confirm dense ranking.
- Check missing or mixed balls data; report any rows where `legal_ball`, `legal_ball_number`, wides/no-balls, or ball numbering is inconsistent.
- Check that team totals reconcile to innings total and that all joins by match ID are unique.
- Never treat missing wicket fields on non-wicket balls as zero-valued wicket categories.

## GitHub suggestion
Keep data files tracked if repository size allows; otherwise use Git LFS or document a Kaggle download link and keep data out of Git. Include the data source URL/license details before publishing. Do not upload datasets with a license that prohibits redistribution.

## Known limitations
This is a starter analytics project, not a certified official stats product. Player names/aliases, dataset scope, incomplete matches, season naming conventions and ball-level anomalies may affect totals. The provided cleaned data is included as received; the cleaning script standardizes types/text and removes exact duplicate rows but does not attempt to repair every cricket-specific edge case.
