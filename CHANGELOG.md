# Changelog

## [0.2.0] - 2026-03-16

### Added
- `fetch_wikiart.py` — full extraction pipeline with `--local-shards` support for torrent downloads
- 16,914 religious/biblical paintings extracted from WikiArt Internet Archive dataset
- Per-image metadata JSON with title, artist, year, styles, genres, tags, media
- `filtered_religious.parquet` index with all filtered paintings
- `manifest.json` dataset summary

### Changed
- Updated README.md with actual numbers (16,914 images, 1,892 artists)
- Updated SOURCES.md — WikiArt as primary source, other sources moved to "future"
- Updated METHODOLOGY.md with actual filtering pipeline (3-layer: genre + tags + title)
- Added `pandas` and `pyarrow` to requirements.txt

### Removed
- `download_wikiart_images.py` (Playwright-based approach, replaced by tar extraction)
- Empty source directories (artbible, biblevsa, freebible, etc.) — will be created when needed
- `WikiArt.parquet` full copy (38MB) — only filtered parquet kept

## [0.1.0] - 2026-03-15

### Added
- Initial repository structure with data pipeline layers (00_raw through 04_splits)
- SOURCES.md documenting 10+ image sources with access methods and licenses
- METHODOLOGY.md with full pipeline documentation
- README.md with overview, schema, and citation
- CONTRIBUTING.md with pipeline guide and PR checklist
