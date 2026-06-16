# Dashboard Mundial FIFA con StatsBomb y Dash

Dashboard interactivo en **Dash (Plotly)** que analiza a los jugadores más
destacados de los Mundiales **2018** y **2022** usando los datos abiertos de
**StatsBomb** (`statsbombpy`). Las estadísticas por jugador (goles, xG,
asistencias, minutos, etc.) se calculan a partir de los eventos del torneo y se
cachean en Parquet para que el dashboard arranque en segundos.

> Nota: StatsBomb open data no incluye el Mundial 2026 porque aún no se ha
> jugado. Por eso el dashboard usa las dos ediciones más recientes disponibles.

## Estructura

```
Wrld_Cup_Predict/
├── requirements.txt
├── scripts/
│   └── build_cache.py          # Descarga datos y genera el cache (1 vez)
├── src/
│   ├── config.py               # IDs de torneo, rutas y parámetros
│   ├── data_loader.py          # Descarga statsbombpy + lectura del cache
│   ├── player_aggregates.py    # Métricas por jugador desde eventos
│   └── minutes.py              # Minutos jugados por jugador
├── app/
│   ├── app.py                  # Entry point del dashboard
│   ├── layout.py               # Layout con las 4 pestañas
│   ├── callbacks.py            # Interactividad
│   └── figures/                # Figuras Plotly por sección
└── data/processed/             # Cache Parquet (generado)
```

## Instalación

Requiere Python 3.11+.

En Windows, si `python` no funciona, usa el launcher **`py`** (viene con la
instalación de Python):

```powershell
py -m pip install -r requirements.txt
```

En Linux/macOS:

```bash
pip install -r requirements.txt
```

## Uso

1. Generar el cache de datos (descarga ~128 partidos desde StatsBomb; tarda unos
   minutos la primera vez):

```powershell
py scripts/build_cache.py
```

2. Lanzar el dashboard:

```powershell
py app/app.py
```

En Windows también puedes hacer doble clic en **`run.bat`** o ejecutar:

```powershell
.\run.ps1
```

Abre [http://127.0.0.1:8050](http://127.0.0.1:8050) en el navegador.

Para acelerar la descarga puedes fijar el número de núcleos:

```bash
# PowerShell
$env:SB_CORES=4; python scripts/build_cache.py
```

## Pestañas del dashboard

- **Resumen**: KPIs del torneo, máximos goleadores, goles por selección y por fase.
- **Top performers**: ranking configurable (goles, xG, asistencias, minutos o
  score compuesto), scatter de xG vs goles y tabla filtrable.
- **Perfil de jugador**: radar de percentiles, mapa de tiros sobre el campo y
  línea de tiempo de goles y asistencias.
- **Comparativa 2018 vs 2022**: totales del torneo y goleadores por edición.

## Métricas y score compuesto

Las métricas se derivan de los eventos (`shot_statsbomb_xg`, `pass_goal_assist`,
etc.). Los goles y tiros excluyen las tandas de penales. El ranking por defecto
usa un score compuesto y normalizado configurable en
[`src/config.py`](src/config.py):

```python
SCORE_WEIGHTS = {"goals": 0.35, "xg": 0.30, "assists": 0.20, "minutes": 0.15}
```

## Atribución

Fuente de datos: **StatsBomb Open Data**
(<https://github.com/statsbomb/open-data>). El uso de estos datos está sujeto al
acuerdo de usuario de StatsBomb; al publicar análisis se debe citar a StatsBomb
como fuente.
