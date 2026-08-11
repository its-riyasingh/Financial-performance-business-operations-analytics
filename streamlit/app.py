import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Financial Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HOME PAGE
# ============================================================

def render_home():

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        """
<div class="hero-box">
<div class="hero-title">Financial Performance &amp; Business Operations Analytics</div>
<div class="hero-subtitle">A structured financial analytics dashboard for evaluating company performance, growth, profitability, cash generation, capital efficiency, and overall financial health.</div>
</div>
""",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # FINANCIAL ANALYTICS HUB
    # --------------------------------------------------------

    st.markdown(
        """
<div class="section-title">Financial Analytics Hub</div>
<div class="section-description">Explore the different analytical views available in the dashboard and compare financial performance across selected companies.</div>
""",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # DASHBOARD COVERAGE
    # --------------------------------------------------------

    st.markdown(
        """
<div class="section-title">Dashboard Coverage</div>
<div class="section-description">Each section focuses on a different aspect of financial analysis.</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # ROW 1
    # ========================================================

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
<div class="dashboard-card card-blue">
<div class="card-title">Executive Overview</div>
<div class="card-description">Compare selected companies at a high level using revenue growth, profit margins, free cash flow, and capital-efficiency indicators.</div>
</div>
""",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
<div class="dashboard-card card-green">
<div class="card-title">Performance &amp; Growth</div>
<div class="card-description">Identify growth leaders, compare revenue and net-income growth, and examine historical growth trends over time.</div>
</div>
""",
            unsafe_allow_html=True
        )


    # ========================================================
    # ROW 2
    # ========================================================

    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.markdown(
            """
<div class="dashboard-card card-purple">
<div class="card-title">Profitability Health</div>
<div class="card-description">Evaluate net profit margin, operating margin, ROE, ROA, and other indicators of profitability and capital efficiency.</div>
</div>
""",
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            """
<div class="dashboard-card card-orange">
<div class="card-title">Company Deep Dive</div>
<div class="card-description">Select an individual company and examine its financial snapshot, historical performance, growth, profitability, and capital-efficiency trends.</div>
</div>
""",
            unsafe_allow_html=True
        )


    # ========================================================
    # ROW 3
    # ========================================================

    st.markdown(
        """
<div class="dashboard-card card-teal">
<div class="card-title">Financial Insights</div>
<div class="card-description">Review predefined analytical rules that summarize financial health, highlight strengths and potential risks, and provide an analyst-oriented view of the selected companies.</div>
</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # INFORMATION BOX
    # ========================================================

    st.markdown(
        """
<div class="info-box">Select a page from the sidebar to begin your analysis.</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # FOOTER
    # ========================================================

    st.markdown(
        """
<div class="footer">This dashboard is designed for financial analysis and demonstration purposes. Insights are based on the project's financial dataset and predefined analytical calculations.</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# NAVIGATION
# ============================================================

home_page = st.Page(
    render_home,
    title="Home",
    default=True
)

executive_page = st.Page(
    "pages/1_Executive_Overview.py",
    title="Executive Overview"
)

growth_page = st.Page(
    "pages/2_Performance_Growth.py",
    title="Performance & Growth"
)

profitability_page = st.Page(
    "pages/3_Profitability_Health.py",
    title="Profitability Health"
)

company_page = st.Page(
    "pages/4_Company_Deep_Dive.py",
    title="Company Deep Dive"
)

insights_page = st.Page(
    "pages/5_Financial_Insights.py",
    title="Financial Insights"
)


pg = st.navigation(
    [
        home_page,
        executive_page,
        growth_page,
        profitability_page,
        company_page,
        insights_page
    ]
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

.stApp {
    background:
        radial-gradient(
            circle at 85% 5%,
            rgba(31, 78, 121, 0.08),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #F5F8FC 0%,
            #EEF3F8 50%,
            #F8FAFC 100%
        );
}

.main .block-container {
    max-width: 1450px;
    padding-top: 3rem;
    padding-bottom: 4rem;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #F4F7FB 100%
        );

    border-right: 1px solid #D7E0EA;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}


/* ============================================================
   HERO
   ============================================================ */

.hero-box {
    background:
        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #EEF5FC 55%,
            #E5EFF9 100%
        );

    border: 1px solid #C9D9E8;
    border-radius: 18px;

    padding: 42px 46px;
    margin-bottom: 38px;

    box-shadow:
        0 8px 25px rgba(31, 78, 121, 0.08);
}

.hero-title {
    color: #173B63;
    font-size: 38px;
    font-weight: 750;
    line-height: 1.2;
    margin-bottom: 14px;
}

.hero-subtitle {
    color: #536B83;
    font-size: 16px;
    line-height: 1.7;
    max-width: 950px;
}


/* ============================================================
   SECTION HEADINGS
   ============================================================ */

.section-title {
    color: #173B63;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 6px;
}

.section-description {
    color: #6B7C8F;
    font-size: 14px;
    margin-bottom: 22px;
}


/* ============================================================
   DASHBOARD CARDS
   ============================================================ */

.dashboard-card {
    min-height: 190px;

    border-radius: 15px;

    padding: 25px 26px;

    margin-bottom: 18px;

    border: 1px solid #D5E0EA;

    box-shadow:
        0 5px 16px rgba(31, 78, 121, 0.06);

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease;
}

.dashboard-card:hover {
    transform: translateY(-2px);

    box-shadow:
        0 9px 24px rgba(31, 78, 121, 0.11);
}


/* ============================================================
   CARD COLORS
   ============================================================ */

.card-blue {
    background:
        linear-gradient(
            135deg,
            #FFFFFF,
            #EDF5FD
        );

    border-left: 5px solid #3B82C4;
}

.card-green {
    background:
        linear-gradient(
            135deg,
            #FFFFFF,
            #EEF8F5
        );

    border-left: 5px solid #3A9B78;
}

.card-purple {
    background:
        linear-gradient(
            135deg,
            #FFFFFF,
            #F4F1FB
        );

    border-left: 5px solid #8064A2;
}

.card-orange {
    background:
        linear-gradient(
            135deg,
            #FFFFFF,
            #FFF6EA
        );

    border-left: 5px solid #D99135;
}

.card-teal {
    background:
        linear-gradient(
            135deg,
            #FFFFFF,
            #ECF8F8
        );

    border-left: 5px solid #3C9292;
}


/* ============================================================
   CARD TEXT
   ============================================================ */

.card-title {
    color: #173B63;
    font-size: 19px;
    font-weight: 700;
    margin-bottom: 12px;
}

.card-description {
    color: #5E7083;
    font-size: 14px;
    line-height: 1.7;
}


/* ============================================================
   INFORMATION BOX
   ============================================================ */

.info-box {
    background:
        linear-gradient(
            135deg,
            #EAF3FC,
            #F4F8FC
        );

    border: 1px solid #C9DCEB;

    border-radius: 12px;

    padding: 18px 22px;

    margin-top: 18px;

    color: #28577F;

    font-size: 14px;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {
    margin-top: 38px;

    padding-top: 20px;

    border-top: 1px solid #D9E1E9;

    color: #8A98A8;

    font-size: 12px;

    line-height: 1.6;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR BRANDING
# ============================================================

with st.sidebar:

    st.markdown(
        """
<div style="font-size:21px;font-weight:700;color:#173B63;margin-bottom:10px;">
Financial Analytics
</div>
""",
        unsafe_allow_html=True
    )

    st.caption(
        "Financial performance and business operations dashboard"
    )


# ============================================================
# RUN APP
# ============================================================

pg.run()