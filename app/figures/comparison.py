"""Figuras de la comparativa entre ediciones del Mundial."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from app.figures.theme import ACCENT, ACCENT_2, EMPTY_LAYOUT, GRID, empty_figure


def top_scorers_side_by_side(
    stats_a: pd.DataFrame, label_a: str,
    stats_b: pd.DataFrame, label_b: str, top_n: int = 10,
) -> go.Figure:
    if stats_a.empty and stats_b.empty:
        return empty_figure()

    def _top(stats):
        d = stats.sort_values("goals", ascending=False).head(top_n)
        return d[d["goals"] > 0].iloc[::-1]

    a, b = _top(stats_a), _top(stats_b)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=a["goals"], y=a["player"], orientation="h", name=label_a,
        marker_color=ACCENT, text=a["goals"], textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=b["goals"], y=b["player"], orientation="h", name=label_b,
        marker_color=ACCENT_2, text=b["goals"], textposition="outside",
    ))
    fig.update_layout(
        **EMPTY_LAYOUT, barmode="group",
        title="Máximos goleadores por edición", xaxis_title="Goles", yaxis_title="",
        legend=dict(orientation="h", y=1.04, x=0.5, xanchor="center"),
    )
    fig.update_xaxes(gridcolor=GRID)
    return fig


def edition_kpi_comparison(
    stats_a: pd.DataFrame, label_a: str,
    stats_b: pd.DataFrame, label_b: str,
) -> go.Figure:
    if stats_a.empty and stats_b.empty:
        return empty_figure()
    metrics = [
        ("goals", "Goles"), ("xg", "xG"), ("assists", "Asistencias"),
        ("shots", "Tiros"),
    ]
    labels = [m[1] for m in metrics]
    vals_a = [float(stats_a[m[0]].sum()) if m[0] in stats_a else 0 for m in metrics]
    vals_b = [float(stats_b[m[0]].sum()) if m[0] in stats_b else 0 for m in metrics]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=vals_a, name=label_a, marker_color=ACCENT,
                         text=[round(v) for v in vals_a], textposition="outside"))
    fig.add_trace(go.Bar(x=labels, y=vals_b, name=label_b, marker_color=ACCENT_2,
                         text=[round(v) for v in vals_b], textposition="outside"))
    fig.update_layout(
        **EMPTY_LAYOUT, barmode="group",
        title="Totales del torneo por edición", yaxis_title="Total",
        legend=dict(orientation="h", y=1.04, x=0.5, xanchor="center"),
    )
    fig.update_yaxes(gridcolor=GRID)
    return fig
