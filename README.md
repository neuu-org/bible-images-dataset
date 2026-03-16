# Bible Images Dataset

Biblical artwork mapped to scripture references for multimodal verse retrieval and image classification.

Part of the [NEUU](https://github.com/neuu-org) biblical scholarship ecosystem.

## Overview

| Metric | Value |
|--------|-------|
| Status | Raw data collected, mapping phase next |
| Total images | 16,914 |
| Primary source | WikiArt (Internet Archive dump, 195K paintings) |
| Unique artists | 1,892 |
| Verse mapping | OSIS format (BOOK.CHAPTER.VERSE) |
| License | Non-commercial research (WikiArt terms) |

## Source

Images were extracted from the [WikiArt Internet Archive dataset](https://archive.org/details/WikiArt_dataset) (195,394 paintings, July 2022 scrape). The extraction filtered for religious/biblical content using three criteria:

1. **Genre**: `religious painting` (9,965 paintings)
2. **Tags**: Biblical keywords — `Christianity`, `Jesus-Christ`, `Moses`, `Crucifixion`, etc. (10,092 matches)
3. **Title**: Regex patterns matching biblical names, events, and themes (8,041 matches)

Combined (with overlap): **16,914 unique images** from **1,892 artists**.

### Top Artists

| Artist | Images | Curated |
|--------|--------|---------|
| Gustave Doré | 301 | yes |
| Peter Paul Rubens | 235 | yes |
| Orthodox Icons | 211 | — |
| James Tissot | 197 | yes |
| Fra Angelico | 168 | yes |
| Pietro Perugino | 166 | — |
| Hieronymus Bosch | 157 | yes |
| Tintoretto | 156 | yes |
| El Greco | 136 | yes |
| Michelangelo | 105 | yes |

> Full source analysis: [SOURCES.md](SOURCES.md)

## Pipeline

```
00_raw  --[normalize_references.py]-->  01_mapped  --[deduplicate.py]-->  02_deduplicated  --[enrich_clip.py]-->  03_enriched  --[create_splits.py]-->  04_splits
```

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 0 | `fetch_wikiart.py` | WikiArt parquet + tar shards | Raw images + metadata per image |
| 1 | `normalize_references.py` | 00_raw | 01_mapped (OSIS-normalized mappings) |
| 2 | `deduplicate.py` | 01_mapped | 02_deduplicated (pHash + CLIP dedup) |
| 3 | `enrich_clip.py` | 02_deduplicated | 03_enriched (CLIP embeddings + quality scores) |
| 4 | `create_splits.py` | 03_enriched | 04_splits (train/val/test, stratified) |

## Repository Structure

```
bible-images-dataset/
├── data/
│   ├── 00_raw/
│   │   └── wikiart/
│   │       ├── images/{key}.jpg          # 16,914 images
│   │       ├── metadata/{key}.json       # Per-image metadata
│   │       ├── filtered_religious.parquet # Index of all filtered paintings
│   │       └── manifest.json             # Dataset summary
│   ├── 01_mapped/                        # OSIS-normalized references (TODO)
│   ├── 02_deduplicated/                  # Near-duplicate removal (TODO)
│   ├── 03_enriched/                      # CLIP embeddings + quality scores (TODO)
│   └── 04_splits/                        # ML-ready splits (TODO)
├── scripts/
│   └── fetch_wikiart.py                  # WikiArt data extraction
├── SOURCES.md
├── METHODOLOGY.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

## Data Format

### Per-image metadata (`metadata/{key}.json`)

```json
{
  "key": "0005928",
  "title": "Abraham Journeying Into the Land of Canaan",
  "artist": "Gustave Doré",
  "completion": 1866,
  "styles": ["Romanticism"],
  "genres": ["religious painting"],
  "tags": ["Christianity", "Old-Testament", "Prophet"],
  "media": ["engraving"],
  "width": 800,
  "height": 636,
  "img_url": "https://uploads.wikiart.org/images/gustave-dore/...",
  "match_reason": "genre;tags;title;artist",
  "source": "wikiart"
}
```

## License

Source images carry their original licenses. Works pre-1928 are public domain. WikiArt terms restrict use to non-commercial research.

This license applies to the mapping dataset, processing scripts, and documentation:
Creative Commons Attribution 4.0 International (CC BY 4.0). See [LICENSE](LICENSE).

## Citation

```bibtex
@misc{neuu_bible_images_2026,
  title={Bible Images Dataset: Biblical Artwork Mapped to Scripture References},
  author={NEUU},
  year={2026},
  publisher={GitHub},
  url={https://github.com/neuu-org/bible-images-dataset}
}
```

## Related Datasets (NEUU Ecosystem)

- [bible-text-dataset](https://github.com/neuu-org/bible-text-dataset) — 20 translations (7 EN + 13 PT-BR)
- [bible-commentaries-dataset](https://github.com/neuu-org/bible-commentaries-dataset) — 31,218 patristic commentaries
- [bible-crossrefs-dataset](https://github.com/neuu-org/bible-crossrefs-dataset) — 1.1M+ cross-references
- [bible-topics-dataset](https://github.com/neuu-org/bible-topics-dataset) — 7,873 unified topics
- [bible-gazetteers-dataset](https://github.com/neuu-org/bible-gazetteers-dataset) — 2,474 entities + 347 symbols
- [bible-dictionary-dataset](https://github.com/neuu-org/bible-dictionary-dataset) — 5,998 dictionary entries
