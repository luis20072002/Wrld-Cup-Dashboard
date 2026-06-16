"""Acceso a los datos cacheados en Parquet y descarga vía statsbombpy."""
from __future__ import annotations

import warnings
from functools import lru_cache

import pandas as pd

from src import config


def _load_parquet(path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró {path}. Ejecuta primero 'python scripts/build_cache.py'."
        )
    return pd.read_parquet(path)


@lru_cache(maxsize=None)
def load_player_stats(edition: str) -> pd.DataFrame:
    return _load_parquet(config.player_stats_path(edition))


@lru_cache(maxsize=None)
def load_matches(edition: str) -> pd.DataFrame:
    return _load_parquet(config.matches_path(edition))


@lru_cache(maxsize=None)
def load_events(edition: str) -> pd.DataFrame:
    return _load_parquet(config.events_path(edition))


def load_player_shots(edition: str, player_id: int) -> pd.DataFrame:
    """Tiros de un jugador concreto (para el mapa de tiros del perfil)."""
    events = load_events(edition)
    shots = events[(events["type"] == "Shot") & (events["player_id"] == player_id)]
    if "period" in shots.columns:
        shots = shots[shots["period"] != 5]
    return shots.copy()


def cache_exists() -> bool:
    return all(
        config.player_stats_path(ed).exists() for ed in config.EDITIONS
    )


def fetch_from_statsbomb(season_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Descarga partidos y eventos de un torneo desde StatsBomb open data.

    Devuelve ``(matches, events)``. Los eventos se concatenan partido a partido
    para garantizar la columna ``match_id``.
    """
    from statsbombpy import sb
    from statsbombpy.api_client import NoAuthWarning

    warnings.simplefilter("ignore", NoAuthWarning)

    matches = sb.matches(competition_id=config.COMPETITION_ID, season_id=season_id)

    all_events = []
    for match_id in matches["match_id"].tolist():
        ev = sb.events(match_id=int(match_id))
        if "match_id" not in ev.columns:
            ev["match_id"] = int(match_id)
        all_events.append(ev)

    events = pd.concat(all_events, ignore_index=True)
    return matches, events
