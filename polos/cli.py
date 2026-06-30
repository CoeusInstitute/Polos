"""Command-line entry point for the Polos runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from polos import __version__
from polos.audit.reader import verify_hash_chain
from polos.runtime.tasks import create_task, init_runtime, list_tasks, read_toolcalls, select_task, update_task_status
from polos.tools.validator import validate_mesh
from polos.verification.runner import required_checks_passed, run_required_checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="polos", description="Polos governed agent harness runtime")
    parser.add_argument("--root", default=".", help="Repository root containing the Polos spec")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("version", help="Print the Polos runtime version")

    validate_parser = subparsers.add_parser("validate", help="Run the structural mesh validator")
    validate_parser.add_argument("--json", action="store_true", help="Emit structured validation output")

    init_parser = subparsers.add_parser("init", help="Create local runtime storage")
    init_parser.add_argument("--force", action="store_true", help="Rewrite generated runtime README files")

    plan_parser = subparsers.add_parser("plan", help="Create a durable task contract and plan stub")
    plan_parser.add_argument("request", help="Original user request")
    plan_parser.add_argument("--title", help="Short task title")
    plan_parser.add_argument("--autonomy", default="L2", help="Autonomy level L0-L6")
    plan_parser.add_argument("--risk", default="low", choices=["low", "medium", "high", "critical"])
    plan_parser.add_argument("--mode", default="plan", help="Requested execution mode")

    run_parser = subparsers.add_parser("run", help="Run a task through the runtime")
    run_parser.add_argument("--task-id", help="Task id under .agent/tasks")
    run_parser.add_argument("--dry-run", action="store_true", help="Simulate without effectful tools")

    audit_parser = subparsers.add_parser("audit", help="Inspect local task/audit records")
    audit_parser.add_argument("--task-id", help="Task id under .agent/tasks")
    audit_parser.add_argument("--json", action="store_true", help="Emit structured audit output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    if args.command == "version":
        print(__version__)
        return 0

    if args.command == "validate":
        result = validate_mesh(root)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
        return result.exit_code

    if args.command == "init":
        created = init_runtime(root, force=args.force)
        for path in created:
            print(path.relative_to(root).as_posix())
        return 0

    if args.command == "plan":
        task = create_task(
            root=root,
            original_request=args.request,
            title=args.title,
            autonomy_level=args.autonomy,
            risk_level=args.risk,
            requested_mode=args.mode,
        )
        print(task.path.relative_to(root).as_posix())
        return 0

    if args.command == "run":
        if not args.dry_run:
            print("polos run is fail-closed: use --dry-run until grants and the tool gateway are configured", file=sys.stderr)
            return 2
        try:
            task = select_task(root, args.task_id)
        except FileNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        results = run_required_checks(root, task.task_id, task.required_checks)
        passed = required_checks_passed(results)
        status = "complete" if passed else "blocked"
        update_task_status(task, status)
        print("dry-run: no tools executed, no model calls made")
        print(f"task_id: {task.task_id}")
        print(f"status: {status}")
        print(f"evidence: {(task.path / 'EVIDENCE.md').relative_to(root).as_posix()}")
        return 0 if passed else 1

    if args.command == "audit":
        try:
            tasks = [select_task(root, args.task_id)] if args.task_id else list_tasks(root)
        except FileNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        payload = {
            "tasks": [task.to_dict() for task in tasks],
            "toolcalls": {task.task_id: read_toolcalls(task) for task in tasks},
            "hash_chains": {task.task_id: verify_hash_chain(task.path / "TOOLCALLS.jsonl") for task in tasks},
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            if not tasks:
                print("No local task records found.")
            for task in tasks:
                print(f"{task.task_id}\t{task.status}\t{task.title}")
                toolcalls = read_toolcalls(task)
                if toolcalls:
                    print(f"  toolcalls: {len(toolcalls)}")
                print(f"  hash_chain_valid: {verify_hash_chain(task.path / 'TOOLCALLS.jsonl')}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
