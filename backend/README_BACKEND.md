# NeuroNav Backend

This repository implements the mode-correct backend for NeuroNav routing.

## Requirements

Ensure you are located inside the `backend` folder and your virtual environment is activated.
```bash
python -m venv .venv
# source .venv/bin/activate  # Mac / Linux
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Setup Environment

Create a `.env` file from the example:
```bash
cp .env.example .env
```
Populate the routing and signals provider keys if using production variables, otherwise default settings have simulated fallbacks.

## Execution

Start the FastAPI application.

```bash
uvicorn main:app --reload
```
Access the swagger API docs at `http://127.0.0.1:8000/docs`.

## Testing

A comprehensive test suite validates API limits, bounding boxes, and routing modes.

```bash
pytest
```

## Migration Notes
- Replaced monolithic `routing` and `scoring` logic with an interconnected robust engine logic (`utils/config.py`, `utils/geometry.py`, `utils/cache.py`).
- Integrated specific route constraints, returning exactly "Preferred Route" and "Longest Route" to map to the new UI requirements.
- Standardized `models.py` for API requests and response definitions.
