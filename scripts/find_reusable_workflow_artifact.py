from __future__ import annotations

import argparse
import json
import os
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


WORKFLOW_PATH = ".github/workflows/generated-artifacts.yml"


class ReusableWorkflowArtifactError(RuntimeError):
    """GitHub artifact provenance could not be established safely."""


def _mapping(value: object, *, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReusableWorkflowArtifactError(
            f"GitHub artifact response has invalid {field}"
        )
    return value


def find_reusable_run(
    *,
    artifact_name: str,
    repository: str,
    fetch_json: Callable[[str], Mapping[str, Any]],
) -> int | None:
    listing = fetch_json(
        f"repos/{repository}/actions/artifacts"
        f"?name={quote(artifact_name, safe='')}&per_page=100"
    )
    artifacts = listing.get("artifacts")
    if not isinstance(artifacts, list):
        raise ReusableWorkflowArtifactError(
            "GitHub artifact response has no artifact list"
        )
    candidates = sorted(
        (
            artifact
            for artifact in artifacts
            if isinstance(artifact, Mapping) and artifact.get("expired") is False
        ),
        key=lambda artifact: str(artifact.get("created_at") or ""),
        reverse=True,
    )
    for artifact in candidates:
        workflow_run = artifact.get("workflow_run")
        if not isinstance(workflow_run, Mapping):
            continue
        run_id = workflow_run.get("id")
        if isinstance(run_id, bool) or not isinstance(run_id, int) or run_id <= 0:
            continue
        run = fetch_json(f"repos/{repository}/actions/runs/{run_id}")
        head_repository = run.get("head_repository")
        if not isinstance(head_repository, Mapping):
            continue
        if (
            run.get("status") == "completed"
            and run.get("conclusion") in {"success", "failure", "cancelled"}
            and run.get("path") == WORKFLOW_PATH
            and head_repository.get("full_name") == repository
        ):
            return run_id
    return None


def _github_fetcher(
    *,
    token: str,
    api_url: str,
) -> Callable[[str], Mapping[str, Any]]:
    def fetch(relative: str) -> Mapping[str, Any]:
        request = Request(
            api_url.rstrip("/") + "/" + relative,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                value = json.load(response)
        except (HTTPError, URLError, OSError, json.JSONDecodeError) as exc:
            raise ReusableWorkflowArtifactError(
                "GitHub reusable-artifact lookup failed"
            ) from exc
        return _mapping(value, field="JSON object")

    return fetch


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Find the newest successful same-repository generated workflow "
            "run publishing a content-addressed artifact"
        )
    )
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    repository = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    if not repository or not token:
        parser.error("GITHUB_REPOSITORY and GH_TOKEN/GITHUB_TOKEN are required")
    try:
        run_id = find_reusable_run(
            artifact_name=args.name,
            repository=repository,
            fetch_json=_github_fetcher(token=token, api_url=api_url),
        )
    except ReusableWorkflowArtifactError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1
    if run_id is not None:
        print(run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
