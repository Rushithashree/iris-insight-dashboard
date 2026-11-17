
from pathlib import Path
import pandas as pd

# Locate the original dataset
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "iris.data"

# Original Iris dataset has no column headings
columns = [
    "sepal_length_cm",
    "sepal_width_cm",
    "petal_length_cm",
    "petal_width_cm",
    "species"
]

def inspect_dataset():
    if not DATA_FILE.exists():
        print("ERROR: iris.data was not found.")
        print("Expected location:", DATA_FILE)
        return

    # Load the original dataset without changing it
    df = pd.read_csv(
        DATA_FILE,
        header=None,
        names=columns,
        skip_blank_lines=True
    )

    # Remove accidental spaces around species labels
    df["species"] = df["species"].astype("string").str.strip()

    print("\n========== IRIS DATASET INSPECTION ==========")

    print("\n1. DATASET DIMENSIONS")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

    print("\n2. FIRST FIVE RECORDS")
    print(df.head().to_string(index=False))

    print("\n3. DATA TYPES")
    print(df.dtypes)

    print("\n4. MISSING VALUES")
    print(df.isnull().sum())

    print("\n5. SPECIES DISTRIBUTION")
    print(df["species"].value_counts(dropna=False))

    print("\n6. DUPLICATE RECORDS")
    duplicate_rows = df[df.duplicated(keep=False)]
    
    print("Duplicate rows including original occurrences:")
    print(duplicate_rows.to_string(index=True))
    
    print("\nNumber of duplicate rows after first occurrence:")
    print(df.duplicated().sum())

    print("\n7. MEASUREMENT SUMMARY")
    print(df[columns[:4]].describe().round(2))

    print("\n8. UNIQUE SPECIES")
    print(sorted(df["species"].dropna().unique()))

    print("\n========== INSPECTION COMPLETE ==========")

if __name__ == "__main__":
    inspect_dataset()
