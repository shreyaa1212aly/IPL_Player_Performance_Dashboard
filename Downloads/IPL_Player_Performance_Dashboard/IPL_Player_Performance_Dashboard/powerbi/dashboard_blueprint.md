# Power BI Dashboard Blueprint

## Measures (DAX examples)
```DAX
Total Runs = SUM(IPL_BALL_BY_BALL[BATTER_RUNS])
Total 4s = SUM(IPL_BALL_BY_BALL[IS_BOUNDARY_4])
Total 6s = SUM(IPL_BALL_BY_BALL[IS_BOUNDARY_6])
Wickets = SUM(IPL_BALL_BY_BALL[WICKET_COUNT])
Matches = DISTINCTCOUNT(IPL_BALL_BY_BALL[MATCH_ID])
Balls Faced = CALCULATE(COUNTROWS(IPL_BALL_BY_BALL), IPL_BALL_BY_BALL[WIDES] = 0)
Batting Strike Rate = DIVIDE([Total Runs] * 100, [Balls Faced])
```

Prefer Oracle views for batting average and bowling calculations; use Power BI measures for visual totals and slicer-responsive display. Do not use the simple `Wickets` measure for credited bowler wickets without filtering wicket kinds.

## Layout guide
- Overview: KPI row; run leaders bar chart; wicket leaders bar chart; season trend line; season/team slicers.
- Batting: sortable matrix (Player, Runs, Matches, Average, Strike Rate, 4s, 6s); scatter plot Average vs Strike Rate sized by Runs.
- Bowling: matrix (Player, Wickets, Economy, Average, Strike Rate); wickets and economy comparison chart.
- Comparison: 2–4 player selection; side-by-side KPI cards and trend chart.
- Drill-through: player profile with selected player, season performance, match list.

## Formatting
Use consistent colors for batting/bowling/team categories; avoid cluttered legends; format average/strike rate/economy to two decimals; include source and definition tooltip; show season context in titles. Set ranking visuals to use dense rank and include tied values.
