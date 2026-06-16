"""Agregación de estadísticas por jugador a partir de eventos de StatsBomb."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import SCORE_WEIGHTS
from src.minutes import minutes_for_tournament


def _col(events: pd.DataFrame, name: str, default=np.nan) -> pd.Series:
    """Devuelve la columna si existe; si no, una serie del valor por defecto."""
    if name in events.columns:
        return events[name]
    return pd.Series(default, index=events.index)


def _xg_assisted(events: pd.DataFrame) -> pd.DataFrame:
    """xG asistido (proxy de xA): xG del tiro generado por cada pase clave."""
    if "shot_key_pass_id" not in events.columns or "id" not in events.columns:
        return pd.DataFrame(columns=["player_id", "xa"])

    shots = events[events["type"] == "Shot"].copy()
    shots = shots[shots["shot_key_pass_id"].notna()]
    if shots.empty:
        return pd.DataFrame(columns=["player_id", "xa"])

    shots = shots[["shot_key_pass_id", "shot_statsbomb_xg"]].rename(
        columns={"shot_key_pass_id": "id", "shot_statsbomb_xg": "xa"}
    )
    passes = events[["id", "player_id"]].dropna(subset=["id"])
    merged = passes.merge(shots, on="id", how="inner")
    if merged.empty:
        return pd.DataFrame(columns=["player_id", "xa"])
    return merged.groupby("player_id", as_index=False)["xa"].sum()


def _normalize(series: pd.Series) -> pd.Series:
    rng = series.max() - series.min()
    if rng == 0 or pd.isna(rng):
        return pd.Series(0.0, index=series.index)
    return (series - series.min()) / rng


def build_player_stats(events: pd.DataFrame) -> pd.DataFrame:
    """Calcula la tabla de estadísticas por jugador para un torneo completo."""
    if events.empty:
        return pd.DataFrame()

    events = events.copy()
    events["type"] = _col(events, "type")
    has_player = events["player_id"].notna() if "player_id" in events.columns else None
    if has_player is None:
        return pd.DataFrame()
    events = events[has_player]
    events["player_id"] = events["player_id"].astype(int)

    shots = events[events["type"] == "Shot"].copy()
    # Excluir la tanda de penales (period 5) para no inflar goles/tiros.
    if "period" in shots.columns:
        shots = shots[shots["period"] != 5]
    shots["shot_outcome"] = _col(shots, "shot_outcome")
    shots["shot_statsbomb_xg"] = _col(shots, "shot_statsbomb_xg").fillna(0.0)
    shots["shot_type"] = _col(shots, "shot_type")
    # Excluir penaltis del xG open-play-ish y de tiros para no inflar.
    non_pen = shots[shots["shot_type"] != "Penalty"]

    goals = (
        shots[shots["shot_outcome"] == "Goal"]
        .groupby("player_id")
        .size()
        .rename("goals")
    )
    xg = non_pen.groupby("player_id")["shot_statsbomb_xg"].sum().rename("xg")
    shot_count = shots.groupby("player_id").size().rename("shots")

    passes = events[events["type"] == "Pass"].copy()
    passes["pass_goal_assist"] = _col(passes, "pass_goal_assist")
    passes["pass_shot_assist"] = _col(passes, "pass_shot_assist")
    assists = (
        passes[passes["pass_goal_assist"] == True]  # noqa: E712
        .groupby("player_id")
        .size()
        .rename("assists")
    )
    key_passes = (
        passes[passes["pass_shot_assist"] == True]  # noqa: E712
        .groupby("player_id")
        .size()
        .rename("key_passes")
    )

    dribbles = events[events["type"] == "Dribble"].copy()
    dribbles["dribble_outcome"] = _col(dribbles, "dribble_outcome")
    dribbles_completed = (
        dribbles[dribbles["dribble_outcome"] == "Complete"]
        .groupby("player_id")
        .size()
        .rename("dribbles_completed")
    )

    matches_played = (
        events.groupby("player_id")["match_id"].nunique().rename("matches")
    )

    # Identidad del jugador: nombre y equipo más frecuentes.
    identity = (
        events.dropna(subset=["player"])
        .groupby("player_id")
        .agg(player=("player", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
             team=("team", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]))
    )

    minutes = minutes_for_tournament(events).set_index("player_id")["minutes"]
    xa = _xg_assisted(events)
    xa = xa.set_index("player_id")["xa"] if not xa.empty else pd.Series(dtype=float, name="xa")

    stats = pd.concat(
        [
            identity,
            goals,
            xg,
            shot_count,
            assists,
            key_passes,
            dribbles_completed,
            matches_played,
            minutes,
            xa,
        ],
        axis=1,
    )

    numeric_cols = [
        "goals", "xg", "shots", "assists", "key_passes",
        "dribbles_completed", "matches", "minutes", "xa",
    ]
    for col in numeric_cols:
        if col not in stats.columns:
            stats[col] = 0.0
        stats[col] = stats[col].fillna(0.0)

    stats["goals_p90"] = np.where(stats["minutes"] > 0, stats["goals"] / stats["minutes"] * 90, 0.0)
    stats["xg_p90"] = np.where(stats["minutes"] > 0, stats["xg"] / stats["minutes"] * 90, 0.0)

    stats["score"] = (
        SCORE_WEIGHTS["goals"] * _normalize(stats["goals"])
        + SCORE_WEIGHTS["xg"] * _normalize(stats["xg"])
        + SCORE_WEIGHTS["assists"] * _normalize(stats["assists"])
        + SCORE_WEIGHTS["minutes"] * _normalize(stats["minutes"])
    ) * 100

    stats = stats.reset_index()
    return stats.sort_values("score", ascending=False).reset_index(drop=True)
