# World Cup ETL Pipeline

An end-to-end data pipeline that loads FIFA World Cup history into PostgreSQL and transforms it with **dbt** to answer questions about teams and players.

Built as a learning project to practice the Medallion architecture (raw → staging → marts) and core data-engineering patterns (sources, refs, joins, CTEs, aggregations, canonicalization).

## What it does

```
                  jfjelstul/worldcup CSVs
                          │
                          │  Python ETL (etl/load.py)
                          ▼
            PostgreSQL: wc_raw schema       ← Bronze (raw, as-is)
                          │
                          │  dbt staging models
                          ▼
            PostgreSQL: wc_silver schema    ← Silver (cleaned, men's WCs only)
                          │
                          │  dbt mart models
                          ▼
            PostgreSQL: wc_gold schema      ← Gold (analytics-ready)
```

## Sample insights

**Top scoring teams (all-time men's World Cup):**

| Team    | Matches | W   | D  | L  | GF  | GA  | GD   |
|---------|--------:|----:|---:|---:|----:|----:|-----:|
| Brazil  |     114 |  79 | 14 | 21 | 237 | 108 | +129 |
| Germany |     118 |  74 | 19 | 25 | 237 | 135 | +102 |
| Argentina |   88 |  53 | 10 | 25 | 152 | 101 |  +51 |
| France  |      73 |  41 |  9 | 23 | 136 |  85 |  +51 |
| Italy   |      83 |  46 | 17 | 20 | 128 |  77 |  +51 |

(Germany combines historical West Germany + East Germany via a `canonicalize_team_name` macro applied in staging.)

**Top scorers (all-time men's World Cup):**

| Rank | Player              | Country     | Goals |
|-----:|---------------------|-------------|------:|
| 1 | Miroslav Klose | Germany | 16 |
| 2 | Ronaldo (Brazilian) | Brazil | 15 |
| 3 | Gerd Müller | West Germany | 14 |
| 4 | Just Fontaine | France | 13 |
| 5 | Lionel Messi | Argentina | 13 |
| 6 | Pelé | Brazil | 12 |
| 7 | Kylian Mbappé | France | 12 |

**Host country performance:** Hosts won their home WC 5 times out of 20 (25%). Hosts also average ~9.8 goals scored vs ~5.4 conceded across all WCs they hosted.

## Dashboard

A Streamlit dashboard visualizes all four marts with a different chart type per section:

| Section | Chart type | Mart |
|---------|-----------|------|
| KPIs (tournaments, matches, goals, teams) | Metric tiles | All |
| Top 10 goal scorers | Lollipop chart | `mart_top_scorers` |
| Distribution of titles | Donut chart | `mart_world_cup_winners` |
| Attack vs defense (per team) | Scatter plot (sized by matches) | `mart_team_performance` |
| Host performance per WC | Grouped bar (scored vs conceded) | `mart_host_performance` |
| Winners timeline | Time-series bar | `mart_world_cup_winners` |
| Reference tables | Tabbed dataframes | All |

Run locally with:
```bash
streamlit run streamlit/app.py
```

## Tech stack

- **Python** — CSV ingestion (pandas + SQLAlchemy)
- **PostgreSQL 14** — data warehouse (running locally without Docker)
- **dbt-postgres** — transformations and modeling
- **Source data** — [jfjelstul/worldcup](https://github.com/jfjelstul/worldcup), a comprehensive academic dataset of World Cup history

## Project structure

```
world-cup-etl-pipeline/
├── datasets/raw/             # CSVs from jfjelstul/worldcup
│   ├── tournaments.csv
│   ├── matches.csv
│   ├── players.csv
│   └── goals.csv
├── etl/
│   └── load.py               # Python ETL: CSVs -> Postgres wc_raw schema
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── macros/
│   │   └── generate_schema_name.sql
│   └── models/
│       ├── staging/
│       │   ├── _sources.yml
│       │   ├── stg_tournaments.sql
│       │   └── stg_matches.sql
│       └── marts/
│           └── mart_team_performance.sql
├── .env.example
├── requirements.txt
└── README.md
```

## Local setup

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ (running locally)

### Steps

1. Clone and create a virtual environment:
   ```bash
   git clone https://github.com/medsahbi10/world-cup-etl-pipeline.git
   cd world-cup-etl-pipeline
   python -m venv .venv
   .venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

2. Create the `wc_raw` schema in your local Postgres and copy `.env.example` to `.env`:
   ```bash
   psql -U postgres -c "CREATE SCHEMA IF NOT EXISTS wc_raw;"
   copy .env.example .env     # then edit .env with your Postgres credentials
   ```

3. Load the CSVs into Postgres:
   ```bash
   python etl/load.py
   ```

4. Run the dbt models:
   ```bash
   cd dbt_project
   dbt run --profiles-dir .
   ```

## Models

### Staging (cleanup)

| Model | Rows | What it does |
|-------|-----:|--------------|
| `stg_tournaments` | 22 | Filters tournaments to men's WCs; canonicalizes `host_country` and `winner` via macro |
| `stg_matches` | 964 | Filters matches to men's WCs via JOIN; canonicalizes home/away team names |

### Marts (analytics)

| Model | Rows | Answers |
|-------|-----:|---------|
| `mart_world_cup_winners` | 22 | Who won each men's World Cup |
| `mart_host_performance` | 21 | How hosts performed at their home tournament |
| `mart_team_performance` | 83 | Per-team all-time stats: W/D/L, goals for/against, goal difference |
| `mart_top_scorers` | 20 | Top scorers in men's WC history (excludes own goals) |

### Macros

| Macro | Purpose |
|-------|---------|
| `canonicalize_team_name(col)` | Maps historical names (West/East Germany) to modern continuous-history equivalents. Used by both staging models. |

## Roadmap

- [ ] Build `stg_goals` and `stg_players` to canonicalize the goals table (currently `mart_top_scorers` still shows "West Germany" in the `country` column)
- [ ] Clean up `given_name = 'not applicable'` for single-name Brazilian players in staging
- [ ] Extend canonicalization to Soviet Union → Russia, Czechoslovakia → Czech Republic, Yugoslavia → Serbia
- [ ] Handle co-hosted tournaments (e.g. Korea/Japan 2002) in `mart_host_performance`
- [ ] Add dbt tests (`not_null`, `unique`, `relationships`) on key columns
- [x] ~~Add a Streamlit dashboard to visualize the marts~~ (done — see `streamlit/app.py`)
- [ ] Add dashboard screenshots to this README

## Notes / decisions

- **Why combine West Germany and Germany?** For "best team ever" analytics, it's more useful to treat the German football team as a continuous entity rather than three separate political eras. The original `home_team_name` / `away_team_name` columns are preserved in staging for traceability.
- **Why filter to men's only?** Keeps scope tight for v1. Adding women's tournaments is a one-line filter change away.
- **Why no Docker?** Built on a machine without Docker. The Python + Postgres + dbt stack works fine as plain user-space processes.
