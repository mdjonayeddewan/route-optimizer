from __future__ import annotations

import streamlit as st


def render_sidebar(config: dict, ga_config: dict) -> None:
    st.sidebar.title("Route Optimizer")
    st.sidebar.caption("Single route finder + GA-based multi-stop optimization")

    with st.sidebar.expander("How to Use", expanded=True):
        st.write("1) Use Single Route tab for source to destination route.")
        st.write("2) Use Multi-Stop tab to optimize delivery stops.")
        st.write("3) Input either 'lat,lon' or place names.")

    with st.sidebar.expander("GA Parameters", expanded=False):
        ga = ga_config["ga"]
        st.write(f"Population: {ga['population_size']}")
        st.write(f"Generations: {ga['generations']}")
        st.write(f"Mutation: {ga['mutation_rate']}")
        st.write(f"Crossover: {ga['crossover_rate']}")
        st.write(f"Elitism: {ga['elitism_count']}")

    st.sidebar.info(f"Routing profile: {config['routing']['profile']}")
