
from pathlib import Path
import pandas as pd
import numpy as np

# --------------------------------------------------
# 1. PROJECT PATHS AND CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = PROJECT_ROOT / "data" / "iris.data"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLUMNS = [
    "sepal_length_cm",
    "sepal_width_cm",
    "petal_length_cm",
    "petal_width_cm",
    "species"
]

NUMERIC_COLUMNS = COLUMNS[:4]

VALID_SPECIES = {
    "Iris-setosa",
    "Iris-versicolor",
    "Iris-virginica"
}


# --------------------------------------------------
# 2. LOAD ORIGINAL DATASET
# --------------------------------------------------

def load_dataset():

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {SOURCE_FILE}"
        )

    df = pd.read_csv(
        SOURCE_FILE,
        header=None,
        names=COLUMNS,
        skip_blank_lines=True
    )

    # Assign a stable row position within this import
    df.insert(
        0,
        "source_row_number",
        range(1, len(df) + 1)
    )

    return df


# --------------------------------------------------
# 3. VALIDATE AND STANDARDIZE RECORDS
# --------------------------------------------------

def validate_dataset(df):

    df = df.copy()

    # Standardize whitespace around species names
    df["species"] = (
        df["species"]
        .astype("string")
        .str.strip()
    )

    issues = []

    for _, row in df.iterrows():

        row_issues = []

        # Validate numerical measurements
        for column in NUMERIC_COLUMNS:

            value = pd.to_numeric(
                pd.Series([row[column]]),
                errors="coerce"
            ).iloc[0]

            if pd.isna(value):
                row_issues.append(
                    f"{column}: missing or non-numeric"
                )

            elif not np.isfinite(value):
                row_issues.append(
                    f"{column}: non-finite value"
                )

            elif value <= 0:
                row_issues.append(
                    f"{column}: value must be positive"
                )

            else:
                df.at[row.name, column] = float(value)

        # Validate species
        species = row["species"]

        if pd.isna(species) or species == "":
            row_issues.append("Species: missing value")

        elif species not in VALID_SPECIES:
            row_issues.append(
                f"Species: invalid category ({species})"
            )

        issues.append(row_issues)

    df["quality_issues"] = [
        "; ".join(row_issues)
        for row_issues in issues
    ]

    df["validation_status"] = [
        "Rejected" if row_issues else "Accepted"
        for row_issues in issues
    ]

    return df


# --------------------------------------------------
# 4. IDENTIFY DUPLICATE RECORDS
# --------------------------------------------------

def flag_duplicates(accepted_df):

    accepted_df = accepted_df.copy()

    # Duplicate identification uses the original
    # four measurements and species only.
    group_sizes = accepted_df.groupby(
        COLUMNS,
        dropna=False
    )["source_row_number"].transform("size")

    accepted_df["is_exact_duplicate"] = (
        group_sizes > 1
    )

    accepted_df["duplicate_group_size"] = (
        group_sizes
    )

    return accepted_df


# --------------------------------------------------
# 5. GENERATE QUALITY REPORT
# --------------------------------------------------

def generate_quality_report(
    original_df,
    accepted_df,
    rejected_df
):

    total_records = len(original_df)
    accepted_records = len(accepted_df)
    rejected_records = len(rejected_df)

    duplicate_occurrences = int(
        accepted_df.duplicated(
            subset=COLUMNS
        ).sum()
    )

    duplicate_rows_flagged = int(
        accepted_df["is_exact_duplicate"].sum()
    )

    duplicate_groups = accepted_df.loc[
        accepted_df["is_exact_duplicate"],
        COLUMNS
    ].drop_duplicates().shape[0]

    species_distribution = (
        accepted_df["species"]
        .value_counts()
        .to_dict()
    )

    report = []

    report.append("IRIS DATA QUALITY REPORT")
    report.append("=" * 45)

    report.append(
        f"Total original records: {total_records}"
    )

    report.append(
        f"Accepted records: {accepted_records}"
    )

    report.append(
        f"Rejected records: {rejected_records}"
    )

    report.append(
        f"Duplicate groups: {duplicate_groups}"
    )

    report.append(
        f"Rows flagged as duplicates: {duplicate_rows_flagged}"
    )

    report.append(
        f"Additional duplicate occurrences: {duplicate_occurrences}"
    )

    report.append("\nSPECIES DISTRIBUTION")

    for species, count in species_distribution.items():
        report.append(f"{species}: {count}")

    report.append("\nREJECTED RECORDS")

    if rejected_df.empty:
        report.append("No rejected records.")
    else:
        for _, row in rejected_df.iterrows():
            report.append(
                f"Source row {row['source_row_number']}: "
                f"{row['quality_issues']}"
            )

    report.append("\nVALIDATION COMPLETE")

    report_text = "\n".join(report)

    report_path = OUTPUT_DIR / "quality_report.txt"

    report_path.write_text(
        report_text,
        encoding="utf-8"
    )

    print("\n" + report_text)


# --------------------------------------------------
# 6. SAVE OUTPUT FILES
# --------------------------------------------------

def save_outputs(accepted_df, rejected_df):

    cleaned_path = OUTPUT_DIR / "cleaned_iris.csv"

    rejected_path = OUTPUT_DIR / "rejected_records.csv"

    accepted_df.to_csv(
        cleaned_path,
        index=False
    )

    rejected_df.to_csv(
        rejected_path,
        index=False
    )

    print("\nOUTPUT FILES CREATED")

    print("Cleaned dataset:", cleaned_path)

    print("Rejected records:", rejected_path)


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

def main():

    print("\nIRIS DATA CLEANING ENGINE")
    print("=" * 45)

    original_df = load_dataset()

    print(
        "Original records loaded:",
        len(original_df)
    )

    validated_df = validate_dataset(original_df)

    accepted_df = validated_df[
        validated_df["validation_status"] == "Accepted"
    ].copy()

    rejected_df = validated_df[
        validated_df["validation_status"] == "Rejected"
    ].copy()

    # Convert accepted numerical measurements
    for column in NUMERIC_COLUMNS:
        accepted_df[column] = pd.to_numeric(
            accepted_df[column]
        ).astype(float)

    accepted_df = flag_duplicates(accepted_df)

    # Keep quality issues in the report and rejected file.
    # Accepted rows do not need an empty issue column.
    accepted_df = accepted_df.drop(
        columns=["quality_issues", "validation_status"]
    )

    save_outputs(accepted_df, rejected_df)

    generate_quality_report(
        original_df,
        accepted_df,
        rejected_df
    )

    print("\nCLEANING ENGINE EXECUTED SUCCESSFULLY")


if __name__ == "__main__":
    main()
