"""Entry point del dashboard Dash del Mundial (datos StatsBomb)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dash
import dash_bootstrap_components as dbc

from app.callbacks import register_callbacks
from app.layout import serve_layout
from src import data_loader

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Mundial · StatsBomb",
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = serve_layout
register_callbacks(app)


def main() -> None:
    if not data_loader.cache_exists():
        print(
            "AVISO: no se encontró el cache de datos.\n"
            "Ejecuta primero:  python scripts/build_cache.py\n"
        )
    app.run(debug=True, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
