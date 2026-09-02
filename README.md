# 🛡️ InsureRisk AI

### AI-Powered Health Insurance Premium & Risk Assessment Platform

InsureRisk AI is a machine-learning application that estimates an applicant's **annual health insurance premium**, presents an engineered **medical-history risk indicator**, and explains which applicant factors influenced the model's estimate.

The application is built with **Python, Streamlit, scikit-learn, XGBoost, SHAP, Pandas, NumPy, Joblib, and ReportLab**.

> **Project type:** End-to-end Machine Learning / Data Science application  
> **Primary use case:** Insurance premium estimation and model explainability  
> **Interface:** Streamlit  
> **Prediction models:** Linear Regression + XGBoost Regressor

---

##  Project Objective

Insurance pricing depends on multiple applicant characteristics. The goal of InsureRisk AI is to provide a simple interface where a user can enter an applicant profile and receive:

- Estimated annual insurance premium
- Monthly premium equivalent
- Medical-history risk indicator
- Model used for the prediction
- Individual feature contributions
- Low / Moderate / High influence levels
- Applicant summary
- Insurance-plan scenario comparison
- Downloadable PDF assessment report
- Recent assessment history during the current session

The application is designed as a **machine-learning demonstration and decision-support prototype**, not as a production underwriting system or medical diagnostic tool.

---

##  Key Features

### 1. Premium Prediction

The application estimates the applicant's annual insurance premium from demographic, financial, lifestyle, medical-history, regional, employment, and insurance-plan information.

### 2. Age-Based Model Selection

The application uses two trained regression models:

| Applicant age | Model |
|---|---|
| Age ≤ 25 | Linear Regression |
| Age > 25 | XGBoost Regressor |

The model-selection logic is implemented in the prediction helper.

### 3. Medical-History Feature Engineering

Medical history is transformed into a numerical `normalized_risk_score`.

The current scoring logic assigns:

| Medical condition | Score |
|---|---:|
| Diabetes | 6 |
| Heart disease | 8 |
| High blood pressure | 6 |
| Thyroid | 5 |
| No disease | 0 |

The maximum combined score is 14, and the value is normalized between 0 and 1.

The application then presents the engineered score as a **Low / Moderate / High medical-history risk indicator**:

- **0–25:** Low
- **>25–60:** Moderate
- **>60:** High

This indicator is a presentation of an engineered model feature and is **not a probability of disease or medical diagnosis**.

### 4. Explainable AI

For individual predictions, the application calculates model-derived feature contributions.

- **Linear Regression:** contribution is calculated from coefficient × processed feature value.
- **XGBoost:** SHAP `TreeExplainer` is used to calculate local feature contributions for the applicant.

The application groups encoded/model features into user-facing factors such as:

- Age
- Dependants
- Income
- Insurance Plan
- Genetic Risk
- Medical History
- Gender
- Region
- Marital Status
- BMI Category
- Smoking Status
- Employment Status



### 5. Contribution Amounts

The UI displays both the **direction** and **magnitude** of each contribution.

For example:

> Insurance Plan is contributing downward by approximately ₹7,602 relative to the model baseline.

Interpretation:

- **Upward contribution:** moves the model estimate higher.
- **Downward contribution:** moves the model estimate lower.
- **High / Moderate / Low influence:** describes the relative magnitude of the contribution.
- The amount is a **model explanation**, not a guaranteed discount or surcharge.

The Streamlit interface explicitly presents these contribution amounts and their interpretation.

### 6. Insurance Plan Scenario Analysis

The application re-estimates the premium for:

- Bronze
- Silver
- Gold

while keeping the rest of the applicant profile unchanged.

This makes the application more useful from a decision-support perspective because users can compare how the selected plan affects the estimated premium.

### 7. PDF Assessment Report

Users can download an assessment report containing:

- Estimated premium
- Medical risk indicator
- Applicant profile
- Top model factors
- Insurance-plan scenario comparison
- Model disclaimer

The PDF is generated with ReportLab.

---

#  Machine Learning Workflow

```text
Applicant Input
      │
      ▼
Data Validation / Feature Preparation
      │
      ▼
Medical History
      │
      ▼
Normalized Risk Score
      │
      ▼
Categorical Encoding + Numeric Features
      │
      ▼
Age-Based Model Selection
      │
      ├── Age ≤ 25 ──► Linear Regression
      │
      └── Age > 25 ──► XGBoost Regressor
                         │
                         ▼
                  Premium Prediction
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Feature Contributions    Risk Indicator
              │                     │
              ▼                     ▼
       Explanation UI          Low / Moderate / High
              │
              ▼
       Scenario Comparison
              │
              ▼
        PDF Assessment
```

---

#  Input Features

The application currently collects the following applicant information:

### Applicant Details

- Age
- Number of Dependants
- Annual Income
- Gender
- Marital Status
- Employment Status

### Health & Lifestyle

- BMI Category
- Smoking Status
- Genetic Risk
- Medical History

### Other Pricing Factors

- Region
- Insurance Plan

These inputs are assembled into the feature structure expected by the trained models.

---

#  Feature Engineering & Preprocessing

The prediction pipeline prepares a DataFrame using a predefined feature schema.

The expected model features include:

- `age`
- `number_of_dependants`
- `income_lakhs`
- `insurance_plan`
- `genetical_risk`
- `normalized_risk_score`
- one-hot encoded categorical features



Insurance plans are encoded as:

```text
Bronze → 1
Silver → 2
Gold   → 3
```



The application loads separate preprocessing/scaling artifacts for the two age-based model paths.

---

#  Model Architecture

## Young Applicant Model

Applicants aged **25 or below** are evaluated using the trained Linear Regression model.

For the linear model, individual contributions are calculated using:

```text
Contribution = coefficient × processed feature value
```

The contributions plus the model intercept correspond to the model prediction.

## XGBoost Model

Applicants **above age 25** are evaluated using the trained XGBoost Regressor.

SHAP TreeExplainer is used to calculate local feature contributions for the individual applicant.

---

#  Explainability Design

The project does not simply display a prediction.

It attempts to answer:

> **"Why did the model produce this estimate?"**

The application groups low-level model features into business-friendly factors and ranks them according to the absolute magnitude of their contribution.

The UI then classifies relative influence:

```text
Relative contribution ≥ 0.66 → High Impact
Relative contribution ≥ 0.33 → Moderate
Otherwise                     → Low Impact
```



This is an **explanation of model behavior**, not causal inference.

---

#  Project Structure

Recommended GitHub structure:

```text
InsureRisk-AI/
│
├── app/
│   ├── main.py
│   ├── prediction_helper.py
│   │
│   └── artifacts/
│       ├── model_young.joblib
│       ├── model_rest.joblib
│       ├── scaler_young.joblib
│       └── scaler_rest.joblib
│
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

If your current files are kept at the repository root, the simpler structure below is also valid:

```text
InsureRisk-AI/
├── main.py
├── prediction_helper.py
├── artifacts/
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

The prediction helper expects an `artifacts` directory beside the Python file and loads the trained models/scalers from there.

---

#  Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd InsureRisk-AI
```

## 2. Create a Conda environment

```bash
conda create -n ml_env python=3.11
conda activate ml_env
```

Or use an existing compatible environment.

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Verify model artifacts

Make sure the following files are present inside `artifacts/`:

```text
model_young.joblib
model_rest.joblib
scaler_young.joblib
scaler_rest.joblib
```

The application loads these artifacts at startup.

## 5. Run the application

```bash
streamlit run main.py
```

The Streamlit interface will open in your browser.

---

#  Dependencies

| Package | Purpose |
|---|---|
| Streamlit | Interactive web application |
| Pandas | DataFrame creation and feature preparation |
| NumPy | Numerical computation |
| Scikit-learn | Linear Regression, preprocessing and scalers |
| XGBoost | Gradient-boosted regression model |
| SHAP | Local model explanations |
| Joblib | Loading trained ML artifacts |
| ReportLab | PDF report generation |

See `requirements.txt` for the installable dependency specification.

---

# 📈 What Makes This an End-to-End ML Project?

From a Data Scientist / ML Engineer perspective, the project covers more than simply training a model.

### Data Science

- Feature engineering
- Categorical encoding
- Numerical preprocessing
- Model selection
- Regression prediction
- Model interpretation
- Scenario analysis

### Machine Learning

- Multiple model architectures
- Separate model paths
- Persisted model artifacts
- Persisted preprocessing artifacts
- Prediction pipeline

### Explainable AI

- Local feature contributions
- SHAP for XGBoost
- Contribution grouping
- Direction + magnitude interpretation

### Application Engineering

- Streamlit frontend
- Session-state management
- Interactive inputs
- Prediction workflow
- Error-safe premium floor
- PDF report generation

### Business Perspective

- Premium estimation
- Risk indicator
- Plan comparison
- Applicant-level explanation

---

# ⚠️ Important Limitations

This project should be presented as a **machine-learning prototype / portfolio project**, not as an actual insurance underwriting engine.

Important limitations include:

1. Model predictions depend on the training dataset and its underlying patterns.
2. SHAP/model contributions explain model behavior; they do not establish causality.
3. The medical risk indicator is an engineered feature representation and is not a medical diagnosis.
4. The medical-history score is based on manually assigned condition weights.
5. The current application uses persisted trained model/scaler artifacts rather than training models inside the Streamlit application.
6. Prediction quality should be evaluated against a held-out test set and appropriate regression metrics before any real-world deployment.
7. Insurance pricing is subject to regulatory, actuarial, fairness, and business requirements that are outside the scope of this prototype.

---

#  Skills Demonstrated

This project demonstrates practical experience with:

**Python • Pandas • NumPy • Scikit-learn • XGBoost • SHAP • Feature Engineering • Regression • Explainable AI • Streamlit • Model Deployment • PDF Reporting • ML Pipelines • Git/GitHub**

---

#  Disclaimer

InsureRisk AI is an educational and portfolio-oriented machine-learning application.

The estimated premium and model contributions are generated from trained machine-learning models. They should not be interpreted as guaranteed insurance prices, medical diagnoses, medical advice, or causal relationships.


