# Requirements Document

## Introduction

This document defines the requirements for the **Credit Risk Explainer** — a local, containerized ML application that predicts credit risk for loan applicants using the UCI German Credit Dataset and provides transparent, human-readable explanations via SHAP values. The system is composed of three main components: a training pipeline, a FastAPI prediction backend, and a Streamlit frontend, all orchestrated via Docker Compose.

The primary goals are reproducibility (Docker-based deployment), transparency (SHAP-based explanations), and usability (a clean Streamlit UI that handles all application states gracefully).

---

## Glossary

- **System**: The complete Credit Risk Explainer application.
- **Pipeline**: The Scikit-learn preprocessing and XGBoost model pipeline persisted as a `.joblib` file.
- **Trainer**: The training script responsible for loading data, fitting the Pipeline, and saving the artifact.
- **API**: The FastAPI backend service that loads the Pipeline and serves predictions.
- **UI**: The Streamlit frontend application that collects applicant input and displays results.
- **Explainer**: The SHAP component that generates local feature-importance explanations for individual predictions.
- **Applicant**: A loan applicant whose features are submitted for credit risk assessment.
- **Risk_Score**: A floating-point probability in [0.0, 1.0] representing the likelihood of credit default.
- **Prediction**: A categorical label — either "High Risk" or "Low Risk" — derived from the Risk_Score.
- **SHAP_Plot**: A SHAP Waterfall or Force Plot visualizing the contribution of each feature to a single prediction.
- **Zero_State**: The initial state of the UI before any prediction has been requested.
- **Docker_Compose**: The orchestration configuration that builds and runs the API and UI containers together.

---

## Requirements

### Requirement 1: Data Preprocessing

**User Story:** As a data scientist, I want the raw UCI German Credit Dataset to be preprocessed within a Scikit-learn Pipeline, so that all transformations are reproducible and encapsulated with the model artifact.

#### Acceptance Criteria

1. WHEN the Trainer is executed, THE Trainer SHALL load the dataset from `data/german_credit_data.csv`.
2. THE Pipeline SHALL apply One-Hot Encoding to all categorical features (`Sex`, `Housing`, `Purpose`).
3. THE Pipeline SHALL apply Ordinal Encoding to ordinal categorical features (`Saving accounts`, `Checking account`) using the domain-ordered categories `["little", "moderate", "quite rich", "rich"]`.
4. THE Pipeline SHALL apply standard numerical scaling to continuous features (`Age`, `Credit amount`, `Duration`).
5. WHEN missing values are present in categorical columns, THE Pipeline SHALL impute them with the most frequent value before encoding.
6. WHEN missing values are present in numerical columns, THE Pipeline SHALL impute them with the median value before scaling.
7. THE Pipeline SHALL preserve the `Job` feature as an integer without transformation.

---

### Requirement 2: Model Training and Persistence

**User Story:** As a data scientist, I want an XGBoost classifier trained within the Pipeline and saved to disk, so that the API can load a single artifact for inference without re-training.

#### Acceptance Criteria

1. THE Pipeline SHALL include an XGBoost Classifier as its final estimator step.
2. WHEN the training dataset exhibits class imbalance, THE Trainer SHALL address it by setting the `scale_pos_weight` parameter of the XGBoost Classifier to the ratio of negative-class samples to positive-class samples.
3. WHEN training is complete, THE Trainer SHALL save the fitted Pipeline as a `.joblib` file to a configurable output path (default: `model/pipeline.joblib`).
4. WHEN the `.joblib` file already exists at the output path, THE Trainer SHALL overwrite it without error.
5. THE Trainer SHALL log the model's ROC-AUC score on a held-out validation set (20% of data) to standard output upon completion.

---

### Requirement 3: Prediction API

**User Story:** As a developer, I want a FastAPI service that accepts applicant data and returns a credit risk prediction, so that the UI and any other client can consume predictions over HTTP.

#### Acceptance Criteria

1. WHEN the API starts, THE API SHALL load the Pipeline from the `.joblib` file into memory exactly once.
2. IF the `.joblib` file is not found at startup, THEN THE API SHALL log a descriptive error and exit with a non-zero status code.
3. THE API SHALL expose a `POST /predict` endpoint that accepts a JSON body conforming to the `ApplicantFeatures` Pydantic schema.
4. THE `ApplicantFeatures` schema SHALL enforce the following fields and types:
   - `age`: integer, range 18–100
   - `sex`: string, one of `["male", "female"]`
   - `job`: integer, range 0–3
   - `housing`: string, one of `["own", "free", "rent"]`
   - `saving_accounts`: string, one of `["little", "moderate", "quite rich", "rich"]`, nullable
   - `checking_account`: string, one of `["little", "moderate", "rich"]`, nullable
   - `credit_amount`: integer, minimum 1
   - `duration`: integer, minimum 1
   - `purpose`: string, one of `["car", "furniture/equipment", "radio/TV", "domestic appliances", "repairs", "education", "business", "vacation/others"]`
5. WHEN a valid `POST /predict` request is received, THE API SHALL return a JSON response containing `risk_score` (float) and `prediction` (string).
6. WHEN the `risk_score` is greater than or equal to 0.5, THE API SHALL set `prediction` to `"High Risk"`.
7. WHEN the `risk_score` is less than 0.5, THE API SHALL set `prediction` to `"Low Risk"`.
8. IF the request body fails Pydantic validation, THEN THE API SHALL return HTTP 422 with a descriptive error message.
9. THE API SHALL expose a `GET /health` endpoint that returns HTTP 200 and `{"status": "ok"}` when the service is running and the Pipeline is loaded.

---

### Requirement 4: SHAP Explanation Generation

**User Story:** As a credit analyst, I want a SHAP-based explanation for each prediction, so that I can understand which applicant features drove the risk assessment.

#### Acceptance Criteria

1. WHEN a prediction is requested, THE Explainer SHALL compute SHAP values for the input instance using a `TreeExplainer` initialized with the XGBoost model extracted from the Pipeline.
2. THE Explainer SHALL apply the same preprocessing transformations to the input instance before computing SHAP values, ensuring feature alignment.
3. WHEN SHAP values are computed, THE UI SHALL render a SHAP Waterfall Plot or Force Plot for the prediction.
4. WHEN the SHAP_Plot is rendered, THE UI SHALL display it within 3 seconds of the prediction response being received on a local machine.
5. THE Explainer SHALL label each feature in the SHAP_Plot using human-readable feature names derived from the Pipeline's column transformer.

---

### Requirement 5: Streamlit User Interface

**User Story:** As a loan officer, I want a web-based form to enter applicant details and view the prediction and explanation, so that I can make informed credit decisions without writing code.

#### Acceptance Criteria

1. THE UI SHALL render a sidebar or form containing labeled input controls for all nine applicant features: `Age`, `Sex`, `Job`, `Housing`, `Saving accounts`, `Checking account`, `Credit amount`, `Duration`, and `Purpose`.
2. WHILE the UI is in Zero_State (no prediction has been submitted), THE UI SHALL display a placeholder message and SHALL NOT render a SHAP_Plot or prediction result.
3. WHEN the user submits the form, THE UI SHALL send a `POST` request to the API's `/predict` endpoint using the `requests` library.
4. WHEN the API returns a successful response, THE UI SHALL display the `prediction` label prominently and the `risk_score` as a formatted percentage.
5. IF the API returns an error response or is unreachable, THEN THE UI SHALL display a user-friendly error message and SHALL NOT crash.
6. THE UI SHALL use color-coded styling to distinguish "High Risk" (red) from "Low Risk" (green) predictions.
7. THE UI SHALL communicate with the API using the Docker Compose service name as the hostname (e.g., `http://api:8000`), configurable via an environment variable.

---

### Requirement 6: Containerization and Orchestration

**User Story:** As a developer, I want the entire application to run with a single `docker-compose up` command, so that the environment is fully reproducible without manual dependency installation.

#### Acceptance Criteria

1. THE System SHALL include a `Dockerfile` for the API service that installs all Python dependencies and exposes port 8000.
2. THE System SHALL include a `Dockerfile` for the UI service that installs all Python dependencies and exposes port 8501.
3. THE Docker_Compose SHALL define both `api` and `ui` services, with the `ui` service depending on the `api` service.
4. WHEN `docker-compose up` is executed, THE Docker_Compose SHALL build both images and start both containers without manual intervention.
5. THE Docker_Compose SHALL mount the `model/` directory as a volume into the API container so that the pre-trained `.joblib` artifact is accessible without rebuilding the image.
6. THE Docker_Compose SHALL configure the `ui` service with an environment variable specifying the API base URL using the `api` service name.
7. WHEN the `api` container is not yet ready, THE Docker_Compose SHALL configure the `ui` service to wait using a health-check dependency condition.

---

### Requirement 7: Code Quality and Type Safety

**User Story:** As a developer, I want the codebase to use type hints and modular functions throughout, so that the code is maintainable, readable, and easy to extend.

#### Acceptance Criteria

1. THE System SHALL use Python type hints on all function signatures in the training script, API module, and UI module.
2. THE API SHALL use Pydantic models for all request and response schemas.
3. THE System SHALL organize code into modular functions with single responsibilities (e.g., separate functions for data loading, preprocessing, training, and evaluation).
4. THE System SHALL include a `requirements.txt` (or equivalent) for each service specifying pinned dependency versions.
