# Bible Images Dataset

Biblical artwork mapped to scripture references for multimodal verse retrieval and image classification.

Part of the [NEUU](https://github.com/neuu-org) biblical scholarship ecosystem.

## Overview

| Metric | Value |
|--------|-------|
| Status | Data collection phase |
| Target images | ~25,000–30,000 (after deduplication) |
| Sources | 10+ (museums, archives, academic datasets) |
| Verse mapping | OSIS format (BOOK.CHAPTER.VERSE) |
| License tiers | Public domain, CC0, CC-BY |
| Embedding model | CLIP ViT-L/14 (768-dim) |
| Episode classes | ~200–400 (creation, crucifixion, exodus, etc.) |

## Sources

| Source | Type | Est. Images | License | Mapping |
|--------|------|-------------|---------|---------|
| Vanderbilt ACT Database | Academic archive | 7,000 | CC | Pre-mapped to scripture |
| FreeBibleImages | Illustration sets | 5,000 | Free use | Pre-mapped by passage |
| BibleVSA Dataset | Academic ML dataset | 2,282 | Academic | Pre-mapped with text |
| Visual Commentary on Scripture | Curated art | 1,200 | CC | Pre-mapped to passage |
| ArtBible.info | Painting archive | 500 | Public domain | Pre-mapped to KJV |
| Internet Archive (Doré, Copping) | Historical engravings | 500 | Public domain | Semi-mapped (captions) |
| Metropolitan Museum API | Museum collection | 3,000 | CC0 | ICONCLASS → verse |
| Rijksmuseum API | Museum collection | 2,000 | CC0 | ICONCLASS → verse |
| James Tissot Collection | Biblical watercolors | 733 | CC0 | Semi-mapped (titles) |
| Wikimedia Commons | Community archive | 2,000 | CC/PD | Title NLP → verse |
| WikiArt (Religious painting genre) | Art encyclopedia | 12,118 | Non-commercial research | Title NLP → verse |

> Full source analysis: [SOURCES.md](SOURCES.md)

## Pipeline

```
00_raw  --[normalize_references.py]-->  01_mapped  --[deduplicate.py]-->  02_deduplicated  --[enrich_clip.py]-->  03_enriched  --[create_splits.py]-->  04_splits
```

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 0 | — | Source downloads | Raw images + metadata per source |
| 1 | `normalize_references.py` | 00_raw | 01_mapped (OSIS-normalized mappings) |
| 2 | `deduplicate.py` | 01_mapped | 02_deduplicated (pHash + CLIP dedup) |
| 3 | `enrich_clip.py` | 02_deduplicated | 03_enriched (CLIP embeddings + quality scores) |
| 4 | `create_splits.py` | 03_enriched | 04_splits (train/val/test, stratified) |

## Repository Structure

```
bible-images-dataset/
├── data/
│   ├── 00_raw/                            # Verbatim downloads per source
│   │   ├── vanderbilt/
│   │   ├── freebible/
│   │   ├── biblevsa/
│   │   ├── visual_commentary/
│   │   ├── artbible/
│   │   ├── internet_archive/
│   │   ├── met/
│   │   ├── rijksmuseum/
│   │   ├── tissot/
│   │   ├── wikimedia/
│   │   ├── wikiart/
│   │   └── manifest.json
│   ├── 01_mapped/                         # OSIS-normalized references
│   │   ├── images/{source}/{image_id}.jpg
│   │   ├── mappings/{source}/{image_id}.json
│   │   └── index.json
│   ├── 02_deduplicated/                   # Near-duplicate removal
│   ├── 03_enriched/                       # CLIP embeddings + quality scores
│   │   ├── embeddings/
│   │   └── mappings/
│   └── 04_splits/                         # ML-ready splits
│       ├── train.json
│       ├── val.json
│       ├── test.json
│       └── label_map.json
├── scripts/
├── SOURCES.md
├── METHODOLOGY.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

## Data Format

### Image-Verse Mapping (per image)

```json
{
  "image_id": "vanderbilt_001234",
  "source": "vanderbilt",
  "source_url": "https://...",
  "filename": "vanderbilt/vanderbilt_001234.jpg",
  "title": "The Creation of Adam",
  "artist": "Michelangelo",
  "date": "c. 1512",
  "license": "public_domain",
  "verses": [
    {"osis": "GEN.1.27", "confidence": "high", "method": "source_metadata"},
    {"osis": "GEN.2.7", "confidence": "medium", "method": "iconclass"}
  ],
  "episode": "creation",
  "iconclass_codes": ["71A221"],
  "quality_score": 85,
  "clip_verse_similarity": 0.34,
  "dimensions": {"width": 1200, "height": 800},
  "sha256": "abc123..."
}
```

### ICONCLASS Mapping

[ICONCLASS](https://iconclass.org/) is a hierarchical classification for art where code `7` = Bible, `71` = Old Testament, `73` = New Testament, with drill-down to specific episodes. Museum images tagged with ICONCLASS codes are programmatically mapped to Bible verses via `build_iconclass_mapping.py`.

## License

Source images carry their original licenses (public domain, CC0, CC-BY). This license applies to the mapping dataset, processing scripts, and documentation.

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
