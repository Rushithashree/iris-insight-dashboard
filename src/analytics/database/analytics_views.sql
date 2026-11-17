
-- =========================================================
-- IRISINSIGHT: MODULE 2
-- REUSABLE SQL ANALYTICS VIEWS
-- Database: iris_analytics_db
-- =========================================================

USE iris_analytics_db;


-- ---------------------------------------------------------
-- VIEW 1: SPECIES DISTRIBUTION
-- Purpose:
-- Count specimens belonging to each species and calculate
-- their percentage of the complete specimen dataset.
-- ---------------------------------------------------------

CREATE OR REPLACE VIEW vw_species_distribution AS
SELECT
    sm.species_id,
    sm.species_name,
    COUNT(s.specimen_id) AS specimen_count,
    ROUND(
        COUNT(s.specimen_id) * 100.0 /
        NULLIF(
            (SELECT COUNT(*) FROM specimen),
            0
        ),
        2
    ) AS species_percentage
FROM species_master sm
LEFT JOIN specimen s
    ON sm.species_id = s.species_id
GROUP BY
    sm.species_id,
    sm.species_name;


-- ---------------------------------------------------------
-- VIEW 2: SPECIES MEASUREMENT AVERAGES
-- Purpose:
-- Calculate average measurements for each species.
-- ---------------------------------------------------------

CREATE OR REPLACE VIEW vw_species_measurement_averages AS
SELECT
    sm.species_id,
    sm.species_name,

    COUNT(s.specimen_id) AS specimen_count,

    ROUND(AVG(s.sepal_length_cm), 2)
        AS avg_sepal_length_cm,

    ROUND(AVG(s.sepal_width_cm), 2)
        AS avg_sepal_width_cm,

    ROUND(AVG(s.petal_length_cm), 2)
        AS avg_petal_length_cm,

    ROUND(AVG(s.petal_width_cm), 2)
        AS avg_petal_width_cm

FROM species_master sm

LEFT JOIN specimen s
    ON sm.species_id = s.species_id

GROUP BY
    sm.species_id,
    sm.species_name;


-- ---------------------------------------------------------
-- VIEW 3: SPECIES MEASUREMENT STATISTICS
-- Purpose:
-- Calculate minimum, maximum, average and population
-- standard deviation for all four measurements.
-- ---------------------------------------------------------

CREATE OR REPLACE VIEW vw_species_measurement_statistics AS
SELECT
    sm.species_id,
    sm.species_name,

    COUNT(s.specimen_id) AS specimen_count,

    ROUND(MIN(s.sepal_length_cm), 2)
        AS min_sepal_length_cm,

    ROUND(MAX(s.sepal_length_cm), 2)
        AS max_sepal_length_cm,

    ROUND(AVG(s.sepal_length_cm), 2)
        AS avg_sepal_length_cm,

    ROUND(STDDEV_POP(s.sepal_length_cm), 2)
        AS sd_sepal_length_cm,


    ROUND(MIN(s.sepal_width_cm), 2)
        AS min_sepal_width_cm,

    ROUND(MAX(s.sepal_width_cm), 2)
        AS max_sepal_width_cm,

    ROUND(AVG(s.sepal_width_cm), 2)
        AS avg_sepal_width_cm,

    ROUND(STDDEV_POP(s.sepal_width_cm), 2)
        AS sd_sepal_width_cm,


    ROUND(MIN(s.petal_length_cm), 2)
        AS min_petal_length_cm,

    ROUND(MAX(s.petal_length_cm), 2)
        AS max_petal_length_cm,

    ROUND(AVG(s.petal_length_cm), 2)
        AS avg_petal_length_cm,

    ROUND(STDDEV_POP(s.petal_length_cm), 2)
        AS sd_petal_length_cm,


    ROUND(MIN(s.petal_width_cm), 2)
        AS min_petal_width_cm,

    ROUND(MAX(s.petal_width_cm), 2)
        AS max_petal_width_cm,

    ROUND(AVG(s.petal_width_cm), 2)
        AS avg_petal_width_cm,

    ROUND(STDDEV_POP(s.petal_width_cm), 2)
        AS sd_petal_width_cm

FROM species_master sm

LEFT JOIN specimen s
    ON sm.species_id = s.species_id

GROUP BY
    sm.species_id,
    sm.species_name;
