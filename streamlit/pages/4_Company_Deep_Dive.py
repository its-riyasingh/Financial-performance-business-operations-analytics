import streamlit as st
import pandas as pd
import plotly.express as px


from utils.filters import company_filter


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Company Deep Dive",
    page_icon=None,
    layout="wide"
)


# ============================================================
# PAGE STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }

    /* Sidebar company pills */
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #1F4E79 !important;
        border: 1px solid #1F4E79 !important;
        border-radius: 6px !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] span,
    [data-testid="stSidebar"] [data-baseweb="tag"] div {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    /* Sidebar reset button */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 40px;
        border-radius: 7px;
        font-size: 13px;
        font-weight: 500;
    }

    /* Plotly chart containers */
    [data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #D9E0E7;
        border-radius: 9px;
        padding: 2px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
    }

    .section-description {
        color: #667085;
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

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

df["fiscal_date"] = pd.to_datetime(
    df["fiscal_date"]
)


# ============================================================
# DETECT FINANCIAL COLUMNS
# ============================================================

def find_column(dataframe, exact_names=None, keywords=None):
    """
    Find a column safely using exact names first,
    then keyword matching.
    """

    exact_names = exact_names or []
    keywords = keywords or []

    columns = list(dataframe.columns)

    # Exact match
    for name in exact_names:
        if name in columns:
            return name

    # Case-insensitive exact match
    lower_map = {
        str(col).lower(): col
        for col in columns
    }

    for name in exact_names:
        if name.lower() in lower_map:
            return lower_map[name.lower()]

    # Keyword matching
    for col in columns:

        col_lower = str(col).lower()

        if all(
            keyword.lower() in col_lower
            for keyword in keywords
        ):
            return col

    return None


# ------------------------------------------------------------
# Revenue
# ------------------------------------------------------------

revenue_col = find_column(
    df,
    exact_names=[
        "revenue",
        "total_revenue",
        "revenue_usd",
        "total_revenue_usd"
    ],
    keywords=["revenue"]
)


# ------------------------------------------------------------
# Net Income
# ------------------------------------------------------------

net_income_col = find_column(
    df,
    exact_names=[
        "net_income",
        "netincome",
        "net_income_usd",
        "total_net_income"
    ],
    keywords=["net", "income"]
)


# ------------------------------------------------------------
# Free Cash Flow
# ------------------------------------------------------------

fcf_col = find_column(
    df,
    exact_names=[
        "free_cash_flow",
        "fcf",
        "free_cash_flow_usd"
    ],
    keywords=["free", "cash", "flow"]
)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = {
    "Revenue": revenue_col,
    "Net Income": net_income_col,
    "Free Cash Flow": fcf_col
}


missing_columns = [
    name
    for name, column in required_columns.items()
    if column is None
]


if missing_columns:

    st.error(
        "Some financial columns could not be detected automatically."
    )

    st.write(
        "Missing:",
        missing_columns
    )

    st.write(
        "Available database columns:"
    )

    st.code(
        "\n".join(df.columns.tolist())
    )

    st.stop()


# ============================================================
# GLOBAL COMPANY FILTER
# ============================================================

selected_companies = company_filter(df)


if not selected_companies:

    st.warning(
        "Please select at least one company from the sidebar."
    )

    st.stop()


filtered_df = df[
    df["symbol"].isin(selected_companies)
].copy()


# ============================================================
# COMPANY SELECTION
# ============================================================

st.title("Company Deep Dive")

st.caption(
    "Explore the financial performance, profitability, growth, "
    "and capital efficiency of an individual company."
)


company = st.selectbox(
    "Select Company",
    sorted(
        filtered_df["symbol"].unique()
    ),
    key="deep_dive_company"
)


company_df = (
    filtered_df[
        filtered_df["symbol"] == company
    ]
    .sort_values("fiscal_date")
    .copy()
)


if company_df.empty:

    st.warning(
        "No financial data available for the selected company."
    )

    st.stop()


# ============================================================
# LATEST FINANCIAL DATA
# ============================================================

latest = company_df.iloc[-1]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_billions(value):

    if pd.isna(value):
        return "N/A"

    return (
        f"${value / 1_000_000_000:,.2f}B"
    )


def format_percent(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


# ============================================================
# COMPANY SNAPSHOT
# ============================================================

st.subheader(
    f"{company} — Financial Snapshot"
)

st.markdown(
    """
    <div class="section-description">
        Latest reported financial metrics for the selected company.
    </div>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Snapshot Card Styling
# ------------------------------------------------------------

st.markdown(
    """
    <style>

    .snapshot-card {
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 10px;
        padding: 18px 20px 16px 20px;
        min-height: 105px;
        box-shadow: 0 2px 6px rgba(31, 78, 121, 0.06);
        position: relative;
        overflow: hidden;
    }

    .snapshot-card::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 4px;
        height: 100%;
        background: #1F4E79;
    }

    .snapshot-label {
        color: #667085;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 8px;
    }

    .snapshot-value {
        color: #172B4D;
        font-size: 27px;
        font-weight: 600;
        line-height: 1.2;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Snapshot Cards
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="snapshot-card">
            <div class="snapshot-label">Revenue</div>
            <div class="snapshot-value">
                {format_billions(latest[revenue_col])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="snapshot-card">
            <div class="snapshot-label">Net Income</div>
            <div class="snapshot-value">
                {format_billions(latest[net_income_col])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="snapshot-card">
            <div class="snapshot-label">Net Profit Margin</div>
            <div class="snapshot-value">
                {format_percent(latest["net_profit_margin"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="snapshot-card">
            <div class="snapshot-label">Free Cash Flow</div>
            <div class="snapshot-value">
                {format_billions(latest[fcf_col])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# LATEST PERFORMANCE
# ============================================================

st.subheader("Latest Performance")


performance = pd.DataFrame(
    {
        "Metric": [
            "Revenue",
            "Net Income",
            "Net Profit Margin",
            "Operating Margin",
            "ROE",
            "ROA",
            "Free Cash Flow"
        ],

        "Value": [
            format_billions(
                latest[revenue_col]
            ),

            format_billions(
                latest[net_income_col]
            ),

            format_percent(
                latest["net_profit_margin"]
            ),

            format_percent(
                latest["operating_margin"]
            ),

            format_percent(
                latest["roe"]
            ),

            format_percent(
                latest["roa"]
            ),

            format_billions(
                latest[fcf_col]
            )
        ]
    }
)


st.dataframe(
    performance,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FINANCIAL TREND
# ============================================================

st.subheader("Financial Trend")

st.markdown(
    """
    <div class="section-description">
        Track whether business scale and bottom-line earnings
        are moving together over time.
    </div>
    """,
    unsafe_allow_html=True
)


trend = company_df[
    [
        "fiscal_date",
        revenue_col,
        net_income_col
    ]
].copy()


trend = trend.rename(
    columns={
        revenue_col: "Revenue",
        net_income_col: "Net Income"
    }
)


trend_long = trend.melt(
    id_vars="fiscal_date",
    value_vars=[
        "Revenue",
        "Net Income"
    ],
    var_name="Metric",
    value_name="Value"
)


fig_financial = px.line(
    trend_long,
    x="fiscal_date",
    y="Value",
    color="Metric",
    markers=True,
    labels={
        "fiscal_date": "Fiscal Date",
        "Value": "Amount",
        "Metric": "Metric"
    },
    template="plotly_white"
)


fig_financial.update_layout(
    height=350,
    margin=dict(
        l=50,
        r=25,
        t=20,
        b=45
    ),
    font=dict(
        color="#344054",
        family="Arial"
    ),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    xaxis=dict(
        gridcolor="#EEF0F3"
    ),
    yaxis=dict(
        title="Financial Value",
        gridcolor="#E4E7EC",
        zerolinecolor="#D0D5DD"
    )
)


fig_financial.update_traces(
    hovertemplate=(
        "<b>%{x|%Y-%m-%d}</b><br>"
        "%{fullData.name}: %{y:,.0f}"
        "<extra></extra>"
    )
)


st.plotly_chart(
    fig_financial,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "displaylogo": False
    }
)


# ============================================================
# GROWTH + PROFITABILITY SIDE BY SIDE
# ============================================================

col1, col2 = st.columns(2)


# ============================================================
# GROWTH TREND
# ============================================================

with col1:

    st.subheader("Growth Trend")

    growth = company_df[
        [
            "fiscal_date",
            "revenue_growth",
            "net_income_growth"
        ]
    ].copy()


    growth_long = growth.melt(
        id_vars="fiscal_date",
        value_vars=[
            "revenue_growth",
            "net_income_growth"
        ],
        var_name="Metric",
        value_name="Growth"
    )


    growth_long["Metric"] = growth_long[
        "Metric"
    ].map(
        {
            "revenue_growth": "Revenue Growth",
            "net_income_growth": "Net Income Growth"
        }
    )


    fig_growth = px.line(
        growth_long,
        x="fiscal_date",
        y="Growth",
        color="Metric",
        markers=True,
        labels={
            "fiscal_date": "Fiscal Date",
            "Growth": "Growth (%)",
            "Metric": "Metric"
        },
        template="plotly_white"
    )


    fig_growth.update_layout(
        height=330,
        margin=dict(
            l=45,
            r=20,
            t=20,
            b=45
        ),
        font=dict(
            color="#344054",
            family="Arial"
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            gridcolor="#EEF0F3"
        ),
        yaxis=dict(
            title="Growth (%)",
            gridcolor="#E4E7EC",
            zerolinecolor="#D0D5DD"
        )
    )


    fig_growth.update_traces(
        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>"
            "%{fullData.name}: %{y:.2f}%"
            "<extra></extra>"
        )
    )


    st.plotly_chart(
        fig_growth,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


# ============================================================
# PROFITABILITY TREND
# ============================================================

with col2:

    st.subheader("Profitability Trend")

    profitability = company_df[
        [
            "fiscal_date",
            "net_profit_margin",
            "operating_margin"
        ]
    ].copy()


    profitability_long = profitability.melt(
        id_vars="fiscal_date",
        value_vars=[
            "net_profit_margin",
            "operating_margin"
        ],
        var_name="Metric",
        value_name="Margin"
    )


    profitability_long["Metric"] = (
        profitability_long["Metric"].map(
            {
                "net_profit_margin": "Net Profit Margin",
                "operating_margin": "Operating Margin"
            }
        )
    )


    fig_profitability = px.line(
        profitability_long,
        x="fiscal_date",
        y="Margin",
        color="Metric",
        markers=True,
        labels={
            "fiscal_date": "Fiscal Date",
            "Margin": "Margin (%)",
            "Metric": "Metric"
        },
        template="plotly_white"
    )


    fig_profitability.update_layout(
        height=330,
        margin=dict(
            l=45,
            r=20,
            t=20,
            b=45
        ),
        font=dict(
            color="#344054",
            family="Arial"
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            gridcolor="#EEF0F3"
        ),
        yaxis=dict(
            title="Margin (%)",
            gridcolor="#E4E7EC",
            zerolinecolor="#D0D5DD"
        )
    )


    fig_profitability.update_traces(
        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>"
            "%{fullData.name}: %{y:.2f}%"
            "<extra></extra>"
        )
    )


    st.plotly_chart(
        fig_profitability,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


# ============================================================
# CAPITAL EFFICIENCY
# ============================================================

st.subheader("Capital Efficiency")

st.markdown(
    """
    <div class="section-description">
        Compare returns generated from shareholder equity
        and the company's asset base over time.
    </div>
    """,
    unsafe_allow_html=True
)


capital = company_df[
    [
        "fiscal_date",
        "roe",
        "roa"
    ]
].copy()


capital_long = capital.melt(
    id_vars="fiscal_date",
    value_vars=[
        "roe",
        "roa"
    ],
    var_name="Metric",
    value_name="Return"
)


capital_long["Metric"] = (
    capital_long["Metric"].map(
        {
            "roe": "ROE",
            "roa": "ROA"
        }
    )
)


fig_capital = px.line(
    capital_long,
    x="fiscal_date",
    y="Return",
    color="Metric",
    markers=True,
    labels={
        "fiscal_date": "Fiscal Date",
        "Return": "Return (%)",
        "Metric": "Metric"
    },
    template="plotly_white"
)


fig_capital.update_layout(
    height=350,
    margin=dict(
        l=50,
        r=25,
        t=20,
        b=45
    ),
    font=dict(
        color="#344054",
        family="Arial"
    ),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    xaxis=dict(
        gridcolor="#EEF0F3"
    ),
    yaxis=dict(
        title="Return (%)",
        gridcolor="#E4E7EC",
        zerolinecolor="#D0D5DD"
    )
)


fig_capital.update_traces(
    hovertemplate=(
        "<b>%{x|%Y-%m-%d}</b><br>"
        "%{fullData.name}: %{y:.2f}%"
        "<extra></extra>"
    )
)


st.plotly_chart(
    fig_capital,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "displaylogo": False
    }
)


# ============================================================
# COMPANY STORY
# ============================================================

st.subheader("Company Story")


latest_margin = latest["net_profit_margin"]
latest_operating = latest["operating_margin"]
latest_roe = latest["roe"]
latest_roa = latest["roa"]


story_parts = []


if pd.notna(latest_margin):

    story_parts.append(
        f"**{company}** currently reports a net profit "
        f"margin of **{latest_margin:.2f}%**."
    )


if pd.notna(latest_operating):

    story_parts.append(
        f"Its operating margin is "
        f"**{latest_operating:.2f}%**."
    )


if pd.notna(latest_roe):

    story_parts.append(
        f"ROE stands at **{latest_roe:.2f}%**."
    )


if pd.notna(latest_roa):

    story_parts.append(
        f"ROA stands at **{latest_roa:.2f}%**."
    )


if story_parts:

    story = " ".join(story_parts)

    st.info(story)


# ============================================================
# ANALYST VIEW
# ============================================================

st.subheader("What should an analyst look for?")


col1, col2 = st.columns(2)


with col1:

    st.markdown(
        """
        **Positive signals**

        - Revenue increasing over time
        - Net income growing with revenue
        - Stable or improving profit margins
        - Positive free cash flow
        - Strong ROE and ROA
        """
    )


with col2:

    st.markdown(
        """
        **Potential warning signals**

        - Revenue growth slowing
        - Net income declining
        - Falling profit margins
        - Negative free cash flow
        - Large gap between ROE and ROA
        """
    )


# ============================================================
# HISTORICAL FINANCIAL DATA
# ============================================================

st.subheader("Historical Financial Data")


history = company_df[
    [
        "fiscal_date",
        revenue_col,
        net_income_col,
        "net_profit_margin",
        "operating_margin",
        "roe",
        "roa",
        fcf_col
    ]
].copy()


history = history.sort_values(
    "fiscal_date",
    ascending=False
)


history.columns = [
    "Fiscal Date",
    "Revenue",
    "Net Income",
    "Net Profit Margin",
    "Operating Margin",
    "ROE",
    "ROA",
    "Free Cash Flow"
]


# ============================================================
# FORMAT HISTORICAL VALUES
# ============================================================

history["Revenue"] = (
    history["Revenue"]
    .apply(format_billions)
)


history["Net Income"] = (
    history["Net Income"]
    .apply(format_billions)
)


history["Free Cash Flow"] = (
    history["Free Cash Flow"]
    .apply(format_billions)
)


history["Net Profit Margin"] = (
    history["Net Profit Margin"]
    .apply(format_percent)
)


history["Operating Margin"] = (
    history["Operating Margin"]
    .apply(format_percent)
)


history["ROE"] = (
    history["ROE"]
    .apply(format_percent)
)


history["ROA"] = (
    history["ROA"]
    .apply(format_percent)
)


st.dataframe(
    history,
    use_container_width=True,
    hide_index=True
)
