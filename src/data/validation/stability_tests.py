import pandas as pd
from evidently.test_preset import DataStabilityTestPreset
from evidently.test_suite import TestSuite

if __name__ == "__main__":
    tests = TestSuite(tests=[
        DataStabilityTestPreset()
    ])

    current_data = pd.read_csv("data/processed/current_data.csv")
    reference_data = pd.read_csv("data/processed/reference_data.csv")

    tests.run(reference_data=current_data, current_data=reference_data)

    tests.save_html("reports/sites/stability_tests.html")
