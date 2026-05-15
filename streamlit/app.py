"""
FIFA Men's World Cup Analytics Dashboard.

Reads the 4 marts in wc_gold and renders them with a variety of chart types,
each chosen to suit the underlying data:
    - KPI metrics
    - Lollipop chart (top scorers)
    - Scatter plot (team attack vs defense)
    - Donut chart (champions distribution)
    - Grouped bar chart (host performance: scored vs conceded)
    - Colored bar timeline (winners over time)
    - Plain table (reference)

Run from the project root:
    streamlit run streamlit/app.py
"""
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

DB_URL = (
    f"postgresql+psycopg2://{os.environ['DATABASE_USER']}:{os.environ['DATABASE_PASSWORD']}"
    f"@{os.environ['DATABASE_HOST']}:{os.environ['DATABASE_PORT']}/{os.environ['DATABASE_NAME']}"
)

st.set_page_config(page_title="World Cup Analytics", page_icon="⚽", layout="wide")


@st.cache_data
def load_marts() -> dict[str, pd.DataFrame]:
    engine = create_engine(DB_URL)
    return {
        "winners": pd.read_sql("SELECT * FROM wc_gold.mart_world_cup_winners ORDER BY year", engine),
        "hosts": pd.read_sql("SELECT * FROM wc_gold.mart_host_performance ORDER BY year", engine),
        "teams": pd.read_sql("SELECT * FROM wc_gold.mart_team_performance ORDER BY goals_for DESC", engine),
        "scorers": pd.read_sql("SELECT * FROM wc_gold.mart_top_scorers ORDER BY goals_scored DESC", engine),
    }


data = load_marts()

st.title("⚽ FIFA Men's World Cup Analytics")
st.caption("Built with Python + PostgreSQL + dbt — data from jfjelstul/worldcup (1930–2022)")

# ── KPI row ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tournaments", len(data["winners"]))
col2.metric("Total matches", int(data["teams"]["matches_played"].sum() / 2))
col3.metric("Total goals scored", int(data["teams"]["goals_for"].sum()))
col4.metric("Distinct teams", len(data["teams"]))

st.markdown("---")

# ── Top scorers (lollipop) ───────────────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    st.subheader("🥇 Top 10 Goal Scorers (all-time)")
    top10 = data["scorers"].head(10).copy()
    top10["display_name"] = (
        top10["given_name"].replace("not applicable", "").str.strip() + " " + top10["family_name"]
    ).str.strip()
    top10 = top10.iloc[::-1]

    fig = go.Figure()
    # The "stick" of the lollipop
    for _, row in top10.iterrows():
        fig.add_shape(
            type="line",
            x0=0, x1=row["goals_scored"], y0=row["display_name"], y1=row["display_name"],
            line=dict(color="#94a3b8", width=2),
        )
    # The "candy" of the lollipop
    fig.add_trace(
        go.Scatter(
            x=top10["goals_scored"],
            y=top10["display_name"],
            mode="markers+text",
            marker=dict(size=22, color=top10["goals_scored"], colorscale="Viridis", showscale=False),
            text=top10["goals_scored"],
            textposition="middle center",
            textfont=dict(color="white", size=11, family="Arial Black"),
            hovertext=top10.apply(lambda r: f"{r['display_name']} ({r['country']}): {r['goals_scored']} goals", axis=1),
            hoverinfo="text",
        )
    )
    fig.update_layout(
        height=420, margin=dict(l=0, r=20, t=10, b=0),
        xaxis_title="Goals scored", yaxis_title=None,
        showlegend=False, plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    st.plotly_chart(fig, use_container_width=True)

# ── Champions distribution (donut) ───────────────────────────────────────────
with right:
    st.subheader("🏆 Distribution of Titles")
    title_counts = data["winners"]["winner"].value_counts().reset_index()
    title_counts.columns = ["country", "titles"]
    fig = px.pie(
        title_counts,
        names="country",
        values="titles",
        hole=0.55,
    )
    fig.update_traces(textposition="inside", textinfo="label+value")
    fig.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Team performance scatter ─────────────────────────────────────────────────
st.subheader("⚔️ Team Performance: Attack vs Defense")
st.caption("Top-right corner = high-scoring but leaky. Bottom-right = the ideal: high attack AND low defense.")

teams_scatter = data["teams"][data["teams"]["matches_played"] >= 10].copy()
fig = px.scatter(
    teams_scatter,
    x="goals_for",
    y="goals_against",
    size="matches_played",
    color="wins",
    text="team_name",
    hover_data=["matches_played", "wins", "draws", "losses", "goal_difference"],
    color_continuous_scale="RdYlGn",
    size_max=40,
    labels={
        "goals_for": "Total goals scored",
        "goals_against": "Total goals conceded",
        "wins": "Wins",
    },
)
fig.update_traces(textposition="top center", textfont_size=10)
fig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Host performance (grouped bar) + Winners timeline ────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("🏠 Host Performance per Tournament")
    hosts_long = data["hosts"].melt(
        id_vars=["year", "host_country", "host_won_their_wc"],
        value_vars=["goals_scored", "goals_conceded"],
        var_name="metric",
        value_name="goals",
    )
    hosts_long["metric"] = hosts_long["metric"].map({"goals_scored": "Scored", "goals_conceded": "Conceded"})
    hosts_long["label"] = hosts_long["year"].astype(str) + " — " + hosts_long["host_country"]
    fig = px.bar(
        hosts_long,
        x="label",
        y="goals",
        color="metric",
        barmode="group",
        color_discrete_map={"Scored": "#22c55e", "Conceded": "#ef4444"},
        labels={"label": "Tournament", "goals": "Goals"},
    )
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=80), xaxis_tickangle=-60, legend_title=None)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("🌟 Winners Through Time")
    st.caption("Each star = one World Cup won. Countries ordered by total titles.")
    winners = data["winners"].copy()
    # Sort y-axis by total titles (most-titled country at the top).
    title_order = winners["winner"].value_counts().index.tolist()[::-1]
    winners["winner"] = pd.Categorical(winners["winner"], categories=title_order, ordered=True)
    fig = px.scatter(
        winners,
        x="year",
        y="winner",
        hover_data={"host_country": True, "count_teams": True, "year": True, "winner": False},
        labels={"winner": "", "year": "Year"},
    )
    fig.update_traces(
        marker=dict(symbol="star", size=22, color="gold", line=dict(width=1.5, color="#b45309")),
    )
    fig.update_layout(
        height=520, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#e2e8f0", dtick=8),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Reference tables ─────────────────────────────────────────────────────────
with st.expander("📋 Full data tables (click to expand)"):
    tab1, tab2, tab3 = st.tabs(["Winners", "Host performance", "Top scorers"])
    with tab1:
        st.dataframe(data["winners"], use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(data["hosts"], use_container_width=True, hide_index=True)
    with tab3:
        st.dataframe(data["scorers"], use_container_width=True, hide_index=True)

st.caption(
    "Pipeline: jfjelstul/worldcup CSVs → Python ETL → PostgreSQL `wc_raw` → "
    "dbt staging (`wc_silver`) → dbt marts (`wc_gold`) → this dashboard."
)
