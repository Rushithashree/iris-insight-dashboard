
-- R04: Mean Sepal Width by Species

SELECT
    species_name,
    specimen_count,
    avg_sepal_width_cm
FROM vw_species_measurement_averages
ORDER BY species_id;
