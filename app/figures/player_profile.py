"""Figuras del perfil individual de jugador: radar, mapa de tiros y timeline."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from app.figures.theme import (
    ACCENT, ACCENT_2, ACCENT_3, EMPTY_LAYOUT, GRID, PITCH_LINE,
    draw_pitch, empty_figure,
)

RADAR_METRICS = [
    ("goals", "Goles"),
    ("xg", "xG"),
    ("assists", "Asistencias"),
    ("shots", "Tiros"),
    ("key_passes", "Pases clave"),
    ("minutes", "Minutos"),
]


def radar(stats: pd.DataFrame, player_id: int) -> go.Figure:
    if stats.empty or player_id is None:
        return empty_figure("Selecciona un jugador")
    row = stats[stats["player_id"] == player_id]
    if row.empty:
        return empty_figure("Jugador no encontrado")
    row = row.iloc[0]

    values, labels = [], []
    for col, label in RADAR_METRICS:
        if col not in stats.columns:
            continue
        col_max = stats[col].max()
        norm = (row[col] / col_max * 100) if col_max > 0 else 0
        values.append(norm)
        labels.append(label)
    values.append(values[0])
    labels.append(labels[0])

    fig = go.Figure(
        go.Scatterpolar(
            r=values, theta=labels, fill="toself",
            line=dict(color=ACCENT), fillcolor="rgba(0,194,168,0.35)",
        )
    )
    fig.update_layout(
        **EMPTY_LAYOUT,
        title=f"Perfil de {row['player']} (percentil del torneo)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=GRID),
            angularaxis=dict(gridcolor=GRID),
        ),
    )
    return fig


def shot_map(shots: pd.DataFrame, player_name: str = "") -> go.Figure:
    fig = go.Figure()
    draw_pitch(fig)
    if shots.empty:
        fig.update_layout(title="Sin tiros registrados")
        return fig

    shots = shots.dropna(subset=["location_x", "location_y"]).copy()
    if shots.empty:
        fig.update_layout(title="Sin coordenadas de tiro")
        return fig

    is_goal = shots["shot_outcome"] == "Goal"
    xg = shots["shot_statsbomb_xg"].fillna(0)

    fig.add_trace(
        go.Scatter(
            x=shots.loc[~is_goal, "location_x"], y=shots.loc[~is_goal, "location_y"],
            mode="markers", name="Tiro",
            marker=dict(
                size=8 + xg[~is_goal] * 30, color=ACCENT_2, opacity=0.7,
                line=dict(width=1, color=PITCH_LINE),
            ),
            customdata=xg[~is_goal].round(3),
            hovertemplate="Tiro · xG=%{customdata}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=shots.loc[is_goal, "location_x"], y=shots.loc[is_goal, "location_y"],
            mode="markers", name="Gol",
            marker=dict(
                size=10 + xg[is_goal] * 30, color=ACCENT_3, symbol="star",
                line=dict(width=1, color="white"),
            ),
            customdata=xg[is_goal].round(3),
            hovertemplate="Gol · xG=%{customdata}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"Mapa de tiros · {player_name}".strip(" ·"),
        legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"),
    )
    return fig


def contributions_timeline(events: pd.DataFrame, player_id: int, player_name: str = "") -> go.Figure:
    if events.empty or player_id is None:
        return empty_figure("Selecciona un jugador")
    df = events[events["player_id"] == player_id].copy()
    if "period" in df.columns:
        df = df[df["period"] != 5]
    goals = df[(df["type"] == "Shot") & (df["shot_outcome"] == "Goal")]
    assists = df[df.get("pass_goal_assist") == True]  # noqa: E712

    if goals.empty and assists.empty:
        return empty_figure("Sin goles ni asistencias")

    fig = go.Figure()
    if not goals.empty:
        fig.add_trace(
            go.Scatter(
                x=goals["minute"], y=[1] * len(goals), mode="markers",
                name="Gol", marker=dict(color=ACCENT_3, size=14, symbol="star"),
                hovertemplate="Gol · min %{x}<extra></extra>",
            )
        )
    if not assists.empty:
        fig.add_trace(
            go.Scatter(
                x=assists["minute"], y=[0.5] * len(assists), mode="markers",
                name="Asistencia", marker=dict(color=ACCENT, size=12, symbol="diamond"),
                hovertemplate="Asistencia · min %{x}<extra></extra>",
            )
        )
    fig.update_layout(
        **EMPTY_LAYOUT,
        title=f"Goles y asistencias por minuto · {player_name}".strip(" ·"),
        xaxis_title="Minuto de partido",
    )
    fig.update_xaxes(range=[0, 125], gridcolor=GRID)
    fig.update_yaxes(range=[0, 1.5], visible=False)
    return fig
