# Data Quality Report

## Dataset Overview

- Ball-by-ball rows after duplicate removal: 288,226
- Match rows after duplicate removal: 1,212
- Duplicate ball rows removed: 0
- Duplicate match rows removed: 0

## Missing Values

- Ball-by-ball missing date rows: 0
- Ball-by-ball missing batter rows: 0
- Ball-by-ball missing bowler rows: 0
- Match missing winner rows: 0

## Season Correction

- Missing seasons before correction: 0
- Seasons recovered: 0
- Missing seasons remaining: 0
- Available seasons: ['2007/08', '2009', '2009/10', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020/21', '2021', '2022', '2023', '2024', '2025', '2026']

## Season Consistency

- Mismatched delivery rows: 0
- Missing match mappings: 0

## Notes

- Null wicket fields are expected for deliveries without wickets; do not replace with zero or an artificial wicket type.
- Balls faced for batting exclude wides. No-balls count as balls faced; verify against the selected data source convention before final reporting.
- Bowling conceded runs exclude byes, leg-byes and penalty runs; wides and no-balls are included.
- Retired hurt, obstructing the field, and run-outs are excluded from bowler wickets.