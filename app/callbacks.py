"""Callbacks que conectan los controles del dashboard con las figuras."""
from __future__ import annotations

import pandas as pd
from dash import Input, Output

from app.figures import comparison, overview, performers, player_profile
from src import data_loader
from src.config import EDITIONS

TABLE_COLUMNS = [
    ("player", "Jugador"), ("team", "Selección"), ("goals", "Goles"),
    ("xg", "xG"), ("assists", "Asist."), ("key_passes", "Pases clave"),
    ("shots", "Tiros"), ("minutes", "Minutos"), ("score", "Score"),
]


def _round_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ("xg", "xa", "score", "goals_p90", "xg_p90"):
        if col in df.columns:
            df[col] = df[col].round(2)
    if "minutes" in df.columns:
        df["minutes"] = df["minutes"].round(0).astype(int)
    return df


def register_callbacks(app) -> None:

    @app.callback(
        Output("kpi-goals", "children"),
        Output("kpi-matches", "children"),
        Output("kpi-xg", "children"),
        Output("kpi-players", "children"),
        Output("overview-scorers", "figure"),
        Output("overview-teams", "figure"),
        Output("overview-stage", "figure"),
        Input("overview-edition", "value"),
    )
    def _update_overview(edition):
        stats = data_loader.load_player_stats(edition)
        matches = data_loader.load_matches(edition)
        total_goals = int(stats["goals"].sum())
        total_xg = round(float(stats["xg"].sum()), 1)
        return (
            f"{total_goals}",
            f"{len(matches)}",
            f"{total_xg}",
            f"{len(stats)}",
            overview.top_scorers_bar(stats),
            overview.goals_by_team_bar(stats),
            overview.goals_by_stage_donut(matches),
        )

    @app.callback(
        Output("performers-ranking", "figure"),
        Output("performers-scatter", "figure"),
        Output("performers-table", "data"),
        Output("performers-table", "columns"),
        Input("performers-edition", "value"),
        Input("performers-metric", "value"),
        Input("performers-topn", "value"),
    )
    def _update_performers(edition, metric, top_n):
        stats = data_loader.load_player_stats(edition)
        ranking = performers.ranking_bar(stats, metric, top_n)
        scatter = performers.xg_vs_goals_scatter(stats, top_n)
        table_df = _round_df(stats.sort_values(metric, ascending=False).head(top_n))
        cols = [{"name": label, "id": key} for key, label in TABLE_COLUMNS
                if key in table_df.columns]
        data = table_df[[c["id"] for c in cols]].to_dict("records")
        return ranking, scatter, data, cols

    @app.callback(
        Output("player-select", "options"),
        Output("player-select", "value"),
        Input("player-edition", "value"),
    )
    def _update_player_options(edition):
        stats = data_loader.load_player_stats(edition)
        top = stats.sort_values("score", ascending=False).head(40)
        options = [
            {"label": f"{r['player']} ({r['team']})", "value": int(r["player_id"])}
            for _, r in top.iterrows()
        ]
        value = options[0]["value"] if options else None
        return options, value

    @app.callback(
        Output("player-radar", "figure"),
        Output("player-shotmap", "figure"),
        Output("player-timeline", "figure"),
        Input("player-edition", "value"),
        Input("player-select", "value"),
    )
    def _update_player(edition, player_id):
        stats = data_loader.load_player_stats(edition)
        name = ""
        if player_id is not None:
            row = stats[stats["player_id"] == player_id]
            name = row.iloc[0]["player"] if not row.empty else ""
        shots = (
            data_loader.load_player_shots(edition, player_id)
            if player_id is not None else pd.DataFrame()
        )
        events = data_loader.load_events(edition)
        return (
            player_profile.radar(stats, player_id),
            player_profile.shot_map(shots, name),
            player_profile.contributions_timeline(events, player_id, name),
        )

    editions = list(EDITIONS.keys())
    edition_a, edition_b = editions[0], editions[-1]

    @app.callback(
        Output("comparison-kpis", "figure"),
        Output("comparison-scorers", "figure"),
        Input("tabs", "active_tab"),
    )
    def _update_comparison(_active_tab):
        stats_a = data_loader.load_player_stats(edition_a)
        stats_b = data_loader.load_player_stats(edition_b)
        label_a = EDITIONS[edition_a]["label"]
        label_b = EDITIONS[edition_b]["label"]
        return (
            comparison.edition_kpi_comparison(stats_a, label_a, stats_b, label_b),
            comparison.top_scorers_side_by_side(stats_a, label_a, stats_b, label_b),
        )
