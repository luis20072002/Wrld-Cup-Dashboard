"""Figuras del resumen de torneo."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.figures.theme import ACCENT_2, EMPTY_LAYOUT, GRID, empty_figure


def top_scorers_bar(stats: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if stats.empty:
        return empty_figure()
    data = stats.sort_values("goals", ascending=False).head(top_n)
    data = data[data["goals"] > 0].iloc[::-1]
    if data.empty:
        return empty_figure("Sin goles registrados")
    fig = px.bar(
        data, x="goals", y="player", orientation="h",
        text="goals", color="goals", color_continuous_scale="Teal",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        **EMPTY_LAYOUT, coloraxis_showscale=False,
        title="Máximos goleadores",
        xaxis_title="Goles", yaxis_title="",
    )
    fig.update_xaxes(gridcolor=GRID)
    return fig


def goals_by_team_bar(stats: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if stats.empty:
        return empty_figure()
    by_team = (
        stats.groupby("team", as_index=False)["goals"].sum()
        .sort_values("goals", ascending=False).head(top_n).iloc[::-1]
    )
    if by_team.empty or by_team["goals"].sum() == 0:
        return empty_figure("Sin goles registrados")
    fig = px.bar(by_team, x="goals", y="team", orientation="h", text="goals")
    fig.update_traces(marker_color=ACCENT_2, textposition="outside", cliponaxis=False)
    fig.update_layout(
        **EMPTY_LAYOUT,
        title="Goles por selección", xaxis_title="Goles", yaxis_title="",
    )
    fig.update_xaxes(gridcolor=GRID)
    return fig


def goals_by_stage_donut(matches: pd.DataFrame) -> go.Figure:
    stage_col = next((c for c in ("stage", "competition_stage") if c in matches.columns), None)
    if stage_col is None:
        return empty_figure("Sin información de fase")
    df = matches.copy()
    df["total_goals"] = df.get("home_score", 0).fillna(0) + df.get("away_score", 0).fillna(0)
    by_stage = df.groupby(stage_col, as_index=False)["total_goals"].sum()
    by_stage = by_stage[by_stage["total_goals"] > 0]
    if by_stage.empty:
        return empty_figure("Sin goles por fase")
    fig = go.Figure(
        go.Pie(
            labels=by_stage[stage_col], values=by_stage["total_goals"], hole=0.55,
            marker=dict(colors=px.colors.sequential.Teal),
        )
    )
    fig.update_layout(
        **EMPTY_LAYOUT, title="Goles por fase del torneo",
    )
    return fig
