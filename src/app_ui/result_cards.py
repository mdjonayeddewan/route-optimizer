from __future__ import annotations

import streamlit as st


def show_route_metrics(distance_km: float, duration_min: float) -> None:
    col1, col2 = st.columns(2)
    col1.metric("Distance (km)", f"{distance_km:.2f}")
    col2.metric("Duration (min)", f"{duration_min:.2f}")


def show_optimization_metrics(original_km: float, optimized_km: float, improvement_pct: float, stop_count: int) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stops", str(stop_count))
    c2.metric("Original (km)", f"{original_km:.2f}")
    c3.metric("Optimized (km)", f"{optimized_km:.2f}")
    c4.metric("Improvement", f"{improvement_pct:.2f}%")
