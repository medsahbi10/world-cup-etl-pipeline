"""
World Cup ETL — loads CSVs from datasets/raw/ into the wc_raw schema in Postgres.

Each CSV becomes one raw table. The table name matches the CSV file name
(without the .csv extension), e.g. matches.csv -> wc_raw.matches.

Run from the project root:
    python etl/load.py
"""
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

ENGINE = create_engine(
    "postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}".format(
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        host=os.environ["DATABASE_HOST"],
        port=os.environ["DATABASE_PORT"],
        dbname=os.environ["DATABASE_NAME"],
    )
)

SCHEMA = "wc_raw"
RAW_DIR = Path(__file__).resolve().parent.parent / "datasets" / "raw"

CSV_FILES = [
    "tournaments.csv",
    "matches.csv",
    "players.csv",
    "goals.csv",
]


def load_csv(csv_path: Path) -> int:
    table_name = csv_path.stem
    df = pd.read_csv(csv_path, encoding="utf-8")
    df.to_sql(table_name, ENGINE, schema=SCHEMA, if_exists="replace", index=False)
    return len(df)


def main() -> None:
    for csv_name in CSV_FILES:
        csv_path = RAW_DIR / csv_name
        row_count = load_csv(csv_path)
        print(f"  loaded {SCHEMA}.{csv_path.stem:<14} <- {csv_name:<18} ({row_count:>5} rows)")


if __name__ == "__main__":
    main()
