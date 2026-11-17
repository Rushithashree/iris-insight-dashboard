
from pathlib import Path
import logging
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# --------------------------------------------------
# 1. PROJECT PATHS AND ENVIRONMENT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "database" / "reports"
LOG_DIR = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------
# 2. LOGGING CONFIGURATION
# --------------------------------------------------

logging.basicConfig(
    filename=LOG_DIR / "report_engine.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 3. DATABASE CONNECTION
# --------------------------------------------------

def create_database_engine():

    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME"
    ]

    missing = [
        variable for variable in required_variables
        if os.getenv(variable) is None
    ]

    if missing:
        raise RuntimeError(
            f"Missing database settings in .env: {missing}"
        )

    database_url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME")
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=3600
    )


engine = create_database_engine()


# --------------------------------------------------
# 4. REPORT REGISTRY
# --------------------------------------------------

REPORT_FILES = {
    "R01": "R01_species_record_count.sql",
    "R02": "R02_species_share.sql",
    "R03": "R03_mean_sepal_length.sql",
    "R04": "R04_mean_sepal_width.sql",
    "R05": "R05_mean_petal_length.sql",
    "R06": "R06_mean_petal_width.sql",
    "R07": "R07_sepal_scatter_data.sql",
    "R08": "R08_petal_scatter_data.sql",
    "R09": "R09_measurement_spread.sql",
    "R10": "R10_filtered_specimen_explorer_app.sql"
}


# --------------------------------------------------
# 5. R10 FILTER PARAMETERS
# --------------------------------------------------

R10_FILTERS = [
    "species_name",
    "specimen_id",
    "min_sepal_length",
    "max_sepal_length",
    "min_sepal_width",
    "max_sepal_width",
    "min_petal_length",
    "max_petal_length",
    "min_petal_width",
    "max_petal_width"
]


def prepare_r10_parameters(filters=None):

    filters = filters or {}

    unknown_filters = set(filters) - set(R10_FILTERS)

    if unknown_filters:
        raise ValueError(
            f"Unsupported filters: {sorted(unknown_filters)}"
        )

    parameters = {
        filter_name: filters.get(filter_name)
        for filter_name in R10_FILTERS
    }

    measurement_pairs = [
        ("min_sepal_length", "max_sepal_length"),
        ("min_sepal_width", "max_sepal_width"),
        ("min_petal_length", "max_petal_length"),
        ("min_petal_width", "max_petal_width")
    ]

    for minimum, maximum in measurement_pairs:

        min_value = parameters[minimum]
        max_value = parameters[maximum]

        if (
            min_value is not None
            and max_value is not None
            and float(min_value) > float(max_value)
        ):
            raise ValueError(
                f"{minimum} cannot exceed {maximum}."
            )

    return parameters


# --------------------------------------------------
# 6. LOAD SQL REPORT
# --------------------------------------------------

def load_report_sql(report_id):

    if report_id not in REPORT_FILES:
        raise ValueError(
            f"Unknown report ID: {report_id}"
        )

    report_path = REPORTS_DIR / REPORT_FILES[report_id]

    if not report_path.exists():
        raise FileNotFoundError(
            f"SQL report not found: {report_path}"
        )

    return report_path.read_text(encoding="utf-8")


# --------------------------------------------------
# 7. EXECUTE REPORT
# --------------------------------------------------

def run_report(report_id, filters=None):

    sql_query = load_report_sql(report_id)

    parameters = {}

    if report_id == "R10":
        parameters = prepare_r10_parameters(filters)

    try:

        with engine.connect() as connection:

            result = pd.read_sql_query(
                sql=text(sql_query),
                con=connection,
                params=parameters
            )

        logger.info(
            "Report %s executed successfully. Rows returned: %s",
            report_id,
            len(result)
        )

        return result

    except Exception:

        logger.exception(
            "Execution failed for report %s",
            report_id
        )

        raise


# --------------------------------------------------
# 8. LIST AVAILABLE REPORTS
# --------------------------------------------------

def list_reports():

    return list(REPORT_FILES.keys())


# --------------------------------------------------
# 9. DATABASE CONNECTION CHECK
# --------------------------------------------------

def test_database_connection():

    with engine.connect() as connection:

        database_name = connection.execute(
            text("SELECT DATABASE()")
        ).scalar_one()

    return database_name
