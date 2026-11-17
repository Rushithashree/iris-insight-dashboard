
from report_engine import (
    run_report,
    list_reports,
    test_database_connection
)


def main():

    print("\nIRIS REPORT ENGINE TEST")
    print("=" * 45)

    # Test 1: Database connection
    database = test_database_connection()

    print("\nTEST 1: DATABASE CONNECTION")
    print("Connected database:", database)

    assert database == "iris_analytics_db"

    # Test 2: Report registry
    reports = list_reports()

    print("\nTEST 2: REPORT REGISTRY")
    print("Available reports:", len(reports))
    print("Report IDs:", reports)

    assert len(reports) == 10

    # Test 3: Execute all ten reports
    print("\nTEST 3: REPORT EXECUTION")

    for report_id in reports:

        result = run_report(report_id)

        print(
            f"{report_id}: SUCCESS | "
            f"Rows returned: {len(result)} | "
            f"Columns: {len(result.columns)}"
        )

    # Test 4: Expected row counts
    print("\nTEST 4: ROW COUNT VALIDATION")

    expected_rows = {
        "R01": 3,
        "R02": 3,
        "R03": 3,
        "R04": 3,
        "R05": 3,
        "R06": 3,
        "R07": 150,
        "R08": 150,
        "R09": 3,
        "R10": 150
    }

    for report_id, expected in expected_rows.items():

        result = run_report(report_id)

        actual = len(result)

        print(
            f"{report_id}: Expected={expected}, "
            f"Actual={actual}"
        )

        assert actual == expected, (
            f"{report_id} row count mismatch"
        )

    # Test 5: R10 species filter
    print("\nTEST 5: R10 SPECIES FILTER")

    filtered_result = run_report(
        "R10",
        filters={
            "species_name": "Iris-setosa"
        }
    )

    print(
        "Setosa records returned:",
        len(filtered_result)
    )

    assert len(filtered_result) == 50

    assert (
        filtered_result["species_name"] == "Iris-setosa"
    ).all()

    # Test 6: R10 measurement range
    print("\nTEST 6: R10 MEASUREMENT FILTER")

    range_result = run_report(
        "R10",
        filters={
            "min_petal_length": 1.0,
            "max_petal_length": 2.0
        }
    )

    print(
        "Records within petal length range:",
        len(range_result)
    )

    assert (
        range_result["petal_length_cm"].between(1.0, 2.0)
    ).all()

    # Test 7: Empty result handling
    print("\nTEST 7: EMPTY RESULT HANDLING")

    empty_result = run_report(
        "R10",
        filters={
            "min_petal_length": 100.0,
            "max_petal_length": 101.0
        }
    )

    print("Rows returned:", len(empty_result))

    assert len(empty_result) == 0

    # Test 8: Invalid filter validation
    print("\nTEST 8: INVALID FILTER VALIDATION")

    try:

        run_report(
            "R10",
            filters={
                "min_petal_length": 5.0,
                "max_petal_length": 2.0
            }
        )

        raise AssertionError(
            "Invalid measurement range was accepted."
        )

    except ValueError as error:

        print("Invalid range correctly rejected:", error)

    print("\n" + "=" * 45)
    print("ALL REPORT ENGINE TESTS PASSED")
    print("=" * 45)


if __name__ == "__main__":
    main()
