"""Descarga datos del Mundial desde StatsBomb open data y los cachea en Parquet.

Ejecutar una sola vez (o cuando se quiera refrescar):

    python scripts/build_cache.py

Genera, por cada edición configurada en src/config.EDITIONS:
    data/processed/matches_<edition>.parquet
    data/processed/events_<edition>.parquet      (versión slim para el dashboard)
    data/processed/player_stats_<edition>.parquet
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.data_loader import fetch_from_statsbomb
from src.player_aggregates import build_player_stats

# Columnas que se conservan en la versión slim de eventos (apta para Parquet y
# suficiente para el mapa de tiros y la línea de tiempo del perfil de jugador).
SLIM_COLUMNS = [
    "match_id", "period", "minute", "second", "type", "team", "player",
    "player_id", "location_x", "location_y", "shot_outcome",
    "shot_statsbomb_xg", "shot_type", "pass_goal_assist", "pass_shot_assist",
]


def _split_location(events: pd.DataFrame) -> pd.DataFrame:
    """Convierte la columna 'location' (lista [x, y]) en dos columnas float."""
    if "location" in events.columns:
        loc = events["location"].apply(
            lambda v: v if isinstance(v, (list, tuple)) and len(v) == 2 else (np.nan, np.nan)
        )
        events["location_x"] = loc.apply(lambda v: v[0])
        events["location_y"] = loc.apply(lambda v: v[1])
    else:
        events["location_x"] = np.nan
        events["location_y"] = np.nan
    return events


def _make_slim(events: pd.DataFrame) -> pd.DataFrame:
    events = _split_location(events.copy())
    for col in SLIM_COLUMNS:
        if col not in events.columns:
            events[col] = np.nan

    is_shot = events["type"] == "Shot"
    is_assist = events.get("pass_goal_assist") == True  # noqa: E712
    is_key_pass = events.get("pass_shot_assist") == True  # noqa: E712
    slim = events[is_shot | is_assist | is_key_pass][SLIM_COLUMNS].copy()

    slim["player_id"] = slim["player_id"].astype("Int64")
    return slim.reset_index(drop=True)


def build_edition(edition: str, season_id: int) -> None:
    print(f"\n=== {config.EDITIONS[edition]['label']} (season_id={season_id}) ===")
    print("Descargando partidos y eventos desde StatsBomb...")
    matches, events = fetch_from_statsbomb(season_id)
    print(f"  {len(matches)} partidos, {len(events):,} eventos.")

    print("Calculando estadísticas por jugador...")
    player_stats = build_player_stats(events)
    print(f"  {len(player_stats)} jugadores agregados.")

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    matches.to_parquet(config.matches_path(edition), index=False)
    _make_slim(events).to_parquet(config.events_path(edition), index=False)
    player_stats.to_parquet(config.player_stats_path(edition), index=False)
    print(f"  Guardado en {config.PROCESSED_DIR}")


def main() -> None:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for edition, meta in config.EDITIONS.items():
        build_edition(edition, meta["season_id"])
    print("\nCache completo. Ahora ejecuta: python app/app.py")


if __name__ == "__main__":
    main()
