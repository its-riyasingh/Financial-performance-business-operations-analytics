import streamlit as st
import pandas as pd
import plotly.express as px

from utils.filters import company_filter


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Financial Insights",
    layout="wide"
)


# ==================================================
# DATABASE CONNECTION
# ==================================================

conn = st.connection(
    "postgresql",
    type="sql"
)

for attempt in range(3):
    try:
        df = conn.query(
            "SELECT * FROM financial_metrics",
            ttl=300
        )
        break
    except Exception:
        if attempt == 2:
            st.error("Database connection failed. Please try again.")
            st.stop()
        time.sleep(2)

df["fiscal_date"] = pd.to_datetime(df["fiscal_date"])


# ==================================================
# COLUMN DETECTION
# ==================================================

def find_column(dataframe, possible_names):
    columns = list(dataframe.columns)

    for name in possible_names:
        if name in columns:
            return name

    lower_map = {
        str(col).lower(): col
        for col in columns
    }

    for name in possible_names:
        if name.lower() in lower_map:
            return lower_map[name.lower()]

    return None


revenue_col = find_column(
    df,
    [
        "total_revenue",
        "revenue",
        "totalRevenue"
    ]
)

net_income_col = find_column(
    df,
    [
        "net_income",
        "netIncome"
    ]
)

fcf_col = find_column(
    df,
    [
        "free_cash_flow",
        "freeCashFlow"
    ]
)


# ==================================================
# VALIDATE DATA
# ==================================================

required_columns = {
    "Revenue": revenue_col,
    "Net Income": net_income_col,
    "Free Cash Flow": fcf_col
}

missing = [
    name
    for name, column in required_columns.items()
    if column is None
]

if missing:
    st.error(
        "Some required financial columns could not be detected."
    )

    st.write("Missing columns:", missing)
    st.write("Available columns:")
    st.code("\n".join(df.columns.tolist()))
    st.stop()


# ==================================================
# GLOBAL COMPANY FILTER
# ==================================================

selected_companies = company_filter(df)

if not selected_companies:
    st.warning(
        "Please select at least one company from the sidebar."
    )
    st.stop()

filtered_df = df[
    df["symbol"].isin(selected_companies)
].copy()


# ==================================================
# LATEST DATA
# ==================================================

latest_df = (
    filtered_df
    .sort_values("fiscal_date")
    .groupby("symbol")
    .tail(1)
    .copy()
)

if latest_df.empty:
    st.warning("No financial data is available.")
    st.stop()


# ==================================================
# CUSTOM STYLING
# ==================================================

st.markdown(
    """
    <style>

    .insight-kpi-card {
        background: linear-gradient(
            135deg,
            #FFFFFF 0%,
            #F3F7FC 100%
        );
        border: 1px solid #D9E3EF;
        border-radius: 10px;
        padding: 18px 20px 16px 20px;
        min-height: 125px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
    }

    .insight-kpi-title {
        color: #52627A;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 10px;
    }

    .insight-kpi-value {
        color: #142B49;
        font-size: 30px;
        font-weight: 600;
        line-height: 1.1;
    }

    .insight-status-card {
        border-radius: 10px;
        padding: 15px 18px;
        border: 1px solid #D9E3EF;
        background: #FFFFFF;
        margin: 6px 0 18px 0;
    }

    .insight-status-strong {
        border-left: 4px solid #2E8B68;
    }

    .insight-status-moderate {
        border-left: 4px solid #C28A19;
    }

    .insight-status-attention {
        border-left: 4px solid #C94B4B;
    }

    .insight-section-card {
        background: #FFFFFF;
        border: 1px solid #D9E3EF;
        border-radius: 10px;
        padding: 18px 20px;
        min-height: 180px;
    }

    .insight-section-title {
        color: #142B49;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 14px;
    }

    .insight-list-item {
        color: #37465A;
        font-size: 14px;
        margin: 9px 0;
    }

    .insight-footer {
        color: #7A8798;
        font-size: 12px;
        margin-top: 24px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# HEADER
# ==================================================

st.title("Financial Insights")

st.caption(
    "Automated interpretation of financial performance, growth, "
    "profitability, cash flow and risk indicators."
)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def format_billions(value):
    if pd.isna(value):
        return "N/A"

    return f"${value / 1_000_000_000:,.2f}B"


def score_metric(value, strong_threshold, moderate_threshold):
    if pd.isna(value):
        return 0

    if value >= strong_threshold:
        return 2

    if value >= moderate_threshold:
        return 1

    return 0


def insight_kpi(title, value):
    html = (
        '<div class="insight-kpi-card">'
        f'<div class="insight-kpi-title">{title}</div>'
        f'<div class="insight-kpi-value">{value}</div>'
        '</div>'
    )

    st.html(html)


# ==================================================
# FINANCIAL HEALTH SCORE
# ==================================================

def calculate_score(row):
    score = 0

    # Profitability
    if pd.notna(row["net_profit_margin"]):
        if row["net_profit_margin"] >= 15:
            score += 2
        elif row["net_profit_margin"] >= 5:
            score += 1

    # Revenue Growth
    if pd.notna(row["revenue_growth"]):
        if row["revenue_growth"] >= 10:
            score += 2
        elif row["revenue_growth"] >= 0:
            score += 1

    # Net Income Growth
    if pd.notna(row["net_income_growth"]):
        if row["net_income_growth"] >= 10:
            score += 2
        elif row["net_income_growth"] >= 0:
            score += 1

    # ROA
    if pd.notna(row["roa"]):
        if row["roa"] >= 10:
            score += 2
        elif row["roa"] >= 5:
            score += 1

    # Free Cash Flow
    if pd.notna(row[fcf_col]):
        if row[fcf_col] > 0:
            score += 2

    # Debt
    if pd.notna(row["debt_to_asset_ratio"]):
        if row["debt_to_asset_ratio"] < 30:
            score += 2
        elif row["debt_to_asset_ratio"] < 50:
            score += 1

    return score


latest_df["health_score"] = latest_df.apply(
    calculate_score,
    axis=1
)


# ==================================================
# HEALTH CATEGORY
# ==================================================

def health_category(score):
    if score >= 9:
        return "Strong"

    if score >= 6:
        return "Moderate"

    return "Needs Attention"


latest_df["health_status"] = latest_df[
    "health_score"
].apply(health_category)


# ==================================================
# OVERALL HEALTH
# ==================================================

st.header("Overall Financial Health")

average_score = latest_df["health_score"].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    insight_kpi(
        "Average Health Score",
        f"{average_score:.1f}/12"
    )

with col2:
    strongest = latest_df.loc[
        latest_df["health_score"].idxmax()
    ]

    insight_kpi(
        "Strongest Company",
        strongest["symbol"]
    )

with col3:
    avg_growth = latest_df["revenue_growth"].mean()

    insight_kpi(
        "Average Revenue Growth",
        f"{avg_growth:.2f}%"
    )

with col4:
    avg_margin = latest_df["net_profit_margin"].mean()

    insight_kpi(
        "Average Profit Margin",
        f"{avg_margin:.2f}%"
    )


# ==================================================
# HEALTH SCORE COMPARISON
# ==================================================

st.subheader("Financial Health by Company")

health_chart = latest_df[
    [
        "symbol",
        "health_score"
    ]
].copy()

health_chart = health_chart.sort_values(
    "health_score",
    ascending=True
)

fig_health = px.bar(
    health_chart,
    x="health_score",
    y="symbol",
    orientation="h",
    text="health_score",
    labels={
        "health_score": "Health Score",
        "symbol": "Company"
    }
)

fig_health.update_traces(
    marker_color="#6FA8DC",
    textposition="outside"
)

fig_health.update_layout(
    height=360,
    margin=dict(l=20, r=30, t=20, b=20),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#1F2937"),
    xaxis=dict(
        range=[0, 13],
        gridcolor="#E5EAF0"
    ),
    yaxis=dict(
        gridcolor="#FFFFFF"
    )
)

st.plotly_chart(
    fig_health,
    use_container_width=True,
    config={
        "displaylogo": False,
        "responsive": True
    }
)


# ==================================================
# COMPANY SCORECARD
# ==================================================

st.subheader("Financial Health Scorecard")

scorecard = latest_df[
    [
        "symbol",
        "health_score",
        "health_status",
        "revenue_growth",
        "net_profit_margin",
        "roe",
        "roa",
        fcf_col,
        "debt_to_asset_ratio"
    ]
].copy()

scorecard.columns = [
    "Company",
    "Health Score",
    "Status",
    "Revenue Growth",
    "Net Profit Margin",
    "ROE",
    "ROA",
    "Free Cash Flow",
    "Debt-to-Asset Ratio"
]

scorecard = scorecard.sort_values(
    "Health Score",
    ascending=False
)

scorecard["Free Cash Flow"] = scorecard[
    "Free Cash Flow"
].apply(format_billions)

st.dataframe(
    scorecard,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# COMPANY INSIGHT
# ==================================================

st.header("Company Insight")

insight_company = st.selectbox(
    "Select Company for Detailed Insight",
    sorted(filtered_df["symbol"].unique()),
    key="financial_insight_company"
)

company_row = latest_df[
    latest_df["symbol"] == insight_company
].iloc[0]


# ==================================================
# COMPANY STATUS
# ==================================================

score = company_row["health_score"]
status = company_row["health_status"]

if status == "Strong":
    status_class = "insight-status-strong"
    status_text = "Strong Financial Profile"

elif status == "Moderate":
    status_class = "insight-status-moderate"
    status_text = "Moderate Financial Profile"

else:
    status_class = "insight-status-attention"
    status_text = "Needs Attention"

st.markdown(
    f"""
    <div class="insight-status-card {status_class}">
        <strong>{insight_company}</strong> — {status_text}
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# STRENGTHS
# ==================================================

strengths = []

if (
    pd.notna(company_row["revenue_growth"])
    and company_row["revenue_growth"] >= 10
):
    strengths.append(
        f"Strong revenue growth of "
        f"{company_row['revenue_growth']:.2f}%."
    )

if (
    pd.notna(company_row["net_profit_margin"])
    and company_row["net_profit_margin"] >= 15
):
    strengths.append(
        f"Strong net profit margin of "
        f"{company_row['net_profit_margin']:.2f}%."
    )

if (
    pd.notna(company_row["roa"])
    and company_row["roa"] >= 10
):
    strengths.append(
        f"Strong asset efficiency with ROA of "
        f"{company_row['roa']:.2f}%."
    )

if (
    pd.notna(company_row[fcf_col])
    and company_row[fcf_col] > 0
):
    strengths.append(
        "Positive free cash flow generation."
    )


# ==================================================
# RISKS
# ==================================================

risks = []

if (
    pd.notna(company_row["revenue_growth"])
    and company_row["revenue_growth"] < 0
):
    risks.append(
        f"Revenue is declining at "
        f"{company_row['revenue_growth']:.2f}%."
    )

if (
    pd.notna(company_row["net_income_growth"])
    and company_row["net_income_growth"] < 0
):
    risks.append(
        f"Net income growth is negative at "
        f"{company_row['net_income_growth']:.2f}%."
    )

if (
    pd.notna(company_row["net_profit_margin"])
    and company_row["net_profit_margin"] < 5
):
    risks.append("Low net profit margin.")

if (
    pd.notna(company_row[fcf_col])
    and company_row[fcf_col] < 0
):
    risks.append("Negative free cash flow.")

if (
    pd.notna(company_row["debt_to_asset_ratio"])
    and company_row["debt_to_asset_ratio"] >= 50
):
    risks.append(
        f"High debt-to-asset ratio of "
        f"{company_row['debt_to_asset_ratio']:.2f}%."
    )


# ==================================================
# DISPLAY STRENGTHS / RISKS
# ==================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("Key Strengths")

    if strengths:
        items = "".join(
            f'<div class="insight-list-item">• {strength}</div>'
            for strength in strengths
        )
    else:
        items = (
            '<div class="insight-list-item">'
            "No major strength indicators identified."
            "</div>"
        )

    st.markdown(
        f"""
        <div class="insight-section-card">
            <div class="insight-section-title">
                Key Strengths
            </div>
            {items}
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.subheader("Potential Risks")

    if risks:
        items = "".join(
            f'<div class="insight-list-item">• {risk}</div>'
            for risk in risks
        )
    else:
        items = (
            '<div class="insight-list-item">'
            "No major warning indicators identified."
            "</div>"
        )

    st.markdown(
        f"""
        <div class="insight-section-card">
            <div class="insight-section-title">
                Potential Risks
            </div>
            {items}
        </div>
        """,
        unsafe_allow_html=True
    )


# ==================================================
# EXECUTIVE SUMMARY
# ==================================================

st.header("Executive Summary")

summary_parts = []

if pd.notna(company_row["revenue_growth"]):

    if company_row["revenue_growth"] > 10:
        summary_parts.append(
            f"{insight_company} is experiencing strong "
            f"revenue growth of "
            f"{company_row['revenue_growth']:.2f}%."
        )

    elif company_row["revenue_growth"] >= 0:
        summary_parts.append(
            f"{insight_company} is growing at a moderate "
            f"revenue rate of "
            f"{company_row['revenue_growth']:.2f}%."
        )

    else:
        summary_parts.append(
            f"{insight_company} is experiencing revenue "
            f"decline of "
            f"{abs(company_row['revenue_growth']):.2f}%."
        )


if pd.notna(company_row["net_profit_margin"]):
    summary_parts.append(
        f"The latest net profit margin is "
        f"{company_row['net_profit_margin']:.2f}%."
    )


if pd.notna(company_row[fcf_col]):

    if company_row[fcf_col] > 0:
        summary_parts.append(
            "The company is generating positive free cash flow."
        )
    else:
        summary_parts.append(
            "The company is currently reporting negative "
            "free cash flow."
        )


if pd.notna(company_row["debt_to_asset_ratio"]):

    if company_row["debt_to_asset_ratio"] < 30:
        summary_parts.append(
            "Debt exposure is relatively low."
        )

    elif company_row["debt_to_asset_ratio"] < 50:
        summary_parts.append(
            "Debt exposure is moderate."
        )

    else:
        summary_parts.append(
            "Debt exposure is relatively high and should "
            "be monitored."
        )


if summary_parts:
    st.info(" ".join(summary_parts))


# ==================================================
# ANALYST CHECKLIST
# ==================================================

st.header("Analyst Checklist")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        **Growth**

        - Is revenue growing?
        - Is net income growing faster than revenue?
        - Is growth consistent over time?

        **Profitability**

        - Are profit margins strong?
        - Are operating margins stable?
        - Is ROA improving?
        """
    )

with col2:
    st.markdown(
        """
        **Financial Health**

        - Is free cash flow positive?
        - Is debt exposure manageable?
        - Is capital being used efficiently?

        **Decision Focus**

        - Growth quality
        - Profitability
        - Cash generation
        - Financial risk
        """
    )


# ==================================================
# FOOTNOTE
# ==================================================

st.caption(
    "Financial Insights are generated from predefined analytical "
    "rules applied to the project's financial dataset. "
    "They are intended for analytical demonstration and do not "
    "constitute investment advice."
)
