# Intelligent Systems Engineering for Mbajk
The Bike Availability Prediction AI is an innovative system designed to forecast the availability of bikes at specific locations. Leveraging advanced machine learning techniques, including Recurrent Neural Networks (RNNs), and real-time data from weather sources and bike stations, the AI model continuously refines its predictions to provide accurate insights into bike availability.

### Key Features:

- Predicts bike availability based on weather and real-time data from bike stations.
- Utilizes Recurrent Neural Networks (RNNs) for dynamic and accurate predictions.
- Automated pipelines ensure continuous data fetching, processing, and model training.
- CI/CD deployment guarantees rapid updates and seamless operation of the backend ML service and web client application.
- Implements data version control (DVC) and experiment tracking (MLflow) for efficient model management and experimentation.
- Optimizes models through quantization techniques and utilizes ONNX format for efficient representation and inference.

Users can access bike availability predictions via a REST API, querying specific locations to obtain real-time insights. Additionally, a user-friendly web client application provides visualization of predictions, enhancing accessibility and usability.

## Installation

```shell
poetry install
```
## Project Structure
```
├── README.md <- File containing project description and setup instructions
├── data
    ├── processed <- Processed data, prepared for training models
    └── raw <- Raw fetched data
├── models <- Trained and serialized models, model predictions, or summaries of models
├── notebooks <- Jupyter notebooks
├── reports <- Generated analysis files
    └── figures <- Generated graphs and images used in the analysis
    └── sites <- Generated sites in the data validation
├── pyproject.toml <- File defining dependencies, library versions, etc.
├── src <- Source code of the project
  ├── __init__.py <- Initializes the "src" directory as a Python module
  ├── data <- Scripts for data downloading, processing, etc.
      └── validation <- Scripts for data validation
  ├── models <- Scripts for training predictive models and using models for prediction
  ├── serve <- Scripts for serving models as web services
  ├── client <- Source code for the user interface
  |── tests <- Tests for the project
  ├── config.py <- Project configuration file
  └── visualization <- Scripts for visualization
```

## Serve
To start the server, run the following command:

```shell
poetry run poe serve
```

## Fetch and Process Data
To fetch and process data, run the following commands:

```shell
poetry run poe fetch_data
poetry run poe process_data
```

## Test
To run tests, execute the following command:

```shell
poetry run poe test
poetry run test_api
```

## Data Validation
To run data validation, execute the following command:

```shell
poetry run poe validate
poetry run poe data_drift
poetry run poe stability_tests
poetry run poe ks_test
```

## Model Validaton
To run model validation, execute the following command:

```shell
poetry run poe validate_predictions
```

## Train models
To run model training, execute the following command:

```shell
poetry run poe train
poetry run poe predict
```
