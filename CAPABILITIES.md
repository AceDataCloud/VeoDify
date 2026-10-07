# Veo capability mapping

Compared with [MCPs at f0eed10abf31](https://github.com/AceDataCloud/MCPs/tree/f0eed10abf310824cb4c33d4944c63d3654ac95b/veo) and the public API contract at PlatformBackend `fa94598267a82545fb1afed6ee26bafd6cbb9ca7`.

The table maps service operations to Dify tools. Different MCP helper functions may use the same action selector or structured JSON input.

| MCP function | Dify equivalent | Notes |
|---|---|---|
| `veo_list_models` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `veo_list_actions` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `veo_get_prompt_guide` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `veo_get_task` | `veo_task_retrieve` | Set action=retrieve |
| `veo_get_tasks_batch` | `veo_tasks_retrieve_batch` | Set action=retrieve_batch |
| `veo_text_to_video` | `veo_generate_video` | Set action=text2video |
| `veo_image_to_video` | `veo_generate_video` |  |
| `veo_get_1080p` | `veo_generate_video` |  |

## Parameter equivalents

- `veo_get_tasks_batch`: `task_ids` → ids.

## Verification boundary

Contract examples and regression tests cover request validation, transport and task handling. Actual Dify browser cases are recorded separately in `tests/e2e-results.json` and `tests/e2e-audit.json` when available. A schema test is not a successful paid generation. Unsupported service availability and untested advanced combinations must not be described as passed.
