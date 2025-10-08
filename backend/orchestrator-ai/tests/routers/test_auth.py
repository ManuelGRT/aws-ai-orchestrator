import sys
import types
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI


class DummyCognitoClient:
    """Simula el cliente boto3 de Cognito."""
    class exceptions:
        class NotAuthorizedException(Exception):
            pass

    def initiate_auth(self, **kwargs):
        # Respuesta válida simulada
        return {
            "AuthenticationResult": {
                "IdToken": "id123",
                "AccessToken": "access123",
                "RefreshToken": "refresh123",
                "ExpiresIn": 3600,
                "TokenType": "Bearer"
            }
        }

fake_boto3 = types.ModuleType("boto3")
fake_boto3.client = lambda *a, **k: DummyCognitoClient()
sys.modules["boto3"] = fake_boto3

from api.routers import auth

# App temporal de test
app = FastAPI()
app.include_router(auth.router)
client = TestClient(app)


def test_authorize_success(monkeypatch):
    class DummyCognito:
        def initiate_auth(self, **kwargs):
            return {
                "AuthenticationResult": {
                    "IdToken": "id123",
                    "AccessToken": "access123",
                    "RefreshToken": "refresh123",
                    "ExpiresIn": 3600,
                    "TokenType": "Bearer",
                }
            }

        class exceptions:
            class NotAuthorizedException(Exception):
                pass

    monkeypatch.setattr(auth, "cog", DummyCognito())

    response = client.get("/authorize")
    assert response.status_code == 200
    data = response.json()
    assert data["id_token"] == "id123"
    assert data["access_token"] == "access123"
    assert data["refresh_token"] == "refresh123"


def test_authorize_invalid_credentials(monkeypatch):
    class DummyCognito:
        class exceptions:
            class NotAuthorizedException(Exception):
                pass

        def initiate_auth(self, **kwargs):
            raise self.exceptions.NotAuthorizedException("Invalid creds")

    monkeypatch.setattr(auth, "cog", DummyCognito())

    response = client.get("/authorize")
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.text


def test_authorize_missing_auth_result(monkeypatch):
    class DummyCognito:
        def initiate_auth(self, **kwargs):
            return {}
        class exceptions:
            class NotAuthorizedException(Exception):
                pass

    monkeypatch.setattr(auth, "cog", DummyCognito())

    response = client.get("/authorize")
    assert response.status_code == 400
    assert "Credenciales inválidas" in response.text


def test_authorize_generic_exception(monkeypatch):
    class DummyCognito:
        class exceptions:
            class NotAuthorizedException(Exception):
                pass

        def initiate_auth(self, **kwargs):
            raise Exception("Unexpected error")

    monkeypatch.setattr(auth, "cog", DummyCognito())

    response = client.get("/authorize")
    assert response.status_code == 400
    assert "Unexpected error" in response.text