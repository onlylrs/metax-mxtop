from __future__ import annotations

import argparse
import json
import sys
import time

from mxtop import __version__
from mxtop.backends import TelemetryBackend, create_backend
from mxtop.models import FrameSnapshot
from mxtop.rendering import render_once
from mxtop.tui import run_tui


def _single_snapshot_with_cpu_sample(backend: TelemetryBackend) -> FrameSnapshot:
    frame = backend.snapshot()
    if frame.processes and any(process.cpu_percent is None for process in frame.processes):
        time.sleep(0.1)
        frame = backend.snapshot()
    return frame


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="An nvitop-like monitor for MetaX GPUs.")
    _ = parser.add_argument("--version", action="version", version=f"mxtop {__version__}")
    _ = parser.add_argument("--backend", choices=["auto", "pymxsml", "mxsmi"], default="auto")
    _ = parser.add_argument("--interval", type=float, default=1.0, help="refresh interval in seconds")
    _ = parser.add_argument("--once", "-1", action="store_true", help="print one text snapshot and exit")
    _ = parser.add_argument("--json", action="store_true", help="print one JSON snapshot and exit")
    _ = parser.add_argument("--no-color", action="store_true", help="disable ANSI color output")
    return parser


def main(argv: list[str] | None = None, backend: TelemetryBackend | None = None) -> int:
    args = build_parser().parse_args(argv)
    selected_backend = backend or create_backend(args.backend)

    if args.json:
        print(json.dumps(_single_snapshot_with_cpu_sample(selected_backend).to_dict(), indent=2, sort_keys=True))
        return 0

    if args.once or not sys.stdout.isatty():
        print(render_once(_single_snapshot_with_cpu_sample(selected_backend), use_color=not args.no_color))
        return 0

    return run_tui(selected_backend, args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
