import json

import dify_plugin  # noqa: F401
import pytest
import requests
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration

from tools.acedata_client import (
    TASK_PATH,
    value_for_field,
)
from tools.acedata_client import (
    AceDataVeoClient as Client,
)
from tools.acedata_client import (
    AceDataVeoError as APIError,
)


def response(body, status=200):
    r = requests.Response()
    r.status_code = status
    r._content = json.dumps(body).encode()
    r.close = lambda: None
    return r


def test_sdk_registration():
    registration = PluginRegistration(DifyPluginEnv())
    assert registration.configuration.name == "veo"


def test_credentials_do_not_generate(monkeypatch):
    calls = []

    def send(url, **kwargs):
        calls.append((url, kwargs))
        return response({})

    monkeypatch.setattr(requests, "post", send)
    Client("test-token").validate()
    assert len(calls) == (1 if TASK_PATH else 0)
    if calls:
        assert calls[0][0] == "https://api.acedata.cloud" + TASK_PATH
        assert calls[0][1]["json"]["action"] == "retrieve"
        assert calls[0][1]["allow_redirects"] is False


@pytest.mark.parametrize("status", [400, 401, 403, 429, 500])
def test_error_responses_are_redacted(monkeypatch, status):
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: response({"error": "private-key-and-content"}, status)
    )
    with pytest.raises(APIError) as error:
        Client("test-token")._request("/veo/test", {})
    assert str(status) in str(error.value)
    assert "private-key-and-content" not in str(error.value)
    assert "test-token" not in str(error.value)


def test_timeout_never_retries_paid_request(monkeypatch):
    calls = []

    def fail(*args, **kwargs):
        calls.append(1)
        raise requests.Timeout("private input")

    monkeypatch.setattr(requests, "post", fail)
    with pytest.raises(APIError):
        Client("test-token")._request("/veo/test", {})
    assert len(calls) == 1


def test_pending_media_is_not_complete():
    result = Client("test-token")._result(
        {
            "response": {
                "status": "running",
                "data": [{"image_url": "https://example.org/preview.png"}],
            }
        },
        "owned-task",
        retrieved=True,
    )
    assert result["status"] == "pending" and result["success"] is False
    assert result["media_urls"] == []


def test_completed_result_preserves_output_and_strips_private_fields():
    result = Client("test-token")._result(
        {
            "response": {
                "status": "succeeded",
                "data": [{"image_url": "https://example.org/final.png"}],
                "request": {"prompt": "private"},
                "user_id": "private",
                "internal_supplier": "private",
            }
        },
        "owned-task",
        retrieved=True,
    )
    assert result["status"] == "succeeded" and result["success"] is True
    assert result["media_urls"] == ["https://example.org/final.png"]
    assert "private" not in json.dumps(result)


def test_failed_task_raises():
    with pytest.raises(APIError):
        Client("test-token")._result(
            {"response": {"status": "failed"}}, "owned-task", retrieved=True
        )


def test_invalid_enum_and_json_are_rejected():
    with pytest.raises(ValueError):
        value_for_field("model", "unknown", {"type": "string", "enum": ["allowed"]})
    with pytest.raises(ValueError):
        value_for_field("content", "not json", {"type": "array", "items": {"type": "object"}})
    with pytest.raises(ValueError):
        value_for_field("duration", True, {"type": "integer"})


def test_empty_task_id_is_not_string_none(monkeypatch):
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: response({"items": [{"title": "result"}]})
    )
    result = Client("test-token")._result({"items": [{"title": "result"}]}, "", synchronous=True)
    assert result["status"] == "succeeded" and result["task_id"] == ""


def test_sync_endpoint_does_not_complete_accepted_async_task():
    result = Client("test-token")._result(
        {"task_id": "owned-task", "status": "pending"}, "owned-task", synchronous=True
    )
    assert result["status"] == "pending" and result["success"] is False


def test_missing_task_null_can_validate_credentials(monkeypatch):
    monkeypatch.setattr(requests, "post", lambda *a, **k: response(None))
    Client("test-token").validate()


def test_readonly_task_query_retries_transient_transport(monkeypatch):
    import tools.acedata_client as module

    calls = []

    def send(*args, **kwargs):
        calls.append(1)
        if len(calls) < 3:
            raise requests.ConnectionError("private transport details")
        return response({})

    monkeypatch.setattr(requests, "post", send)
    monkeypatch.setattr(module.time, "sleep", lambda _: None)
    Client("test-token").validate()
    assert len(calls) == 3
