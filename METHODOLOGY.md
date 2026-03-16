# Metodologia — Bible Images Dataset

**Componente**: Mapeamento imagem-versiculo para arte biblica
**Objetivo**: Construir um dataset que associa obras de arte biblica a versiculos especificos, habilitando classificacao de imagens e busca multimodal
**Versao**: 0.1
**Data**: 15 de marco de 2026

---

## 1. Visao Geral

Este dataset mapeia imagens de arte biblica (pinturas, gravuras, iluminuras, aquarelas) a versiculos da Biblia no formato OSIS (BOOK.CHAPTER.VERSE). Cada imagem recebe um ou mais versiculos associados, com nivel de confianca e metodo de mapeamento.

O objetivo final e treinar modelos que, dada uma imagem, identifiquem qual passagem biblica ela representa — e vice-versa, dada uma passagem, recuperem imagens relevantes.

---

## 2. Fontes de Dados

As fontes estao organizadas em tres tiers de prioridade baseados na qualidade do mapeamento imagem-versiculo.

### Tier 1 — Pre-mapeadas

Fontes que ja fornecem a associacao imagem-versiculo nos seus metadados. Maior confianca, menor esforco de processamento.

- **Vanderbilt ACT Database**: ~7.000 imagens pesquisaveis por referencia biblica
- **FreeBibleImages**: ~5.000 imagens organizadas por story sets (passagens)
- **BibleVSA**: 2.282 iluminuras com pares texto-imagem (dataset academico de ML)
- **Visual Commentary on Scripture**: ~1.200 obras curadas com passagem associada
- **ArtBible.info**: ~500 pinturas linkadas a passagens KJV
- **Internet Archive**: ~500 gravuras historicas (Dore, Copping) com legendas biblicas

### Tier 2 — APIs de Museus + ICONCLASS

Fontes com grandes colecoes CC0, onde o mapeamento e feito via codigos ICONCLASS ou NLP sobre titulos/descricoes.

- **Metropolitan Museum API**: ~3.000 imagens biblicas filtradas, CC0
- **Rijksmuseum API**: ~2.000 imagens com tags ICONCLASS, CC0
- **James Tissot Collection**: 733 aquarelas biblicas, CC0

### Tier 3 — Complementares

- **Wikimedia Commons**: ~2.000 imagens em categorias de arte biblica

> Detalhes completos de cada fonte em [SOURCES.md](SOURCES.md)

---

## 3. ICONCLASS — Taxonomia de Arte Biblica

[ICONCLASS](https://iconclass.org/) e uma classificacao hierarquica para arte onde:

```
7     = Biblia
71    = Antigo Testamento
71A   = Genesis: criacao
71A2  = Criacao de Adao
73    = Novo Testamento
73C   = Paixao de Cristo
73C7  = Crucificacao
73D   = Ressurreicao
```

Museus (Met, Rijksmuseum) tagueiam suas colecoes com codigos ICONCLASS. O script `build_iconclass_mapping.py` converte esses codigos em referencias OSIS, criando a ponte entre metadados museologicos e versiculos.

**Processo**:
1. Download do vocabulario ICONCLASS (subtree "7")
2. Mapeamento semi-automatico: codigo → passagem biblica (curadoria manual + LLM)
3. Para imagens de museus: lookup do codigo ICONCLASS → refs OSIS

---

## 4. Pipeline de Processamento

### Fase 0: Aquisicao (00_raw)

Download/scrape de cada fonte, armazenamento verbatim sem transformacoes. Cada fonte tem seu subdiretorio com `manifest.json` registrando contagens, datas e URLs.

### Fase 1: Mapeamento e Normalizacao (01_mapped)

`normalize_references.py`:

- **Tier 1**: Extrai refs dos metadados da fonte, normaliza para formato OSIS
- **Tier 2**: Aplica tabela ICONCLASS → OSIS via `build_iconclass_mapping.py`
- **Fallback NLP**: Para imagens sem metadata estruturado, usa titulo/descricao com GPT-4o-mini para inferir passagem

Normalizacao de referencias reutiliza o mapeamento `ABBREV_TO_NAME` do [bible-text-dataset](https://github.com/neuu-org/bible-text-dataset).

### Fase 2: Deduplicacao (02_deduplicated)

`deduplicate.py`:

Muitas fontes sobrepoem (mesma gravura de Dore em Vanderbilt, Wikimedia e Internet Archive). Abordagem em dois estagios:

1. **Perceptual hashing** (pHash/dHash via `imagehash`): cluster de imagens com Hamming distance < 8
2. **CLIP embedding similarity**: para casos limites, cosine similarity > 0.95 = duplicata

Dentro de cada cluster: manter a versao de maior resolucao, mergear mapeamentos de todas as duplicatas.

### Fase 3: Enriquecimento (03_enriched)

`enrich_clip.py`:

1. **CLIP embeddings**: Gerar vetores 768-dim com `clip-vit-large-patch14`
2. **Similarity score**: CLIP(imagem) vs CLIP(texto do versiculo) como sinal de confianca
3. **Quality score**: Composito de resolucao + CLIP similarity + confianca do mapeamento + confiabilidade da fonte

### Fase 4: Splits para ML (04_splits)

`create_splits.py`:

- Granularidade: **episodio** (~200-400 classes como "criacao", "diluvio", "crucificacao")
- Split 70/15/15 train/val/test, estratificado por episodio
- **Artist-aware**: mesmo artista nao aparece em train E test (evitar data leakage)

---

## 5. Validacao

### Automatizada (`validate.py`)

1. **Schema**: Todo JSON de mapeamento conforme schema definido
2. **Referencias OSIS**: Todo `osis` resolve para versiculo valido (livro existe, capitulo/versiculo dentro dos limites)
3. **Integridade de imagem**: SHA256 confere, arquivo carregavel via PIL, resolucao minima 100x100
4. **Cobertura**: Distribuicao por livro, testamento, episodio. Flag para categorias sub-representadas
5. **Duplicatas**: Nenhum `image_id` repetido
6. **Licenca**: Flag para imagens sem metadata de licenca

### Manual

- Amostra de 50 imagens por fonte: verificar se a imagem realmente retrata a passagem mapeada
- Target: >90% de acuracia para mapeamentos com confianca "high"

---

## 6. Metricas de Qualidade

| Metrica | Descricao |
|---------|-----------|
| Cobertura por livro | % dos 66 livros com pelo menos 1 imagem |
| Cobertura AT/NT | Distribuicao de imagens por testamento |
| CLIP similarity media | Similaridade media CLIP(imagem, versiculo) |
| Duplicatas removidas | % de imagens eliminadas na deduplicacao |
| Confianca alta | % de mapeamentos com confianca "high" |

---

## 7. Limitacoes e Viezes

### Viezes conhecidos

- **Viez narrativo**: Passagens narrativas (Genesis, Evangelhos) tem muito mais representacao artistica que livros poeticos ou profeticos
- **Viez cultural**: Arte ocidental (europeia) domina as fontes, sub-representando tradicoes artisticas orientais, africanas e latino-americanas
- **Viez temporal**: Maioria das obras sao dos seculos XV-XIX
- **Viez de episodio**: Cenas como Crucificacao, Natividade e Criacao sao desproporcionalmente representadas

### Mitigacoes

- Documentar distribuicao de episodios no `index.json`
- Priorizar fontes diversas (Tissot para NT, Dore para AT)
- Usar data augmentation para classes sub-representadas no treinamento

---

## 8. Casos de Uso

1. **Classificacao de imagens**: Dado uma imagem, prever qual episodio/passagem biblica ela representa
2. **Busca multimodal**: Texto → imagem (encontrar arte para um versiculo) e imagem → texto (encontrar versiculo para uma arte)
3. **Enriquecimento da bible-api**: Endpoint `/api/bible/verses/{book}/{ch}/{vs}/images/` retornando arte associada
4. **Pesquisa acadêmica**: Estudo quantitativo de representacao biblica na historia da arte
