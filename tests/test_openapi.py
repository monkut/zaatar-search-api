"""/openapi/ YAML endpoint test."""

import yaml


class TestOpenapiEndpoint:
    def test_openapi_json(self, client):
        response = client.get("/openapi/openapi.json")
        assert response.status_code == 200
        data = response.get_json()
        assert "openapi" in data
        assert "paths" in data
        assert "/web_search" in data["paths"]
        assert "/web_fetch" in data["paths"]

    def test_openapi_yaml(self, client):
        response = client.get("/openapi/yaml")
        assert response.status_code == 200
        assert response.content_type == "text/yaml; charset=utf-8"
        spec = yaml.safe_load(response.data)
        assert "openapi" in spec
        assert "/web_search" in spec["paths"]
        assert "/web_fetch" in spec["paths"]

    def test_openapi_spec_info(self, client):
        response = client.get("/openapi/openapi.json")
        data = response.get_json()
        assert data["info"]["title"] == "Zaatar Search API"
        assert data["info"]["version"] == "0.1.0"
