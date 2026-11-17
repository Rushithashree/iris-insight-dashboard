
-- R01: Species Record Count

SELECT
    species_id,
    species_name,
    specimen_count
FROM vw_species_distribution
ORDER BY species_id;
