"""Exporta capturas PNG y un informe HTML estático para el README público.

Requiere cache generado previamente con scripts/build_cache.py.

    py scripts/export_previews.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config, data_loader
from app.figures import comparison, overview, performers, player_profile

DOCS_DIR = config.PROJECT_ROOT / "docs"
PREVIEW_DIR = DOCS_DIR / "preview"
REPORT_PATH = DOCS_DIR / "report.html"

IMAGE_OPTS = dict(width=960, height=540, scale=2)


def _save_png(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(str(path), **IMAGE_OPTS)
    print(f"  PNG -> {path.relative_to(config.PROJECT_ROOT)}")


def _build_figures():
    stats_2018 = data_loader.load_player_stats("2018")
    stats_2022 = data_loader.load_player_stats("2022")
    matches_2022 = data_loader.load_matches("2022")

    top_2022 = stats_2022.sort_values("score", ascending=False).iloc[0]
    top_player_id = int(top_2022["player_id"])
    top_player_name = str(top_2022["player"])

    figures = [
        ("overview_scorers_2022.png", "Máximos goleadores — Mundial 2022",
         overview.top_scorers_bar(stats_2022)),
        ("overview_teams_2022.png", "Goles por selección — Mundial 2022",
         overview.goals_by_team_bar(stats_2022)),
        ("performers_ranking_2022.png", "Top performers por score — Mundial 2022",
         performers.ranking_bar(stats_2022, "score", 15)),
        ("performers_scatter_2022.png", "xG vs goles — Mundial 2022",
         performers.xg_vs_goals_scatter(stats_2022, 15)),
        ("player_radar_top_2022.png", f"Perfil — {top_player_name} (2022)",
         player_profile.radar(stats_2022, top_player_id)),
        ("comparison_scorers.png", "Goleadores 2018 vs 2022",
         comparison.top_scorers_side_by_side(
             stats_2018, config.EDITIONS["2018"]["label"],
             stats_2022, config.EDITIONS["2022"]["label"],
         )),
        ("overview_stage_2022.png", "Goles por fase — Mundial 2022",
         overview.goals_by_stage_donut(matches_2022)),
    ]
    return figures, stats_2018, stats_2022


def _write_report(sections: list[tuple[str, object]]) -> None:
    parts = [
        "<!DOCTYPE html>",
        "<html lang='es'>",
        "<head>",
        "<meta charset='utf-8'/>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'/>",
        "<title>Mundial FIFA — Informe StatsBomb</title>",
        "<style>",
        "body{font-family:system-ui,sans-serif;background:#111;margin:0;padding:24px;color:#eee;}",
        "h1{font-size:1.5rem;margin-bottom:8px;}",
        "p{color:#aaa;margin-top:0;}",
        ".chart{background:#1b1d23;border-radius:8px;padding:12px;margin:24px 0;}",
        "footer{color:#666;font-size:0.85rem;margin-top:32px;border-top:1px solid #333;padding-top:16px;}",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Dashboard Mundial FIFA (2018 y 2022)</h1>",
        "<p>Vista previa estática generada desde StatsBomb Open Data. "
        "Gráficos interactivos (zoom, hover).</p>",
    ]
    for title, fig in sections:
        parts.append(f"<div class='chart'><h2>{title}</h2>")
        parts.append(fig.to_html(full_html=False, include_plotlyjs="cdn"))
        parts.append("</div>")
    parts.append(
        f"<footer>{config.STATSBOMB_CREDIT} · "
        "Código del proyecto bajo licencia MIT.</footer>"
    )
    parts.append("</body></html>")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"  HTML -> {REPORT_PATH.relative_to(config.PROJECT_ROOT)}")


def main() -> None:
    if not data_loader.cache_exists():
        print(
            "ERROR: no hay cache en data/processed/.\n"
            "Ejecuta primero: py scripts/build_cache.py"
        )
        sys.exit(1)

    print("Exportando vistas previas...")
    figure_specs, _, _ = _build_figures()
    html_sections = []
    for filename, title, fig in figure_specs:
        _save_png(fig, PREVIEW_DIR / filename)
        html_sections.append((title, fig))
    _write_report(html_sections)
    print("Exportación completa.")


if __name__ == "__main__":
    main()
