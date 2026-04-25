#!/usr/bin/env python3
"""
One-shot pre-deploy build. Runs:

  1. scripts/og/render.py        — regenerate OG card JPEGs
  2. scripts/build-feeds.py      — refresh sitemap.xml + feed.xml
  3. scripts/inject-meta.py      — update <meta> + JSON-LD on every page

Order matters: OG images must exist before inject-meta runs (it picks up
per-post .jpg files only if they exist on disk).

Usage:
    python scripts/build.py                      # full build
    python scripts/build.py --post <slug>        # render + meta for one post
                                                  (sitemap/feed always full)
    python scripts/build.py --skip-og            # skip OG render (faster)
"""
from __future__ import annotations
import argparse, subprocess, sys, time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
PYTHON  = sys.executable


def step(label: str, cmd: list[str]) -> None:
    print(f"\n== {label} " + "=" * max(2, 60 - len(label)), flush=True)
    t0 = time.time()
    result = subprocess.run(cmd)
    dt = time.time() - t0
    if result.returncode != 0:
        print(f"\nFAILED: {label} (exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)
    print(f"   -> {dt:.1f}s", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", default=None,
                    help="Limit OG render and meta injection to one slug.")
    ap.add_argument("--skip-og", action="store_true",
                    help="Skip OG image rendering.")
    args = ap.parse_args()

    if not args.skip_og:
        cmd = [PYTHON, str(SCRIPTS / "og" / "render.py")]
        if args.post: cmd += ["--post", args.post]
        step("1/3  render OG cards", cmd)
    else:
        print("== skipping OG render ==")

    step("2/3  build sitemap + RSS",
         [PYTHON, str(SCRIPTS / "build-feeds.py")])

    cmd = [PYTHON, str(SCRIPTS / "inject-meta.py")]
    if args.post: cmd += ["--post", args.post]
    step("3/3  inject meta + JSON-LD", cmd)

    print("\nBuild complete. Ready to deploy.")


if __name__ == "__main__":
    main()
