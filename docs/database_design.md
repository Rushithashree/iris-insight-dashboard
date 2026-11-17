
# DATABASE DESIGN DECISIONS

1. Database Name:
   iris_analytics_db

2. Database Engine:
   MySQL 8.0 with InnoDB

3. Design Approach:
   Relational database with normalized master and transaction tables.

4. Main Tables:
   - species_master
   - import_batch
   - measurement_records
   - data_quality_log

5. Primary Key Strategy:
   System-generated integer identifiers.

6. Foreign Key Strategy:
   Enforce species and import batch relationships.

7. Duplicate Handling:
   Preserve all original records.
   Flag identical measurements for review.
   Do not automatically delete duplicate observations.

8. Source Traceability:
   Store original source row number and import batch identifier.

9. Measurement Validation:
   Require positive numerical measurements.

10. Referential Integrity:
    Use foreign keys to prevent invalid species and import references.
