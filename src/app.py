"""AtaraxiaDive — FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="AtaraxiaDive", version="0.1.0")


@app.get("/health", response_class=JSONResponse)
async def health_check() -> dict[str, str]:
    """Health-check endpoint — verifica que la aplicación está activa."""
    return {"status": "ok"}

# Routers de cada BC se registran aquí al implementar cada incremento
