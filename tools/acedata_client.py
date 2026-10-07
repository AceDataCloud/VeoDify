"""Veo API client. Paid submissions are never retried automatically."""

from __future__ import annotations

import json
import time
from typing import Any

import requests

BASE = "https://api.acedata.cloud"
CONTRACTS = {
    "veo_generate_video": {
        "path": "/veo/videos",
        "schema": {
            "type": "object",
            "required": ["action"],
            "properties": {
                "model": {
                    "enum": ["veo3", "veo3-fast", "veo31-fast", "veo31", "veo31-fast-ingredients"],
                    "rank": 5,
                    "type": "string",
                    "description": "$t(veo_videos_model)",
                },
                "resolution": {
                    "enum": ["4k", "1080p", "gif"],
                    "rank": 5,
                    "type": "string",
                    "description": "$t(veo_videos_resolution)",
                },
                "action": {
                    "enum": ["text2video", "image2video", "ingredients2video", "get1080p"],
                    "rank": 0,
                    "type": "string",
                    "description": "$t(veo_videos_action)",
                },
                "prompt": {
                    "rank": 10,
                    "type": "string",
                    "example": "White ceramic coffee mug on glossy marble counter, top with morning window light. Camera slowly rotates 360 degrees around the mug, pausing briefly at the handle.",
                    "description": "$t(veo_videos_prompt)",
                },
                "video_id": {
                    "rank": 10,
                    "type": "string",
                    "description": "$t(veo_videos_video_id)",
                },
                "translation": {
                    "rank": 10,
                    "type": "boolean",
                    "description": "$t(veo_videos_translation)",
                },
                "aspect_ratio": {
                    "rank": 10,
                    "enum": ["16:9", "9:16"],
                    "type": "string",
                    "description": "$t(veo_videos_aspect_ratio)",
                },
                "image_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "$t(veo_videos_image_urls)",
                },
                "callback_url": {
                    "rank": 100,
                    "type": "string",
                    "description": "$t(veo_videos_callback_url)",
                },
                "async": {"rank": 101, "type": "boolean", "description": "$t(veo_videos_async)"},
            },
        },
        "defaults": {"model": "veo31-fast", "action": "text2video", "aspect_ratio": "16:9"},
        "operation": "generate",
    }
}
TASK_PATH = "/veo/tasks"
FAMILY = "veo"
OUTPUT_FIELDS = {
    "_id",
    "absolute",
    "aspect_ratio",
    "audio_id",
    "audio_url",
    "bounding_box",
    "code",
    "complete_at",
    "content",
    "cost",
    "created",
    "created_at",
    "data",
    "description",
    "duration",
    "elapsed",
    "error",
    "face_infos",
    "file_url",
    "finished_at",
    "format",
    "height",
    "id",
    "image_id",
    "image_url",
    "image_urls",
    "images",
    "input_tokens",
    "is_extend_result",
    "items",
    "landmarks",
    "left",
    "lyric",
    "message",
    "model",
    "name",
    "normalized",
    "output_format",
    "output_tokens",
    "points",
    "prompt",
    "response",
    "seed",
    "size",
    "started_at",
    "state",
    "status",
    "success",
    "task",
    "task_id",
    "text",
    "title",
    "top",
    "total_tokens",
    "trace_id",
    "translation",
    "url",
    "usage",
    "video_id",
    "video_url",
    "videos",
    "width",
    "x",
    "y",
    "z_index",
}


class AceDataVeoError(RuntimeError):
    pass


def clean_result(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: clean_result(v) for k, v in value.items() if k in OUTPUT_FIELDS}
    if isinstance(value, list):
        return [clean_result(v) for v in value]
    return value


def output_urls(value: Any) -> list[str]:
    result: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, item in node.items():
                if (
                    key in {"image_url", "audio_url", "video_url", "file_url", "url"}
                    and isinstance(item, str)
                    and item.startswith("https://")
                ):
                    result.append(item)
                elif isinstance(item, (dict, list)):
                    walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return list(dict.fromkeys(result))


def value_for_field(name: str, value: Any, schema: dict[str, Any]) -> Any:
    typ = schema.get("type")
    if isinstance(value, str):
        value = value.strip()
        if typ in {"array", "object"} or (name == "image" and value.startswith("[")):
            try:
                value = json.loads(value)
            except ValueError:
                if typ == "array" and schema.get("items", {}).get("type") == "string":
                    value = [line.strip() for line in value.splitlines() if line.strip()]
                else:
                    raise ValueError(f"{name} must contain valid JSON.") from None
    if typ in {"number", "integer"}:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric.")
        if typ == "integer":
            if value != int(value):
                raise ValueError(f"{name} must be an integer.")
            value = int(value)
        if (
            "minimum" in schema
            and value < schema["minimum"]
            or ("maximum" in schema and value > schema["maximum"])
        ):
            raise ValueError(f"{name} is outside its supported range.")
    if typ == "boolean" and (not isinstance(value, bool)):
        raise ValueError(f"{name} must be boolean.")
    if typ == "array" and (not isinstance(value, list)):
        raise ValueError(f"{name} must be an array.")
    if typ == "object" and (not isinstance(value, dict)):
        raise ValueError(f"{name} must be an object.")
    if typ == "string" and (not isinstance(value, str)):
        raise ValueError(f"{name} must be text.")
    if schema.get("enum") and value not in schema["enum"]:
        raise ValueError(f"Unsupported {name}.")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", 100):
            raise ValueError(f"Unsupported number of {name} items.")
    return value


class AceDataVeoClient:
    def __init__(self, bearer_token: str) -> None:
        if not isinstance(bearer_token, str) or not bearer_token.strip():
            raise ValueError("An Ace Data Cloud token is required.")
        self._token = bearer_token.strip().removeprefix("Bearer ").strip()
        if not self._token:
            raise ValueError("An Ace Data Cloud token is required.")

    def _request(
        self, path: str, payload: dict[str, Any], *, validation: bool = False, _attempt: int = 0
    ) -> dict[str, Any]:
        try:
            with requests.post(
                BASE + path,
                json=payload,
                headers={"Authorization": "Bearer " + self._token, "Accept": "application/json"},
                timeout=(10, 60),
                allow_redirects=False,
            ) as response:
                if validation and response.status_code in {400, 404}:
                    return {}
                if response.status_code != 200:
                    raise AceDataVeoError(
                        f"Ace Data Cloud HTTP {response.status_code}. Check service access and request history before resubmitting."
                    )
                body = response.json()
        except requests.RequestException as exc:
            if path == TASK_PATH and _attempt < 2:
                time.sleep(0.5 * (_attempt + 1))
                return self._request(path, payload, validation=validation, _attempt=_attempt + 1)
            raise AceDataVeoError(
                f"Connection failed ({type(exc).__name__}). Check request history for an accepted task before resubmitting."
            ) from None
        except ValueError:
            raise AceDataVeoError("The API returned invalid JSON.") from None
        if validation and body is None:
            return {}
        if not isinstance(body, dict):
            raise AceDataVeoError("The API returned an invalid result.")
        if not validation and (body.get("success") is False or body.get("error")):
            raise AceDataVeoError(
                "The API reported a failure. Check the request in the Ace Data Cloud console."
            )
        return body

    def validate(self) -> None:
        if TASK_PATH:
            self._request(
                TASK_PATH,
                {"action": "retrieve", "id": "00000000-0000-0000-0000-000000000000"},
                validation=True,
            )

    def payload(self, tool: str, params: dict[str, Any]) -> tuple[str, dict[str, Any], bool]:
        contract = CONTRACTS[tool]
        schema = contract["schema"]
        fields = schema.get("properties", {})
        values = {**contract.get("defaults", {}), **params}
        data = {
            name: value_for_field(name, value, fields[name])
            for name, value in values.items()
            if name in fields
            and name not in {"async", "callback_url", "stream"}
            and (value is not None)
            and (value != "")
        }
        if "async" in fields:
            data["async"] = True
        if "response_format" in fields:
            data["response_format"] = "url"
        for name in schema.get("required", []):
            if name not in data:
                raise ValueError(f"{name} is required.")
        return (contract["path"], data, "async" in fields)

    def invoke(self, tool: str, params: dict[str, Any]) -> dict[str, Any]:
        if tool == "task":
            task_id = params.get("task_id")
            if not isinstance(task_id, str) or not task_id.strip():
                raise ValueError("task_id is required.")
            wait = value_for_field(
                "wait_seconds",
                params.get("wait_seconds", 0),
                {"type": "integer", "minimum": 0, "maximum": 240},
            )
            deadline = time.monotonic() + wait
            while True:
                body = self._request(TASK_PATH, {"action": "retrieve", "id": task_id})
                result = self._result(body, task_id, retrieved=True)
                if result["status"] != "pending" or time.monotonic() >= deadline:
                    return result
                time.sleep(min(5, max(0, deadline - time.monotonic())))
        path, data, is_async = self.payload(tool, params)
        body = self._request(path, data)
        return self._result(body, str(body.get("task_id") or ""), synchronous=not is_async)

    def _result(
        self,
        body: dict[str, Any],
        task_id: str,
        *,
        retrieved: bool = False,
        synchronous: bool = False,
    ) -> dict[str, Any]:
        result = body.get("response") if retrieved else body
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except ValueError:
                result = {}
        if not isinstance(result, dict):
            result = {}
        states = []

        def visit(node: Any) -> None:
            if isinstance(node, dict):
                for k, v in node.items():
                    if k in {"state", "status"} and isinstance(v, str):
                        states.append(v.lower())
                    elif k in {"data", "content", "task"}:
                        visit(v)
            elif isinstance(node, list):
                for v in node:
                    visit(v)

        visit(result)
        if (
            result.get("success") is False
            or result.get("error")
            or any((x in {"failed", "error", "cancelled", "canceled", "rejected"} for x in states))
        ):
            raise AceDataVeoError("Task failed. Check its details in the Ace Data Cloud console.")
        urls = output_urls(result)
        terminal = {"complete", "completed", "succeeded", "succeed", "success", "finished"}
        done = (synchronous and (not task_id) or bool(urls)) and (
            not states or all((x in terminal for x in states))
        )
        if retrieved and body.get("finished_at") and result and (not states):
            done = True
        if not done and (not task_id):
            raise AceDataVeoError(
                "No task ID or completed output returned. Check request history before resubmitting."
            )
        return {
            "status": "succeeded" if done else "pending",
            "success": done,
            "task_id": task_id,
            "trace_id": str(result.get("trace_id") or body.get("trace_id") or ""),
            "media_urls": urls if done else [],
            "data": clean_result(result.get("data", result)),
            "result": clean_result(result),
        }
