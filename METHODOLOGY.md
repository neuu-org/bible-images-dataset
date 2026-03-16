# Metodologia — Bible Images Dataset

**Componente**: Mapeamento imagem-versiculo para arte biblica
**Objetivo**: Construir um dataset que associa obras de arte biblica a versiculos especificos, habilitando classificacao de imagens e busca multimodal
**Versao**: 0.2
**Data**: 16 de marco de 2026

---

## 1. Visao Geral

Este dataset mapeia imagens de arte biblica (pinturas, gravuras, iluminuras, aquarelas) a versiculos da Biblia no formato OSIS (BOOK.CHAPTER.VERSE). Cada imagem recebe um ou mais versiculos associados, com nivel de confianca e metodo de mapeamento.

O objetivo final e treinar modelos que, dada uma imagem, identifiquem qual passagem biblica ela representa — e vice-versa, dada uma passagem, recuperem imagens relevantes.

---

## 2. Fonte de Dados

### WikiArt (Internet Archive dump)

Fonte primaria: dataset completo do WikiArt hospedado no Internet Archive (195,394 pinturas, scrape de julho 2022).

**Formato do dataset original**:
- 20 shards WebDataset (.tar), ~5GB cada
- 1 arquivo parquet com metadados de todas as 195K obras
- CLIP embeddings pre-calculados (ViT-B/32)

**Aquisicao**: Download via torrent (103GB total) e extracao seletiva das imagens religiosas/biblicas.

---

## 3. Filtragem

O script `fetch_wikiart.py` aplica tres camadas de filtragem sobre o parquet de metadados:

### Camada 1: Genero
Pinturas com `genres` contendo "religious painting".
- Resultado: 9,965 obras

### Camada 2: Tags
Pinturas com `tags` contendo keywords biblicos. Lista curada de ~80 termos em categorias:
- **Personagens**: Jesus-Christ, Virgin-Mary, Moses, Abraham, Adam, Eve, etc.
- **Eventos AT**: creation, genesis, flood, babel, exodus, etc.
- **Eventos NT**: nativity, annunciation, crucifixion, resurrection, last-supper, etc.
- **Geral**: Christianity, bible, gospel, saint, holy, prayer, etc.
- Resultado: 10,092 obras

### Camada 3: Titulo
Pinturas cujo titulo faz match com regex patterns biblicos (ex: `\bchrist\b`, `\bmoses\b`, `\bcrucifi`, `\blast\s+supper\b`).
- Resultado: 8,041 obras

### Resultado combinado
Uniao das tres camadas: **16,914 imagens unicas** de **1,892 artistas**.

Adicionalmente, o script mantem uma lista curada de ~50 artistas conhecidos por arte biblica (Dore, Rubens, Rembrandt, Fra Angelico, etc.) usada como flag de qualidade (`match_reason` inclui "artist").

---

## 4. Extracao

Para cada imagem filtrada, o script extrai do shard `.tar` correspondente:
- **Imagem JPG**: salva como `data/00_raw/wikiart/images/{key}.jpg`
- **Metadata JSON**: salva como `data/00_raw/wikiart/metadata/{key}.json`

O `key` (7 digitos) identifica unicamente cada obra. Os 3 primeiros digitos indicam o shard de origem.

---

## 5. Pipeline de Processamento (proximo)

### Fase 1: Mapeamento e Normalizacao (01_mapped)

`normalize_references.py` (a implementar):

- Usar titulo + tags para inferir passagem biblica via NLP
- Para artistas curados (Dore, Tissot): mapear titulos descritivos como "Abraham Journeying Into the Land of Canaan" → GEN.12.1-5
- Para imagens com tag `Jesus-Christ` + titulo especifico: mapear a episodio do NT
- Fallback: LLM para inferencia de passagem a partir do titulo

### Fase 2: Deduplicacao (02_deduplicated)

`deduplicate.py` (a implementar):

1. **Perceptual hashing** (pHash/dHash): cluster de imagens com Hamming distance < 8
2. **CLIP similarity**: cosine similarity > 0.95 = duplicata
3. Manter versao de maior resolucao, mergear mapeamentos

### Fase 3: Enriquecimento (03_enriched)

`enrich_clip.py` (a implementar):

1. **CLIP embeddings**: vetores 768-dim com `clip-vit-large-patch14`
2. **Similarity score**: CLIP(imagem) vs CLIP(texto do versiculo)
3. **Quality score**: composito de resolucao + CLIP similarity + confianca

### Fase 4: Splits para ML (04_splits)

`create_splits.py` (a implementar):

- Granularidade: episodio (~200-400 classes)
- Split 70/15/15 train/val/test, estratificado por episodio
- **Artist-aware**: mesmo artista nao aparece em train E test

---

## 6. Validacao

### Automatizada
1. Schema: todo JSON conforme schema definido
2. Referencias OSIS: todo `osis` resolve para versiculo valido
3. Integridade: SHA256 confere, imagem carregavel via PIL, resolucao minima 100x100
4. Cobertura: distribuicao por livro, testamento, episodio
5. Duplicatas: nenhum `image_id` repetido

### Manual
- Amostra de 50 imagens por fonte: verificar se a imagem retrata a passagem mapeada
- Target: >90% acuracia para mapeamentos com confianca "high"

---

## 7. Limitacoes e Viezes

### Viezes conhecidos

- **Viez narrativo**: Passagens narrativas (Genesis, Evangelhos) tem muito mais representacao artistica que livros poeticos ou profeticos
- **Viez cultural**: Arte ocidental (europeia) domina as fontes
- **Viez temporal**: Maioria das obras sao dos seculos XV-XIX
- **Viez de episodio**: Crucificacao, Natividade e Criacao sao desproporcionalmente representadas

### Mitigacoes

- Documentar distribuicao de episodios
- Priorizar fontes diversas em futuras iteracoes
- Data augmentation para classes sub-representadas

---

## 8. Casos de Uso

1. **Classificacao de imagens**: dada uma imagem, prever qual episodio/passagem biblica ela representa
2. **Busca multimodal**: texto → imagem e imagem → texto
3. **Enriquecimento da bible-api**: endpoint `/api/bible/verses/{book}/{ch}/{vs}/images/`
4. **Pesquisa academica**: estudo quantitativo de representacao biblica na historia da arte
