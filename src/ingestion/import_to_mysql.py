
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CLEANED_FILE = (
    PROJECT_ROOT / "data" / "processed" / "cleaned_iris.csv"
)

REJECTED_FILE = (
    PROJECT_ROOT / "data" / "processed" / "rejected_records.csv"
)

SOURCE_FILE_NAME = "iris.data"
EXPECTED_DATABASE = "iris_analytics_db"

MEASUREMENT_COLUMNS = [
    "sepal_length_cm",
    "sepal_width_cm",
    "petal_length_cm",
    "petal_width_cm"
]

DATA_COLUMNS = MEASUREMENT_COLUMNS + ["species"]

EXPECTED_SPECIES = {
    "Iris-setosa",
    "Iris-versicolor",
    "Iris-virginica"
}


# ============================================================
# 2. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


# ============================================================
# 3. CREATE DATABASE CONNECTION
# ============================================================

def create_database_engine():

    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        raise ValueError(
            "Database configuration is incomplete. "
            "Check your .env file."
        )

    if DB_NAME != EXPECTED_DATABASE:
        raise ValueError(
            f"Incorrect database configured: {DB_NAME}. "
            f"Expected: {EXPECTED_DATABASE}"
        )

    connection_url = URL.create(
        "mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True
    )


# ============================================================
# 4. LOAD AND VALIDATE DATASET FILES
# ============================================================

def load_dataset():

    if not CLEANED_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {CLEANED_FILE}"
        )

    if not REJECTED_FILE.exists():
        raise FileNotFoundError(
            f"Rejected dataset not found: {REJECTED_FILE}"
        )

    cleaned_df = pd.read_csv(CLEANED_FILE)
    rejected_df = pd.read_csv(REJECTED_FILE)

    required_columns = [
        "source_row_number",
        *DATA_COLUMNS
    ]

    missing_columns = [
        column for column in required_columns
        if column not in cleaned_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Normalize species names to avoid whitespace mismatches.
    cleaned_df["species"] = (
        cleaned_df["species"]
        .astype("string")
        .str.strip()
    )

    # Validate source row numbers.
    cleaned_df["source_row_number"] = pd.to_numeric(
        cleaned_df["source_row_number"],
        errors="raise"
    )

    if cleaned_df["source_row_number"].isna().any():
        raise ValueError("Source row numbers cannot be empty.")

    if cleaned_df["source_row_number"].duplicated().any():
        raise ValueError("Duplicate source row numbers detected.")

    # Validate numeric measurements.
    for column in MEASUREMENT_COLUMNS:

        cleaned_df[column] = pd.to_numeric(
            cleaned_df[column],
            errors="raise"
        )

        if cleaned_df[column].isna().any():
            raise ValueError(
                f"Missing values detected in {column}."
            )

        if (cleaned_df[column] <= 0).any():
            raise ValueError(
                f"Non-positive measurements detected in {column}."
            )

    # Validate species categories.
    actual_species = set(cleaned_df["species"].dropna().unique())

    invalid_species = actual_species - EXPECTED_SPECIES

    if invalid_species:
        raise ValueError(
            f"Unexpected species in CSV: {invalid_species}"
        )

    return cleaned_df, rejected_df


# ============================================================
# 5. VERIFY DATABASE AND SPECIES MASTER
# ============================================================

def get_species_mapping(connection):

    active_database = connection.execute(
        text("SELECT DATABASE()")
    ).scalar()

    if active_database != EXPECTED_DATABASE:
        raise RuntimeError(
            f"Connected to {active_database}, "
            f"expected {EXPECTED_DATABASE}."
        )

    rows = connection.execute(
        text("""
            SELECT species_id, species_name
            FROM species_master
            ORDER BY species_id
        """)
    ).mappings().all()

    # Normalize database species names as well.
    species_map = {
        str(row["species_name"]).strip(): row["species_id"]
        for row in rows
    }

    missing_species = EXPECTED_SPECIES - set(species_map)

    if missing_species:
        raise ValueError(
            "Species missing from species_master: "
            f"{sorted(missing_species)}"
        )

    if len(species_map) != len(rows):
        raise ValueError(
            "Duplicate species names found in species_master."
        )

    print(f"Connected database: {active_database}")
    print(f"Species verified: {len(species_map)}")

    return species_map


# ============================================================
# 6. INSERT IMPORT BATCH
# ============================================================

def create_import_batch(
    connection,
    total_records,
    accepted_records,
    rejected_records
):

    existing_batch = connection.execute(
        text("""
            SELECT import_batch_id
            FROM import_batch
            WHERE source_file_name = :source_name
            LIMIT 1
        """),
        {"source_name": SOURCE_FILE_NAME}
    ).first()

    if existing_batch:
        raise RuntimeError(
            "The source file has already been imported. "
            f"Existing batch ID: {existing_batch.import_batch_id}. "
            "Import stopped to prevent duplicate records."
        )

    result = connection.execute(
        text("""
            INSERT INTO import_batch (
                source_file_name,
                total_records,
                accepted_records,
                rejected_records
            )
            VALUES (
                :source_name,
                :total,
                :accepted,
                :rejected
            )
        """),
        {
            "source_name": SOURCE_FILE_NAME,
            "total": total_records,
            "accepted": accepted_records,
            "rejected": rejected_records
        }
    )

    return result.lastrowid


# ============================================================
# 7. INSERT SPECIMEN RECORDS
# ============================================================

def insert_specimens(connection, cleaned_df, species_map, batch_id):

    insert_query = text("""
        INSERT INTO specimen (
            species_id,
            import_batch_id,
            source_row_number,
            sepal_length_cm,
            sepal_width_cm,
            petal_length_cm,
            petal_width_cm
        )
        VALUES (
            :species_id,
            :batch_id,
            :source_row,
            :sepal_length,
            :sepal_width,
            :petal_length,
            :petal_width
        )
    """)

    inserted_count = 0

    for row in cleaned_df.to_dict(orient="records"):

        species_name = str(row["species"]).strip()

        connection.execute(
            insert_query,
            {
                "species_id": species_map[species_name],
                "batch_id": batch_id,
                "source_row": int(row["source_row_number"]),
                "sepal_length": float(row["sepal_length_cm"]),
                "sepal_width": float(row["sepal_width_cm"]),
                "petal_length": float(row["petal_length_cm"]),
                "petal_width": float(row["petal_width_cm"])
            }
        )

        inserted_count += 1

    return inserted_count


# ============================================================
# 8. RECORD DUPLICATE MEASUREMENTS
# ============================================================

def log_duplicate_records(connection, cleaned_df, batch_id):

    duplicate_mask = cleaned_df.duplicated(
        subset=DATA_COLUMNS,
        keep="first"
    )

    duplicate_records = cleaned_df.loc[duplicate_mask]

    for row in duplicate_records.to_dict(orient="records"):

        specimen_id = connection.execute(
            text("""
                SELECT specimen_id
                FROM specimen
                WHERE import_batch_id = :batch_id
                  AND source_row_number = :source_row
            """),
            {
                "batch_id": batch_id,
                "source_row": int(row["source_row_number"])
            }
        ).scalar()

        if specimen_id is None:
            raise RuntimeError(
                "Could not find specimen for duplicate quality log."
            )

        description = (
            "Additional exact duplicate measurement occurrence. "
            f"Source row: {int(row['source_row_number'])}. "
            "Record retained without deletion."
        )

        connection.execute(
            text("""
                INSERT INTO data_quality_log (
                    import_batch_id,
                    specimen_id,
                    issue_type,
                    severity,
                    description,
                    resolution_status
                )
                VALUES (
                    :batch_id,
                    :specimen_id,
                    :issue_type,
                    :severity,
                    :description,
                    :status
                )
            """),
            {
                "batch_id": batch_id,
                "specimen_id": specimen_id,
                "issue_type": "EXACT_DUPLICATE_MEASUREMENTS",
                "severity": "Low",
                "description": description,
                "status": "Reviewed"
            }
        )

    return len(duplicate_records)


# ============================================================
# 9. RECORD REJECTED ROWS, IF ANY
# ============================================================

def log_rejected_records(connection, rejected_df, batch_id):

    for row in rejected_df.to_dict(orient="records"):

        issues = row.get(
            "quality_issues",
            "Validation failure"
        )

        if pd.isna(issues):
            issues = "Validation failure"

        connection.execute(
            text("""
                INSERT INTO data_quality_log (
                    import_batch_id,
                    specimen_id,
                    issue_type,
                    severity,
                    description,
                    resolution_status
                )
                VALUES (
                    :batch_id,
                    NULL,
                    :issue_type,
                    :severity,
                    :description,
                    :status
                )
            """),
            {
                "batch_id": batch_id,
                "issue_type": "VALIDATION_FAILURE",
                "severity": "High",
                "description": (
                    f"Rejected source row "
                    f"{row.get('source_row_number', 'Unknown')}. "
                    f"Issues: {issues}"
                ),
                "status": "Pending"
            }
        )

    return len(rejected_df)


# ============================================================
# 10. EXECUTE IMPORT TRANSACTION
# ============================================================

def execute_import(engine, cleaned_df, rejected_df):

    total_records = len(cleaned_df) + len(rejected_df)

    with engine.begin() as connection:

        species_map = get_species_mapping(connection)

        batch_id = create_import_batch(
            connection,
            total_records,
            len(cleaned_df),
            len(rejected_df)
        )

        inserted_count = insert_specimens(
            connection,
            cleaned_df,
            species_map,
            batch_id
        )

        duplicate_count = log_duplicate_records(
            connection,
            cleaned_df,
            batch_id
        )

        rejected_count = log_rejected_records(
            connection,
            rejected_df,
            batch_id
        )

        if inserted_count != len(cleaned_df):
            raise RuntimeError(
                "Inserted specimen count does not match accepted count."
            )

    return batch_id, inserted_count, duplicate_count, rejected_count


# ============================================================
# 11. MAIN PROGRAM
# ============================================================

def main():

    engine = None

    try:

        print("\nIRIS DATASET - MYSQL IMPORT")
        print("=" * 50)

        cleaned_df, rejected_df = load_dataset()

        print(f"Accepted records: {len(cleaned_df)}")
        print(f"Rejected records: {len(rejected_df)}")

        engine = create_database_engine()

        batch_id, inserted, duplicates, rejected = execute_import(
            engine,
            cleaned_df,
            rejected_df
        )

        print("\nIMPORT COMPLETED SUCCESSFULLY")
        print("=" * 50)
        print(f"Database: {EXPECTED_DATABASE}")
        print(f"Import batch ID: {batch_id}")
        print(f"Specimen records inserted: {inserted}")
        print(f"Rejected records: {rejected}")
        print(f"Duplicate occurrences logged: {duplicates}")

        print("\nVALIDATION SUMMARY")
        print("=" * 50)
        print(f"Total source records: {len(cleaned_df) + len(rejected_df)}")
        print(f"Accepted records: {inserted}")
        print(f"Rejected records: {rejected}")

    except Exception as error:

        print("\nIMPORT FAILED")
        print(f"Reason: {error}")
        print(
            "The database transaction was rolled back "
            "if the failure occurred during import."
        )

    finally:

        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    main()
