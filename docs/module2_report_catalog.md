
# Module 2: Analytical Report Catalogue

## 1. Module Overview

Module 2 implements a reusable SQL-based analytical reporting system
for the Iris Species Inventory Dashboard.

The system uses MySQL 8 for structured data storage and analytical
queries, SQLAlchemy for database connectivity, and Pandas for
retrieving report results.

Ten analytical reports are registered under report identifiers R01
to R10.

## 2. Report Catalogue

| Report ID | Report Name | Description | Expected Output |
|---|---|---|---|
| R01 | Species Record Count | Counts specimen records for each Iris species. | 3 rows |
| R02 | Species Share | Calculates each species' percentage of total records. | 3 rows |
| R03 | Mean Sepal Length | Calculates average sepal length by species. | 3 rows |
| R04 | Mean Sepal Width | Calculates average sepal width by species. | 3 rows |
| R05 | Mean Petal Length | Calculates average petal length by species. | 3 rows |
| R06 | Mean Petal Width | Calculates average petal width by species. | 3 rows |
| R07 | Sepal Scatter Data | Retrieves sepal length and width for specimen-level visualization. | 150 rows |
| R08 | Petal Scatter Data | Retrieves petal length and width for specimen-level visualization. | 150 rows |
| R09 | Measurement Spread | Reports minimum, maximum, range, mean, and population standard deviation for each measurement and species. | 3 rows |
| R10 | Filtered Specimen Explorer | Retrieves specimen records using optional species, ID, and measurement-range filters. | Variable |

## 3. Measurement Variables

All measurements are recorded in centimetres (cm).

- Sepal length
- Sepal width
- Petal length
- Petal width

## 4. Database Views

The following reusable SQL views support analytical reporting:

- `vw_species_distribution`
- `vw_species_measurement_averages`
- `vw_species_measurement_statistics`

These views reduce repeated aggregation logic across report queries.

## 5. Report Execution Architecture

1. The report engine receives a report identifier.
2. The identifier is checked against the report registry.
3. The corresponding SQL file is loaded.
4. SQLAlchemy establishes a connection to the MySQL database.
5. The SQL query is executed.
6. Pandas retrieves the result as a DataFrame.
7. Execution details are recorded in the application log.

R10 uses bound parameters for optional filters in the Python application.

## 6. Data Integrity Considerations

The reporting system preserves all 150 source records.

Identical measurement combinations are not treated as proof of
duplicate physical specimens. Records are retained, and duplicate
occurrences are documented separately through the data-quality log.

## 7. Intended Use

The reports support:

- Species distribution analysis
- Comparative measurement analysis
- Descriptive statistical analysis
- Specimen-level scatter plot preparation
- Filtered specimen exploration

The outputs are descriptive analyses of the supplied Iris dataset.
They are not intended to identify unknown species or establish
biological causation.

## 8. Export Policy

Report results are exported as CSV files for reproducibility,
inspection, and downstream visualization.

The export process does not modify the MySQL database or source data.

## 9. Limitations

- The dataset contains 150 records and three Iris species.
- The analysis is descriptive rather than predictive.
- Results depend on the quality and scope of the source dataset.
- The specimen identifier is a database record identifier, not
  confirmation of a unique physical plant.
