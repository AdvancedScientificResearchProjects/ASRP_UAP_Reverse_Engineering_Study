#!/usr/bin/env python3
"""Download open-access PDFs listed in references/sources.json.

ASRP UAP Reverse-Engineering Study - literature fetcher.
Standard: UNIFIED_ASRP_STANDARD v6.1

Only entries with ``open_access: true`` AND a non-empty ``oa_pdf_url`` are
fetched. These URLs point to legal open-access copies (PubMed Central /
Europe PMC, publisher open-access pages, journal OJS sites). Paywalled works are
never downloaded. PDFs are written to references/pdf/ (git-ignored) together
with a SHA-256 manifest, references/pdf/MANIFEST.json.

Standard library only. Usage:
    python3 scripts/fetch_literature.py --dry-run
    python3 scripts/fetch_literature.py
    python3 scripts/fetch_literature.py --only nubase2020 --force
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = "literature-fetcher/1.0"  # generic on purpose: no organisation or personal details are sent
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES = REPO_ROOT / "references" / "sources.json"
DEFAULT_OUT = REPO_ROOT / "references" / "pdf"
MAX_BYTES = 100 * 1024 * 1024  # refuse anything above 100 MB


def ssl_context() -> ssl.SSLContext:
    """Default TLS verification; some macOS Python builds ship without a CA bundle, so add the system one."""
    ctx = ssl.create_default_context()
    if not ctx.get_ca_certs() and os.path.exists("/etc/ssl/cert.pem"):
        ctx.load_verify_locations("/etc/ssl/cert.pem")
    return ctx


def load_sources(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["sources"] if isinstance(data, dict) else data


def eligible(src: dict) -> bool:
    return bool(src.get("open_access")) and bool(src.get("oa_pdf_url"))


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path, retries: int, timeout: float, delay: float) -> tuple[bool, str]:
    """Fetch url into dest. Returns (ok, message). Verifies the %PDF magic bytes."""
    last = ""
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*;q=0.8"})
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
                body = resp.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                return False, "file larger than 100 MB, skipped"
            if not body.startswith(b"%PDF"):
                return False, "response is not a PDF (landing page or access challenge); download manually from the URL"
            tmp = dest.with_suffix(".part")
            tmp.write_bytes(body)
            tmp.replace(dest)
            return True, f"{len(body)} bytes"
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}"
            if exc.code in (401, 403, 404, 410):
                break  # not retryable
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = f"{type(exc).__name__}: {exc}"
        if attempt < retries:
            time.sleep(delay * attempt)
    return False, last or "unknown error"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Download open-access PDFs listed in references/sources.json.")
    ap.add_argument("--sources", type=Path, default=DEFAULT_SOURCES, help="path to sources.json")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory (git-ignored)")
    ap.add_argument("--dry-run", action="store_true", help="list what would be downloaded; write nothing")
    ap.add_argument("--only", nargs="*", default=None, help="restrict to these source ids")
    ap.add_argument("--force", action="store_true", help="re-download files that already exist")
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between requests (politeness) and retry backoff base")
    args = ap.parse_args(argv)

    sources = load_sources(args.sources)
    if args.only:
        wanted = set(args.only)
        sources = [s for s in sources if s.get("id") in wanted]
    todo = [s for s in sources if eligible(s)]
    skipped = [s for s in sources if not eligible(s)]

    print(f"sources: {len(sources)} | open-access PDFs: {len(todo)} | not downloadable (closed / no legal PDF): {len(skipped)}")
    if args.dry_run:
        for s in todo:
            print(f"  [would fetch] {s['id']:<20} {s['oa_pdf_url']}")
        for s in skipped:
            reason = "no legal OA PDF" if s.get("open_access") else "not open access"
            print(f"  [skip]        {s['id']:<20} {reason}")
        print("dry run: nothing written")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "MANIFEST.json"
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = {e["id"]: e for e in json.loads(manifest_path.read_text(encoding="utf-8"))["files"]}
        except (ValueError, KeyError):
            manifest = {}

    failures = 0
    for i, s in enumerate(todo):
        dest = args.out / f"{s['id']}.pdf"
        if dest.exists() and not args.force:
            print(f"  [exists]  {s['id']}")
            ok, msg = True, "already present"
        else:
            ok, msg = download(s["oa_pdf_url"], dest, args.retries, args.timeout, args.delay)
            print(f"  [{'ok' if ok else 'fail'}]    {s['id']}: {msg}")
            if i < len(todo) - 1:
                time.sleep(args.delay)
        entry = {"id": s["id"], "doi": s.get("doi"), "url": s["oa_pdf_url"], "status": "ok" if ok else "failed", "message": msg}
        if ok and dest.exists():
            entry.update(file=dest.name, bytes=dest.stat().st_size, sha256=sha256_of(dest),
                         checked_at=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"))
        else:
            failures += 1
        manifest[s["id"]] = entry

    manifest_path.write_text(json.dumps({
        "generator": "scripts/fetch_literature.py",
        "user_agent": USER_AGENT,
        "updated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "files": sorted(manifest.values(), key=lambda e: e["id"]),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"done: {len(todo) - failures} ok, {failures} failed; manifest: {manifest_path}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
