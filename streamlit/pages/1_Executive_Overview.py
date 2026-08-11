import streamlit as st
import pandas as pd
import plotly.express as px

from utils.filters import company_filter


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Executive Overview",
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
   KPI SUMMARY CARDS
   ========================================= */

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #D9E0E7;
    border-radius: 10px;
    padding: 18px 20px 16px 20px;
    min-height: 125px;
    box-shadow: 0 2px 6px rgba(16, 24, 40, 0.05);
}

.kpi-label {
    color: #526581;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 10px;
}

.kpi-value {
    color: #1F2937;
    font-size: 30px;
    font-weight: 600;
    line-height: 1.1;
}

.kpi-description {
    color: #8A97A8;
    font-size: 12px;
    margin-top: 10px;
    line-height: 1.4;
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
       SIDEBAR RESET BUTTON
       ========================================= */

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 40px;
        border-radius: 7px;
        font-size: 13px;
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

df = conn.query(
    "SELECT * FROM financial_metrics",
    ttl=0
)

df["fiscal_date"] = pd.to_datetime(
    df["fiscal_date"]
)


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

filtered_df = filtered_df.sort_values(
    "fiscal_date"
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
# HEADER
# ============================================================

st.title("Executive Overview")

st.caption(
    "A high-level view of company growth, profitability, "
    "cash generation, and financial strength."
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

avg_revenue_growth = latest_df[
    "revenue_growth"
].mean()

avg_profit_margin = latest_df[
    "net_profit_margin"
].mean()

positive_fcf_count = (
    latest_df["free_cash_flow"] > 0
).sum()

total_companies = len(latest_df)


# ============================================================
# KPI SUMMARY
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Companies Selected</div>
            <div class="kpi-value">{total_companies}</div>
            <div class="kpi-description">
                Companies currently included
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Revenue Growth</div>
            <div class="kpi-value">{avg_revenue_growth:.2f}%</div>
            <div class="kpi-description">
                Latest reported growth
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Profit Margin</div>
            <div class="kpi-value">{avg_profit_margin:.2f}%</div>
            <div class="kpi-description">
                Latest net profit margin
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Positive Free Cash Flow</div>
            <div class="kpi-value">{positive_fcf_count}/{total_companies}</div>
            <div class="kpi-description">
                Companies generating positive FCF
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# COMPANY PERFORMANCE
# ============================================================

st.subheader("Company Performance")

st.caption(
    "Compare the latest growth and profitability metrics across "
    "the selected companies."
)

col1, col2 = st.columns(2)


# ============================================================
# REVENUE GROWTH
# ============================================================

with col1:

    growth_chart = latest_df[
        ["symbol", "revenue_growth"]
    ].sort_values(
        "revenue_growth",
        ascending=False
    )

    fig_growth = px.bar(
        growth_chart,
        x="symbol",
        y="revenue_growth",
        text="revenue_growth",
        title="Revenue Growth",
        labels={
            "symbol": "Company",
            "revenue_growth": "Growth (%)"
        },
        template="plotly_white"
    )

    fig_growth.update_traces(
        marker_color="#5B6FE8",
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Revenue Growth: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig_growth.update_layout(
        height=300,
        margin=dict(
            l=45,
            r=20,
            t=50,
            b=40
        ),
        showlegend=False,
        font=dict(
            color="#344054",
            family="Arial"
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
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
# NET PROFIT MARGIN
# ============================================================

with col2:

    margin_chart = latest_df[
        ["symbol", "net_profit_margin"]
    ].sort_values(
        "net_profit_margin",
        ascending=False
    )

    fig_margin = px.bar(
        margin_chart,
        x="symbol",
        y="net_profit_margin",
        text="net_profit_margin",
        title="Net Profit Margin",
        labels={
            "symbol": "Company",
            "net_profit_margin": "Margin (%)"
        },
        template="plotly_white"
    )

    fig_margin.update_traces(
        marker_color="#6FA8DC",
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Net Profit Margin: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig_margin.update_layout(
        height=300,
        margin=dict(
            l=45,
            r=20,
            t=50,
            b=40
        ),
        showlegend=False,
        font=dict(
            color="#344054",
            family="Arial"
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            gridcolor="#E4E7EC",
            zerolinecolor="#D0D5DD"
        )
    )

    st.plotly_chart(
        fig_margin,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


# ============================================================
# PROFITABILITY VS CAPITAL EFFICIENCY
# ============================================================

st.subheader("Profitability vs Capital Efficiency")

st.caption(
    "Compare profitability with returns generated from shareholder "
    "equity. Bubble size represents free cash flow."
)

scatter_df = latest_df.copy()

scatter_df["fcf_size"] = (
    scatter_df["free_cash_flow"]
    .abs()
    .clip(lower=1)
)

fig_scatter = px.scatter(
    scatter_df,
    x="net_profit_margin",
    y="roe",
    size="fcf_size",
    hover_name="symbol",
    text="symbol",
    labels={
        "net_profit_margin": "Net Profit Margin (%)",
        "roe": "ROE (%)",
        "fcf_size": "Free Cash Flow"
    },
    template="plotly_white"
)

fig_scatter.update_traces(
    textposition="top center",
    marker=dict(
        color="#6C7CE5",
        opacity=0.75,
        line=dict(
            width=1,
            color="#FFFFFF"
        )
    ),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "Net Profit Margin: %{x:.2f}%<br>"
        "ROE: %{y:.2f}%<br>"
        "Free Cash Flow: $%{marker.size:,.0f}"
        "<extra></extra>"
    )
)

fig_scatter.update_layout(
    height=350,
    margin=dict(
        l=50,
        r=30,
        t=25,
        b=45
    ),
    font=dict(
        color="#344054",
        family="Arial"
    ),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    xaxis=dict(
        gridcolor="#E4E7EC",
        zerolinecolor="#D0D5DD"
    ),
    yaxis=dict(
        gridcolor="#E4E7EC",
        zerolinecolor="#D0D5DD"
    )
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "displaylogo": False
    }
)


# ============================================================
# FINANCIAL TREND
# ============================================================

st.subheader("Financial Trend")

st.caption(
    "Track how revenue and net income have changed over time."
)

trend_company = st.selectbox(
    "Select Company",
    sorted(filtered_df["symbol"].unique()),
    key="executive_trend_company"
)

trend_df = filtered_df[
    filtered_df["symbol"] == trend_company
].sort_values(
    "fiscal_date"
)


# ============================================================
# REVENUE + NET INCOME
# ============================================================

col1, col2 = st.columns(2)


with col1:

    fig_revenue = px.area(
        trend_df,
        x="fiscal_date",
        y="total_revenue",
        title="Revenue Trend",
        labels={
            "fiscal_date": "Fiscal Year",
            "total_revenue": "Revenue"
        },
        template="plotly_white"
    )

    fig_revenue.update_traces(
        line_color="#4F81BD",
        fillcolor="rgba(79,129,189,0.18)",
        hovertemplate=(
            "<b>%{x|%Y}</b><br>"
            "Revenue: $%{y:,.0f}"
            "<extra></extra>"
        )
    )

    fig_revenue.update_layout(
        height=300,
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
            gridcolor="#E4E7EC"
        )
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


with col2:

    fig_income = px.line(
        trend_df,
        x="fiscal_date",
        y="net_income",
        markers=True,
        title="Net Income Trend",
        labels={
            "fiscal_date": "Fiscal Year",
            "net_income": "Net Income"
        },
        template="plotly_white"
    )

    fig_income.update_traces(
        line=dict(
            color="#6C7CE5",
            width=2.5
        ),
        marker=dict(
            size=7
        ),
        hovertemplate=(
            "<b>%{x|%Y}</b><br>"
            "Net Income: $%{y:,.0f}"
            "<extra></extra>"
        )
    )

    fig_income.update_layout(
        height=300,
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
            gridcolor="#E4E7EC"
        )
    )

    st.plotly_chart(
        fig_income,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


# ============================================================
# PROFITABILITY TREND + CASH GENERATION
# ============================================================

col1, col2 = st.columns(2)


# ============================================================
# PROFITABILITY TREND
# ============================================================

with col1:

    st.markdown("#### Profitability Trend")

    st.caption(
            "Profitability metrics by each selected company."
        )

    profitability_df = trend_df[
        [
            "fiscal_date",
            "net_profit_margin",
            "operating_margin"
        ]
    ].copy()

    fig_profitability = px.line(
        profitability_df,
        x="fiscal_date",
        y=[
            "net_profit_margin",
            "operating_margin"
        ],
        markers=True,
        labels={
            "fiscal_date": "Fiscal Year",
            "value": "Margin (%)",
            "variable": "Metric"
        },
        template="plotly_white"
    )

    fig_profitability.update_traces(
        hovertemplate=(
            "<b>%{x|%Y}</b><br>"
            "%{fullData.name}: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig_profitability.update_layout(
        height=300,
        margin=dict(
            l=45,
            r=20,
            t=20,
            b=40
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
            gridcolor="#E4E7EC"
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
# CASH GENERATION
# ============================================================

with col2:

    st.markdown("#### Cash Generation")

    st.caption(
        "Latest free cash flow generated by each selected company."
    )

    fcf_df = latest_df[
        ["symbol", "free_cash_flow"]
    ].sort_values(
        "free_cash_flow",
        ascending=True
    )

    fig_fcf = px.bar(
        fcf_df,
        x="free_cash_flow",
        y="symbol",
        orientation="h",
        text="free_cash_flow",
        labels={
            "free_cash_flow": "Free Cash Flow",
            "symbol": "Company"
        },
        template="plotly_white"
    )

    fig_fcf.update_traces(
        marker_color="#7A9CC6",
        texttemplate="$%{x:.3s}",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Free Cash Flow: $%{x:,.0f}"
            "<extra></extra>"
        )
    )

    fig_fcf.update_layout(
        height=300,
        margin=dict(
            l=35,
            r=55,
            t=20,
            b=40
        ),
        showlegend=False,
        font=dict(
            color="#344054",
            family="Arial"
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(
            gridcolor="#E4E7EC"
        ),
        yaxis=dict(
            gridcolor="#EEF0F3"
        )
    )

    st.plotly_chart(
        fig_fcf,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


# ============================================================
# EXECUTIVE TAKEAWAY
# ============================================================

st.subheader("Executive Takeaway")

best_growth = latest_df.loc[
    latest_df["revenue_growth"].idxmax()
]

best_margin = latest_df.loc[
    latest_df["net_profit_margin"].idxmax()
]

best_roe = latest_df.loc[
    latest_df["roe"].idxmax()
]

st.info(
    f"""
    **{best_growth["symbol"]}** currently leads the selected companies
    in revenue growth at **{best_growth["revenue_growth"]:.2f}%**.

    **{best_margin["symbol"]}** has the strongest net profit margin
    at **{best_margin["net_profit_margin"]:.2f}%**.

    **{best_roe["symbol"]}** currently has the highest ROE
    at **{best_roe["roe"]:.2f}%**.
    """
)