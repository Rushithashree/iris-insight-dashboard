import streamlit as st
import pandas as pd
import plotly.express as px

from src.analytics.report_engine import (
    run_report,
    list_reports,
    test_database_connection,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Iris Insight | Analytics Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
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
        color: #475569;
        margin-top: 5px;
    }

    .section-title {
        color: #183153;
        font-size: 20px;
        font-weight: 650;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DCE3EB;
        border-radius: 12px;
        padding: 16px;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #334155 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #142B4A !important;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    [data-testid="stCaptionContainer"] {
        color: #475569;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# DATA ACCESS AND VALIDATION
# --------------------------------------------------

EXPECTED_DATABASE = "iris_analytics_db"

MEASUREMENT_REPORTS = {
    "R03": {
        "label": "Sepal Length",
        "column": "avg_sepal_length_cm",
    },
    "R04": {
        "label": "Sepal Width",
        "column": "avg_sepal_width_cm",
    },
    "R05": {
        "label": "Petal Length",
        "column": "avg_petal_length_cm",
    },
    "R06": {
        "label": "Petal Width",
        "column": "avg_petal_width_cm",
    },
}


@st.cache_data(ttl=60, show_spinner=False)
def load_overview_data():
    """
    Retrieve the Overview data from the live MySQL database.

    R01 supplies species counts.
    R03-R06 supply species-level mean measurements.
    The report registry supplies the number of available reports.
    """

    database_name = test_database_connection()

    if database_name != EXPECTED_DATABASE:
        raise RuntimeError(
            f"Connected to '{database_name}', "
            f"but expected '{EXPECTED_DATABASE}'."
        )

    # Species distribution
    species_data = run_report("R01")

    required_species_columns = {
        "species_id",
        "species_name",
        "specimen_count",
    }

    if not required_species_columns.issubset(species_data.columns):
        raise ValueError(
            "R01 returned unexpected columns. "
            f"Received: {list(species_data.columns)}"
        )

    if species_data.empty:
        raise ValueError("R01 returned no species records.")

    species_data = species_data.copy()
    species_data["specimen_count"] = pd.to_numeric(
        species_data["specimen_count"],
        errors="raise",
    )

    if species_data["specimen_count"].isna().any():
        raise ValueError("Species counts contain missing values.")

    if (species_data["specimen_count"] < 0).any():
        raise ValueError("Negative species counts were detected.")

    species_data["specimen_count"] = (
        species_data["specimen_count"].astype(int)
    )

    total_specimens = int(species_data["specimen_count"].sum())
    species_groups = int(species_data["species_name"].nunique())

    if total_specimens <= 0:
        raise ValueError("The database contains no specimen records.")

    if species_groups <= 0:
        raise ValueError("No species groups were returned.")

    # Species-level mean measurement reports
    measurement_frames = []

    for report_id, report_info in MEASUREMENT_REPORTS.items():
        report_data = run_report(report_id)

        required_columns = {
            "species_name",
            report_info["column"],
        }

        if not required_columns.issubset(report_data.columns):
            raise ValueError(
                f"{report_id} returned unexpected columns. "
                f"Expected: {sorted(required_columns)}; "
                f"received: {list(report_data.columns)}"
            )

        selected = report_data[
            ["species_name", report_info["column"]]
        ].copy()

        selected[report_info["column"]] = pd.to_numeric(
            selected[report_info["column"]],
            errors="raise",
        )

        if selected[report_info["column"]].isna().any():
            raise ValueError(
                f"{report_id} contains missing measurement averages."
            )

        selected = selected.rename(
            columns={
                report_info["column"]: report_info["label"]
            }
        )

        measurement_frames.append(selected)

    measurement_summary = measurement_frames[0]

    for frame in measurement_frames[1:]:
        measurement_summary = measurement_summary.merge(
            frame,
            on="species_name",
            how="inner",
            validate="one_to_one",
        )

    if len(measurement_summary) != species_groups:
        raise ValueError(
            "The measurement reports and species distribution "
            "do not contain the same number of species."
        )

    available_reports = len(list_reports())

    if available_reports <= 0:
        raise ValueError("No SQL reports are registered.")

    smallest_group = species_data.loc[
        species_data["specimen_count"].idxmin()
    ]

    largest_group = species_data.loc[
        species_data["specimen_count"].idxmax()
    ]

    # Prepare long-form data for the comparison chart
    measurement_long = measurement_summary.melt(
        id_vars=["species_name"],
        var_name="measurement",
        value_name="mean_value_cm",
    )

    return {
        "database_name": database_name,
        "total_specimens": total_specimens,
        "species_groups": species_groups,
        "measurement_variables": len(MEASUREMENT_REPORTS),
        "available_reports": available_reports,
        "smallest_species": str(smallest_group["species_name"]),
        "smallest_count": int(smallest_group["specimen_count"]),
        "largest_species": str(largest_group["species_name"]),
        "largest_count": int(largest_group["specimen_count"]),
        "species_data": species_data,
        "measurement_summary": measurement_summary,
        "measurement_long": measurement_long,
    }


# --------------------------------------------------
# APPLICATION IDENTITY
# --------------------------------------------------

st.sidebar.markdown(
    """
    <div style="padding: 12px 5px 20px 5px;">
        <div style="font-size: 25px; font-weight: 750; color: #183153;">
            🌿 IRIS INSIGHT
        </div>
        <div style="font-size: 11px; color: #475569; letter-spacing: 1px;">
            ANALYTICS INTELLIGENCE PLATFORM
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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
    "Report Centre",
]

selected_page = st.sidebar.radio(
    "WORKSPACE NAVIGATION",
    pages,
    index=0,
)

st.sidebar.divider()

st.sidebar.markdown("**PROJECT INFORMATION**")
st.sidebar.caption("Dataset: UCI Iris")
st.sidebar.caption(f"Database: {EXPECTED_DATABASE}")
st.sidebar.caption("Measurements: 4")
st.sidebar.caption("Species groups: 3")

st.sidebar.divider()

st.sidebar.markdown(
    """
    <div style="color: #475569; font-size: 12px;">
        IRIS INSIGHT<br>
        Scientific Data Analytics<br>
        Version 1.0
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">Iris Insight</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Species Measurement and Analytics Intelligence Platform'
    '</div>',
    unsafe_allow_html=True,
)

st.write("")


# --------------------------------------------------
# PAGE 1: ANALYTICS OVERVIEW
# --------------------------------------------------

if selected_page == "Overview":

    st.markdown("## Analytics Overview")

    st.caption(
        "A database-backed workspace for exploring Iris specimen "
        "measurements and species-level patterns."
    )

    refresh_col, status_col = st.columns([1, 3])

    with refresh_col:
        if st.button("Refresh Overview", use_container_width=True):
            load_overview_data.clear()
            st.rerun()

    try:
        with st.spinner("Retrieving analytical data from MySQL..."):
            overview = load_overview_data()

    except Exception as error:
        st.error("The Analytics Overview could not retrieve live data.")
        st.warning(
            "Check the MySQL service, your local .env configuration, "
            "the report engine, and the R01-R06 SQL report files."
        )

        with st.expander("Technical error details"):
            st.code(str(error))

        st.stop()

    with status_col:
        st.success(
            f"Live database connection established: "
            f"{overview['database_name']}"
        )

    st.divider()

    # KPI ROW 1
    st.markdown("### Dataset Summary")

    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        "Total Specimens",
        f"{overview['total_specimens']:,}",
    )

    kpi2.metric(
        "Species Groups",
        overview["species_groups"],
    )

    kpi3.metric(
        "Measurement Variables",
        overview["measurement_variables"],
    )

    # KPI ROW 2
    kpi4, kpi5, kpi6 = st.columns(3)

    with kpi4:
        st.metric(
            "Smallest Species Group",
            overview["smallest_count"],
        )
        st.caption(overview["smallest_species"])

    with kpi5:
        st.metric(
            "Largest Species Group",
            overview["largest_count"],
        )
        st.caption(overview["largest_species"])

    kpi6.metric(
        "Available SQL Reports",
        overview["available_reports"],
        help=(
            "Number of reports registered in the report engine. "
            "This does not independently certify every report."
        ),
    )

    st.caption(
        "KPI values are retrieved or calculated from the connected "
        "MySQL database. The four measurement variables represent "
        "the four defined Iris measurement attributes."
    )

    st.divider()

    # OVERVIEW CHARTS
    st.markdown("### Analytical Workspace")

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("**Species Distribution**")

        distribution_chart = px.pie(
            overview["species_data"],
            names="species_name",
            values="specimen_count",
            hole=0.58,
            title="Specimen records by species",
        )

        distribution_chart.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Specimens: %{value}<br>"
                "Share: %{percent}<extra></extra>"
            ),
        )

        distribution_chart.update_layout(
            margin=dict(l=15, r=15, t=55, b=15),
            legend_title_text="Species",
        )

        st.plotly_chart(
            distribution_chart,
            use_container_width=True,
        )

    with chart_right:
        st.markdown("**Mean Measurement Comparison**")

        measurement_chart = px.bar(
            overview["measurement_long"],
            x="measurement",
            y="mean_value_cm",
            color="species_name",
            barmode="group",
            title="Species-level mean measurements",
            labels={
                "measurement": "Measurement",
                "mean_value_cm": "Mean value (cm)",
                "species_name": "Species",
            },
            hover_data={
                "mean_value_cm": ":.2f",
            },
        )

        measurement_chart.update_layout(
            margin=dict(l=15, r=15, t=55, b=15),
            legend_title_text="Species",
            xaxis_title="Measurement variable",
            yaxis_title="Mean value (cm)",
        )

        st.plotly_chart(
            measurement_chart,
            use_container_width=True,
        )

    st.divider()

    # DATA TABLE
    st.markdown("### Species Record Summary")

    display_species = overview["species_data"][
        ["species_name", "specimen_count"]
    ].rename(
        columns={
            "species_name": "Species",
            "specimen_count": "Specimen Count",
        }
    )

    display_species["Percentage"] = (
        display_species["Specimen Count"]
        / overview["total_specimens"]
        * 100
    ).round(2)

    st.dataframe(
        display_species,
        use_container_width=True,
        hide_index=True,
    )

    # AUTOMATIC FINDINGS
    st.markdown("### Recent Analytical Findings")

    counts = overview["species_data"]["specimen_count"]

    if counts.nunique() == 1:
        st.info(
            "The species groups contain equal numbers of specimen records."
        )
    else:
        difference = overview["largest_count"] - overview["smallest_count"]
        st.info(
            f"{overview['largest_species']} has the largest record group "
            f"({overview['largest_count']}), while "
            f"{overview['smallest_species']} has the smallest "
            f"({overview['smallest_count']}). "
            f"The difference is {difference} record(s)."
        )

    means = overview["measurement_summary"].set_index("species_name")

    for measurement in [
        "Sepal Length",
        "Sepal Width",
        "Petal Length",
        "Petal Width",
    ]:
        highest_species = means[measurement].idxmax()
        highest_value = float(means[measurement].max())

        st.write(
            f"- Highest mean **{measurement.lower()}**: "
            f"**{highest_species}** "
            f"({highest_value:.2f} cm)."
        )


# --------------------------------------------------
# PAGE 2: SPECIES ANALYTICS
# --------------------------------------------------

elif selected_page == "Species Analytics":

    st.markdown("## Species Analytics")

    st.caption(
        "Compare measurement characteristics across the three Iris species."
    )

    st.info(
        "The interactive species analysis workspace will be implemented "
        "in the next development stage. The live Overview charts already "
        "use the R03-R06 database reports."
    )


# --------------------------------------------------
# PAGE 3: ASK IRIS
# --------------------------------------------------

elif selected_page == "Ask Iris":

    st.markdown("## Ask Iris")

    st.caption(
        "Explore the scientific dataset using natural-language questions."
    )

    st.markdown("### What would you like to investigate?")

    question = st.text_area(
        "Enter your analytical question",
        placeholder=(
            "Example: Which species has the highest "
            "average petal length?"
        ),
        height=110,
    )

    st.button(
        "Interpret Question",
        disabled=True,
        help=(
            "The safe natural-language query engine will be implemented "
            "in a later stage."
        ),
    )

    st.markdown("### How the query engine will work")

    st.write("1. Interpret the question.")
    st.write("2. Identify measurements and analytical conditions.")
    st.write("3. Select a predefined parameterized SQL template.")
    st.write("4. Validate the query and its parameters.")
    st.write("5. Execute against the MySQL database.")
    st.write("6. Present verified results and explanations.")

    st.caption("Natural-language execution is not enabled yet.")


# --------------------------------------------------
# PAGE 4: SPECIMEN EXPLORER
# --------------------------------------------------

elif selected_page == "Specimen Explorer":

    st.markdown("## Specimen Explorer")

    st.caption(
        "Explore individual specimen records using measurement-based filters."
    )

    st.info(
        "Interactive species selection, measurement ranges, specimen tables, "
        "pagination, and individual record inspection will be implemented "
        "in the Specimen Explorer stage."
    )


# --------------------------------------------------
# PAGE 5: QUALITY INTELLIGENCE
# --------------------------------------------------

elif selected_page == "Quality Intelligence":

    st.markdown("## Data Quality Intelligence")

    st.caption(
        "Inspect data integrity, repeated measurements, and import validation."
    )

    st.info(
        "Quality summaries, duplicate-group inspection, validation statistics, "
        "and import history will be connected in the Quality Intelligence stage."
    )


# --------------------------------------------------
# PAGE 6: REPORT CENTRE
# --------------------------------------------------

elif selected_page == "Report Centre":

    st.markdown("## Report Centre")

    st.caption(
        "Access the analytical SQL reports and their exported results."
    )

    st.info(
        "The existing R01-R10 report engine and CSV exports will be integrated "
        "with interactive execution and download controls in the Report Centre stage."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "IRIS INSIGHT | Scientific Measurement Analytics | "
    "MySQL + Python + Streamlit + Plotly"
)
