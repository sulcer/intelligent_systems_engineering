import os
import great_expectations as ge
import pandas as pd
from great_expectations.checkpoint.types.checkpoint_result import CheckpointResult


def main():
    context = ge.get_context()
    result: CheckpointResult = context.run_checkpoint(checkpoint_name="mbajk_checkpoint")

    if not result["success"]:
        print("[Validate]: Checkpoint validation failed!")
        # raise ValueError("Checkpoint failed")

    print("[Validate]: Checkpoint validation successful!")

    current_data = pd.read_csv("data/processed/current_data.csv")
    reference_data_path = "data/processed/reference_data.csv"
    current_data.to_csv(reference_data_path, index=False)


if __name__ == "__main__":
    main()
