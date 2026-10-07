from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.acedata_client import AceDataVeoClient, AceDataVeoError


class VeoProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        token = credentials.get("acedata_bearer_token")
        if not isinstance(token, str) or not token.strip():
            raise ToolProviderCredentialValidationError("Missing `acedata_bearer_token`.")
        try:
            AceDataVeoClient(bearer_token=token).validate()
        except (AceDataVeoError, ValueError):
            raise ToolProviderCredentialValidationError(
                "Unable to validate the token. Check its service access and network connection."
            ) from None
