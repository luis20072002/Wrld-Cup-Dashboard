"""Paleta y utilidades visuales compartidas por las figuras Plotly."""
from __future__ import annotations

import plotly.graph_objects as go

from src.config import PITCH_LENGTH, PITCH_WIDTH

TEMPLATE = "plotly_dark"
ACCENT = "#00C2A8"
ACCENT_2 = "#F2C14E"
ACCENT_3 = "#E15554"
GRID = "rgba(255,255,255,0.08)"
PITCH_GREEN = "#1f5c2e"
PITCH_LINE = "rgba(255,255,255,0.55)"

EMPTY_LAYOUT = dict(
    template=TEMPLATE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=50, b=40),
)


def empty_figure(message: str = "Sin datos disponibles") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(**EMPTY_LAYOUT)
    fig.add_annotation(
        text=message, showarrow=False, font=dict(size=15, color="#8a8a8a"),
        xref="paper", yref="paper", x=0.5, y=0.5,
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def draw_pitch(fig: go.Figure) -> go.Figure:
    """Dibuja medio/entero campo (StatsBomb 120x80) con shapes sobre la figura."""
    line = dict(color=PITCH_LINE, width=1.4)
    shapes = [
        dict(type="rect", x0=0, y0=0, x1=PITCH_LENGTH, y1=PITCH_WIDTH, line=line),
        dict(type="line", x0=60, y0=0, x1=60, y1=PITCH_WIDTH, line=line),
        dict(type="circle", x0=50, y0=30, x1=70, y1=50, line=line),
        # Áreas
        dict(type="rect", x0=0, y0=18, x1=18, y1=62, line=line),
        dict(type="rect", x0=102, y0=18, x1=PITCH_LENGTH, y1=62, line=line),
        dict(type="rect", x0=0, y0=30, x1=6, y1=50, line=line),
        dict(type="rect", x0=114, y0=30, x1=PITCH_LENGTH, y1=50, line=line),
    ]
    fig.update_layout(
        shapes=shapes,
        **EMPTY_LAYOUT,
    )
    fig.update_xaxes(range=[-2, PITCH_LENGTH + 2], visible=False, constrain="domain")
    fig.update_yaxes(
        range=[-2, PITCH_WIDTH + 2], visible=False,
        scaleanchor="x", scaleratio=1,
    )
    return fig
