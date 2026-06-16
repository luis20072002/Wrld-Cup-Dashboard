"""Configuración central del proyecto: torneos, rutas y parámetros del dashboard."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

COMPETITION_ID = 43  # FIFA World Cup (StatsBomb open data)

# Ediciones cubiertas por el dashboard. StatsBomb open data no incluye 2026
# (aún no se ha jugado), por lo que se usan las dos ediciones más recientes.
EDITIONS = {
    "2018": {"season_id": 3, "label": "Mundial 2018"},
    "2022": {"season_id": 106, "label": "Mundial 2022"},
}

DEFAULT_EDITION = "2022"
DEFAULT_TOP_N = 15
TOP_N_RANGE = (5, 25)

# Pesos del score compuesto usado como ranking por defecto. Cada componente se
# normaliza 0-1 dentro del torneo antes de aplicar el peso.
SCORE_WEIGHTS = {
    "goals": 0.35,
    "xg": 0.30,
    "assists": 0.20,
    "minutes": 0.15,
}

# Métricas seleccionables para ordenar el ranking de top performers.
RANKING_METRICS = {
    "score": "Score compuesto",
    "goals": "Goles",
    "xg": "xG",
    "assists": "Asistencias",
    "minutes": "Minutos",
}

STATSBOMB_CREDIT = "Fuente de datos: StatsBomb Open Data"

PITCH_LENGTH = 120.0
PITCH_WIDTH = 80.0


def events_path(edition: str) -> Path:
    return PROCESSED_DIR / f"events_{edition}.parquet"


def player_stats_path(edition: str) -> Path:
    return PROCESSED_DIR / f"player_stats_{edition}.parquet"


def matches_path(edition: str) -> Path:
    return PROCESSED_DIR / f"matches_{edition}.parquet"
