# Privacy policy — Veo by Ace Data Cloud

Effective date: 2026-10-07. Maintainer/contact: Ace Data Cloud, dev@acedata.cloud.

This plugin sends your API key in an HTTPS Authorization header to `api.acedata.cloud`. It sends video prompts, reference image/audio/video URLs and generation settings, together with task IDs where applicable. Such inputs may contain personal information if you include it. The API also receives ordinary connection metadata, including the Dify server's IP address and usage required to operate the service.

The plugin's only direct API recipient is Ace Data Cloud. API processing, retention and service providers follow the [Ace Data Cloud privacy policy](https://platform.acedata.cloud/privacy). Reference URLs are sent to the API; the plugin does not fetch arbitrary URLs or download media. It returns selected result fields and media links to Dify. It does not intentionally log keys, raw API errors, or saved request bodies, and has no database, telemetry or additional persistent storage. Dify handles credential storage, workflow history and downstream media rendering under your deployment's policies. API-side zero retention is not promised by this plugin.

Only submit text and media you are authorized to use. Remove the credential from Dify or revoke it in the Ace Data Cloud console to stop use. Contact dev@acedata.cloud for API data questions and your Dify administrator for local history. This release does not train custom models, clone voices, execute generated code/tools, or perform payments or asset transfers.
