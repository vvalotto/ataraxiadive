"""AtaraxiaDive — FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from competencia.api.router import router as competencia_router

app = FastAPI(title="AtaraxiaDive", version="0.1.0")

app.include_router(competencia_router)


@app.get("/health", response_class=JSONResponse)
async def health_check() -> dict[str, str]:
    """Health-check endpoint — verifica que la aplicación está activa."""
    return {"status": "ok"}
