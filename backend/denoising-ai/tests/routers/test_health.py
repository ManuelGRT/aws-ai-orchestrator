import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.routers import health as health_router  # tu archivo con el router de health

# Crear app de test
app = FastAPI()
app.include_router(health_router.router)
client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"health": "OK"}  # coincide con tu función
