from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
HOOKS_PATH = ".githooks"
PRE_PUSH = ROOT / HOOKS_PATH / "pre-push"


class HookInstallationError(RuntimeError):
    """Raised when repository hook installation would overwrite user policy."""


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def configured_hooks_path(root: Path = ROOT) -> str | None:
    result = _git(root, "config", "--local", "--get", "core.hooksPath")
    if result.returncode == 1:
        return None
    if result.returncode:
        raise HookInstallationError(result.stderr.strip())
    value = result.stdout.strip()
    return value or None


def check(root: Path = ROOT) -> None:
    hook = root / HOOKS_PATH / "pre-push"
    if not hook.is_file():
        raise HookInstallationError(f"missing tracked pre-push hook: {hook}")
    configured = configured_hooks_path(root)
    if configured != HOOKS_PATH:
        raise HookInstallationError(
            f"core.hooksPath is {configured!r}; expected {HOOKS_PATH!r}"
        )


def install(root: Path = ROOT) -> None:
    hook = root / HOOKS_PATH / "pre-push"
    if not hook.is_file():
        raise HookInstallationError(f"missing tracked pre-push hook: {hook}")
    configured = configured_hooks_path(root)
    if configured not in {None, HOOKS_PATH}:
        raise HookInstallationError(
            "refusing to replace an existing local core.hooksPath: "
            f"{configured}"
        )
    if configured is None:
        result = _git(root, "config", "--local", "core.hooksPath", HOOKS_PATH)
        if result.returncode:
            raise HookInstallationError(result.stderr.strip())
    try:
        hook.chmod(hook.stat().st_mode | 0o111)
    except OSError as exc:
        raise HookInstallationError(f"unable to mark {hook} executable") from exc
    check(root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install Quorune's repository-owned pre-push hooks"
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            check()
        else:
            install()
    except HookInstallationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        "Quorune pre-push hooks are configured through "
        "core.hooksPath=.githooks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
