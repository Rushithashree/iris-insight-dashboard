
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Iris Insight | Analytics Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# PROFESSIONAL LIGHT THEME
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F7FA;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5EAF0;
    }

    .main-title {
        font-size: 30px;
        font-weight: 700;
        color: #183153;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 14px;
        color: #64748B;
        margin-top: 5px;
    }

    .section-title {
        color: #183153;
        font-size: 20px;
        font-weight: 650;
    }

    .info-card {
        background-color: #FFFFFF;
        border: 1px solid #E3E9F0;
        border-radius: 12px;
        padding: 18px;
        min-height: 105px;
    }

    .info-label {
        color: #64748B;
        font-size: 13px;
    }

    .info-value {
        color: #183153;
        font-size: 23px;
        font-weight: 700;
        margin-top: 8px;
    }

    .status-text {
        color: #64748B;
        font-size: 12px;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E3E9F0;
        border-radius: 12px;
        padding: 16px;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# APPLICATION IDENTITY
# --------------------------------------------------

st.sidebar.markdown(
    """
    <div style="padding: 12px 5px 20px 5px;">
        <div style="font-size: 25px; font-weight: 750;
                    color: #183153;">
            🌿 IRIS INSIGHT
        </div>
        <div style="font-size: 11px; color: #64748B;
                    letter-spacing: 1px;">
            ANALYTICS INTELLIGENCE PLATFORM
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

pages = [
    "Overview",
    "Species Analytics",
    "Ask Iris",
    "Specimen Explorer",
    "Quality Intelligence",
    "Report Centre"
]

selected_page = st.sidebar.radio(
    "WORKSPACE NAVIGATION",
    pages,
    index=0
)

st.sidebar.divider()

st.sidebar.markdown("**PROJECT INFORMATION**")
st.sidebar.caption("Dataset: UCI Iris")
st.sidebar.caption("Database: iris_analytics_db")
st.sidebar.caption("Measurements: 4")
st.sidebar.caption("Species groups: 3")

st.sidebar.divider()

st.sidebar.markdown(
    """
    <div class="status-text">
        IRIS INSIGHT<br>
        Scientific Data Analytics<br>
        Version 1.0
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">Iris Insight</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Species Measurement and Analytics Intelligence Platform'
    '</div>',
    unsafe_allow_html=True
)

st.write("")

# --------------------------------------------------
# PAGE 1: OVERVIEW
# --------------------------------------------------

if selected_page == "Overview":

    st.markdown("## Analytics Overview")

    st.caption(
        "A consolidated workspace for exploring "
        "Iris specimen measurements and species-level patterns."
    )

    st.info(
        "The database-backed KPI cards and analytical "
        "visualizations will be connected in Stage 3.2."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Specimens", "Awaiting data")

    with col2:
        st.metric("Species Groups", "Awaiting data")

    with col3:
        st.metric("Measurement Variables", "4")

    with col4:
        st.metric("Verified SQL Reports", "10")

    st.markdown("### Analytical Workspace")

    left, right = st.columns(2)

    with left:
        st.markdown("**Species Distribution**")
        st.info("Species distribution chart will appear here.")

    with right:
        st.markdown("**Measurement Overview**")
        st.info("Measurement comparison chart will appear here.")

    st.markdown("### Recent Analytical Findings")
    st.info(
        "Automatically calculated statistical findings "
        "will appear here after the analytics engine is connected."
    )

# --------------------------------------------------
# PAGE 2: SPECIES ANALYTICS
# --------------------------------------------------

elif selected_page == "Species Analytics":

    st.markdown("## Species Analytics")

    st.caption(
        "Compare measurement characteristics across "
        "the three Iris species."
    )

    st.info(
        "This section will contain species averages, "
        "measurement distributions, standard deviations "
        "and interactive Plotly charts."
    )

# --------------------------------------------------
# PAGE 3: ASK IRIS
# --------------------------------------------------

elif selected_page == "Ask Iris":

    st.markdown("## Ask Iris")

    st.caption(
        "Explore your scientific dataset using natural-language questions."
    )

    st.markdown("### What would you like to investigate?")

    question = st.text_area(
        "Enter your analytical question",
        placeholder=(
            "Example: Which species has the highest "
            "average petal length?"
        ),
        height=110
    )

    st.button(
        "Interpret Question",
        disabled=True,
        help="The query intelligence engine will be implemented in Stage 3.6."
    )

    st.markdown("### How the query engine will work")

    st.write("1. Interpret the question.")
    st.write("2. Identify measurements and analytical conditions.")
    st.write("3. Generate a parameterized SQL query.")
    st.write("4. Validate SQL safety and query structure.")
    st.write("5. Execute against the MySQL database.")
    st.write("6. Present verified results and explanations.")

    st.caption(
        "Natural-language execution is not enabled yet."
    )

# --------------------------------------------------
# PAGE 4: SPECIMEN EXPLORER
# --------------------------------------------------

elif selected_page == "Specimen Explorer":

    st.markdown("## Specimen Explorer")

    st.caption(
        "Explore individual specimen records using "
        "measurement-based filters."
    )

    st.info(
        "Interactive species selection, measurement ranges, "
        "specimen tables and individual record inspection "
        "will be implemented in Stage 3.4."
    )

# --------------------------------------------------
# PAGE 5: QUALITY INTELLIGENCE
# --------------------------------------------------

elif selected_page == "Quality Intelligence":

    st.markdown("## Data Quality Intelligence")

    st.caption(
        "Inspect data integrity, duplicate measurements "
        "and import validation results."
    )

    st.info(
        "Quality summaries, duplicate-group inspection, "
        "validation statistics and import history "
        "will be connected in Stage 3.5."
    )

# --------------------------------------------------
# PAGE 6: REPORT CENTRE
# --------------------------------------------------

elif selected_page == "Report Centre":

    st.markdown("## Report Centre")

    st.caption(
        "Access the ten verified analytical SQL reports "
        "and their exported results."
    )

    st.info(
        "The existing R01-R10 report engine and CSV exports "
        "will be integrated in a later stage."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "IRIS INSIGHT | Scientific Measurement Analytics | "
    "MySQL + Python + Streamlit + Plotly"
)
