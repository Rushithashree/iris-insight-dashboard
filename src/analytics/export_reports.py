
from pathlib import Path
from datetime import datetime
import json
import logging

from report_engine import run_report, list_reports


# --------------------------------------------------
# 1. PROJECT DIRECTORIES
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXPORT_DIR = PROJECT_ROOT / "exports"
REPORT_EXPORT_DIR = EXPORT_DIR / "reports"
METADATA_DIR = EXPORT_DIR / "metadata"

REPORT_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOGGING
# --------------------------------------------------

logging.basicConfig(
    filename=PROJECT_ROOT / "logs" / "export_engine.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 3. EXPORT REPORTS
# --------------------------------------------------

def export_all_reports():

    manifest = {
        "project": "Iris Species Inventory Dashboard",
        "database": "iris_analytics_db",
        "exported_at": datetime.now().astimezone().isoformat(),
        "export_format": "CSV",
        "reports": []
    }

    report_ids = list_reports()

    print("\nIRIS REPORT EXPORT ENGINE")
    print("=" * 55)

    print("Registered reports:", len(report_ids))

    for report_id in report_ids:

        print(f"\nExporting {report_id}...")

        # Execute the report using the reusable report engine.
        dataframe = run_report(report_id)

        # Generate output filename.
        output_filename = f"{report_id}_report.csv"

        output_path = REPORT_EXPORT_DIR / output_filename

        # Export without changing the source database.
        dataframe.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        report_metadata = {
            "report_id": report_id,
            "filename": output_filename,
            "row_count": int(len(dataframe)),
            "column_count": int(len(dataframe.columns)),
            "columns": list(dataframe.columns),
            "file_size_bytes": output_path.stat().st_size,
            "status": "SUCCESS"
        }

        manifest["reports"].append(report_metadata)

        logger.info(
            "%s exported successfully. Rows: %s",
            report_id,
            len(dataframe)
        )

        print("Status: SUCCESS")
        print("Rows:", len(dataframe))
        print("Columns:", len(dataframe.columns))
        print("File:", output_filename)

    # --------------------------------------------------
    # 4. SAVE EXPORT MANIFEST
    # --------------------------------------------------

    manifest_path = (
        METADATA_DIR / "export_manifest.json"
    )

    with open(
        manifest_path,
        "w",
        encoding="utf-8"
    ) as manifest_file:

        json.dump(
            manifest,
            manifest_file,
            indent=4
        )

    print("\n" + "=" * 55)
    print("EXPORT SUMMARY")
    print("=" * 55)

    print("Reports exported:", len(manifest["reports"]))
    print("Export directory:", REPORT_EXPORT_DIR)
    print("Manifest:", manifest_path)

    print("\nALL REPORT EXPORTS COMPLETED")


if __name__ == "__main__":

    try:
        export_all_reports()

    except Exception:

        logger.exception("Report export process failed")

        print("\nEXPORT FAILED.")
        print("Check logs/export_engine.log for details.")

        raise
