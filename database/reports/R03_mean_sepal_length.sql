
-- R03: Mean Sepal Length by Species

SELECT
    species_name,
    specimen_count,
    avg_sepal_length_cm
FROM vw_species_measurement_averages
ORDER BY species_id;
