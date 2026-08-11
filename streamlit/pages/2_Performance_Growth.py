import streamlit as st
import pandas as pd
import plotly.express as px

from utils.filters import company_filter


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Performance & Growth",
    page_icon=None,
    layout="wide"
)


# ============================================================
# PAGE-SPECIFIC STYLING
# Global colors/background are controlled by config.toml
# ============================================================

st.markdown(
    """
    <style>

    /* =========================================
       MAIN PAGE SPACING
       ========================================= */

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }


    /* =========================================
       SIDEBAR COMPANY PILLS
       ========================================= */

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


    /* =========================================
       SIDEBAR BUTTON
       ========================================= */

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 40px;
        border-radius: 7px;
        font-size: 13px;
        font-weight: 500;
    }


    /* =========================================
       GROWTH LEADER KPI CARDS
       ========================================= */

    .growth-kpi-card {
        background: #FFFFFF;
        border: 1px solid #D9E0E7;
        border-radius: 10px;
        padding: 18px 20px 16px 20px;
        min-height: 125px;
        box-shadow: 0 2px 6px rgba(16, 24, 40, 0.05);
    }

    .growth-kpi-label {
        color: #526581;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 10px;
    }

    .growth-kpi-value {
        color: #1F2937;
        font-size: 30px;
        font-weight: 600;
        line-height: 1.1;
    }

    .growth-kpi-description {
        color: #8A97A8;
        font-size: 12px;
        margin-top: 10px;
        line-height: 1.4;
    }


    /* =========================================
       POSITIVE GROWTH BADGE
       ========================================= */

    .growth-badge {
        display: inline-block;
        background: #E8F6EF;
        color: #198754;
        border-radius: 12px;
        padding: 3px 8px;
        margin-top: 9px;
        font-size: 12px;
        font-weight: 500;
    }


    /* =========================================
       PLOTLY CHART CONTAINERS
       ========================================= */

    [data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #D9E0E7;
        border-radius: 9px;
        padding: 2px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
    }


    /* =========================================
       SECTION SPACING
       ========================================= */

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
# DATABASE
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
# SIDEBAR / GLOBAL COMPANY FILTER
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

filtered_df = filtered_df.sort_values(
    "fiscal_date"
)


# ============================================================
# HEADER
# ============================================================

st.title("Performance & Growth")

st.caption(
    "Which companies are growing fastest, and is that growth sustainable?"
)


# ============================================================
# LATEST DATA
# ============================================================

latest_df = (
    filtered_df
    .sort_values("fiscal_date")
    .groupby("symbol")
    .tail(1)
    .copy()
)


# ============================================================
# GROWTH LEADERS
# ============================================================

st.subheader("Growth Leaders")

col1, col2, col3 = st.columns(3)


# ============================================================
# HIGHEST REVENUE GROWTH
# ============================================================

with col1:

    best_revenue = latest_df.loc[
        latest_df["revenue_growth"].idxmax()
    ]

    revenue_growth = best_revenue["revenue_growth"]

    st.markdown(
        f"""<div class="growth-kpi-card">
<div class="growth-kpi-label">Highest Revenue Growth</div>
<div class="growth-kpi-value">{best_revenue["symbol"]}</div>
<div class="growth-badge">↑ {revenue_growth:.2f}%</div>
</div>""",
        unsafe_allow_html=True
    )


# ============================================================
# HIGHEST NET INCOME GROWTH
# ============================================================

with col2:

    best_income = latest_df.loc[
        latest_df["net_income_growth"].idxmax()
    ]

    income_growth = best_income["net_income_growth"]

    st.markdown(
        f"""<div class="growth-kpi-card">
<div class="growth-kpi-label">Highest Net Income Growth</div>
<div class="growth-kpi-value">{best_income["symbol"]}</div>
<div class="growth-badge">↑ {income_growth:.2f}%</div>
</div>""",
        unsafe_allow_html=True
    )


# ============================================================
# AVERAGE REVENUE GROWTH
# ============================================================

with col3:

    avg_growth = latest_df["revenue_growth"].mean()

    st.markdown(
        f"""<div class="growth-kpi-card">
<div class="growth-kpi-label">Average Revenue Growth</div>
<div class="growth-kpi-value">{avg_growth:.2f}%</div>
<div class="growth-badge">↑ {avg_growth:.2f}%</div>
</div>""",
        unsafe_allow_html=True
    )


# ============================================================
# GROWTH COMPARISON
# ============================================================

st.subheader("Revenue Growth vs Net Income Growth")

st.markdown(
    """
    <div class="section-description">
        Compare the latest revenue and net income growth across
        the selected companies.
    </div>
    """,
    unsafe_allow_html=True
)


growth_chart = latest_df[
    [
        "symbol",
        "revenue_growth",
        "net_income_growth"
    ]
].copy()


growth_long = growth_chart.melt(
    id_vars="symbol",
    value_vars=[
        "revenue_growth",
        "net_income_growth"
    ],
    var_name="Metric",
    value_name="Growth"
)


growth_long["Metric"] = growth_long[
    "Metric"
].map({
    "revenue_growth": "Revenue Growth",
    "net_income_growth": "Net Income Growth"
})


fig_growth = px.bar(
    growth_long,
    x="symbol",
    y="Growth",
    color="Metric",
    barmode="group",
    text="Growth",
    labels={
        "symbol": "Company",
        "Growth": "Growth (%)",
        "Metric": "Metric"
    },
    template="plotly_white"
)


fig_growth.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "%{fullData.name}: %{y:.2f}%"
        "<extra></extra>"
    )
)


fig_growth.update_layout(
    height=340,
    margin=dict(
        l=45,
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
        showgrid=False
    ),
    yaxis=dict(
        title="Growth (%)",
        gridcolor="#E4E7EC",
        zerolinecolor="#D0D5DD"
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
# REVENUE GROWTH RANKING
# ============================================================

st.subheader("Revenue Growth Ranking")


growth_ranking = latest_df[
    [
        "symbol",
        "revenue_growth",
        "net_income_growth"
    ]
].sort_values(
    "revenue_growth",
    ascending=False
).copy()


growth_ranking.columns = [
    "Company",
    "Revenue Growth (%)",
    "Net Income Growth (%)"
]


st.dataframe(
    growth_ranking,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Revenue Growth (%)": st.column_config.NumberColumn(
            format="%.2f%%"
        ),
        "Net Income Growth (%)": st.column_config.NumberColumn(
            format="%.2f%%"
        )
    }
)


# ============================================================
# HISTORICAL GROWTH
# ============================================================

st.subheader("Historical Growth")

st.markdown(
    """
    <div class="section-description">
        Track how revenue and net income growth have changed
        over time for the selected company.
    </div>
    """,
    unsafe_allow_html=True
)


trend_company = st.selectbox(
    "Select Company",
    sorted(filtered_df["symbol"].unique()),
    key="performance_trend_company"
)


company_df = (
    filtered_df[
        filtered_df["symbol"] == trend_company
    ]
    .sort_values("fiscal_date")
    .copy()
)


# ============================================================
# HISTORICAL REVENUE + NET INCOME GROWTH
# ============================================================

col1, col2 = st.columns(2)


# ============================================================
# REVENUE GROWTH TREND
# ============================================================

with col1:

    revenue_growth_trend = company_df[
        [
            "fiscal_date",
            "revenue_growth"
        ]
    ].dropna().copy()


    revenue_growth_trend["Year"] = (
        revenue_growth_trend["fiscal_date"]
        .dt.year
    )


    revenue_growth_trend = (
        revenue_growth_trend[
            [
                "Year",
                "revenue_growth"
            ]
        ]
        .drop_duplicates("Year")
        .sort_values("Year")
    )


    fig_revenue_growth = px.line(
        revenue_growth_trend,
        x="Year",
        y="revenue_growth",
        markers=True,
        title=f"{trend_company} — Revenue Growth",
        labels={
            "Year": "Fiscal Year",
            "revenue_growth": "Revenue Growth (%)"
        },
        template="plotly_white"
    )


    fig_revenue_growth.update_traces(
        line=dict(
            color="#4F81BD",
            width=2.5
        ),
        marker=dict(
            size=7
        ),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Revenue Growth: %{y:.2f}%"
            "<extra></extra>"
        )
    )


    fig_revenue_growth.update_layout(
        height=310,
        margin=dict(
            l=45,
            r=20,
            t=50,
            b=40
        ),
        font=dict(
            color="#344054",
            family="Arial"
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            gridcolor="#EEF0F3"
        ),
        yaxis=dict(
            title="Growth (%)",
            gridcolor="#E4E7EC",
            zerolinecolor="#D0D5DD"
        )
    )


    st.plotly_chart(
        fig_revenue_growth,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


# ============================================================
# NET INCOME GROWTH TREND
# ============================================================

with col2:

    income_growth_trend = company_df[
        [
            "fiscal_date",
            "net_income_growth"
        ]
    ].dropna().copy()


    income_growth_trend["Year"] = (
        income_growth_trend["fiscal_date"]
        .dt.year
    )


    income_growth_trend = (
        income_growth_trend[
            [
                "Year",
                "net_income_growth"
            ]
        ]
        .drop_duplicates("Year")
        .sort_values("Year")
    )


    fig_income_growth = px.line(
        income_growth_trend,
        x="Year",
        y="net_income_growth",
        markers=True,
        title=f"{trend_company} — Net Income Growth",
        labels={
            "Year": "Fiscal Year",
            "net_income_growth": "Net Income Growth (%)"
        },
        template="plotly_white"
    )


    fig_income_growth.update_traces(
        line=dict(
            color="#6C7CE5",
            width=2.5
        ),
        marker=dict(
            size=7
        ),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Net Income Growth: %{y:.2f}%"
            "<extra></extra>"
        )
    )


    fig_income_growth.update_layout(
        height=310,
        margin=dict(
            l=45,
            r=20,
            t=50,
            b=40
        ),
        font=dict(
            color="#344054",
            family="Arial"
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            gridcolor="#EEF0F3"
        ),
        yaxis=dict(
            title="Growth (%)",
            gridcolor="#E4E7EC",
            zerolinecolor="#D0D5DD"
        )
    )


    st.plotly_chart(
        fig_income_growth,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


# ============================================================
# BUSINESS TAKEAWAY
# ============================================================

st.subheader("Growth Story")


best_company = latest_df.loc[
    latest_df["revenue_growth"].idxmax()
]


worst_company = latest_df.loc[
    latest_df["revenue_growth"].idxmin()
]


st.info(
    f"""
    **{best_company['symbol']}** currently leads the selected companies
    with **{best_company['revenue_growth']:.2f}% revenue growth**.

    **{worst_company['symbol']}** has the lowest reported revenue growth
    at **{worst_company['revenue_growth']:.2f}%**.

    This comparison helps distinguish companies that are expanding
    rapidly from those experiencing slower growth.
    """
)
