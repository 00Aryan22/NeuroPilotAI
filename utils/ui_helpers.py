from pathlib import Path
from typing import Dict, List

import plotly.express as px
import pandas as pd
import streamlit as st


def inject_css(css_path: str = "styles/main.css") -> None:
    css_file = Path(css_path)
    if css_file.exists():
        st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def glass_card(title: str, value: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
            <div class="card-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="section-wrap">
            <h2>{title}</h2>
            <p>{caption}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def usage_chart(metrics: Dict[str, int]):
    df = pd.DataFrame({"Metric": list(metrics.keys()), "Count": list(metrics.values())})
    fig = px.bar(df, x="Metric", y="Count", color="Metric", template="plotly_dark")
    fig.update_layout(height=330, margin=dict(l=20, r=20, t=30, b=20))
    return fig


def timeline_chart(events: List[dict]):
    if not events:
        events = [{"event": "No events yet", "count": 0}]
    df = pd.DataFrame(events)
    fig = px.line(df, x="event", y="count", template="plotly_dark", markers=True)
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
    return fig
