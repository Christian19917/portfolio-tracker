import streamlit as st



st.set_page_config(
    page_title="Portfolio Tracker",
    page_icon="📈",
    layout="wide",
)

pages = [
    st.Page(
        "pages/overview.py",
        title="Overview",
        icon="🏠",
        default=True,
    ),
    st.Page(
        "pages/performance.py",
        title="Performance",
        icon="📈",
    ),
    st.Page(
        "pages/allocation.py",
        title="Allocation",
        icon="🥧",
    ),
    st.Page(
        "pages/transactions.py",
        title="Transactions",
        icon="💳",
    ),    
]

navigation = st.navigation(
    pages,
    position="sidebar",
)

navigation.run()