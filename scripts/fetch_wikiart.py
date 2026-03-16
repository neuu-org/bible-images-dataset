#!/usr/bin/env python3
"""
fetch_wikiart.py

Downloads religious/biblical paintings from the WikiArt Internet Archive dataset.
Reads from WikiArt.parquet metadata, filters by genre/tags/artists, and extracts
matching images from WebDataset tar shards.

Strategy:
  1. Download WikiArt.parquet (metadata only, ~30MB)
  2. Filter for religious paintings by genre, tags, and curated artist list
  3. Identify which tar shards contain the matching images
  4. Download only the needed shards and extract matching images + metadata

Output: data/00_raw/wikiart/

Usage:
    python scripts/fetch_wikiart.py                           # Full pipeline
    python scripts/fetch_wikiart.py --dry-run                  # Show what would be downloaded
    python scripts/fetch_wikiart.py --step metadata            # Only download + filter parquet
    python scripts/fetch_wikiart.py --step images              # Only extract images (parquet must exist)
    python scripts/fetch_wikiart.py --max-images 50            # Limit for testing
    python scripts/fetch_wikiart.py --artists-only             # Only curated biblical artists
    python scripts/fetch_wikiart.py --artist gustave-dore      # Only one specific artist
    python scripts/fetch_wikiart.py --artist rembrandt --artist el-greco  # Multiple artists
    python scripts/fetch_wikiart.py --list-artists             # Show all artists in filtered data
"""

import argparse
import json
import os
import re
import shutil
import tarfile
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = REPO_ROOT / "data" / "00_raw" / "wikiart"
PARQUET_PATH = OUTPUT_DIR / "WikiArt.parquet"
FILTERED_PATH = OUTPUT_DIR / "filtered_religious.parquet"
IMAGES_DIR = OUTPUT_DIR / "images"
METADATA_DIR = OUTPUT_DIR / "metadata"

ARCHIVE_BASE = "https://archive.org/download/WikiArt_dataset"
PARQUET_URL = f"{ARCHIVE_BASE}/WikiArt.parquet"
SHARD_URL_TEMPLATE = f"{ARCHIVE_BASE}/WikiArt_{{:03d}}.tar"

# ---------------------------------------------------------------------------
# Curated list of artists known for biblical/religious art
# ---------------------------------------------------------------------------
BIBLICAL_ARTISTS = [
    # --- Renaissance masters ---
    "michelangelo",
    "raphael",
    "leonardo-da-vinci",
    "sandro-botticelli",
    "fra-angelico",
    "giotto",
    "giovanni-bellini",
    "titian",
    "tintoretto",
    "paolo-veronese",
    "andrea-mantegna",
    "piero-della-francesca",
    "filippino-lippi",
    "fra-filippo-lippi",
    "perugino",
    "correggio",
    "albrecht-durer",
    "lucas-cranach-the-elder",
    "hans-holbein-the-younger",
    "hans-memling",
    "rogier-van-der-weyden",
    "jan-van-eyck",
    "hieronymus-bosch",
    "pieter-bruegel-the-elder",
    "el-greco",
    # --- Baroque masters ---
    "caravaggio",
    "rembrandt",
    "peter-paul-rubens",
    "anthony-van-dyck",
    "guido-reni",
    "nicolas-poussin",
    "diego-velazquez",
    "bartolome-esteban-murillo",
    "francisco-de-zurbaran",
    "artemisia-gentileschi",
    "georges-de-la-tour",
    "giovanni-battista-tiepolo",
    # --- Romantic / 19th century ---
    "gustave-dore",
    "william-blake",
    "eugene-delacroix",
    "william-holman-hunt",
    "john-everett-millais",
    "dante-gabriel-rossetti",
    "ford-madox-brown",
    "james-tissot",
    "carl-heinrich-bloch",
    "julius-schnorr-von-carolsfeld",
    "alexandre-cabanel",
    "william-adolphe-bouguereau",
    "gustave-moreau",
    "henry-ossawa-tanner",
    # --- Byzantine / Orthodox / Icons ---
    "andrei-rublev",
    "theophanes-the-greek",
    # --- Modern ---
    "marc-chagall",
    "georges-rouault",
    "salvador-dali",
    "he-qi",
]

# ---------------------------------------------------------------------------
# Tags and keywords that indicate biblical content
# ---------------------------------------------------------------------------
BIBLICAL_TAGS = {
    # Personagens
    "jesus", "christ", "jesus-christ", "mary", "virgin-mary", "madonna",
    "moses", "abraham", "david", "adam", "eve", "noah", "joseph",
    "john-the-baptist", "paul", "peter", "apostle", "apostles",
    "angel", "angels", "archangel", "satan", "devil",
    # Eventos AT
    "creation", "genesis", "exodus", "flood", "babel",
    "sacrifice", "burning-bush", "ten-commandments", "red-sea",
    "garden-of-eden", "forbidden-fruit", "original-sin",
    # Eventos NT
    "nativity", "annunciation", "baptism", "temptation",
    "sermon-on-the-mount", "transfiguration", "miracle",
    "last-supper", "crucifixion", "resurrection", "ascension",
    "pentecost", "good-samaritan", "prodigal-son",
    "raising-of-lazarus", "entry-into-jerusalem",
    # Geral
    "bible", "biblical", "scripture", "gospel",
    "christian", "christianity", "church", "cathedral",
    "saint", "saints", "holy", "sacred", "prayer",
    "heaven", "hell", "paradise", "judgment", "apocalypse",
    "cross", "crucifix", "pieta", "madonna-and-child",
    "holy-family", "holy-spirit", "trinity",
}

BIBLICAL_TITLE_PATTERNS = [
    r"\bchrist\b", r"\bjesus\b", r"\bmadonna\b", r"\bvirgin\b",
    r"\bcrucifi", r"\bnativity\b", r"\bannunciat", r"\bbaptism\b",
    r"\bresurrect", r"\bascension\b", r"\blast\s+supper\b",
    r"\bholy\s+family\b", r"\bpieta\b", r"\bpietà\b",
    r"\badam\b.*\beve\b", r"\beve\b.*\badam\b",
    r"\bmoses\b", r"\babraham\b", r"\bnoah\b", r"\bdavid\b.*\bgoliath\b",
    r"\bgarden\s+of\s+eden\b", r"\bflood\b", r"\bexodus\b",
    r"\bjudgment\b", r"\bapocalyps", r"\brevelation\b",
    r"\bsaint\s+\w+", r"\bst\.\s+\w+",
    r"\bbibl", r"\bgospel\b", r"\bpsalm\b", r"\bgenesis\b",
    r"\bparable\b", r"\bprodigal\b", r"\bsamaritan\b",
    r"\blazarus\b", r"\btransfigurat", r"\bpentecost\b",
    r"\bsermon\b", r"\bmiracle\b", r"\bprophet\b",
]


def download_file(url, dest, dry_run=False):
    """Download a file with progress bar."""
    import requests
    from tqdm import tqdm

    if dry_run:
        print(f"  [dry-run] Would download: {url}")
        print(f"            To: {dest}")
        return False

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        print(f"  [skip] Already exists: {dest.name}")
        return True

    print(f"  Downloading: {url}")
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))

    with open(dest, "wb") as f, tqdm(
        total=total, unit="B", unit_scale=True, desc=dest.name
    ) as bar:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

    return True


def normalize_artist_slug(name):
    """Convert artist name to WikiArt URL slug format."""
    import unicodedata
    if not name:
        return ""
    slug = name.lower().strip()
    # Normalize unicode accents (é -> e, ü -> u, etc.)
    slug = unicodedata.normalize("NFD", slug)
    slug = "".join(c for c in slug if unicodedata.category(c) != "Mn")
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def to_str_list(val):
    """Convert a column value (array, list, str, or None) to a list of lowercase strings."""
    if val is None:
        return []
    try:
        if hasattr(val, "__iter__") and not isinstance(val, str):
            return [str(v).lower() for v in val if v is not None]
    except (TypeError, ValueError):
        pass
    return [str(val).lower()]


def is_biblical_by_tags(tags_val):
    """Check if painting tags contain biblical keywords."""
    tags_list = to_str_list(tags_val)
    if not tags_list:
        return False
    tags_joined = " ".join(tags_list)
    return any(tag in tags_joined for tag in BIBLICAL_TAGS)


def is_biblical_by_title(title):
    """Check if painting title matches biblical patterns."""
    if not title or not isinstance(title, str):
        return False
    title_lower = title.lower()
    return any(re.search(p, title_lower) for p in BIBLICAL_TITLE_PATTERNS)


def filter_religious_paintings(df, artists_only=False):
    """Filter dataframe for religious/biblical paintings.

    Three-layer filter:
      1. genre == "religious painting" (or similar)
      2. tags contain biblical keywords
      3. title matches biblical patterns
      4. artist is in curated biblical artists list

    Returns filtered dataframe with a 'match_reason' column.
    """
    import pandas as pd

    # Layer 1: Genre
    genre_mask = df["genres"].apply(
        lambda v: any("religious" in s for s in to_str_list(v))
    )

    # Layer 2: Tags
    tag_mask = df["tags"].fillna("").apply(is_biblical_by_tags)

    # Layer 3: Title
    title_mask = df["title"].fillna("").apply(is_biblical_by_title)

    # Layer 4: Biblical artist
    artist_slugs = df["artist"].fillna("").apply(normalize_artist_slug)
    artist_mask = artist_slugs.isin(BIBLICAL_ARTISTS)

    if artists_only:
        combined_mask = artist_mask & (genre_mask | tag_mask | title_mask)
    else:
        combined_mask = genre_mask | tag_mask | title_mask

    filtered = df[combined_mask].copy()

    # Build match_reason column
    reasons = []
    for idx in filtered.index:
        parts = []
        if genre_mask.at[idx]:
            parts.append("genre")
        if tag_mask.at[idx]:
            parts.append("tags")
        if title_mask.at[idx]:
            parts.append("title")
        if artist_mask.at[idx]:
            parts.append("artist")
        reasons.append(";".join(parts))
    filtered["match_reason"] = reasons

    return filtered


def step_metadata(args):
    """Step 1: Download parquet and filter for religious paintings."""
    import pandas as pd

    print("\n=== Step 1: Load WikiArt.parquet ===\n")
    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Use local parquet from --local-shards if available
    if args.local_shards:
        local_parquet = Path(args.local_shards) / "WikiArt.parquet"
        if local_parquet.exists() and not PARQUET_PATH.exists():
            print(f"  Copying parquet from local: {local_parquet}")
            shutil.copy2(local_parquet, PARQUET_PATH)

    if not PARQUET_PATH.exists():
        if not download_file(PARQUET_URL, PARQUET_PATH, dry_run=args.dry_run):
            if args.dry_run:
                print("\n  [dry-run] Would filter parquet for religious paintings")
                return
            return

    print("\n=== Step 2: Filter for religious/biblical paintings ===\n")
    df = pd.read_parquet(PARQUET_PATH)
    print(f"  Total paintings in WikiArt: {len(df):,}")

    # Show genre distribution
    print("\n  Genre distribution:")
    for genre, count in df["genres"].value_counts().head(15).items():
        marker = " <--" if "religious" in str(genre).lower() else ""
        print(f"    {genre}: {count:,}{marker}")

    # Filter
    filtered = filter_religious_paintings(df, artists_only=args.artists_only)

    if args.max_images and len(filtered) > args.max_images:
        filtered = filtered.head(args.max_images)

    print(f"\n  Filtered religious/biblical paintings: {len(filtered):,}")

    # Stats
    print("\n  Match reasons:")
    all_reasons = []
    for r in filtered["match_reason"]:
        all_reasons.extend(r.split(";"))
    for reason, count in Counter(all_reasons).most_common():
        if reason:
            print(f"    {reason}: {count:,}")

    print(f"\n  Unique artists: {filtered['artist'].nunique()}")
    print("\n  Top 20 artists:")
    for artist, count in filtered["artist"].value_counts().head(20).items():
        biblical = " *" if normalize_artist_slug(artist) in BIBLICAL_ARTISTS else ""
        print(f"    {artist}: {count}{biblical}")

    # Identify shards needed
    if "key" in filtered.columns:
        filtered["shard"] = filtered["key"].astype(str).str[:3].astype(int)
        shards_needed = sorted(filtered["shard"].unique())
        print(f"\n  Tar shards needed: {len(shards_needed)} of 20")
        print(f"  Shard IDs: {shards_needed}")

    # Save filtered parquet
    if not args.dry_run:
        filtered.to_parquet(FILTERED_PATH, index=False)
        print(f"\n  Saved: {FILTERED_PATH}")
        print(f"  Size: {FILTERED_PATH.stat().st_size / 1024:.1f} KB")
    else:
        print(f"\n  [dry-run] Would save filtered parquet to: {FILTERED_PATH}")


def save_image_metadata(row, meta_path):
    """Save per-image metadata JSON from a parquet row."""
    import pandas as pd

    meta = {
        "key": str(row.get("key")),
        "title": row.get("title"),
        "artist": row.get("artist"),
        "completion": int(row["completion"]) if pd.notna(row.get("completion")) else None,
        "styles": list(row["styles"]) if row.get("styles") is not None else [],
        "genres": list(row["genres"]) if row.get("genres") is not None else [],
        "tags": list(row["tags"]) if row.get("tags") is not None else [],
        "media": list(row["media"]) if row.get("media") is not None else [],
        "width": int(row["width"]) if pd.notna(row.get("width")) else None,
        "height": int(row["height"]) if pd.notna(row.get("height")) else None,
        "artist_birth": str(row.get("artist_birth")) if row.get("artist_birth") is not None else None,
        "artist_death": str(row.get("artist_death")) if row.get("artist_death") is not None else None,
        "artist_nations": list(row["artist_nations"]) if row.get("artist_nations") is not None else [],
        "img_url": row.get("img_url"),
        "match_reason": row.get("match_reason", ""),
        "source": "wikiart",
    }
    # Convert numpy types to native Python
    meta = json.loads(json.dumps(meta, default=str))
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def apply_artist_filter(df, artist_slugs):
    """Filter dataframe by artist slug(s)."""
    if not artist_slugs:
        return df
    mask = df["artist"].apply(normalize_artist_slug).isin(artist_slugs)
    filtered = df[mask]
    print(f"  Artist filter: {len(filtered):,} images from {artist_slugs}")
    return filtered


def step_images(args):
    """Step 2: Download images from Internet Archive tar shards."""
    import pandas as pd
    from tqdm import tqdm

    if not FILTERED_PATH.exists():
        print(f"ERROR: {FILTERED_PATH} not found. Run --step metadata first.")
        return

    df = pd.read_parquet(FILTERED_PATH)

    # Apply artist filter
    if args.artist:
        df = apply_artist_filter(df, args.artist)
        if df.empty:
            print("  No images match the artist filter.")
            print("  Use --list-artists to see available artists.")
            return

    if args.max_images and len(df) > args.max_images:
        df = df.head(args.max_images)

    print(f"\n=== Step 3: Download images ({len(df):,} paintings) ===\n")

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    # First: save all metadata from parquet (no download needed)
    print("  Saving metadata JSONs...")
    for _, row in df.iterrows():
        key = str(row["key"])
        meta_path = METADATA_DIR / f"{key}.json"
        if not meta_path.exists() and not args.dry_run:
            save_image_metadata(row, meta_path)

    # Group by shard
    df["shard"] = df["key"].astype(str).str[:3].astype(int)
    shard_groups = df.groupby("shard")

    total_extracted = 0
    total_skipped = 0

    for shard_id, group in shard_groups:
        # Skip shards not in --shard filter
        if args.shard and shard_id not in args.shard:
            continue

        shard_keys = set(group["key"].astype(str))

        # Check how many we already have
        already_have = sum(1 for k in shard_keys if (IMAGES_DIR / f"{k}.jpg").exists())
        need = len(shard_keys) - already_have

        if need == 0:
            total_skipped += len(shard_keys)
            continue

        print(f"\n  Shard {shard_id:03d}: {need} images to extract ({already_have} already exist)")

        if args.dry_run:
            total_extracted += need
            total_skipped += already_have
            print(f"  [dry-run] Would extract {need} images from shard {shard_id:03d}")
            continue

        # Resolve shard path: local or download
        if args.local_shards:
            local_dir = Path(args.local_shards)
            shard_path = local_dir / f"WikiArt_{shard_id:03d}.tar"
            if not shard_path.exists():
                print(f"  [skip] Local shard not found: {shard_path}")
                continue
            tmp_path = None  # Don't delete local files
        else:
            shard_url = SHARD_URL_TEMPLATE.format(shard_id)
            shard_path = OUTPUT_DIR / f"_tmp_shard_{shard_id:03d}.tar"
            tmp_path = shard_path
            if not download_file(shard_url, shard_path):
                continue

        try:
            # Extract matching files
            print(f"  Extracting {need} images from shard...")
            with tarfile.open(str(shard_path), "r") as tar:
                for member in tqdm(tar, desc=f"  Shard {shard_id:03d}", leave=False):
                    if not member.isfile():
                        continue

                    # Key is first 7 chars of filename
                    basename = Path(member.name).name
                    file_key = basename.split("_")[0] if "_" in basename else Path(basename).stem

                    if file_key not in shard_keys:
                        continue

                    ext = Path(member.name).suffix.lower()
                    if ext in (".jpg", ".jpeg", ".png"):
                        dest = IMAGES_DIR / f"{file_key}.jpg"
                        if dest.exists():
                            continue
                        f = tar.extractfile(member)
                        if f:
                            dest.write_bytes(f.read())
                            total_extracted += 1

        except Exception as e:
            print(f"  [error] Shard {shard_id:03d}: {e}")

        finally:
            # Only delete temp files (downloaded shards), never local ones
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()

    print(f"\n  Total extracted: {total_extracted:,}")
    if total_skipped:
        print(f"  Skipped (already exist): {total_skipped:,}")


def list_artists(args):
    """Show all artists in the filtered dataset."""
    import pandas as pd

    if not FILTERED_PATH.exists():
        print(f"ERROR: {FILTERED_PATH} not found. Run --step metadata first.")
        return

    df = pd.read_parquet(FILTERED_PATH)
    print(f"\n  Artists in filtered dataset ({df['artist'].nunique()} unique):\n")
    print(f"  {'Artist':<45} {'Slug':<35} {'Count':>5}")
    print(f"  {'-'*45} {'-'*35} {'-'*5}")

    for artist, count in df["artist"].value_counts().items():
        slug = normalize_artist_slug(artist)
        biblical = " *" if slug in BIBLICAL_ARTISTS else ""
        print(f"  {artist:<45} {slug:<35} {count:>5}{biblical}")

    print(f"\n  * = curated biblical artist")
    print(f"  Use: --artist <slug> to filter by artist")


def generate_manifest(args):
    """Generate manifest.json summarizing what was downloaded."""
    import pandas as pd

    if not FILTERED_PATH.exists():
        print("  [skip] No filtered parquet found, skipping manifest")
        return

    df = pd.read_parquet(FILTERED_PATH)

    image_count = len(list(IMAGES_DIR.glob("*.jpg"))) if IMAGES_DIR.exists() else 0

    manifest = {
        "source": "WikiArt (Internet Archive dump, July 2022)",
        "source_url": "https://archive.org/details/WikiArt_dataset",
        "license": "Non-commercial research only (WikiArt terms)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_filtered": len(df),
        "total_downloaded": image_count,
        "unique_artists": int(df["artist"].nunique()),
        "genre_distribution": df["genres"].apply(
            lambda v: ", ".join(to_str_list(v)) if v is not None else "unknown"
        ).value_counts().head(20).to_dict(),
        "top_artists": df["artist"].value_counts().head(30).to_dict(),
        "match_reasons": dict(Counter(
            r for reasons in df["match_reason"]
            for r in reasons.split(";") if r
        )),
        "fields_available": [
            "key", "artist", "title", "completion", "styles", "genres",
            "tags", "media", "width", "height", "aesthetic",
            "artist_birth", "artist_death", "artist_nations",
            "artist_movements", "img_url", "caption",
        ],
    }

    manifest_path = OUTPUT_DIR / "manifest.json"
    if not args.dry_run:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"\n  Manifest saved: {manifest_path}")
    else:
        print(f"\n  [dry-run] Would save manifest to: {manifest_path}")
        print(f"  Filtered paintings: {len(df):,}")
        print(f"  Unique artists: {int(df['artist'].nunique())}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch religious/biblical paintings from WikiArt Internet Archive dataset"
    )
    parser.add_argument(
        "--step",
        choices=["metadata", "images", "all"],
        default="all",
        help="Which step to run (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without downloading",
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=None,
        help="Limit number of images to process (useful for testing)",
    )
    parser.add_argument(
        "--artists-only",
        action="store_true",
        help="Only include paintings from curated biblical artists list",
    )
    parser.add_argument(
        "--artist",
        action="append",
        metavar="SLUG",
        help="Filter by artist slug (e.g., gustave-dore, rembrandt). Can repeat.",
    )
    parser.add_argument(
        "--list-artists",
        action="store_true",
        help="List all artists in the filtered dataset and exit",
    )
    parser.add_argument(
        "--shard",
        type=int,
        action="append",
        metavar="N",
        help="Only process specific shard(s) 0-19 (e.g., --shard 0 --shard 1)",
    )
    parser.add_argument(
        "--local-shards",
        type=str,
        metavar="DIR",
        help="Path to local directory with WikiArt_XXX.tar files (from torrent download)",
    )
    args = parser.parse_args()

    # Check dependencies
    try:
        import pandas  # noqa: F401
        import requests  # noqa: F401
        from tqdm import tqdm  # noqa: F401
    except ImportError as e:
        print(f"Error: Missing dependency: {e.name}")
        print("Install with: pip install pandas requests tqdm pyarrow")
        return

    print("=" * 60)
    print("  WikiArt Religious Paintings Fetcher")
    print("=" * 60)
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Step: {args.step}")
    print(f"  Dry run: {args.dry_run}")
    print(f"  Artists only: {args.artists_only}")
    if args.artist:
        print(f"  Artist filter: {args.artist}")
    if args.max_images:
        print(f"  Max images: {args.max_images}")

    if args.list_artists:
        list_artists(args)
        return

    if args.step in ("metadata", "all"):
        step_metadata(args)

    if args.step in ("images", "all"):
        step_images(args)

    generate_manifest(args)

    print("\n" + "=" * 60)
    print("  Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
