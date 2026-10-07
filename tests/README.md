# Verification

Run `python -m pytest tests -q` and `ruff check .`. Unit tests exercise actual SDK registration, read-only credential validation, sanitized errors, no automatic paid retry, transient read-only task retry, and pending/completed output handling.

The API schemas come from the PlatformBackend revision in `contract-source.json`. Real E2E uses isolated Dify CE 1.17.1 + plugin daemon 0.6.10-local with official remote debugging and signature verification enabled. A browser runs Start → tool → task retrieval → Output (synchronous APIs omit the task node). Preserve the task ID, verify terminal output and media, and reconcile Usage by task or trace. Never resubmit generation merely because polling was interrupted. E2E makes paid API calls and is not part of CI.

`e2e-progress.json` is the current progress snapshot. It is not a claim of Marketplace publication or installation. Terminal evidence and browser screenshots are added after real validation completes.

## Completed primary-operation evidence

`e2e-results.json` records terminal successful real Dify workflows, actual output, media decode and matched nonzero billing. `evidence/` contains unmodified browser screenshots and the exact workflow graph. The screenshots show actual Dify run history/results. This proves the recorded cases, not every model/optional endpoint. Full Marketplace installation still depends on official publication.
