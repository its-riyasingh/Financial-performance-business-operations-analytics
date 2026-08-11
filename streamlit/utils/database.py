import streamlit as st


@st.cache_resource
def get_connection():
    return st.connection("postgresql", type="sql")


@st.cache_data(ttl=300)
def load_financial_data():
    conn = get_connection()

    df = conn.query(
        "SELECT * FROM financial_metrics",
        ttl=300
    )

    return df