import streamlit as st
import pandas as pd
import plotly.express as px

from utils.filters import company_filter


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Profitability Health",
    page_icon=None,
    layout="wide"
)


# ============================================================
# PAGE STYLING
# Global background/theme is controlled by config.toml
# ============================================================

st.markdown(
    """
    <style>

    /* Main content spacing */
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

    /* Small section descriptions */
    .section-description {
        color: #667085;
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 12px;
    }


    /* ============================================================
       PROFITABILITY KPI CARDS
       ============================================================ */

    .profitability-kpi-card {
        background: linear-gradient(
            135deg,
            #FFFFFF 0%,
            #F3F7FC 100%
        );
        border: 1px solid #D9E3EF;
        border-radius: 10px;
        padding: 18px 20px 16px 20px;
        min-height: 115px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
        margin-bottom: 18px;
    }

    .profitability-kpi-title {
        color: #52627A;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .profitability-kpi-value {
        color: #142B49;
        font-size: 30px;
        font-weight: 600;
        line-height: 1.1;
        margin-bottom: 9px;
    }

    .profitability-kpi-delta {
        display: inline-block;
        background: #E6F5EE;
        color: #17804D;
        border-radius: 999px;
        padding: 3px 9px;
        font-size: 12px;
        font-weight: 500;
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
# LATEST FINANCIAL DATA
# ============================================================

latest_df = (
    filtered_df
    .sort_values("fiscal_date")
    .groupby("symbol")
    .tail(1)
    .copy()
)


if latest_df.empty:
    st.warning(
        "No financial data is available for the selected companies."
    )
    st.stop()


# ============================================================
# HELPER FUNCTION
# ============================================================

def safe_idxmax(dataframe, column):
    """
    Safely return the index of the maximum valid value.
    """

    valid = dataframe[column].dropna()

    if valid.empty:
        return None

    return valid.idxmax()


def format_currency_billions(value):
    """
    Format large financial values into readable billions.
    """

    if pd.isna(value):
        return "N/A"

    return f"${value / 1_000_000_000:,.2f}B"


# ============================================================
# HEADER
# ============================================================

st.title("Profitability Health")

st.caption(
    "Are companies converting revenue into profit efficiently, "
    "and are they generating strong returns from their resources?"
)


# ============================================================
# PROFITABILITY LEADERS
# ============================================================

st.subheader("Profitability Leaders")

margin_idx = safe_idxmax(
    latest_df,
    "net_profit_margin"
)

operating_idx = safe_idxmax(
    latest_df,
    "operating_margin"
)

roe_idx = safe_idxmax(
    latest_df,
    "roe"
)

roa_idx = safe_idxmax(
    latest_df,
    "roa"
)


# ------------------------------------------------------------
# KPI CARD HELPER
# ------------------------------------------------------------

def profitability_kpi_card(title, value, delta=None):

    delta_html = ""

    if delta is not None:
        delta_html = (
            f'<div class="profitability-kpi-delta">'
            f'↑ {delta}'
            f'</div>'
        )

    html = (
        '<div class="profitability-kpi-card">'
        f'<div class="profitability-kpi-title">{title}</div>'
        f'<div class="profitability-kpi-value">{value}</div>'
        f'{delta_html}'
        '</div>'
    )

    st.html(html)


# ------------------------------------------------------------
# KPI CARDS
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    if margin_idx is not None:
        highest_margin = latest_df.loc[margin_idx]
        profitability_kpi_card(
            "Best Net Profit Margin",
            highest_margin["symbol"],
            f'{highest_margin["net_profit_margin"]:.2f}%'
        )
    else:
        profitability_kpi_card(
            "Best Net Profit Margin",
            "N/A"
        )

with col2:
    if operating_idx is not None:
        highest_operating = latest_df.loc[operating_idx]
        profitability_kpi_card(
            "Best Operating Margin",
            highest_operating["symbol"],
            f'{highest_operating["operating_margin"]:.2f}%'
        )
    else:
        profitability_kpi_card(
            "Best Operating Margin",
            "N/A"
        )

with col3:
    if roe_idx is not None:
        highest_roe = latest_df.loc[roe_idx]
        profitability_kpi_card(
            "Highest ROE",
            highest_roe["symbol"],
            f'{highest_roe["roe"]:.2f}%'
        )
    else:
        profitability_kpi_card(
            "Highest ROE",
            "N/A"
        )

with col4:
    if roa_idx is not None:
        highest_roa = latest_df.loc[roa_idx]
        profitability_kpi_card(
            "Highest ROA",
            highest_roa["symbol"],
            f'{highest_roa["roa"]:.2f}%'
        )
    else:
        profitability_kpi_card(
            "Highest ROA",
            "N/A"
        )


# ============================================================
# PROFITABILITY COMPARISON
# ============================================================

st.subheader("Profitability Comparison")

st.markdown(
    """
    <div class="section-description">
        Compare the latest net profit margin and operating margin
        across the selected companies.
    </div>
    """,
    unsafe_allow_html=True
)


profitability_data = latest_df[
    [
        "symbol",
        "net_profit_margin",
        "operating_margin"
    ]
].copy()


profitability_long = profitability_data.melt(
    id_vars="symbol",
    value_vars=[
        "net_profit_margin",
        "operating_margin"
    ],
    var_name="Metric",
    value_name="Margin"
)


profitability_long["Metric"] = profitability_long[
    "Metric"
].map({
    "net_profit_margin": "Net Profit Margin",
    "operating_margin": "Operating Margin"
})


fig_profitability = px.bar(
    profitability_long,
    x="symbol",
    y="Margin",
    color="Metric",
    barmode="group",
    text="Margin",
    labels={
        "symbol": "Company",
        "Margin": "Margin (%)",
        "Metric": "Metric"
    },
    template="plotly_white"
)


fig_profitability.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "%{fullData.name}: %{y:.2f}%"
        "<extra></extra>"
    )
)


fig_profitability.update_layout(
    height=350,
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
        title="Margin (%)",
        gridcolor="#E4E7EC",
        zerolinecolor="#D0D5DD"
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
        Compare returns generated from shareholder equity and
        total assets across the selected companies.
    </div>
    """,
    unsafe_allow_html=True
)


capital_data = latest_df[
    [
        "symbol",
        "roe",
        "roa"
    ]
].copy()


capital_long = capital_data.melt(
    id_vars="symbol",
    value_vars=[
        "roe",
        "roa"
    ],
    var_name="Metric",
    value_name="Return"
)


capital_long["Metric"] = capital_long[
    "Metric"
].map({
    "roe": "ROE",
    "roa": "ROA"
})


fig_capital = px.bar(
    capital_long,
    x="symbol",
    y="Return",
    color="Metric",
    barmode="group",
    text="Return",
    labels={
        "symbol": "Company",
        "Return": "Return (%)",
        "Metric": "Metric"
    },
    template="plotly_white"
)


fig_capital.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "%{fullData.name}: %{y:.2f}%"
        "<extra></extra>"
    )
)


fig_capital.update_layout(
    height=350,
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
        title="Return (%)",
        gridcolor="#E4E7EC",
        zerolinecolor="#D0D5DD"
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


st.caption(
    "Higher ROE and ROA generally indicate stronger capital efficiency. "
    "However, unusually high ROE should be interpreted alongside ROA "
    "and the company's capital structure."
)


# ============================================================
# PROFITABILITY SCORECARD
# ============================================================

st.subheader("Profitability Scorecard")


scorecard = latest_df[
    [
        "symbol",
        "net_profit_margin",
        "operating_margin",
        "roe",
        "roa",
        "free_cash_flow"
    ]
].copy()


scorecard = scorecard.sort_values(
    "net_profit_margin",
    ascending=False
)


scorecard.columns = [
    "Company",
    "Net Profit Margin (%)",
    "Operating Margin (%)",
    "ROE (%)",
    "ROA (%)",
    "Free Cash Flow"
]


st.dataframe(
    scorecard,
    use_container_width=True,
    hide_index=True,
    column_config={

        "Net Profit Margin (%)":
            st.column_config.NumberColumn(
                "Net Profit Margin (%)",
                format="%.2f%%"
            ),

        "Operating Margin (%)":
            st.column_config.NumberColumn(
                "Operating Margin (%)",
                format="%.2f%%"
            ),

        "ROE (%)":
            st.column_config.NumberColumn(
                "ROE (%)",
                format="%.2f%%"
            ),

        "ROA (%)":
            st.column_config.NumberColumn(
                "ROA (%)",
                format="%.2f%%"
            ),

        "Free Cash Flow":
            st.column_config.NumberColumn(
                "Free Cash Flow",
                format="$%.0f"
            )
    }
)


# ============================================================
# PROFITABILITY TREND
# ============================================================

st.subheader("Profitability Trend")

st.markdown(
    """
    <div class="section-description">
        Track profitability and capital efficiency over time
        for an individual company.
    </div>
    """,
    unsafe_allow_html=True
)


trend_company = st.selectbox(
    "Select Company",
    sorted(
        filtered_df["symbol"]
        .dropna()
        .unique()
    ),
    key="profitability_trend_company"
)


trend_df = (
    filtered_df[
        filtered_df["symbol"] == trend_company
    ]
    .sort_values("fiscal_date")
    .copy()
)


# ============================================================
# YEARLY DATA
# ============================================================

trend_df["year"] = (
    trend_df["fiscal_date"]
    .dt.year
)


trend_yearly = (
    trend_df
    .sort_values("fiscal_date")
    .groupby("year")
    .tail(1)
    .sort_values("year")
    .copy()
)


trend_yearly["Year"] = (
    trend_yearly["year"]
    .astype(str)
)


# ============================================================
# TWO TREND CHARTS SIDE BY SIDE
# ============================================================

col1, col2 = st.columns(2)


# ============================================================
# MARGIN EVOLUTION
# ============================================================

with col1:

    margin_trend = trend_yearly[
        [
            "Year",
            "net_profit_margin",
            "operating_margin"
        ]
    ].copy()


    margin_long = margin_trend.melt(
        id_vars="Year",
        value_vars=[
            "net_profit_margin",
            "operating_margin"
        ],
        var_name="Metric",
        value_name="Margin"
    )


    margin_long["Metric"] = margin_long[
        "Metric"
    ].map({
        "net_profit_margin": "Net Profit Margin",
        "operating_margin": "Operating Margin"
    })


    fig_margin_trend = px.line(
        margin_long,
        x="Year",
        y="Margin",
        color="Metric",
        markers=True,
        labels={
            "Year": "Fiscal Year",
            "Margin": "Margin (%)",
            "Metric": "Metric"
        },
        title=f"{trend_company} — Margin Evolution",
        template="plotly_white"
    )


    fig_margin_trend.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{fullData.name}: %{y:.2f}%"
            "<extra></extra>"
        )
    )


    fig_margin_trend.update_layout(
        height=330,
        margin=dict(
            l=45,
            r=20,
            t=55,
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
            gridcolor="#E4E7EC",
            zerolinecolor="#D0D5DD"
        )
    )


    st.plotly_chart(
        fig_margin_trend,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


# ============================================================
# ROE / ROA TREND
# ============================================================

with col2:

    return_trend = trend_yearly[
        [
            "Year",
            "roe",
            "roa"
        ]
    ].copy()


    return_long = return_trend.melt(
        id_vars="Year",
        value_vars=[
            "roe",
            "roa"
        ],
        var_name="Metric",
        value_name="Return"
    )


    return_long["Metric"] = return_long[
        "Metric"
    ].map({
        "roe": "ROE",
        "roa": "ROA"
    })


    fig_return_trend = px.line(
        return_long,
        x="Year",
        y="Return",
        color="Metric",
        markers=True,
        labels={
            "Year": "Fiscal Year",
            "Return": "Return (%)",
            "Metric": "Metric"
        },
        title=f"{trend_company} — Return on Capital",
        template="plotly_white"
    )


    fig_return_trend.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{fullData.name}: %{y:.2f}%"
            "<extra></extra>"
        )
    )


    fig_return_trend.update_layout(
        height=330,
        margin=dict(
            l=45,
            r=20,
            t=55,
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
            title="Return (%)",
            gridcolor="#E4E7EC",
            zerolinecolor="#D0D5DD"
        )
    )


    st.plotly_chart(
        fig_return_trend,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False
        }
    )


# ============================================================
# PROFITABILITY STORY
# ============================================================

st.subheader("Profitability Story")


avg_margin = latest_df[
    "net_profit_margin"
].mean()


avg_operating = latest_df[
    "operating_margin"
].mean()


avg_roe = latest_df[
    "roe"
].mean()


avg_roa = latest_df[
    "roa"
].mean()


# ------------------------------------------------------------
# SAFE LEADERS
# ------------------------------------------------------------

if margin_idx is not None:

    margin_leader = highest_margin["symbol"]
    margin_value = highest_margin["net_profit_margin"]

else:

    margin_leader = "N/A"
    margin_value = None


if roe_idx is not None:

    roe_leader = highest_roe["symbol"]
    roe_value = highest_roe["roe"]

else:

    roe_leader = "N/A"
    roe_value = None


# ------------------------------------------------------------
# STORY
# ------------------------------------------------------------

if margin_value is not None:

    margin_sentence = (
        f"Among the selected companies, **{margin_leader}** "
        f"currently has the strongest net profit margin at "
        f"**{margin_value:.2f}%**. This means it retains the "
        f"largest proportion of revenue as bottom-line profit."
    )

else:

    margin_sentence = (
        "Net profit margin data is unavailable "
        "for the selected companies."
    )


if roe_value is not None:

    roe_sentence = (
        f"Meanwhile, **{roe_leader}** leads on ROE at "
        f"**{roe_value:.2f}%**. A very high ROE should be "
        f"interpreted alongside ROA and the company's capital "
        f"structure rather than treated as a standalone measure "
        f"of financial strength."
    )

else:

    roe_sentence = (
        "ROE data is unavailable for the selected companies."
    )


story = (
    f"{margin_sentence} "
    f"{roe_sentence} "
    f"Across the selected companies, average net profit margin "
    f"is **{avg_margin:.2f}%**, while average operating margin "
    f"is **{avg_operating:.2f}%**."
)


st.info(story)


# ============================================================
# ANALYST INTERPRETATION
# ============================================================

st.subheader("What should an analyst look for?")

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        """
        **Strong profitability signals**

        - High and stable net profit margin
        - High operating margin
        - Positive and growing free cash flow
        - Strong ROE
        - Strong ROA
        """
    )


with col2:

    st.markdown(
        """
        **Potential warning signals**

        - Falling profit margins
        - High ROE but weak ROA
        - Declining operating margin
        - Negative free cash flow
        - Large divergence between revenue growth and profit growth
        """
    )