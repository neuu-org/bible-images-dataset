# Fontes de Dados — Bible Images Dataset

---

## Fonte Primaria — WikiArt (Internet Archive)

### WikiArt Dataset (Internet Archive dump)

| Campo | Valor |
|-------|-------|
| URL | https://archive.org/details/WikiArt_dataset |
| Total no dataset | 195,394 imagens |
| Filtradas (religioso/biblico) | 16,914 imagens |
| Artistas unicos | 1,892 |
| Licenca | Uso nao-comercial para pesquisa. Obras pre-1928 sao dominio publico |
| Acesso | Torrent (103 GB) ou HTTP por shard |
| Formato | 20 shards WebDataset (.tar) + parquet de metadados |
| Data do scrape | Julho 2022 |

O dataset do Internet Archive contem toda a colecao WikiArt com metadados ricos em formato parquet.

**Metadados disponiveis por obra**: `title`, `artist`, `completion` (ano), `styles`, `genres`, `tags`, `media`, `width`, `height`, `img_url`, `caption`, `aesthetic` (score), `artist_birth`, `artist_death`, `artist_nations`, `artist_movements`, CLIP embeddings pre-calculados.

### Filtragem aplicada

Tres camadas de filtragem para identificar pinturas biblicas/religiosas:

1. **Genero** (`genres` contem "religious painting"): 9,965 obras
2. **Tags** (keywords biblicos como `Christianity`, `Jesus-Christ`, `Moses`, `Crucifixion`, `Virgin-Mary`, etc.): 10,092 obras
3. **Titulo** (regex para nomes/eventos biblicos como "Christ", "Madonna", "Crucifixion", "Moses", etc.): 8,041 obras

A uniao dessas camadas resultou em **16,914 imagens unicas**.

### Distribuicao de tags (top 20 nas pinturas religiosas)

| Tag | Contagem |
|-----|----------|
| Christianity | 4,515 |
| saints-and-apostles | 2,242 |
| Mythology | 2,103 |
| Jesus-Christ | 1,276 |
| Virgin-Mary | 864 |
| Holy places | 852 |
| Prophet | 751 |
| angels-and-archangels | 709 |
| Virgin-and-Child | 614 |
| Crucifixion | 204 |
| Old-Testament | 197 |
| St. John the Baptist | 196 |
| Annunciation | 151 |
| Holy-Family | 133 |
| St.-Peter | 99 |
| Cross | 96 |
| Moses | 84 |

### Top 20 artistas

| Artista | Obras | Curado |
|---------|-------|--------|
| Gustave Doré | 301 | sim |
| Giovanni Battista Piranesi | 245 | — |
| Peter Paul Rubens | 235 | sim |
| Orthodox Icons | 211 | — |
| James Tissot | 197 | sim |
| Fra Angelico | 168 | sim |
| Pietro Perugino | 166 | — |
| Hieronymus Bosch | 157 | sim |
| Tintoretto | 156 | sim |
| Bartolomé Esteban Murillo | 151 | sim |
| Romanesque Architecture | 144 | — |
| El Greco | 136 | sim |
| Hans Memling | 129 | sim |
| Francisco de Zurbarán | 127 | sim |
| Raphael | 114 | sim |
| Paolo Veronese | 114 | sim |
| Titian | 114 | sim |
| Sandro Botticelli | 109 | sim |
| Michelangelo | 105 | sim |
| Palma il Giovane | 104 | — |

### Script de extracao

```bash
# Pipeline completo (com shards locais do torrent)
python scripts/fetch_wikiart.py --local-shards /path/to/WikiArt_dataset

# Apenas metadata + filtragem
python scripts/fetch_wikiart.py --step metadata

# Apenas extracao de imagens
python scripts/fetch_wikiart.py --step images --local-shards /path/to/WikiArt_dataset

# Dry-run
python scripts/fetch_wikiart.py --dry-run

# Filtrar por artista
python scripts/fetch_wikiart.py --step images --artist gustave-dore --local-shards /path/to/shards
```

---

## Fontes Futuras (a explorar)

Fontes adicionais que podem complementar o dataset em iteracoes futuras.

### Tier 1 — Pre-mapeadas (imagem ja associada a passagem)

| Fonte | Est. Imagens | Licenca | Acesso |
|-------|-------------|---------|--------|
| Vanderbilt ACT Database | ~7,000 | CC | Scrape HTML |
| FreeBibleImages | ~5,000 | Uso livre | Download por story set |
| BibleVSA Dataset | 2,282 | Academico | Download ZIP |
| Visual Commentary on Scripture | ~1,200 | CC | Scrape HTML |
| ArtBible.info | ~500 | Dominio publico | Scrape HTML |

### Tier 2 — APIs de Museus + ICONCLASS

| Fonte | Est. Imagens | Licenca | Acesso |
|-------|-------------|---------|--------|
| Metropolitan Museum API | ~3,000 | CC0 | REST API |
| Rijksmuseum API | ~2,000 | CC0 | REST API + ICONCLASS |
| James Tissot Collection | 733 | CC0 | Met API / Wikimedia |

### Tier 3 — Complementares

| Fonte | Est. Imagens | Licenca |
|-------|-------------|---------|
| Wikimedia Commons | ~2,000 | CC/PD (varia) |
| Pitts Theology Library | 65,000+ | Academico |
| Cathopic Public Domain | A verificar | Dominio publico |

---

## Ferramenta-chave: ICONCLASS

[ICONCLASS](https://iconclass.org/) e um sistema de classificacao hierarquico para conteudo de obras de arte:

```
7       Biblia
├── 71  Antigo Testamento
│   ├── 71A  Genesis: criacao, Adao e Eva
│   ├── 71C  Genesis: Noe
│   ├── 71D  Genesis: Abraao
│   └── ...
├── 73  Novo Testamento
│   ├── 73A  Infancia e juventude de Cristo
│   ├── 73B  Vida publica de Cristo
│   ├── 73C  Paixao de Cristo
│   ├── 73D  Ressurreicao e aparicoes
│   └── ...
```

Museus como Met e Rijksmuseum tagueiam colecoes com ICONCLASS. Ao construir uma tabela `ICONCLASS code → passagem OSIS`, podemos mapear automaticamente imagens de museus a versiculos.
