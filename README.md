# GA-Based Delivery Route Optimizer and Shortest Route Finder

A professional, portfolio-ready Streamlit application for shortest path discovery and GA-based multi-stop delivery route optimization.

## Features

- Single route finder (source to destination)
  - Supports place names and direct `lat,lon` inputs
  - Uses OpenRouteService (ORS) for real drivable route geometry
  - Shows distance, duration, and route map
- Multi-stop delivery optimizer
  - Accepts start, multiple stops, and optional end point
  - Uses permutation-based Genetic Algorithm (GA) for stop order optimization
  - Compares original vs optimized route cost
  - Renders final optimized route on interactive map
- Data and output support
  - CSV-based sample data in `data/raw`
  - Writes optimized route summaries to `data/processed`
  - Saves maps/reports to `outputs`
  - Saves best route metadata to `models/saved`
- Deployment readiness
  - `.env` / Streamlit secrets based API key loading
  - `requirements.txt`, `.streamlit/config.toml`, test suite with `pytest`

## Project Structure

- `app.py`: Streamlit entry point
- `src/api`: ORS + geocoding integrations
- `src/core`: main route and optimization engines
- `src/app_ui`: Streamlit UI components
- `src/visualization`: map/route plotting helpers
- `src/utils`: validators, file IO, helpers, logging
- `models`: GA optimizer and fitness logic
- `tests`: meaningful unit tests

## Setup

### 1. Create and activate virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API key

Option A: `.env`

```env
OPENROUTESERVICE_API_KEY=your_real_key
```

Option B: `.streamlit/secrets.toml`

```toml
OPENROUTESERVICE_API_KEY = "your_real_key"
```

## Run the App

From project root:

```bash
streamlit run app.py
```

## Run Tests

```bash
pytest
```

## Genetic Algorithm (Short Explanation)

The optimizer treats each candidate solution as a permutation of delivery stop indices.

- Chromosome: stop order permutation
- Fitness: inverse of route cost
- Selection: tournament
- Crossover: ordered crossover (permutation-safe)
- Mutation: swap mutation
- Elitism: top candidates survive each generation

Route cost during GA is computed using a fast haversine matrix for speed. After best order is found, ORS is used to fetch realistic drivable route geometry and summary.

## Local and Cloud Deployment Notes

- The app is designed for local execution and Streamlit Cloud deployment.
- Never commit real API keys.
- Keep `.streamlit/secrets.toml` private.

## Deploy on Streamlit Community Cloud (GitHub)

### 1. Push project to GitHub

- Push this repository to GitHub (public or private).
- Keep `app.py` at repository root (already done in this project).

### 2. Keep required files in repo

- `app.py` (Streamlit entrypoint)
- `requirements.txt` (Python dependencies)
- `.streamlit/config.toml` (Streamlit app config)
- `runtime.txt` (Python runtime for cloud build)

### 3. Configure secrets in Streamlit Cloud

Do not upload real keys in GitHub. In Streamlit Cloud, open app settings and add:

```toml
OPENROUTESERVICE_API_KEY = "your_real_key"
```

### 4. Create app in Streamlit Community Cloud

- Go to Streamlit Community Cloud and click **New app**.
- Select your GitHub repository and branch.
- Set main file path to `app.py`.
- Click **Deploy**.

### 5. Redeploy on updates

- Every push to the selected branch triggers a new deployment.
- If requirements change, Streamlit Cloud automatically rebuilds environment.

## Future Improvements

- Optional ORS matrix API integration for road-network-based GA cost
- Time window and vehicle constraints (VRP-lite)
- Better caching for repeated route calls
- Downloadable PDF report generation
