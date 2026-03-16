#!/usr/bin/env python3
"""
download_wikiart_images.py

Downloads WikiArt images using Playwright to bypass Cloudflare protection.
Reads from filtered_religious.parquet metadata and downloads !Large.jpg versions.

Requires: pip install playwright pandas pyarrow
          python -m playwright install chromium

Usage:
    python scripts/download_wikiart_images.py                          # Download all
    python scripts/download_wikiart_images.py --artist gustave-dore    # Single artist
    python scripts/download_wikiart_images.py --max-images 50          # Limit
    python scripts/download_wikiart_images.py --dry-run                # Preview only
"""

import argparse
import asyncio
import json
import re
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
FILTERED_PATH = REPO_ROOT / "data" / "00_raw" / "wikiart" / "filtered_religious.parquet"
IMAGES_DIR = REPO_ROOT / "data" / "00_raw" / "wikiart" / "images"
METADATA_DIR = REPO_ROOT / "data" / "00_raw" / "wikiart" / "metadata"

DELAY_MS = 800  # Delay between downloads (respect rate limits)


def normalize_artist_slug(name):
    if not name:
        return ""
    slug = name.lower().strip()
    slug = unicodedata.normalize("NFD", slug)
    slug = "".join(c for c in slug if unicodedata.category(c) != "Mn")
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def get_large_url(img_url):
    """Convert an img_url to the !Large.jpg version."""
    if not img_url or not isinstance(img_url, str):
        return None
    base = img_url.split("!")[0]
    if not base.lower().endswith((".jpg", ".jpeg", ".png")):
        return None
    return base + "!Large.jpg"


async def download_images(args):
    import pandas as pd
    from playwright.async_api import async_playwright

    if not FILTERED_PATH.exists():
        print(f"ERROR: {FILTERED_PATH} not found.")
        print("Run: python scripts/fetch_wikiart.py --step metadata")
        return

    df = pd.read_parquet(FILTERED_PATH)

    # Apply artist filter
    if args.artist:
        mask = df["artist"].apply(normalize_artist_slug).isin(args.artist)
        df = df[mask]
        print(f"  Artist filter: {len(df)} images from {args.artist}")

    if df.empty:
        print("  No images match the filter. Use --list-artists with fetch_wikiart.py")
        return

    if args.max_images:
        df = df.head(args.max_images)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    # Filter out already downloaded
    to_download = []
    skipped = 0
    for _, row in df.iterrows():
        key = str(row["key"])
        img_path = IMAGES_DIR / f"{key}.jpg"
        if img_path.exists() and img_path.stat().st_size > 1000:
            skipped += 1
            continue
        url = get_large_url(row.get("img_url"))
        if url:
            to_download.append({"key": key, "url": url, "row": row})

    print(f"\n  Total to download: {len(to_download)}")
    print(f"  Already downloaded: {skipped}")

    if not to_download:
        print("  Nothing to download!")
        return

    if args.dry_run:
        for item in to_download[:10]:
            print(f"  [dry-run] {item['key']}: {item['url']}")
        if len(to_download) > 10:
            print(f"  ... and {len(to_download) - 10} more")
        return

    # Launch Playwright
    print("\n  Launching browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Navigate to WikiArt to pass Cloudflare challenge
        print("  Passing Cloudflare challenge...")
        await page.goto("https://www.wikiart.org/pt/gustave-dore", wait_until="domcontentloaded", timeout=60000)

        # Wait for Cloudflare to resolve
        for attempt in range(6):
            await page.wait_for_timeout(5000)
            title = await page.title()
            if "wikiart" in title.lower() or "gustave" in title.lower() or "doré" in title.lower():
                print(f"  Cloudflare passed! Title: {title}")
                break
            print(f"  Waiting for Cloudflare... ({attempt+1}/6) Title: {title}")
        else:
            print(f"  WARNING: Cloudflare may not have resolved. Title: {title}")
            print("  Attempting downloads anyway...")

        # Download images using context.request (shares cookies with browser)
        downloaded = 0
        failed = 0

        for i, item in enumerate(to_download):
            key = item["key"]
            url = item["url"]
            row = item["row"]

            try:
                resp = await context.request.get(url)
                if resp.status == 200:
                    body = await resp.body()
                    if len(body) > 1000:
                        # Save image
                        img_path = IMAGES_DIR / f"{key}.jpg"
                        img_path.write_bytes(body)

                        # Save metadata
                        meta_path = METADATA_DIR / f"{key}.json"
                        if not meta_path.exists():
                            meta = {
                                "key": key,
                                "title": row.get("title"),
                                "artist": row.get("artist"),
                                "completion": int(row["completion"]) if pd.notna(row.get("completion")) else None,
                                "styles": list(row["styles"]) if row.get("styles") is not None else [],
                                "genres": list(row["genres"]) if row.get("genres") is not None else [],
                                "tags": list(row["tags"]) if row.get("tags") is not None else [],
                                "media": list(row["media"]) if row.get("media") is not None else [],
                                "width": int(row["width"]) if pd.notna(row.get("width")) else None,
                                "height": int(row["height"]) if pd.notna(row.get("height")) else None,
                                "img_url": row.get("img_url"),
                                "source": "wikiart",
                            }
                            meta = json.loads(json.dumps(meta, default=str))
                            with open(meta_path, "w", encoding="utf-8") as f:
                                json.dump(meta, f, indent=2, ensure_ascii=False)

                        downloaded += 1
                        if downloaded % 10 == 0 or downloaded <= 3:
                            print(f"  [{downloaded}/{len(to_download)}] {key}: {len(body):,} bytes")
                    else:
                        failed += 1
                        if failed <= 3:
                            print(f"  [fail] {key}: too small ({len(body)} bytes)")
                else:
                    failed += 1
                    if failed <= 5:
                        print(f"  [fail] {key}: HTTP {resp.status}")
            except Exception as e:
                failed += 1
                if failed <= 5:
                    print(f"  [error] {key}: {e}")

            # Rate limit
            await page.wait_for_timeout(DELAY_MS)

        await browser.close()

    print(f"\n  Downloaded: {downloaded}")
    print(f"  Failed: {failed}")
    print(f"  Skipped (exist): {skipped}")


def main():
    parser = argparse.ArgumentParser(
        description="Download WikiArt images via Playwright (bypasses Cloudflare)"
    )
    parser.add_argument("--artist", action="append", metavar="SLUG",
                        help="Filter by artist slug (can repeat)")
    parser.add_argument("--max-images", type=int, help="Limit number of images")
    parser.add_argument("--dry-run", action="store_true", help="Preview without downloading")
    args = parser.parse_args()

    asyncio.run(download_images(args))


if __name__ == "__main__":
    main()
