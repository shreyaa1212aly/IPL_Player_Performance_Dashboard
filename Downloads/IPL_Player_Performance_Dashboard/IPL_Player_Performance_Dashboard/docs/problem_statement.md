# Problem Statement

IPL viewers, analysts and fantasy-cricket enthusiasts need a reliable way to compare player performances across seasons without manually reading many scorecards. This project converts ball-by-ball and match-level IPL data into consistent batting and bowling aggregates, season rankings, and an interactive Power BI dashboard.


## Objectives
- Prepare and validate ball-by-ball and match datasets with Python.
- Use Oracle SQL to create aggregate views, ranking queries and reusable player-level metrics.
- Build Power BI KPI cards, trend charts, leaderboards, slicers and player comparison/drill-through.
- Document KPI definitions and test totals for five sample players against official sources.

## Users / questions answered
- Who scored the most runs or took the most wickets in a selected season?
- How do players compare on average, strike rate, economy, bowling average and bowling strike rate?
- How did a player perform across seasons or teams?
- Who are the season leaders, including ties?
- Which sample metrics reconcile to official scorecards?

## Success criteria
- KPI calculations documented and reproducible.
- Five player-season samples checked and recorded with source references.
- Dense rank tie behavior verified.
- Dashboard filters and drill-through work across the intended pages.
- Data-quality report records missing values, duplicate checks, scope and known limitations.
