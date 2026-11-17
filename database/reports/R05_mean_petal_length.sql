
-- R05: Mean Petal Length by Species

SELECT
    species_name,
    specimen_count,
    avg_petal_length_cm
FROM vw_species_measurement_averages
ORDER BY species_id;
