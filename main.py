#!/usr/bin/env python3
"""
main.py — Entry point for Guns, Grit & Gravity.

A text adventure in deep space where the stars don't care
and neither does the sheriff.

Usage:
    python main.py
    python main.py --load quicksave
"""

from __future__ import annotations
import sys
import argparse
from engine import Engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Guns, Grit & Gravity — A Space Western Text Adventure"
    )
    parser.add_argument(
        "--load",
        metavar="SAVENAME",
        help="Load a saved game on startup",
    )
    parser.add_argument(
        "--no-footnotes",
        action="store_true",
        help="Disable footnotes",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    engine = Engine()

    if args.no_footnotes:
        engine.narrator.set_footnotes(False)

    if args.load:
        # Load specified save, then start (which prints the room)
        engine.start()
        engine.process(f"load {args.load}")
    else:
        engine.start()

    while engine.is_running():
        raw = engine.narrator.prompt()
        engine.process(raw)

    sys.exit(0)


if __name__ == "__main__":
    main()
