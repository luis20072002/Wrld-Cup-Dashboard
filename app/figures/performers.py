"""Figuras de la sección de top performers."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.figures.theme import EMPTY_LAYOUT, GRID, empty_figure
from src.config import RANKING_METRICS


def ranking_bar(stats: pd.DataFrame, metric: str, top_n: int) -> go.Figure:
    if stats.empty or metric not in stats.columns:
        return empty_figure()
    data = stats.sort_values(metric, ascending=False).head(top_n)
    data = data[data[metric] > 0].iloc[::-1]
    if data.empty:
        return empty_figure("Sin valores para esta métrica")
    label = RANKING_METRICS.get(metric, metric)
    fig = px.bar(
        data, x=metric, y="player", orientation="h",
        color=metric, color_continuous_scale="Teal",
        hover_data=["team", "goals", "xg", "assists", "minutes"],
        text=data[metric].round(2),
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        **EMPTY_LAYOUT, coloraxis_showscale=False,
        title=f"Top {top_n} por {label}", xaxis_title=label, yaxis_title="",
    )
    fig.update_xaxes(gridcolor=GRID)
    return fig


def xg_vs_goals_scatter(stats: pd.DataFrame, top_n: int) -> go.Figure:
    if stats.empty:
        return empty_figure()
    data = stats.sort_values("score", ascending=False).head(max(top_n, 20))
    data = data[(data["goals"] > 0) | (data["xg"] > 0)]
    if data.empty:
        return empty_figure("Sin tiros registrados")
    fig = px.scatter(
        data, x="xg", y="goals", size="shots", color="team",
        hover_name="player", size_max=28,
    )
    max_val = float(max(data["xg"].max(), data["goals"].max())) + 0.5
    fig.add_trace(
        go.Scatter(
            x=[0, max_val], y=[0, max_val], mode="lines",
            line=dict(color="rgba(255,255,255,0.35)", dash="dash"),
            name="xG = Goles", hoverinfo="skip",
        )
    )
    fig.update_layout(
        **EMPTY_LAYOUT,
        title="Rendimiento: xG esperado vs goles reales",
        xaxis_title="xG acumulado", yaxis_title="Goles",
        legend=dict(font=dict(size=10)),
    )
    fig.update_xaxes(gridcolor=GRID)
    fig.update_yaxes(gridcolor=GRID)
    return fig
