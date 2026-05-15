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

(Germany combines historical West Germany + East Germany via a canonicalization step in the staging layer.)

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

## Models so far

| Model | Layer | What it does |
|-------|-------|--------------|
| `stg_tournaments` | staging | Filters tournaments to men's WCs only (22 rows) |
| `stg_matches` | staging | Filters matches to men's WCs via JOIN; adds `team_canonical` columns merging historical names like West Germany → Germany (964 rows) |
| `mart_team_performance` | marts | Aggregates per-team stats across all WCs: matches played, W/D/L, goals for/against, goal difference (83 teams) |

## Roadmap

- [ ] `mart_top_scorers` — best players by goals scored (uses `goals.csv` + JOIN to `stg_matches`)
- [ ] `mart_world_cup_winners` — winners and runners-up of each WC
- [ ] `mart_host_performance` — do hosts perform better?
- [ ] Extend canonicalization to Soviet Union → Russia, Czechoslovakia → Czech Republic, Yugoslavia → Serbia
- [ ] Add dbt tests (`not_null`, `unique`) on key columns
- [ ] Add a Streamlit dashboard to visualize results

## Notes / decisions

- **Why combine West Germany and Germany?** For "best team ever" analytics, it's more useful to treat the German football team as a continuous entity rather than three separate political eras. The original `home_team_name` / `away_team_name` columns are preserved in staging for traceability.
- **Why filter to men's only?** Keeps scope tight for v1. Adding women's tournaments is a one-line filter change away.
- **Why no Docker?** Built on a machine without Docker. The Python + Postgres + dbt stack works fine as plain user-space processes.
