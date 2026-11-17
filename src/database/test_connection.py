
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Locate the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load database credentials
load_dotenv(PROJECT_ROOT / ".env")

# Read configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Check required settings
required_values = {
    "DB_HOST": DB_HOST,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_NAME": DB_NAME
}

missing = [
    key for key, value in required_values.items()
    if not value
]

if missing:
    raise ValueError(
        f"Missing database settings in .env: {missing}"
    )

# Construct connection URL safely
database_url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME
)

# Create SQLAlchemy engine
engine = create_engine(
    database_url,
    pool_pre_ping=True
)

def test_connection():
    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT DATABASE(), VERSION()")
            )

            database_name, mysql_version = result.fetchone()

            print("\n========== DATABASE CONNECTION ==========")
            print("Connection Status: SUCCESS")
            print("Database Name:", database_name)
            print("MySQL Version:", mysql_version)

            print("\n========== AVAILABLE TABLES ==========")

            from sqlalchemy import inspect

            inspector = inspect(engine)
            tables = inspector.get_table_names()

            for table in tables:
                print("-", table)

            print("\nTotal Tables:", len(tables))

            expected_tables = {
                "species_master",
                "import_batch",
                "specimen",
                "data_quality_log"
            }

            if expected_tables.issubset(set(tables)):
                print("Schema Verification: PASSED")
            else:
                print("Schema Verification: INCOMPLETE")
                print(
                    "Missing tables:",
                    expected_tables - set(tables)
                )

            print("\n========== TEST COMPLETED ==========")

    except Exception as error:
        print("\nDATABASE CONNECTION FAILED")
        print("Error:", error)

    finally:
        engine.dispose()


if __name__ == "__main__":
    test_connection()
