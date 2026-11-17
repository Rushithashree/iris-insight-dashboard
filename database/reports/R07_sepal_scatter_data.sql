
-- R07: Sepal Length vs Sepal Width

SELECT
    s.specimen_id,
    sm.species_name,
    s.sepal_length_cm,
    s.sepal_width_cm
FROM specimen s
JOIN species_master sm
    ON s.species_id = sm.species_id
ORDER BY s.specimen_id;
