
from pathlib import Path
import numpy as np
import pandas as pd

from report_engine import run_report


# --------------------------------------------------
# 1. LOAD THE INDEPENDENT REFERENCE DATASET
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_iris.csv"
)

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Reference dataset not found: {DATASET_PATH}"
    )

reference = pd.read_csv(DATASET_PATH)

measurements = [
    "sepal_length_cm",
    "sepal_width_cm",
    "petal_length_cm",
    "petal_width_cm"
]

required_columns = measurements + ["species"]

missing_columns = [
    column for column in required_columns
    if column not in reference.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns in cleaned dataset: {missing_columns}"
    )


# --------------------------------------------------
# 2. VALIDATION UTILITIES
# --------------------------------------------------

passed = 0
failed = 0


def check_result(description, condition):

    global passed, failed

    if condition:
        passed += 1
        print(f"PASS: {description}")

    else:
        failed += 1
        print(f"FAIL: {description}")


def compare_numeric(actual, expected, tolerance=0.01):

    return np.allclose(
        np.asarray(actual, dtype=float),
        np.asarray(expected, dtype=float),
        atol=tolerance,
        rtol=0
    )


# --------------------------------------------------
# 3. REFERENCE SPECIES STATISTICS
# --------------------------------------------------

reference_counts = (
    reference["species"]
    .value_counts()
    .sort_index()
)

reference_percentages = (
    reference_counts / len(reference) * 100
).round(2)

reference_means = (
    reference.groupby("species")[measurements]
    .mean()
    .round(2)
)

print("\nIRIS REPORT VALIDATION")
print("=" * 60)

print("Reference records:", len(reference))
print("\nReference species counts:")
print(reference_counts)


# --------------------------------------------------
# 4. R01 - SPECIES RECORD COUNT
# --------------------------------------------------

r01 = run_report("R01")

r01_counts = (
    r01.set_index("species_name")["specimen_count"]
    .sort_index()
)

check_result(
    "R01 species record counts match reference data",
    r01_counts.equals(reference_counts)
)


# --------------------------------------------------
# 5. R02 - SPECIES SHARE
# --------------------------------------------------

r02 = run_report("R02")

r02 = r02.set_index("species_name").sort_index()

check_result(
    "R02 species percentages match reference data",
    compare_numeric(
        r02["species_percentage"],
        reference_percentages.loc[r02.index]
    )
)


# --------------------------------------------------
# 6. R03-R06 - MEASUREMENT AVERAGES
# --------------------------------------------------

average_reports = {
    "R03": "avg_sepal_length_cm",
    "R04": "avg_sepal_width_cm",
    "R05": "avg_petal_length_cm",
    "R06": "avg_petal_width_cm"
}

for report_id, average_column in average_reports.items():

    result = run_report(report_id)

    result = (
        result.set_index("species_name")
        .sort_index()
    )

    measurement_column = average_column.replace(
        "avg_", ""
    )

    expected = reference_means.loc[
        result.index, measurement_column
    ]

    check_result(
        f"{report_id} measurement averages match reference data",
        compare_numeric(
            result[average_column],
            expected
        )
    )


# --------------------------------------------------
# 7. R07 - SEPAL SCATTER DATA
# --------------------------------------------------

r07 = run_report("R07")

reference_sepal = reference[
    ["species", "sepal_length_cm", "sepal_width_cm"]
].copy()

database_sepal = r07[
    ["species_name", "sepal_length_cm", "sepal_width_cm"]
].copy()

reference_sepal = reference_sepal.rename(
    columns={"species": "species_name"}
)

sort_columns = [
    "species_name",
    "sepal_length_cm",
    "sepal_width_cm"
]

reference_sepal = (
    reference_sepal.sort_values(sort_columns)
    .reset_index(drop=True)
)

database_sepal = (
    database_sepal.sort_values(sort_columns)
    .reset_index(drop=True)
)

check_result(
    "R07 sepal scatter data matches reference records",
    len(database_sepal) == len(reference_sepal)
    and database_sepal["species_name"].equals(
        reference_sepal["species_name"]
    )
    and compare_numeric(
        database_sepal[measurements[:2]],
        reference_sepal[measurements[:2]]
    )
)


# --------------------------------------------------
# 8. R08 - PETAL SCATTER DATA
# --------------------------------------------------

r08 = run_report("R08")

reference_petal = reference[
    ["species", "petal_length_cm", "petal_width_cm"]
].copy()

database_petal = r08[
    ["species_name", "petal_length_cm", "petal_width_cm"]
].copy()

reference_petal = reference_petal.rename(
    columns={"species": "species_name"}
)

sort_columns = [
    "species_name",
    "petal_length_cm",
    "petal_width_cm"
]

reference_petal = (
    reference_petal.sort_values(sort_columns)
    .reset_index(drop=True)
)

database_petal = (
    database_petal.sort_values(sort_columns)
    .reset_index(drop=True)
)

check_result(
    "R08 petal scatter data matches reference records",
    len(database_petal) == len(reference_petal)
    and database_petal["species_name"].equals(
        reference_petal["species_name"]
    )
    and compare_numeric(
        database_petal[measurements[2:]],
        reference_petal[measurements[2:]]
    )
)


# --------------------------------------------------
# 9. R09 - MEASUREMENT SPREAD
# --------------------------------------------------

r09 = run_report("R09")

r09_indexed = r09.set_index("species_name")

species_names = sorted(reference["species"].unique())

check_result(
    "R09 contains statistics for all three species",
    len(r09) == 3
    and set(r09["species_name"]) == set(species_names)
)

print("\nR09 NUMERICAL VALIDATION:")

# SQL statistics are rounded to two decimal places.
# A tolerance of 0.0051 accounts for that rounding.

tolerance = 0.0051

for species_name in species_names:

    group = reference[
        reference["species"] == species_name
    ]

    database_row = r09_indexed.loc[species_name]

    for column in measurements:

        prefix = column.replace("_cm", "")

        expected_statistics = {
            f"min_{prefix}_cm": group[column].min(),
            f"max_{prefix}_cm": group[column].max(),
            f"{prefix}_range_cm": (
                group[column].max() - group[column].min()
            ),
            f"avg_{prefix}_cm": group[column].mean(),
            f"sd_{prefix}_cm": group[column].std(ddof=0)
        }

        for database_column, expected_value in (
            expected_statistics.items()
        ):

            actual_value = float(
                database_row[database_column]
            )

            matches = np.isclose(
                actual_value,
                expected_value,
                atol=tolerance,
                rtol=0
            )

            check_result(
                f"R09 {species_name} - {database_column}",
                matches
            )

            if not matches:

                print(
                    f"    Database: {actual_value:.4f} | "
                    f"Reference: {expected_value:.4f}"
                )



# --------------------------------------------------
# 10. R10 - FILTERED SPECIMEN EXPLORER
# --------------------------------------------------

r10_all = run_report("R10")

check_result(
    "R10 unfiltered query returns all 150 records",
    len(r10_all) == len(reference)
)

r10_setosa = run_report(
    "R10",
    filters={"species_name": "Iris-setosa"}
)

check_result(
    "R10 species filter returns 50 setosa records",
    len(r10_setosa) == 50
    and (r10_setosa["species_name"] == "Iris-setosa").all()
)

r10_range = run_report(
    "R10",
    filters={
        "min_petal_length": 1.0,
        "max_petal_length": 2.0
    }
)

check_result(
    "R10 petal-length filter respects inclusive boundaries",
    (
        r10_range["petal_length_cm"].between(1.0, 2.0).all()
    )
)

r10_empty = run_report(
    "R10",
    filters={
        "min_petal_length": 100.0,
        "max_petal_length": 101.0
    }
)

check_result(
    "R10 handles valid filters with zero matching records",
    len(r10_empty) == 0
)


# --------------------------------------------------
# 11. FINAL VALIDATION SUMMARY
# --------------------------------------------------

print("\n" + "=" * 60)
print("INDEPENDENT VALIDATION SUMMARY")
print("=" * 60)

print("Tests passed:", passed)
print("Tests failed:", failed)

if failed == 0:

    print("\nALL INDEPENDENT VALIDATION CHECKS PASSED")

else:

    print("\nVALIDATION NEEDS ATTENTION")

    raise SystemExit(1)
