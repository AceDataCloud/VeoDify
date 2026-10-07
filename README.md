# Veo

**Author:** acedatacloud

**Type:** tool provider plugin

Use the Ace Data Cloud Veo APIs in Dify. This free plugin requires your own Ace Data Cloud token; API calls incur the current service usage charges.

## Tools

| Tool | API |
|---|---|
| `veo_generate_video` | `/veo/videos` |

The separate task tool retrieves or waits up to 240 seconds for a submitted task.

## Credentials and installation

Create a token for this service at https://platform.acedata.cloud/console/credentials. Authorize the provider with `acedata_bearer_token` without the `Bearer ` prefix. Validation makes a free task query; it never generates output.

During review, use the official Dify remote-debug workflow in an isolated workspace. Install through Marketplace after publication. Source availability does not imply Marketplace listing.

## Workflow

Use Start → Veo tool → Output. Select the model and parameters described by the tool. Generation is asynchronous: preserve `task_id`, then use the task tool until `status` is `succeeded`. If still pending, query the same ID again. Do not repeat a paid submission to check its progress.

Outputs include `status`, `success`, `task_id`, `trace_id`, `data`, `result` and `media_urls`. Completed images use Dify image messages; other media includes output links. Pending tasks are not complete, and failed requests raise tool errors. The tool table defines this release's supported endpoints. Nested API values use JSON arrays or objects.

The contract follows the current public API. The plugin fixes HTTPS to `api.acedata.cloud`, disables redirects and paid automatic retries, masks upstream error bodies, and omits stored requests/account/routing metadata. Requests have a 10-second connection and 60-second read timeout. API model availability and pricing can change; check https://platform.acedata.cloud/models and reconcile the task/trace in https://platform.acedata.cloud/console/usages. Dify execution counts are not the API billing ledger. No automatic fallback is added.

See [PRIVACY.md](PRIVACY.md). Submit only inputs you may use. Never include keys in prompts or exported workflows.

## Source and support

- Source: https://github.com/AceDataCloud/VeoDify
- Issues: https://github.com/AceDataCloud/VeoDify/issues
- Contact: dev@acedata.cloud
- [Simplified Chinese](readme/README_zh_Hans.md)
- License: MIT

Development: Python 3.12, `pip install -r requirements.txt`, `pytest tests -q`, `ruff check .`, and `dify plugin package .`.
