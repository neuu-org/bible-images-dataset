# Contributing

Guide for adding new image sources, expanding verse mappings, or improving the pipeline.

## Adding Images from a New Source

### 1. Download/scrape to 00_raw

Create a script in `scripts/` (e.g., `scrape_new_source.py`) that downloads images and metadata to:

```
data/00_raw/{source_name}/
├── images/                    # Original image files
├── metadata/                  # Source-specific metadata (JSON, CSV, etc.)
└── manifest.json              # Download inventory
```

### 2. Normalize references

Run `normalize_references.py` to map source metadata to OSIS verse references:

```bash
python scripts/normalize_references.py --source new_source
```

### 3. Validate

```bash
python scripts/validate.py --layer 01_mapped --source new_source
```

### 4. Commit

Follow conventional commits:
```
feat: add {source_name} images ({count} images, {books} coverage)
```

---

## Pull Request Checklist

- [ ] New scraper/fetcher script added to `scripts/` (if new source)
- [ ] Images stored in `data/00_raw/{source}/images/`
- [ ] Metadata includes license information for each image
- [ ] `normalize_references.py` runs without errors on new data
- [ ] `validate.py` passes on new data
- [ ] CHANGELOG.md updated
- [ ] No secrets or API keys in committed files
- [ ] Large files (images, embeddings) tracked by Git LFS

---

## Cost Estimation

Before running enrichment on a large batch:

| Operation | Model | Cost per image | 1,000 images | 20,000 images |
|-----------|-------|----------------|--------------|---------------|
| CLIP embedding | Local GPU | Free | Free | Free |
| CLIP embedding | Colab Pro | ~$0.001 | ~$1 | ~$15 |
| Title-to-verse NLP | GPT-4o-mini | ~$0.0005 | ~$0.50 | ~$10 |
| ICONCLASS mapping | GPT-4o-mini | ~$0.005 | ~$5 | N/A (one-time) |

**Recommendation**: Always test with `--max-files 10` first to verify output quality and actual cost.
