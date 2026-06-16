"""Cálculo de minutos jugados por jugador a partir de eventos de un partido.

StatsBomb open data no expone estadísticas agregadas de jugador, así que los
minutos se derivan de los eventos: quién entró/salió en cada sustitución y la
duración total del partido (último minuto registrado, incluyendo descuentos).
"""
from __future__ import annotations

import pandas as pd


def _name_to_id(match_events: pd.DataFrame) -> dict:
    pairs = match_events[["player", "player_id"]].dropna()
    return dict(zip(pairs["player"], pairs["player_id"].astype(int)))


def minutes_for_match(match_events: pd.DataFrame) -> pd.DataFrame:
    """Devuelve minutos jugados por jugador en un único partido.

    Columnas de salida: ``player_id``, ``minutes``.
    """
    if match_events.empty or "player_id" not in match_events.columns:
        return pd.DataFrame(columns=["player_id", "minutes"])

    match_end = float(match_events["minute"].max() or 0)
    name_to_id = _name_to_id(match_events)

    came_on: dict[int, float] = {}
    went_off: dict[int, float] = {}

    if "type" in match_events.columns:
        subs = match_events[match_events["type"] == "Substitution"]
        for _, row in subs.iterrows():
            minute = float(row.get("minute", 0) or 0)
            off_id = row.get("player_id")
            if pd.notna(off_id):
                went_off[int(off_id)] = minute
            replacement = row.get("substitution_replacement")
            if pd.notna(replacement) and replacement in name_to_id:
                came_on[name_to_id[replacement]] = minute

    records = []
    for player_id in match_events["player_id"].dropna().unique():
        pid = int(player_id)
        start = came_on.get(pid, 0.0)
        end = went_off.get(pid, match_end)
        records.append({"player_id": pid, "minutes": max(0.0, end - start)})

    return pd.DataFrame(records)


def minutes_for_tournament(events: pd.DataFrame) -> pd.DataFrame:
    """Suma de minutos por jugador en todo el torneo.

    Columnas de salida: ``player_id``, ``minutes``.
    """
    if events.empty or "match_id" not in events.columns:
        return pd.DataFrame(columns=["player_id", "minutes"])

    per_match = [
        minutes_for_match(group) for _, group in events.groupby("match_id")
    ]
    per_match = [df for df in per_match if not df.empty]
    if not per_match:
        return pd.DataFrame(columns=["player_id", "minutes"])

    return (
        pd.concat(per_match, ignore_index=True)
        .groupby("player_id", as_index=False)["minutes"]
        .sum()
    )
