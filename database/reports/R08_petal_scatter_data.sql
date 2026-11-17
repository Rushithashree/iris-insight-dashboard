
-- R08: Petal Length vs Petal Width

SELECT
    s.specimen_id,
    sm.species_name,
    s.petal_length_cm,
    s.petal_width_cm
FROM specimen s
JOIN species_master sm
    ON s.species_id = sm.species_id
ORDER BY s.specimen_id;
