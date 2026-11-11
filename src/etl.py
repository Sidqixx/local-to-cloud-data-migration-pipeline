
import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ==========================================
# 1. CONFIGURATION
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "data" / "processed"
LOG_DIR = ROOT_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    filename=LOG_DIR / "etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

TABLES = {
    "customers": ["customer_id"],
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"]
}


# ==========================================
# 2. DATABASE CONNECTION
# ==========================================

def create_db_engine():
    db_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME")
    )

    return create_engine(db_url)


# ==========================================
# 3. EXTRACT
# ==========================================

def extract_data(engine, table_name):
    logger.info(f"Extracting table: {table_name}")

    query = text(f'SELECT * FROM processed."{table_name}"')

    df = pd.read_sql_query(query, con=engine)

    logger.info(
        f"Extracted {len(df)} records from {table_name}"
    )

    return df


# ==========================================
# 4. TRANSFORM
# ==========================================

def transform_data(df, table_name):
    logger.info(f"Transforming table: {table_name}")

    df = df.copy()

    # Standardize whitespace in text columns
    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    logger.info(f"Transformation completed: {table_name}")

    return df


# ==========================================
# 5. VALIDATE
# ==========================================

def validate_data(df, table_name, original_count):
    logger.info(f"Validating table: {table_name}")

    primary_keys = TABLES[table_name]

    # Check empty dataset
    if df.empty:
        raise ValueError(f"{table_name} is empty")

    # Check missing primary keys
    if df[primary_keys].isnull().any().any():
        raise ValueError(
            f"NULL primary key found in {table_name}"
        )

    # Check duplicate primary keys
    duplicate_count = df.duplicated(
        subset=primary_keys
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"{duplicate_count} duplicate records in {table_name}"
        )

    # Check record count
    if len(df) != original_count:
        raise ValueError(
            f"Record count mismatch in {table_name}"
        )

    logger.info(f"Validation passed: {table_name}")


# ==========================================
# 6. LOAD
# ==========================================

def load_data(df, table_name):
    output_path = OUTPUT_DIR / f"{table_name}.parquet"

    df.to_parquet(
        output_path,
        index=False,
        engine="pyarrow"
    )

    # Read back to verify output
    check_df = pd.read_parquet(output_path)

    if len(check_df) != len(df):
        raise ValueError(
            f"Parquet verification failed: {table_name}"
        )

    logger.info(
        f"Loaded {len(check_df)} records to {output_path}"
    )


# ==========================================
# 7. MAIN PIPELINE
# ==========================================

def main():
    logger.info("========== ETL PIPELINE STARTED ==========")

    engine = create_db_engine()

    try:
        # Test database connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("Database connection successful")

        for table_name in TABLES:
            # Extract
            df = extract_data(engine, table_name)
            original_count = len(df)

            # Transform
            transformed_df = transform_data(
                df, table_name
            )

            # Validate
            validate_data(
                transformed_df,
                table_name,
                original_count
            )

            # Load
            load_data(transformed_df, table_name)

        logger.info("========== ETL PIPELINE SUCCESS ==========")

    except Exception:
        logger.exception("ETL PIPELINE FAILED")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
