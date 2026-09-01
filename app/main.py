import streamlit as st
from prediction_helper import predict_with_explanation, predict_premium, get_medical_risk_indicator, create_pdf_report

st.set_page_config(
    page_title="InsureRisk AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    :root {
        --accent: #4f8cff;
        --accent-2: #7c5cff;
        --success: #2dd4bf;
        --warning: #f5b942;
        --danger: #ff6b6b;
        --muted: #9aa4b2;
        --panel: rgba(255,255,255,.035);
        --border: rgba(255,255,255,.10);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 4rem;
        padding-bottom: 3rem;
    }

    /* ---------- Hero ---------- */
    .hero {
        position: relative;
        overflow: hidden;
        min-height: 250px;
        padding: 2.4rem 2.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        border: 1px solid rgba(79,140,255,.25);
        border-radius: 22px;
        background:
            radial-gradient(circle at 85% 20%, rgba(124,92,255,.20), transparent 35%),
            radial-gradient(circle at 10% 90%, rgba(79,140,255,.13), transparent 32%),
            linear-gradient(135deg, rgba(79,140,255,.10), rgba(255,255,255,.025));
        margin: 0 0 1.5rem;
        box-shadow: 0 16px 45px rgba(0,0,0,.18);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        right: -70px;
        top: -80px;
        border-radius: 50%;
        background: rgba(79,140,255,.10);
        filter: blur(5px);
    }

    .hero-kicker {
        color: #79a7ff;
        font-size: .78rem;
        font-weight: 750;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: .7rem;
        text-align: center;
    }

    .hero-title {
        font-size: 2.75rem;
        font-weight: 800;
        letter-spacing: -0.045em;
        margin-bottom: .35rem;
        text-align: center;
    }

    .hero-subtitle {
        color: #aab3c0;
        font-size: 1.03rem;
        text-align: center;
    }

    /* ---------- Section headings ---------- */
    .section-title {
        display: flex;
        align-items: center;
        gap: .55rem;
        font-size: 1.18rem;
        font-weight: 750;
        margin: 1.35rem 0 .75rem;
    }

    .section-title::before {
        content: "";
        width: 4px;
        height: 22px;
        border-radius: 99px;
        background: linear-gradient(180deg, var(--accent), var(--accent-2));
    }

    /* ---------- Form ---------- */
    div[data-testid="stForm"] {
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 1.15rem 1.25rem 1.25rem;
        background: rgba(255,255,255,.018);
        box-shadow: 0 12px 35px rgba(0,0,0,.12);
    }

    div[data-testid="stForm"] label {
        font-weight: 600;
    }

    div[data-testid="stNumberInput"] > div,
    div[data-baseweb="select"] > div {
        border-radius: 11px !important;
    }

    /* Primary action */
    button[kind="primaryFormSubmit"] {
        background: linear-gradient(90deg, #4f8cff, #6c63ff) !important;
        border: none !important;
        border-radius: 11px !important;
        min-height: 46px;
        font-weight: 750 !important;
        box-shadow: 0 8px 24px rgba(79,140,255,.22);
        transition: transform .15s ease, box-shadow .15s ease;
    }

    button[kind="primaryFormSubmit"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 11px 28px rgba(79,140,255,.32);
    }

    /* ---------- Result cards ---------- */
    .premium-card {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(45,212,191,.24);
        border-radius: 18px;
        padding: 1.45rem;
        text-align: center;
        margin-top: .7rem;
        background:
            radial-gradient(circle at 50% 0%, rgba(45,212,191,.10), transparent 60%),
            rgba(255,255,255,.025);
        box-shadow: 0 12px 35px rgba(0,0,0,.12);
    }

    .premium-card::before {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        top: 0;
        height: 3px;
        background: linear-gradient(90deg, #2dd4bf, #4f8cff);
    }

    .premium-label {
        color: #9aa4b2;
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .11em;
        font-weight: 650;
    }

    .premium-value {
        font-size: 2.75rem;
        font-weight: 850;
        letter-spacing: -0.045em;
        margin: .22rem 0;
        background: linear-gradient(90deg, #ffffff, #9ff7e8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .premium-period {
        color: #8f99a8;
    }

    div[data-testid="stMetric"] {
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 14px 16px;
        background: rgba(255,255,255,.025);
        min-height: 90px;
        box-shadow: 0 8px 25px rgba(0,0,0,.08);
    }

    div[data-testid="stMetricLabel"] {
        color: #aab3c0 !important;
    }

    div[data-testid="stMetricValue"] {
        font-weight: 750 !important;
    }

    /* ---------- Risk ---------- */
    .risk-card {
        border: 1px solid rgba(245,185,66,.22);
        border-radius: 16px;
        padding: 14px 16px;
        min-height: 90px;
        background: linear-gradient(135deg, rgba(245,185,66,.08), rgba(255,255,255,.02));
    }

    .risk-label {
        color: #aab3c0;
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    .risk-value {
        font-size: 1.8rem;
        font-weight: 800;
        margin-top: .2rem;
    }

    .risk-score {
        display: inline-block;
        margin-top: .35rem;
        padding: .2rem .55rem;
        border-radius: 999px;
        color: #f8d98c;
        background: rgba(245,185,66,.12);
        border: 1px solid rgba(245,185,66,.20);
        font-size: .76rem;
        font-weight: 700;
    }

    /* ---------- Risk meter ---------- */
    .risk-meter {
        margin-top: .55rem;
        height: 8px;
        width: 100%;
        border-radius: 99px;
        background: rgba(255,255,255,.08);
        overflow: hidden;
    }

    .risk-meter-fill {
        height: 100%;
        border-radius: 99px;
        background: linear-gradient(90deg, #2dd4bf 0%, #f5b942 55%, #ff6b6b 100%);
    }

    .risk-scale {
        display: flex;
        justify-content: space-between;
        margin-top: .28rem;
        color: #737d8c;
        font-size: .68rem;
    }

    /* ---------- Result overview ---------- */
    .result-strip {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: .75rem .9rem;
        margin: .75rem 0 1rem;
        border: 1px solid rgba(79,140,255,.14);
        border-radius: 13px;
        background: linear-gradient(90deg, rgba(79,140,255,.06), rgba(124,92,255,.035));
    }

    .result-strip-title {
        color: #aab3c0;
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    .result-strip-value {
        font-weight: 750;
        color: #e9edf3;
    }

    .status-pill {
        display: inline-block;
        padding: .28rem .6rem;
        border-radius: 999px;
        font-size: .72rem;
        font-weight: 750;
        background: rgba(45,212,191,.10);
        border: 1px solid rgba(45,212,191,.18);
        color: #62e5d0;
    }

    /* ---------- Scenario cards ---------- */
    .scenario-card {
        position: relative;
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 16px;
        padding: 1rem 1.05rem;
        background: rgba(255,255,255,.025);
        min-height: 125px;
        overflow: hidden;
    }

    .scenario-card.selected {
        border-color: rgba(79,140,255,.38);
        background: linear-gradient(135deg, rgba(79,140,255,.09), rgba(255,255,255,.025));
    }

    .scenario-card.best {
        border-color: rgba(45,212,191,.32);
    }

    .scenario-plan {
        font-size: .82rem;
        color: #aab3c0;
        font-weight: 650;
    }

    .scenario-price {
        font-size: 1.65rem;
        font-weight: 800;
        margin: .3rem 0 .2rem;
    }

    .scenario-delta {
        font-size: .73rem;
        color: #8f99a8;
    }

    .scenario-badge {
        display: inline-block;
        margin-top: .45rem;
        padding: .2rem .5rem;
        border-radius: 999px;
        font-size: .68rem;
        font-weight: 750;
        background: rgba(79,140,255,.10);
        color: #8db3ff;
    }

    .scenario-badge.best-badge {
        background: rgba(45,212,191,.10);
        color: #62e5d0;
    }

    .impact-legend {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        margin: .35rem 0 .9rem;
        color: #9aa4b2;
        font-size: .74rem;
    }

    .impact-legend span {
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .legend-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        display: inline-block;
    }

    .legend-low {
        background: #34D399;
    }

    .legend-moderate {
        background: #FB923C;
    }

    .legend-high {
        background: #F43F5E;
    }

    .legend-direction {
        color: #727d8d;
    }

    /* ---------- Factor explanation ---------- */
    .factor-row {
        display: flex;
        align-items: center;
        gap: 11px;
        margin: .72rem 0;
    }

    .factor-name {
        width: 175px;
        font-size: .91rem;
        font-weight: 600;
        color: #d7dce4;
    }

    .factor-bar-wrap {
        flex: 1;
        height: 9px;
        background: rgba(255,255,255,.075);
        border-radius: 99px;
        overflow: hidden;
    }

    .factor-bar {
        height: 100%;
        border-radius: 99px;
    }

    .factor-impact {
        width: 105px;
        text-align: right;
        font-size: .80rem;
        font-weight: 700;
    }

    /* Impact level colors: Low = blue, Moderate = amber, High = purple */
    .impact-low {
        color: #34D399;
    }

    .impact-moderate {
        color: #FB923C;
    }

    .impact-high {
        color: #F43F5E;
    }

    /* Direction remains separate from impact level */
    .direction-up {
        color: #2dd4bf;
    }

    .direction-down {
        color: #ff7b86;
    }

    .direction-neutral {
        color: #9aa4b2;
    }

    /* ---------- Applicant summary ---------- */
    .summary-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 18px;
        padding: .55rem 0;
        border-bottom: 1px solid rgba(255,255,255,.055);
    }

    .summary-label {
        color: #8f99a8;
        font-size: .82rem;
    }

    .summary-value {
        color: #e5e9ef;
        font-size: .88rem;
        font-weight: 650;
        text-align: right;
    }

    /* ---------- Insights ---------- */
    .insight-card {
        border-left: 3px solid #4f8cff;
        border-top: 1px solid rgba(255,255,255,.06);
        border-right: 1px solid rgba(255,255,255,.06);
        border-bottom: 1px solid rgba(255,255,255,.06);
        border-radius: 0 12px 12px 0;
        padding: .65rem .85rem;
        margin: .42rem 0;
        background: rgba(79,140,255,.045);
    }

    .insight-up {
        border-left-color: #2dd4bf;
        background: rgba(45,212,191,.045);
    }

    .insight-down {
        border-left-color: #ff6b6b;
        background: rgba(255,107,107,.045);
    }

    /* ---------- Notes / footer ---------- */
    .small-note {
        color: #8f99a8;
        font-size: .80rem;
        line-height: 1.5;
        padding: .75rem .85rem;
        border-radius: 11px;
        background: rgba(255,255,255,.025);
        border: 1px solid rgba(255,255,255,.05);
    }

    .footer {
        text-align: center;
        color: #777f8d;
        font-size: .78rem;
        margin-top: 2rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(255,255,255,.07);
    }

    /* Download button */
    .stDownloadButton button {
        border-radius: 11px !important;
        font-weight: 700 !important;
        border: 1px solid rgba(79,140,255,.30) !important;
        background: rgba(79,140,255,.07) !important;
    }

    @media (max-width: 800px) {
        .block-container {
            padding-top: 2.5rem;
        }

        .hero {
            min-height: 210px;
            padding: 2rem 1.25rem;
        }

        .hero-title {
            font-size: 2rem;
        }

        .factor-name {
            width: 125px;
        }

        .factor-impact {
            width: 90px;
        }
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# App state
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "result" not in st.session_state:
    st.session_state.result = None


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 🛡️ InsureRisk AI")
    st.caption("Health Insurance Premium & Risk Assessment")

    if st.button("↺  New Assessment", use_container_width=True):
        st.session_state.result = None
        st.session_state.history = []
        st.rerun()

    st.divider()

    st.markdown("### About")
    st.write(
        "Estimate an insurance premium from an applicant profile and "
        "understand which model features influenced the estimate."
    )

    st.divider()

    st.markdown("### Model architecture")
    st.write("• Age ≤ 25 → Linear Regression")
    st.write("• Age > 25 → XGBoost Regressor")
    st.write("• Medical history → engineered risk score")
    st.write("• Individual explanation → model contribution / SHAP")

    st.divider()

    st.markdown(
        '<div class="small-note">'
        "This is an insurance-pricing ML demonstration. "
        "The risk indicator is an engineered model feature, not a medical diagnosis."
        "</div>",
        unsafe_allow_html=True,
    )


# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-kicker">AI-Powered Insurance Analytics</div>
    <div class="hero-title">InsureRisk AI</div>
    <div class="hero-subtitle">
        Health Insurance Premium & Risk Assessment Platform
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# Options
# -----------------------------
categorical_options = {
    "Gender": ["Male", "Female"],
    "Marital Status": ["Unmarried", "Married"],
    "BMI Category": ["Normal", "Obesity", "Overweight", "Underweight"],
    "Smoking Status": ["No Smoking", "Regular", "Occasional"],
    "Employment Status": ["Salaried", "Self-Employed", "Freelancer"],
    "Region": ["Northwest", "Southeast", "Northeast", "Southwest"],
    "Medical History": [
        "No Disease",
        "Diabetes",
        "High blood pressure",
        "Diabetes & High blood pressure",
        "Thyroid",
        "Heart disease",
        "High blood pressure & Heart disease",
        "Diabetes & Thyroid",
        "Diabetes & Heart disease",
    ],
    "Insurance Plan": ["Bronze", "Silver", "Gold"],
}


# -----------------------------
# Input form
# -----------------------------
with st.form("assessment_form"):
    st.markdown('<div class="section-title">Applicant Details</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", min_value=18, max_value=100, value=30, step=1)
    with c2:
        number_of_dependants = st.number_input(
            "Number of Dependants", min_value=0, max_value=20, value=0, step=1
        )
    with c3:
        income_lakhs = st.number_input(
            "Annual Income (₹ Lakhs)",
            min_value=0.0,
            max_value=200.0,
            value=5.0,
            step=0.5,
            format="%.1f",
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        gender = st.selectbox("Gender", categorical_options["Gender"])
    with c2:
        marital_status = st.selectbox(
            "Marital Status", categorical_options["Marital Status"]
        )
    with c3:
        employment_status = st.selectbox(
            "Employment Status", categorical_options["Employment Status"]
        )

    st.markdown('<div class="section-title">Health & Lifestyle</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        bmi_category = st.selectbox("BMI Category", categorical_options["BMI Category"])
    with c2:
        smoking_status = st.selectbox(
            "Smoking Status", categorical_options["Smoking Status"]
        )
    with c3:
        genetical_risk = st.number_input(
            "Genetic Risk", min_value=0, max_value=5, value=0, step=1
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        medical_history = st.selectbox(
            "Medical History", categorical_options["Medical History"]
        )
    with c2:
        region = st.selectbox("Region", categorical_options["Region"])
    with c3:
        insurance_plan = st.selectbox(
            "Insurance Plan", categorical_options["Insurance Plan"]
        )

    st.markdown("")
    submitted = st.form_submit_button(
        "Calculate Premium",
        type="primary",
        use_container_width=True,
    )


# -----------------------------
# Prediction
# -----------------------------
if submitted:
    input_dict = {
        "Age": age,
        "Number of Dependants": number_of_dependants,
        "Income in Lakhs": income_lakhs,
        "Genetical Risk": genetical_risk,
        "Insurance Plan": insurance_plan,
        "Employment Status": employment_status,
        "Gender": gender,
        "Marital Status": marital_status,
        "BMI Category": bmi_category,
        "Smoking Status": smoking_status,
        "Region": region,
        "Medical History": medical_history,
    }

    result = predict_with_explanation(input_dict)
    risk = get_medical_risk_indicator(result["normalized_risk_score"])

    result["risk"] = risk
    result["input_dict"] = input_dict

    st.session_state.result = result

    st.session_state.history.insert(
        0,
        {
            "Premium": result["prediction"],
            "Risk": risk["label"],
            "Age": age,
            "Plan": insurance_plan,
            "Medical History": medical_history,
        },
    )
    st.session_state.history = st.session_state.history[:10]


# -----------------------------
# Results
# -----------------------------
result = st.session_state.result

if result:
    st.divider()
    st.markdown("## Assessment Result")

    top1, top2, top3 = st.columns(3)

    with top1:
        st.markdown(
            f"""
            <div class="premium-card">
                <div class="premium-label">Estimated Annual Premium</div>
                <div class="premium-value">₹{result["prediction"]:,.0f}</div>
                <div class="premium-period">per year</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top2:
        st.metric("Monthly Equivalent", f"₹{result['prediction'] / 12:,.0f}")
        st.metric("Model Used", result["model_used"])

    with top3:
        st.markdown(
            f"""
            <div class="risk-card">
                <div class="risk-label">Medical Risk Indicator</div>
                <div class="risk-value">{result["risk"]["label"]}</div>
                <span class="risk-score">{result["risk"]["score"]:.0f}/100</span>
                <div class="risk-meter">
                    <div class="risk-meter-fill"
                         style="width:{min(100, max(0, result["risk"]["score"]))}%;">
                    </div>
                </div>
                <div class="risk-scale"><span>Low</span><span>Moderate</span><span>High</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="result-strip">
            <div>
                <div class="result-strip-title">Assessment complete</div>
                <div class="result-strip-value">
                    Model-based estimate generated from the submitted applicant profile
                </div>
            </div>
            <span class="status-pill">● {result["model_used"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")

    left, right = st.columns([1.15, 1])

    # -------------------------
    # Factor explanation
    # -------------------------
    with left:
        st.markdown("### What is influencing this estimate?")
        st.caption(
            "Each amount represents the model-derived contribution of that factor "
            "relative to the model baseline. ↑ means an upward contribution; "
            "↓ means a downward contribution."
        )

        factors = result["factors"]
        max_abs = max([abs(f["contribution"]) for f in factors], default=1)

        for factor in factors:
            contribution = factor["contribution"]
            width = max(5, min(100, abs(contribution) / max_abs * 100))

            impact = factor["impact"].replace(" Impact", "").strip().lower()

            if impact == "high":
                impact_class = "impact-high"
                bar_color = "#F43F5E"
            elif impact == "moderate":
                impact_class = "impact-moderate"
                bar_color = "#FB923C"
            else:
                impact_class = "impact-low"
                bar_color = "#34D399"

            if contribution > 0:
                direction = "↑"
                direction_class = "direction-up"
            elif contribution < 0:
                direction = "↓"
                direction_class = "direction-down"
            else:
                direction = "—"
                direction_class = "direction-neutral"

            amount = f"₹{abs(contribution):,.0f}"

            st.markdown(
                f"""
                <div class="factor-row">
                    <div class="factor-name">{factor["label"]}</div>
                    <div class="factor-bar-wrap">
                        <div class="factor-bar"
                             style="width:{width}%; background:{bar_color};">
                        </div>
                    </div>
                    <div class="factor-impact {impact_class}">
                        <strong class="{direction_class}">{direction} {amount}</strong><br>
                        <span>{impact.title()} influence</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### Contribution Summary")

        for factor in factors:
            contribution = factor["contribution"]

            if contribution > 0:
                direction_text = "contributing upward"
            elif contribution < 0:
                direction_text = "contributing downward"
            else:
                direction_text = "having approximately no contribution"

            if contribution == 0:
                st.markdown(
                    f"• **{factor['label']}** is {direction_text} "
                    "relative to the model baseline."
                )
            else:
                st.markdown(
                    f"• **{factor['label']}** is {direction_text} by approximately "
                    f"**₹{abs(contribution):,.0f}** relative to the model baseline."
                )

        st.markdown(
            f'<div class="small-note">'
            f"<strong>Medical risk interpretation:</strong> the {result['risk']['label'].lower()} "
            f"indicator is based on the engineered medical-history score "
            f"({result['risk']['score']:.0f}/100). It is a presentation of the model feature, "
            "not a medical diagnosis.<br><br>"
            "<strong>How to interpret contribution amounts:</strong> a positive amount means "
            "the factor moved the model estimate upward, while a negative contribution "
            "moved it downward. These values explain model behavior for this applicant "
            "and should not be interpreted as medical or causal effects."
            "</div>",
            unsafe_allow_html=True,
        )

    # -------------------------
    # Applicant summary
    # -------------------------
    with right:
        st.markdown("### Applicant Summary")

        summary = [
            ("Age", f"{age} years"),
            ("Income", f"₹{income_lakhs:.1f} Lakh"),
            ("Dependants", str(number_of_dependants)),
            ("Gender", gender),
            ("BMI", bmi_category),
            ("Smoking", smoking_status),
            ("Medical History", medical_history),
            ("Insurance Plan", insurance_plan),
            ("Region", region),
        ]

        for label, value in summary:
            st.markdown(
                f"""
                <div class="summary-item">
                    <span class="summary-label">{label}</span>
                    <span class="summary-value">{value}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -------------------------
    # Key insights
    # -------------------------
    st.markdown("### Key Insights")
    st.caption(
        "A concise interpretation of every model-derived factor contribution for this applicant."
    )

    for f in result["factors"]:
        contribution = f["contribution"]

        if contribution > 0:
            direction_text = "contributing upward"
            insight_class = "insight-up"
            icon = "↑"
        elif contribution < 0:
            direction_text = "contributing downward"
            insight_class = "insight-down"
            icon = "↓"
        else:
            direction_text = "has approximately no contribution"
            insight_class = ""
            icon = "—"

        if contribution == 0:
            message = (
                f"<strong>{f['label']}</strong> has approximately no contribution "
                "relative to the model baseline."
            )
        else:
            message = (
                f"<strong>{f['label']}</strong> is {direction_text} by approximately "
                f"<strong>₹{abs(contribution):,.0f}</strong> relative to the model baseline."
            )

        st.markdown(
            f'<div class="insight-card {insight_class}">'
            f'<strong>{icon}</strong>&nbsp;&nbsp;{message}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="small-note">'
        "<strong>Reading the explanation:</strong> impact describes the relative magnitude "
        "of a factor's model contribution. The ₹ amount describes the direction and size "
        "of that contribution for this applicant. It does not represent a guaranteed "
        "premium discount or surcharge."
        "</div>",
        unsafe_allow_html=True,
    )

    # -------------------------
    # Plan comparison
    # -------------------------
    st.markdown("")
    st.markdown("### Insurance Plan Comparison")

    comparison_rows = []
    for plan in categorical_options["Insurance Plan"]:
        scenario = dict(result["input_dict"])
        scenario["Insurance Plan"] = plan
        premium = predict_premium(scenario)
        comparison_rows.append(
            {"Plan": plan, "Estimated Annual Premium": premium}
        )

    selected_premium = result["prediction"]
    lowest_premium = min(row["Estimated Annual Premium"] for row in comparison_rows)

    cc1, cc2, cc3 = st.columns(3)
    for col, row in zip([cc1, cc2, cc3], comparison_rows):
        premium = row["Estimated Annual Premium"]
        is_selected = row["Plan"] == insurance_plan
        is_lowest = premium == lowest_premium

        if is_selected:
            delta_text = "Selected plan"
        elif premium > selected_premium:
            delta_text = f"₹{premium - selected_premium:,.0f} above selected"
        else:
            delta_text = f"₹{selected_premium - premium:,.0f} below selected"

        classes = "scenario-card"
        if is_selected:
            classes += " selected"
        if is_lowest:
            classes += " best"

        badges = []
        if is_selected:
            badges.append('<span class="scenario-badge">Selected</span>')
        if is_lowest:
            badges.append('<span class="scenario-badge best-badge">Lowest estimate</span>')

        with col:
            st.markdown(
                f"""
                <div class="{classes}">
                    <div class="scenario-plan">{row["Plan"]}</div>
                    <div class="scenario-price">₹{premium:,.0f}</div>
                    <div class="scenario-delta">{delta_text}</div>
                    {" ".join(badges)}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.caption(
        "Scenario analysis re-estimates the premium for each plan while keeping the rest of the applicant profile unchanged."
    )

    # -------------------------
    # Download report
    # -------------------------
    report_bytes = create_pdf_report(
        result=result,
        comparison_rows=comparison_rows,
    )

    st.download_button(
        "Download Assessment Report",
        data=report_bytes,
        file_name="insurerisk_assessment.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


# -----------------------------
# History
# -----------------------------
if st.session_state.history:
    st.divider()
    st.markdown("### Recent Assessments")

    history_rows = []
    for item in st.session_state.history:
        history_rows.append(
            {
                "Age": item["Age"],
                "Plan": item["Plan"],
                "Risk": item["Risk"],
                "Medical History": item["Medical History"],
                "Premium": f"₹{item['Premium']:,.0f}",
            }
        )

    st.dataframe(history_rows, use_container_width=True, hide_index=True)


# -----------------------------
# Model information
# -----------------------------
with st.expander("How InsureRisk AI works"):
    st.markdown("""
    **1. Applicant information**  
    The application collects demographic, financial, lifestyle, medical-history,
    employment and insurance-plan information.

    **2. Feature engineering**  
    Medical history is converted into a normalized risk-score feature used by the
    trained model.

    **3. Age-based model selection**  
    Applicants aged 25 or below use the young-applicant Linear Regression model.
    Applicants above 25 use the XGBoost model.

    **4. Premium prediction**  
    The selected model estimates the annual insurance premium.

    **5. Individual explanation**  
    The application calculates model-derived feature contributions and translates
    technical features into user-friendly insurance factors.
    """)

st.markdown(
    '<div class="footer">InsureRisk AI • Machine Learning Insurance Pricing Demonstration</div>',
    unsafe_allow_html=True,
)
