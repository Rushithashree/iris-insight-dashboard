
SELECT
    s.specimen_id,
    s.source_row_number,
    sm.species_name,
    s.sepal_length_cm,
    s.sepal_width_cm,
    s.petal_length_cm,
    s.petal_width_cm,
    s.import_batch_id
FROM specimen s
JOIN species_master sm
    ON s.species_id = sm.species_id
WHERE
    (:species_name IS NULL OR sm.species_name = :species_name)
    AND (:specimen_id IS NULL OR s.specimen_id = :specimen_id)
    AND (:min_sepal_length IS NULL OR s.sepal_length_cm >= :min_sepal_length)
    AND (:max_sepal_length IS NULL OR s.sepal_length_cm <= :max_sepal_length)
    AND (:min_sepal_width IS NULL OR s.sepal_width_cm >= :min_sepal_width)
    AND (:max_sepal_width IS NULL OR s.sepal_width_cm <= :max_sepal_width)
    AND (:min_petal_length IS NULL OR s.petal_length_cm >= :min_petal_length)
    AND (:max_petal_length IS NULL OR s.petal_length_cm <= :max_petal_length)
    AND (:min_petal_width IS NULL OR s.petal_width_cm >= :min_petal_width)
    AND (:max_petal_width IS NULL OR s.petal_width_cm <= :max_petal_width)
ORDER BY s.specimen_id;
