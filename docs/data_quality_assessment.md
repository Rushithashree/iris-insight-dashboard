
# IRIS DATASET - DATA QUALITY ASSESSMENT

## 1. Inspection Results

| Quality Parameter | Observed Result | Status |
|---|---:|---|
| Total records | 150 | Passed |
| Total attributes | 5 | Passed |
| Numeric measurement columns | 4 | Passed |
| Species categories | 3 | Passed |
| Missing measurement values | 0 | Passed |
| Missing species values | 0 | Passed |
| Exact duplicate rows | 3 | Requires review |
| Species distribution | 50 each | Passed |

## 2. Species Distribution

| Species | Record Count |
|---|---:|
| Iris-setosa | 50 |
| Iris-versicolor | 50 |
| Iris-virginica | 50 |

## 3. Duplicate Record Assessment

Three exact duplicate rows were detected.

An exact duplicate means that all five attribute values match another row.

These records will be flagged for review rather than automatically removed.

The dataset contains no unique physical specimen identifiers. Therefore, it is not possible to determine whether identical rows represent repeated observations or distinct specimens with identical measurements.

## 4. Data Quality Rules

1. All four measurement fields must contain numeric values.
2. Measurement values must be greater than zero.
3. Species must match one of the three approved categories.
4. Missing species values must be rejected.
5. Missing measurement values must be flagged.
6. Duplicate measurement records must be identified and reviewed.
7. Every database specimen record must receive a unique system-generated identifier.

## 5. Conclusion

The initial inspection confirms that the Iris dataset contains 150 records, five attributes, and three equally represented species categories.

No missing values were identified. Three exact duplicate records require review.

The original dataset will be preserved, and data quality checks will be incorporated into the ingestion process.
