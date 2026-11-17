
-- R09: Measurement Spread by Species

SELECT
    species_name,
    specimen_count,

    min_sepal_length_cm,
    max_sepal_length_cm,
    ROUND(
        max_sepal_length_cm - min_sepal_length_cm, 2
    ) AS sepal_length_range_cm,
    avg_sepal_length_cm,
    sd_sepal_length_cm,

    min_sepal_width_cm,
    max_sepal_width_cm,
    ROUND(
        max_sepal_width_cm - min_sepal_width_cm, 2
    ) AS sepal_width_range_cm,
    avg_sepal_width_cm,
    sd_sepal_width_cm,

    min_petal_length_cm,
    max_petal_length_cm,
    ROUND(
        max_petal_length_cm - min_petal_length_cm, 2
    ) AS petal_length_range_cm,
    avg_petal_length_cm,
    sd_petal_length_cm,

    min_petal_width_cm,
    max_petal_width_cm,
    ROUND(
        max_petal_width_cm - min_petal_width_cm, 2
    ) AS petal_width_range_cm,
    avg_petal_width_cm,
    sd_petal_width_cm

FROM vw_species_measurement_statistics
ORDER BY species_id;
