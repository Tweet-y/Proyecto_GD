# Análisis y visualización de tendencias epidemiológicas globales

Proyecto del curso de Gestión de Datos. Procesa, analiza y visualiza los reportes de COVID-19 de Johns Hopkins University (JHU CSSE) con Python, Pandas, NumPy, Matplotlib, Seaborn y un dashboard en Streamlit y Plotly.

El periodo que se puede consultar va del 22 de enero de 2020 al 9 de marzo de 2023, que es hasta donde llega la serie global de JHU. Los recuperados dejan de estar publicados el 4 de agosto de 2021: en esas fechas el dashboard muestra «Sin reporte» en vez de un cero. Al abrirlo, `dashboard/data.py` descarga las series temporales desde el repositorio de JHU. Hace falta conexión a internet.

## Requisitos

- Python 3.10 o superior
- Conexión a internet la primera vez que se abre el dashboard

## Instalación

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
```

Activar el entorno:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (cmd)
.\.venv\Scripts\activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias del dashboard:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para los notebooks de limpieza, análisis y mapas, instalar además:

```bash
python -m pip install -r requirements-notebooks.txt
python -m ipykernel install --user --name gd-covid --display-name "Python (GD COVID)"
```

`geopandas` y `contextily` arrastran librerías geoespaciales. Si esa instalación falla, el dashboard sigue funcionando: solo se pierden los mapas de `03_visualizaciones.ipynb`.

## Ejecutar el dashboard

Con el entorno activado, desde la raíz del repositorio:

```bash
python -m streamlit run dashboard/main.py
```

Streamlit abre http://localhost:8501. La primera carga descarga tres CSV de JHU y puede tardar unos segundos. El caché dura una hora.

El comando tiene que ser `dashboard/main.py`. No existe un `main.py` en la raíz, y los módulos `data`, `metrics` y `ui` se importan desde la carpeta `dashboard/`.

## Notebooks

Ejecutarlos en este orden, con el kernel del entorno virtual:

1. `01_limpieza_datos.ipynb` o `01_limpieza_datos_optimizado.ipynb`
2. `02_analisis_exploratorio.ipynb` o `02_analisis_exploratorio_optimizado.ipynb`
3. `03_visualizaciones.ipynb` o `03_visualizaciones_optimizado.ipynb`

Las versiones `*_optimizado` usan Dask y guardan Parquet en `data/`. `time` y `datetime` son de la biblioteca estándar: no hay que instalarlos con pip.

## Estructura

- `dashboard/main.py`: filtros, métricas y las dos vistas (dashboard y tabla).
- `dashboard/ui.py`: estilos y componentes visuales.
- `dashboard/data.py`: descarga, limpieza y mapeo de continentes de las series JHU.
- `dashboard/metrics.py`: casos nuevos, medias móviles, picos y alerta de rebrote.
- `data/`: Parquet generados por los notebooks.
- `covid_clean_enero2021.csv`, `perfilado.html`, `grafico_regresion_por_pais.png`: salidas del análisis.
- `requirements.txt`: dependencias del dashboard.
- `requirements-notebooks.txt`: dependencias de los notebooks, incluye las del dashboard.

## Problemas frecuentes

**`streamlit` no se reconoce como comando.** El entorno no está activado, o el ejecutable no está en el `PATH`. Usar `python -m streamlit run dashboard/main.py`.

**`ModuleNotFoundError: No module named 'data'` (o `ui` / `metrics`).** El comando se lanzó como `streamlit run main.py` o desde dentro de otra carpeta. Volver a la raíz del repositorio y usar `python -m streamlit run dashboard/main.py`.

**`ModuleNotFoundError` de `streamlit`, `pandas` o `plotly`.** El `pip` no es el del entorno virtual. Con el entorno activado: `python -m pip install -r requirements.txt`.

**El dashboard dice que no pudo cargar los datos.** No hay acceso a `raw.githubusercontent.com`, o JHU cambió la ruta de los CSV. Revisar la conexión y el mensaje de error que muestra la app.

**PowerShell bloquea la activación.** Ejecutar una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y volver a activar el entorno.
