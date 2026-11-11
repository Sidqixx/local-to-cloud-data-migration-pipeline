import pandas as pd
from pathlib import Path

folder = Path("data/processed")

for file in folder.glob("*.parquet"):
    df = pd.read_parquet(file)

    print(f"\nTable: {file.stem}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(df.dtypes)