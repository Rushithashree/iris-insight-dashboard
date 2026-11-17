
# IRIS SPECIES INVENTORY DASHBOARD
## Data Dictionary

### 1. Dataset Information

Dataset Name: Iris Dataset
Source: UCI Machine Learning Repository
Total Records: 150
Total Attributes: 5
Measurement Unit: Centimetres (cm)
Species Categories: 3

### 2. Attribute Definitions

| Attribute | Data Type | Unit | Description | Validation |
|---|---|---|---|---|
| sepal_length_cm | FLOAT | cm | Length of the sepal | Positive numeric value |
| sepal_width_cm | FLOAT | cm | Width of the sepal | Positive numeric value |
| petal_length_cm | FLOAT | cm | Length of the petal | Positive numeric value |
| petal_width_cm | FLOAT | cm | Width of the petal | Positive numeric value |
| species | VARCHAR | Not applicable | Scientific species category | Must belong to an approved species |

### 3. Species Categories

1. Iris-setosa
2. Iris-versicolor
3. Iris-virginica

### 4. Measurement Characteristics

All four measurement attributes are continuous numerical variables.

The original dataset stores measurements in centimetres.

### 5. Data Source and Integrity

The original dataset is retained without modifying its observations.

Each imported record will receive a system-generated specimen identifier.

Identical measurement records will not automatically be deleted because identical values do not establish that two records represent the same physical specimen.

### 6. Database Design Implications

- Every specimen record must have a unique primary key.
- Species information will be maintained in a separate species master table.
- Each specimen record will reference a valid species identifier.
- Measurement values must be positive.
- Original source records must remain traceable.
