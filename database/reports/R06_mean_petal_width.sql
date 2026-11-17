
-- R06: Mean Petal Width by Species

SELECT
    species_name,
    specimen_count,
    avg_petal_width_cm
FROM vw_species_measurement_averages
ORDER BY species_id;
