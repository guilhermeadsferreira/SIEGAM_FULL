from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.routes import alerts_routes

app = FastAPI(title="Modulo Envios API", version="1.0")

app.include_router(alerts_routes.router)

@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})
