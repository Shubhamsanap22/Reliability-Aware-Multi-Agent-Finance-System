import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

# dashboard.py:
#
# financial_multi_agent/
# └── app/
#     └── ui/
#         └── dashboard.py
#
# parents[2] = financial_multi_agent/

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# BACKEND IMPORT
# ============================================================

from main import create_application


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Decision Support System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 20px;
        color: #9aa4b2;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .agent-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30343b;
        background-color: #17191e;
        margin-bottom: 15px;
    }

    .agent-name {
        font-size: 21px;
        font-weight: 600;
    }

    .metric-label {
        font-size: 13px;
        color: #9aa4b2;
    }

    .metric-value {
        font-size: 20px;
        font-weight: 600;
    }

    .pipeline {
        padding: 15px;
        border-radius: 10px;
        background-color: #17191e;
        border: 1px solid #30343b;
        text-align: center;
        font-size: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    'Financial Decision Support System'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Adaptive Resource-Constrained Multi-Agent System'
    '</div>',
    unsafe_allow_html=True,
)


st.write(
    "The system analyzes a financial query, identifies the "
    "required capabilities, dynamically selects specialized "
    "agents, manages computational budget, executes the "
    "selected team, and monitors execution reliability."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("System Components")

    st.success("Query Analyzer")

    st.success("Capability Registry")

    st.success("Dynamic Team Builder")

    st.success("Budget Manager")

    st.success("Executor")

    st.success("Failure Handler")

    st.success("Reliability Monitor")

    st.success("Local → API Data Fallback")

    st.divider()

    st.header("Example Queries")

    example_queries = [
        "Analyze the risk of TCS.",
        "Analyze the market trend for TCS.",
        "Should I invest in TCS?",
        "Build a portfolio using TCS and INFY.",
        "Perform technical analysis on TCS.",
        "Analyze the fundamental strength of TCS.",
        "Analyze the sentiment for TCS.",
        "I want ₹20 lakh in 8 years with moderate risk",
    ]

    selected_example = st.selectbox(
        "Choose an example",
        ["-- Select --"] + example_queries,
    )


# ============================================================
# QUERY INPUT
# ============================================================

default_query = ""

if selected_example != "-- Select --":
    default_query = selected_example


query = st.text_area(
    "Financial Query",
    value=default_query,
    placeholder=(
        "Example: Analyze the risk of TCS."
    ),
    height=120,
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze_clicked = st.button(
    "Analyze & Execute",
    type="primary",
    use_container_width=True,
)


# ============================================================
# MAIN EXECUTION
# ============================================================

if analyze_clicked:

    if not query.strip():

        st.warning(
            "Please enter a financial query."
        )

    else:

        # ----------------------------------------------------
        # Create the complete application
        # ----------------------------------------------------

        try:

            orchestrator = create_application()

        except Exception as error:

            st.error(
                "Unable to initialize the application."
            )

            st.exception(error)

            st.stop()


        # ====================================================
        # QUERY ANALYSIS
        # ====================================================

        analyzer = orchestrator.analyzer

        requirement = analyzer.analyze(
            query
        )


        # ====================================================
        # TEAM BUILDING
        # ====================================================

        team_builder = (
            orchestrator.team_builder
        )

        team = team_builder.build_team(
            requirement
        )


        # ====================================================
        # DISPLAY QUERY UNDERSTANDING
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '1. Query Understanding'
            '</div>',
            unsafe_allow_html=True,
        )


        col1, col2 = st.columns(2)


        with col1:

            st.markdown(
                "**Original Query**"
            )

            st.info(
                requirement.query
            )


        with col2:

            st.markdown(
                "**Required Capabilities**"
            )

            for capability in (
                requirement.required_capabilities
            ):

                display_name = (
                    capability
                    .replace("_", " ")
                    .title()
                )

                st.success(
                    display_name
                )


        # ====================================================
        # DISPLAY SELECTED TEAM
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '2. Dynamically Selected Agent Team'
            '</div>',
            unsafe_allow_html=True,
        )


        if not team:

            st.warning(
                "No suitable agent was selected."
            )

        else:

            for agent in team:

                st.markdown(
                    '<div class="agent-card">',
                    unsafe_allow_html=True,
                )

                col1, col2, col3 = st.columns(3)


                with col1:

                    st.markdown(
                        '<div class="metric-label">'
                        'AGENT'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f'<div class="agent-name">'
                        f'{agent.name}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


                with col2:

                    st.markdown(
                        '<div class="metric-label">'
                        'RELIABILITY'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f'<div class="metric-value">'
                        f'{agent.reliability:.2f}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


                with col3:

                    st.markdown(
                        '<div class="metric-label">'
                        'ESTIMATED COST'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f'<div class="metric-value">'
                        f'{agent.estimated_cost}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


                st.markdown(
                    '</div>',
                    unsafe_allow_html=True,
                )


        # ====================================================
        # EXECUTION PIPELINE
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '3. Execution Pipeline'
            '</div>',
            unsafe_allow_html=True,
        )


        pipeline = [
            "Query Analyzer",
            "Team Builder",
            "Budget Manager",
            "Executor",
            "Agent",
            "Reliability Monitor",
        ]


        pipeline_columns = st.columns(
            len(pipeline)
        )


        for column, component in zip(
            pipeline_columns,
            pipeline,
        ):

            with column:

                st.markdown(
                    f'<div class="pipeline">'
                    f'{component}'
                    f'</div>',
                    unsafe_allow_html=True,
                )


        # ====================================================
        # EXECUTE AGENTS
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '4. Agent Execution'
            '</div>',
            unsafe_allow_html=True,
        )


        with st.spinner(
            "Executing selected agent team..."
        ):

            executor = (
                orchestrator.executor
            )

            results = (
                executor.run_agents_with_fallback(
                    agents=team,
                    query=requirement.query,
                )
            )


        # ====================================================
        # RELIABILITY UPDATE
        # ====================================================

        reliability_monitor = (
            orchestrator.reliability_monitor
        )


        for agent, result in zip(
            team,
            results,
        ):

            reliability_monitor.update(
                agent,
                result.status,
            )


        # ====================================================
        # EXECUTION RESULTS
        # ====================================================

        for agent, result in zip(
            team,
            results,
        ):

            st.markdown(
                f"### {result.agent_name}"
            )


            # ------------------------------------------------
            # Agent status
            # ------------------------------------------------

            if result.status.value == "completed":

                st.success(
                    f"Status: "
                    f"{result.status.value.title()}"
                )

            else:

                st.error(
                    f"Status: "
                    f"{result.status.value.title()}"
                )


            # ------------------------------------------------
            # Metrics
            # ------------------------------------------------

            col1, col2, col3, col4 = st.columns(4)


            with col1:

                st.metric(
                    "Reliability",
                    f"{result.reliability:.2f}",
                )


            with col2:

                st.metric(
                    "Allocated Budget",
                    result.allocated_budget,
                )


            with col3:

                st.metric(
                    "Used Budget",
                    result.used_budget,
                )


            with col4:

                st.metric(
                    "Remaining",
                    result.remaining_agent_budget,
                )


            # ------------------------------------------------
            # Agent output
            # ------------------------------------------------

            if result.output:

                st.markdown(
                    "**Analysis Result**"
                )

                st.text(
                    result.output
                )


            # ------------------------------------------------
            # Failure information
            # ------------------------------------------------

            if result.failure_reason:

                st.error(
                    f"Failure Reason: "
                    f"{result.failure_reason}"
                )


        # ====================================================
        # GLOBAL BUDGET
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '5. Resource Usage'
            '</div>',
            unsafe_allow_html=True,
        )


        budget_state = (
            orchestrator.executor
            .budget_manager
            .state
        )


        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "Global Budget",
                budget_state.global_budget,
            )


        with col2:

            st.metric(
                "Allocated",
                budget_state.allocated_budget,
            )


        with col3:

            st.metric(
                "Used",
                budget_state.used_budget,
            )


        with col4:

            st.metric(
                "Remaining",
                budget_state.remaining_budget,
            )


        # ====================================================
        # DATA SOURCE
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '6. Data Layer'
            '</div>',
            unsafe_allow_html=True,
        )


        data_col1, data_col2 = st.columns(2)


        with data_col1:

            st.success(
                "Primary Source: "
                "Local Historical Market Data"
            )


        with data_col2:

            st.info(
                "Fallback: "
                "Alpha Vantage API"
            )


        st.caption(
            "The system attempts to use validated local "
            "historical data first. If local data is missing "
            "or the requested symbol is unavailable, the "
            "configured API fallback can be used."
        )


        # ====================================================
        # FINAL SUMMARY
        # ====================================================

        completed = sum(
            result.status.value == "completed"
            for result in results
        )

        failed = sum(
            result.status.value == "failed"
            for result in results
        )


        st.markdown(
            '<div class="section-title">'
            '7. Execution Summary'
            '</div>',
            unsafe_allow_html=True,
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Agents Selected",
                len(team),
            )


        with col2:

            st.metric(
                "Completed",
                completed,
            )


        with col3:

            st.metric(
                "Failed",
                failed,
            )


        if failed == 0:

            st.success(
                "All selected agents completed successfully."
            )

        else:

            st.warning(
                "One or more agents failed. "
                "The failure handler and fallback mechanism "
                "were applied according to the configured policy."
            )