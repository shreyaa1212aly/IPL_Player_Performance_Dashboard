# 🏏 IPL Player Performance Dashboard

An interactive data analytics dashboard built using **Python, Streamlit, Pandas, and Plotly** to explore and analyze Indian Premier League (IPL) player performances.

The project transforms IPL ball-by-ball and match data into meaningful batting and bowling insights through interactive visualizations and season-wise analysis.

## 📌 Project Overview

The IPL Player Performance Dashboard helps users explore player statistics, compare performances, and understand trends across IPL seasons.

It uses data cleaning, processing, and visualization techniques to turn raw cricket data into an interactive analytical experience.

## ✨ Features

- **Batting Analysis:** Explore player batting performance and key statistics.
- **Bowling Analysis:** Analyze bowling performance using relevant statistical metrics.
- **Season-wise Analysis:** Examine batting and bowling trends across different IPL seasons.
- **Interactive Visualizations:** Explore performance data through interactive charts.
- **Data Processing:** Clean, validate, and prepare raw IPL datasets using Pandas.
- **Interactive Dashboard:** Navigate insights through a Streamlit web application.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data cleaning and analysis |
| Streamlit | Interactive dashboard development |
| Plotly | Interactive data visualizations |
| Git & GitHub | Version control and project hosting |

## 📂 Project Structure

```text
IPL_Player_Performance_Dashboard/
│
├── app.py
├── requirements.txt
├── README.md
│
├── .streamlit/
│   └── config.toml
│
├── data/
│   ├── ipl_matches_clean.csv
│   └── processed/
│       ├── ball_by_ball_clean.csv
│       ├── batting_analysis.csv
│       ├── bowling_analysis.csv
│       ├── matches_clean.csv
│       ├── season_batting_analysis.csv
│       └── season_bowling_analysis.csv
│
├── docs/
│   ├── data_quality_report.md
│   ├── problem_statement.md
│   ├── star_schema.md
│   └── README_project_files.txt
│
├── scripts/
│   ├── clean_validate.py
│   ├── explore_data.py
│   ├── fix_seasons.py
│   ├── investigate_seasons.py
│   └── player_analysis.py
│
├── sql/
│   ├── 01_schema.sql
│   └── 02_batting_bowling_queries.sql
│
└── powerbi/
    └── dashboard_blueprint.md
```

## ⚙️ Installation and Setup

Follow these steps to run the dashboard locally.

### 1. Clone the repository

```bash
git clone https://github.com/shreyaa1212aly/IPL_Player_Performance_Dashboard.git
```

### 2. Navigate to the project directory

```bash
cd IPL_Player_Performance_Dashboard
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

For Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the Streamlit application

```bash
python -m streamlit run app.py
```

The dashboard will open in your browser at:

`http://localhost:8501`

## 📊 Data Processing Workflow

1. Load the IPL match and ball-by-ball datasets.
2. Clean and validate the datasets.
3. Prepare processed batting and bowling statistics.
4. Generate season-wise analytical datasets.
5. Load the processed data into the Streamlit application.
6. Display insights through interactive visualizations.

## 🎯 Project Objectives

- Apply Python programming to a real-world sports analytics problem.
- Practice data cleaning and exploratory data analysis.
- Understand player performance through statistical analysis.
- Build an interactive dashboard using Streamlit.
- Develop practical skills in data analytics and visualization.

## 🚀 Future Improvements

- Add player-to-player performance comparisons.
- Include team-wise performance analysis.
- Add advanced cricket metrics and filters.
- Integrate additional seasons and updated datasets.
- Expand the dashboard with predictive analytics and machine learning.

## 👩‍💻 Author

**Shreya Tiwari**

B.Tech Student | Aspiring Data Scientist & AI/ML Engineer

---

⭐ If you find this project interesting, consider giving the repository a star!
