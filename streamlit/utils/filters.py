import streamlit as st


# ============================================================
# GLOBAL COMPANY FILTER
# ============================================================

def company_filter(df):

    # --------------------------------------------------------
    # Get available companies
    # --------------------------------------------------------

    companies = sorted(
        df["symbol"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    # --------------------------------------------------------
    # Create persistent session-state variable
    # --------------------------------------------------------

    if "selected_companies" not in st.session_state:

        # Default selection when dashboard first opens
        st.session_state["selected_companies"] = companies.copy()


    # --------------------------------------------------------
    # Make sure saved companies still exist in current data
    # --------------------------------------------------------

    st.session_state["selected_companies"] = [
        company
        for company in st.session_state["selected_companies"]
        if company in companies
    ]


    # --------------------------------------------------------
    # Sidebar
    # --------------------------------------------------------

    st.sidebar.subheader("Dashboard Filters")

    st.sidebar.markdown(
        "Select Companies"
    )


    # --------------------------------------------------------
    # Callback when user changes selection
    # --------------------------------------------------------

    def update_company_selection():

        st.session_state["selected_companies"] = (
            st.session_state["company_filter_widget"]
        )


    # --------------------------------------------------------
    # Company multiselect
    # --------------------------------------------------------

    st.sidebar.multiselect(
        label="",
        options=companies,
        key="company_filter_widget",
        default=st.session_state["selected_companies"],
        on_change=update_company_selection
    )


    # --------------------------------------------------------
    # Reset button
    # --------------------------------------------------------

    if st.sidebar.button(
        "Reset Company Filter",
        use_container_width=True
    ):

        st.session_state["selected_companies"] = companies.copy()

        # Update widget value immediately
        st.session_state["company_filter_widget"] = companies.copy()

        st.rerun()


    # --------------------------------------------------------
    # Return persistent selection
    # --------------------------------------------------------

    return st.session_state["selected_companies"]