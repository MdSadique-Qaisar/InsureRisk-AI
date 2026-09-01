from pathlib import Path
import io
import joblib
import pandas as pd
import numpy as np

# SHAP is required for individual explanations from the XGBoost model.
import shap


# ---------------------------------------------------------
# Model paths
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = BASE_DIR / "artifacts"

model_young = joblib.load(ARTIFACT_DIR / "model_young.joblib")
model_rest = joblib.load(ARTIFACT_DIR / "model_rest.joblib")

scaler_young = joblib.load(ARTIFACT_DIR / "scaler_young.joblib")
scaler_rest = joblib.load(ARTIFACT_DIR / "scaler_rest.joblib")


# ---------------------------------------------------------
# Feature configuration
# ---------------------------------------------------------
EXPECTED_COLUMNS = [
    "age",
    "number_of_dependants",
    "income_lakhs",
    "insurance_plan",
    "genetical_risk",
    "normalized_risk_score",
    "gender_Male",
    "region_Northwest",
    "region_Southeast",
    "region_Southwest",
    "marital_status_Unmarried",
    "bmi_category_Obesity",
    "bmi_category_Overweight",
    "bmi_category_Underweight",
    "smoking_status_Occasional",
    "smoking_status_Regular",
    "employment_status_Salaried",
    "employment_status_Self-Employed",
]

INSURANCE_PLAN_ENCODING = {
    "Bronze": 1,
    "Silver": 2,
    "Gold": 3,
}

# User-facing factor groups.
FACTOR_GROUPS = {
    "Age": ["age"],
    "Dependants": ["number_of_dependants"],
    "Income": ["income_lakhs"],
    "Insurance Plan": ["insurance_plan"],
    "Genetic Risk": ["genetical_risk"],
    "Medical History": ["normalized_risk_score"],
    "Gender": ["gender_Male"],
    "Region": [
        "region_Northwest",
        "region_Southeast",
        "region_Southwest",
    ],
    "Marital Status": ["marital_status_Unmarried"],
    "BMI Category": [
        "bmi_category_Obesity",
        "bmi_category_Overweight",
        "bmi_category_Underweight",
    ],
    "Smoking Status": [
        "smoking_status_Occasional",
        "smoking_status_Regular",
    ],
    "Employment Status": [
        "employment_status_Salaried",
        "employment_status_Self-Employed",
    ],
}


# ---------------------------------------------------------
# Medical-history feature engineering
# ---------------------------------------------------------
def calculate_normalized_risk(medical_history):
    risk_scores = {
        "diabetes": 6,
        "heart disease": 8,
        "high blood pressure": 6,
        "thyroid": 5,
        "no disease": 0,
        "none": 0,
    }

    diseases = medical_history.lower().split(" & ")
    total_risk_score = sum(risk_scores.get(disease, 0) for disease in diseases)

    max_score = 14
    min_score = 0

    normalized_risk_score = (
        total_risk_score - min_score
    ) / (max_score - min_score)

    return float(normalized_risk_score)


def get_medical_risk_indicator(normalized_score):
    """
    This is a presentation layer for the engineered medical-history score.
    It is NOT a medical diagnosis or a probability of disease.
    """
    score = float(normalized_score) * 100

    if score <= 25:
        label = "Low"
        description = "Low medical-history risk indicator."
    elif score <= 60:
        label = "Moderate"
        description = "Moderate medical-history risk indicator."
    else:
        label = "High"
        description = "High medical-history risk indicator."

    return {
        "score": score,
        "label": label,
        "description": description,
    }


# ---------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------
def preprocess_input(input_dict):
    df = pd.DataFrame(
        0.0,
        columns=EXPECTED_COLUMNS,
        index=[0],
    )

    # Numeric inputs
    df.loc[0, "age"] = input_dict["Age"]
    df.loc[0, "number_of_dependants"] = input_dict["Number of Dependants"]
    df.loc[0, "income_lakhs"] = input_dict["Income in Lakhs"]
    df.loc[0, "insurance_plan"] = INSURANCE_PLAN_ENCODING.get(
        input_dict["Insurance Plan"], 1
    )
    df.loc[0, "genetical_risk"] = input_dict["Genetical Risk"]

    # Gender
    if input_dict["Gender"] == "Male":
        df.loc[0, "gender_Male"] = 1

    # Region
    region_column = {
        "Northwest": "region_Northwest",
        "Southeast": "region_Southeast",
        "Southwest": "region_Southwest",
    }.get(input_dict["Region"])

    if region_column:
        df.loc[0, region_column] = 1

    # Marital status
    if input_dict["Marital Status"] == "Unmarried":
        df.loc[0, "marital_status_Unmarried"] = 1

    # BMI
    bmi_column = {
        "Obesity": "bmi_category_Obesity",
        "Overweight": "bmi_category_Overweight",
        "Underweight": "bmi_category_Underweight",
    }.get(input_dict["BMI Category"])

    if bmi_column:
        df.loc[0, bmi_column] = 1

    # Smoking
    smoking_column = {
        "Occasional": "smoking_status_Occasional",
        "Regular": "smoking_status_Regular",
    }.get(input_dict["Smoking Status"])

    if smoking_column:
        df.loc[0, smoking_column] = 1

    # Employment
    employment_column = {
        "Salaried": "employment_status_Salaried",
        "Self-Employed": "employment_status_Self-Employed",
    }.get(input_dict["Employment Status"])

    if employment_column:
        df.loc[0, employment_column] = 1

    # Medical history → engineered feature
    df.loc[0, "normalized_risk_score"] = calculate_normalized_risk(
        input_dict["Medical History"]
    )

    df = handle_scaling(input_dict["Age"], df)

    return df


def handle_scaling(age, df):
    if age <= 25:
        scaler_object = scaler_young
    else:
        scaler_object = scaler_rest

    cols_to_scale = scaler_object["cols_to_scale"]
    scaler = scaler_object["scaler"]

    # income_level was part of the original scaler but is not a user input.
    # The original prediction pipeline supplies a neutral placeholder.
    df["income_level"] = 1.0

    df[cols_to_scale] = scaler.transform(df[cols_to_scale])

    df.drop("income_level", axis="columns", inplace=True)

    return df


# ---------------------------------------------------------
# Model selection and prediction
# ---------------------------------------------------------
def get_model_and_scaler(age):
    if age <= 25:
        return model_young, scaler_young, "Linear Regression"
    return model_rest, scaler_rest, "XGBoost Regressor"


def predict_premium(input_dict):
    input_df = preprocess_input(input_dict)
    model, _, _ = get_model_and_scaler(input_dict["Age"])

    prediction = float(model.predict(input_df)[0])

    # Premium cannot logically be negative.
    return max(0.0, prediction)


# ---------------------------------------------------------
# Individual model explanations
# ---------------------------------------------------------
def _linear_contributions(model, input_df):
    """
    For Linear Regression:
        contribution = coefficient × processed feature value

    The sum of contributions + intercept equals the model prediction.
    """
    feature_names = list(input_df.columns)

    coefficients = np.asarray(model.coef_).reshape(-1)
    values = input_df.iloc[0].astype(float).to_numpy()

    contributions = coefficients * values

    return dict(zip(feature_names, contributions))


def _xgb_contributions(model, input_df):
    """
    For XGBoost:
        SHAP TreeExplainer calculates local feature contributions
        for the exact applicant.
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(input_df)

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    values = np.asarray(shap_values)

    if values.ndim == 2:
        values = values[0]

    return dict(zip(input_df.columns, values.astype(float)))


def _group_contributions(raw_contributions):
    grouped = []

    for label, feature_names in FACTOR_GROUPS.items():
        contribution = sum(
            raw_contributions.get(feature, 0.0)
            for feature in feature_names
        )

        grouped.append(
            {
                "label": label,
                "contribution": float(contribution),
            }
        )

    grouped.sort(
        key=lambda x: abs(x["contribution"]),
        reverse=True,
    )

    return grouped


def _impact_label(contribution, max_contribution):
    """
    Converts a numerical model contribution into a compact UI label.
    This describes relative model impact, not probability.
    """
    if max_contribution <= 0:
        return "Low Impact"

    relative = abs(contribution) / max_contribution

    if relative >= 0.66:
        return "High Impact"
    if relative >= 0.33:
        return "Moderate"
    return "Low Impact"


def get_factor_explanations(model, input_df, input_dict):
    if hasattr(model, "get_booster"):
        raw = _xgb_contributions(model, input_df)
    else:
        raw = _linear_contributions(model, input_df)

    grouped = _group_contributions(raw)

    max_abs = max(
        [abs(item["contribution"]) for item in grouped],
        default=1.0,
    )

    for item in grouped:
        item["impact"] = _impact_label(
            item["contribution"],
            max_abs,
        )

    return grouped


# ---------------------------------------------------------
# Main prediction + explanation API
# ---------------------------------------------------------
def predict_with_explanation(input_dict):
    input_df = preprocess_input(input_dict)

    model, _, model_name = get_model_and_scaler(
        input_dict["Age"]
    )

    prediction = float(model.predict(input_df)[0])
    prediction = max(0.0, prediction)

    factors = get_factor_explanations(
        model,
        input_df,
        input_dict,
    )

    normalized_risk_score = calculate_normalized_risk(
        input_dict["Medical History"]
    )

    return {
        "prediction": prediction,
        "factors": factors,
        "normalized_risk_score": normalized_risk_score,
        "model_used": model_name,
    }


# ---------------------------------------------------------
# PDF report
# ---------------------------------------------------------
def create_pdf_report(result, comparison_rows):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        textColor=colors.grey,
        fontSize=10,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=12,
        spaceAfter=8,
    )

    story = []

    story.append(Paragraph("InsureRisk AI", title_style))
    story.append(
        Paragraph(
            "Health Insurance Premium & Risk Assessment",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            f"Estimated Annual Premium: ₹{result['prediction']:,.0f}",
            heading_style,
        )
    )

    risk = result["risk"]
    story.append(
        Paragraph(
            f"Medical Risk Indicator: {risk['label']} "
            f"({risk['score']:.0f}/100)",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph("Applicant Profile", heading_style)
    )

    inp = result["input_dict"]

    profile = [
        ["Field", "Value"],
        ["Age", str(inp["Age"])],
        ["Income", f"₹{inp['Income in Lakhs']:.1f} Lakh"],
        ["Dependants", str(inp["Number of Dependants"])],
        ["Gender", inp["Gender"]],
        ["Marital Status", inp["Marital Status"]],
        ["Employment", inp["Employment Status"]],
        ["BMI Category", inp["BMI Category"]],
        ["Smoking Status", inp["Smoking Status"]],
        ["Genetic Risk", str(inp["Genetical Risk"])],
        ["Medical History", inp["Medical History"]],
        ["Region", inp["Region"]],
        ["Insurance Plan", inp["Insurance Plan"]],
    ]

    table = Table(profile, colWidths=[170, 310])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table)

    story.append(
        Paragraph(
            "Top Model Factors",
            heading_style,
        )
    )

    factors = [["Factor", "Direction", "Impact"]]

    for factor in result["factors"][:7]:
        direction = (
            "Upward"
            if factor["contribution"] > 0
            else "Downward"
        )

        factors.append(
            [
                factor["label"],
                direction,
                factor["impact"],
            ]
        )

    factor_table = Table(
        factors,
        colWidths=[220, 120, 140],
    )

    factor_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(factor_table)

    story.append(
        Paragraph(
            "Insurance Plan Scenario Comparison",
            heading_style,
        )
    )

    plans = [["Plan", "Estimated Annual Premium"]]

    for row in comparison_rows:
        plans.append(
            [
                row["Plan"],
                f"₹{row['Estimated Annual Premium']:,.0f}",
            ]
        )

    plan_table = Table(plans, colWidths=[220, 260])
    plan_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(plan_table)
    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            "Disclaimer: This report is generated from a machine-learning "
            "insurance-pricing model. Model contributions describe how the "
            "trained model arrived at the estimate and should not be interpreted "
            "as medical diagnosis, medical advice, or causal relationships.",
            styles["Normal"],
        )
    )

    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()
