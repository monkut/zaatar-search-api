"""Ollama client unit tests."""

from unittest.mock import patch

import httpx
import pytest

from zaatar.clients.ollama import _is_model_available, pull_model, summarize


class TestIsModelAvailable:
    @patch("zaatar.clients.ollama.httpx.Client")
    def test_model_found(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={"models": [{"model": "gemma3:4b"}, {"model": "mistral:7b"}]},
            request=httpx.Request("GET", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        assert _is_model_available("gemma3:4b") is True

    @patch("zaatar.clients.ollama.httpx.Client")
    def test_model_not_found(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={"models": [{"model": "mistral:7b"}]},
            request=httpx.Request("GET", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        assert _is_model_available("gemma3:4b") is False

    @patch("zaatar.clients.ollama.httpx.Client")
    def test_no_models(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={"models": []},
            request=httpx.Request("GET", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        assert _is_model_available("gemma3:4b") is False


class TestPullModel:
    @patch("zaatar.clients.ollama._is_model_available", return_value=True)
    def test_pull_skipped_when_available(self, mock_available):
        pull_model("gemma3:4b")
        mock_available.assert_called_once_with("gemma3:4b")

    @patch("zaatar.clients.ollama.httpx.Client")
    @patch("zaatar.clients.ollama._is_model_available", return_value=False)
    def test_pull_model_when_not_available(self, _mock_available, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={"status": "success"},
            request=httpx.Request("POST", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.post.return_value = mock_response

        pull_model("gemma3:4b")

        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args
        assert call_kwargs[1]["json"]["model"] == "gemma3:4b"
        assert call_kwargs[1]["json"]["stream"] is False

    @patch("zaatar.clients.ollama.httpx.Client")
    @patch("zaatar.clients.ollama._is_model_available", return_value=False)
    def test_pull_model_http_error(self, _mock_available, mock_client_class):
        mock_response = httpx.Response(
            500,
            json={"error": "internal error"},
            request=httpx.Request("POST", "http://test"),
        )
        mock_response.raise_for_status = lambda: (_ for _ in ()).throw(
            httpx.HTTPStatusError("error", request=mock_response.request, response=mock_response)
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            pull_model("bad-model")


class TestSummarize:
    @patch("zaatar.clients.ollama.httpx.Client")
    def test_summarize_success(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={"response": "Python is a programming language used for web development."},
            request=httpx.Request("POST", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.post.return_value = mock_response

        results = [
            {"title": "Python", "url": "https://python.org", "description": "Python programming language"},
            {"title": "Flask", "url": "https://flask.palletsprojects.com", "description": "Flask web framework"},
        ]
        summary = summarize("python web development", results)

        assert summary == "Python is a programming language used for web development."
        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs[1]["json"]
        assert payload["model"] == "gemma3:4b"
        assert payload["stream"] is False
        assert "python web development" in payload["prompt"]

    @patch("zaatar.clients.ollama.httpx.Client")
    def test_summarize_empty_response(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={"response": ""},
            request=httpx.Request("POST", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.post.return_value = mock_response

        results = [{"title": "Test", "url": "https://example.com", "description": "desc"}]
        summary = summarize("test", results)

        assert summary == ""

    @patch("zaatar.clients.ollama.httpx.Client")
    def test_summarize_custom_model(self, mock_client_class):
        mock_response = httpx.Response(
            200,
            json={"response": "Summary text"},
            request=httpx.Request("POST", "http://test"),
        )
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.post.return_value = mock_response

        results = [{"title": "Test", "url": "https://example.com", "description": "desc"}]
        summarize("test", results, model="mistral:7b")

        call_kwargs = mock_client.post.call_args
        assert call_kwargs[1]["json"]["model"] == "mistral:7b"

    @patch("zaatar.clients.ollama.httpx.Client")
    def test_summarize_connect_error(self, mock_client_class):
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.post.side_effect = httpx.ConnectError("connection refused")

        results = [{"title": "Test", "url": "https://example.com", "description": "desc"}]
        with pytest.raises(httpx.ConnectError):
            summarize("test", results)
