"""Layout del dashboard: cabecera, controles y las cuatro pestañas."""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from src.config import (
    DEFAULT_EDITION, DEFAULT_TOP_N, EDITIONS, RANKING_METRICS,
    STATSBOMB_CREDIT, TOP_N_RANGE,
)

EDITION_OPTIONS = [{"label": meta["label"], "value": ed} for ed, meta in EDITIONS.items()]
METRIC_OPTIONS = [{"label": label, "value": key} for key, label in RANKING_METRICS.items()]


def _kpi_card(card_id: str, title: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.Div(title, className="text-muted small text-uppercase"),
            html.H3(id=card_id, className="mb-0 fw-bold"),
        ]),
        className="text-center shadow-sm",
    )


def _edition_dropdown(component_id: str, default: str = DEFAULT_EDITION) -> dcc.Dropdown:
    return dcc.Dropdown(
        id=component_id, options=EDITION_OPTIONS, value=default,
        clearable=False, className="mb-2",
    )


def _overview_tab() -> dbc.Tab:
    return dbc.Tab(label="Resumen", tab_id="tab-overview", children=dbc.Container([
        dbc.Row([
            dbc.Col([html.Label("Edición"), _edition_dropdown("overview-edition")], md=4),
        ], className="my-3"),
        dbc.Row([
            dbc.Col(_kpi_card("kpi-goals", "Goles"), md=3),
            dbc.Col(_kpi_card("kpi-matches", "Partidos"), md=3),
            dbc.Col(_kpi_card("kpi-xg", "xG total"), md=3),
            dbc.Col(_kpi_card("kpi-players", "Jugadores"), md=3),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="overview-scorers"), lg=6),
            dbc.Col(dcc.Graph(id="overview-teams"), lg=6),
        ]),
        dbc.Row([dbc.Col(dcc.Graph(id="overview-stage"), lg=6)]),
    ], fluid=True))


def _performers_tab() -> dbc.Tab:
    return dbc.Tab(label="Top performers", tab_id="tab-performers", children=dbc.Container([
        dbc.Row([
            dbc.Col([html.Label("Edición"), _edition_dropdown("performers-edition")], md=3),
            dbc.Col([
                html.Label("Métrica de ranking"),
                dcc.Dropdown(id="performers-metric", options=METRIC_OPTIONS,
                             value="score", clearable=False),
            ], md=3),
            dbc.Col([
                html.Label("Top N"),
                dcc.Slider(
                    id="performers-topn", min=TOP_N_RANGE[0], max=TOP_N_RANGE[1],
                    step=1, value=DEFAULT_TOP_N,
                    marks={n: str(n) for n in range(TOP_N_RANGE[0], TOP_N_RANGE[1] + 1, 5)},
                    tooltip={"placement": "bottom"},
                ),
            ], md=6),
        ], className="my-3 align-items-end"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="performers-ranking"), lg=6),
            dbc.Col(dcc.Graph(id="performers-scatter"), lg=6),
        ]),
        dbc.Row([dbc.Col([
            html.H6("Tabla de ranking", className="mt-3"),
            dash_table.DataTable(
                id="performers-table",
                page_size=12, sort_action="native", filter_action="native",
                style_table={"overflowX": "auto"},
                style_cell={"backgroundColor": "#1b1d23", "color": "#e8e8e8",
                            "border": "1px solid #2c2f36", "padding": "6px",
                            "fontSize": "13px"},
                style_header={"backgroundColor": "#11141a", "fontWeight": "bold"},
            ),
        ])]),
    ], fluid=True))


def _player_tab() -> dbc.Tab:
    return dbc.Tab(label="Perfil de jugador", tab_id="tab-player", children=dbc.Container([
        dbc.Row([
            dbc.Col([html.Label("Edición"), _edition_dropdown("player-edition")], md=3),
            dbc.Col([
                html.Label("Jugador"),
                dcc.Dropdown(id="player-select", clearable=False),
            ], md=5),
        ], className="my-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="player-radar"), lg=5),
            dbc.Col(dcc.Graph(id="player-shotmap"), lg=7),
        ]),
        dbc.Row([dbc.Col(dcc.Graph(id="player-timeline"))]),
    ], fluid=True))


def _comparison_tab() -> dbc.Tab:
    return dbc.Tab(label="Comparativa 2018 vs 2022", tab_id="tab-comparison",
                   children=dbc.Container([
        dbc.Alert(
            "Pocos jugadores coinciden entre ediciones; la comparación es "
            "principalmente a nivel de torneo.",
            color="info", className="my-3",
        ),
        dbc.Row([
            dbc.Col(dcc.Graph(id="comparison-kpis"), lg=5),
            dbc.Col(dcc.Graph(id="comparison-scorers"), lg=7),
        ]),
    ], fluid=True))


def serve_layout() -> html.Div:
    header = dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("Mundial FIFA · Análisis StatsBomb", className="fw-bold"),
            html.Span("Dash + Plotly", className="text-muted small"),
        ]),
        color="dark", dark=True, className="mb-2 shadow-sm",
    )
    footer = html.Footer(
        dbc.Container(html.Small(STATSBOMB_CREDIT, className="text-muted")),
        className="py-3 mt-2 border-top",
    )
    return html.Div([
        header,
        dbc.Tabs(
            [_overview_tab(), _performers_tab(), _player_tab(), _comparison_tab()],
            id="tabs", active_tab="tab-overview",
        ),
        footer,
    ])
