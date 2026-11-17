
-- R02: Species Share Percentage

SELECT
    species_name,
    specimen_count,
    species_percentage
FROM vw_species_distribution
ORDER BY species_id;
