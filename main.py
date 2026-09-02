from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine, Base
from backend.routers import (
    auth, chambas, postulaciones, verificaciones, 
    pagos, chat, notificaciones, resenas, estimador, reportes, admin, support
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API REST de Producción para CHAMBA RD — Conectando clientes y técnicos profesionales en República Dominicana.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(chambas.router, prefix="/api/v1")
app.include_router(postulaciones.router, prefix="/api/v1")
app.include_router(verificaciones.router, prefix="/api/v1")
app.include_router(pagos.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(notificaciones.router, prefix="/api/v1")
app.include_router(resenas.router, prefix="/api/v1")
app.include_router(estimador.router, prefix="/api/v1")
app.include_router(reportes.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(support.router, prefix="/api/v1")

import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# PWA Support Endpoints
@app.get("/manifest.webmanifest")
def serve_manifest():
    if os.path.exists("manifest.webmanifest"):
        return FileResponse("manifest.webmanifest", media_type="application/manifest+json")
    if os.path.exists("public/manifest.webmanifest"):
        return FileResponse("public/manifest.webmanifest", media_type="application/manifest+json")
    return {"name": "CHAMBA RD", "short_name": "CHAMBA RD"}

@app.get("/sw.js")
def serve_service_worker():
    if os.path.exists("sw.js"):
        return FileResponse("sw.js", media_type="application/javascript")
    if os.path.exists("public/sw.js"):
        return FileResponse("public/sw.js", media_type="application/javascript")
    return {"error": "sw not found"}

if os.path.exists("public/icons"):
    app.mount("/icons", StaticFiles(directory="public/icons"), name="icons")
elif os.path.exists("icons"):
    app.mount("/icons", StaticFiles(directory="icons"), name="icons")

if os.path.exists("public"):
    app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/")
def root():
    # If index.html exists, serve the PWA root directly
    if os.path.exists("index.html"):
        return FileResponse("index.html", media_type="text/html")
    if os.path.exists("public/index.html"):
        return FileResponse("public/index.html", media_type="text/html")
    return {
        "app": "CHAMBA RD API",
        "status": "online",
        "version": "1.0.0",
        "region": "República Dominicana 🇩🇴",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
