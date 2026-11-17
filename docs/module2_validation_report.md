
# Module 2: Analytical Validation Report

## 1. Objective

The objective of independent validation is to compare SQL report
outputs with calculations performed independently using the
processed Iris reference dataset.

## 2. Reference Dataset

| Attribute | Value |
|---|---|
| Dataset | Iris |
| Total records | 150 |
| Numerical measurement variables | 4 |
| Species categories | 3 |
| Records per species | 50 |
| Measurement unit | Centimetres |

## 3. Validation Method

The SQL reports are executed through the Python report engine.
Pandas independently calculates reference statistics from
`data/processed/cleaned_iris.csv`.

The comparison covers:

- Species counts and percentages
- Species-wise measurement averages
- Sepal scatter data
- Petal scatter data
- Measurement summary statistics
- Optional specimen filters
- Empty-result handling

## 4. Numerical Validation

The R09 report includes:

- Minimum
- Maximum
- Range
- Mean
- Population standard deviation

SQL statistics are rounded to two decimal places. Comparisons
account for this rounding.

## 5. Report Engine Functional Tests

The report engine test script verifies:

- Database connection
- Ten registered reports
- Successful SQL execution
- Expected result row counts
- Species filtering
- Measurement-range filtering
- Empty-result handling
- Rejection of invalid measurement ranges

## 6. Validation Outcome

The initial report-engine functional test completed successfully.

Independent validation of R01-R10 was executed using the reference
dataset. The final numerical validation outcome must be recorded
after all R09 comparisons have been executed.

Final validation status: To be confirmed from the final terminal output.

## 7. Conclusion

Independent analytical validation provides a reproducible method
for checking that SQL report outputs correspond to calculations
from the processed reference dataset.

The validated reports provide the analytical foundation for the
Iris Species Inventory Dashboard.
