# Fontes de Dados — Bible Images Dataset

Documentacao detalhada de todas as fontes pesquisadas para construcao do dataset de imagens biblicas.

---

## Tier 1 — Fontes Pre-mapeadas

Fontes que ja fornecem associacao direta entre imagem e passagem biblica.

### 1. Vanderbilt ACT Database

| Campo | Valor |
|-------|-------|
| URL | https://diglib.library.vanderbilt.edu/act-search.pl |
| Imagens estimadas | ~7.000 |
| Licenca | Creative Commons |
| Acesso | Scrape HTML — busca por referencia biblica |
| Mapeamento | Pre-mapeado (imagens pesquisaveis por versiculo) |
| Formatos | JPEG |

A Vanderbilt Divinity Library mantém o Art in the Christian Tradition (ACT), um banco de imagens pesquisavel por referencia biblica. Cada imagem esta associada a uma ou mais passagens, com metadados de artista, periodo e meio.

**Vantagens**: Mapeamento direto imagem-versiculo, curadoria academica, grande volume.
**Limitacoes**: Necessita scraping HTML, velocidade de download depende do servidor.

---

### 2. FreeBibleImages

| Campo | Valor |
|-------|-------|
| URL | https://www.freebibleimages.org |
| Imagens estimadas | ~5.000 (760+ story sets) |
| Licenca | Uso livre (verificar termos por set) |
| Acesso | Download por story set (JPEG) |
| Mapeamento | Pre-mapeado (sets organizados por passagem) |
| Formatos | JPEG, alta resolucao |

Colecao de ilustracoes biblicas organizadas em "story sets" — cada set cobre uma passagem especifica. Inclui ilustracoes modernas, fotografias de locais biblicos e arte classica.

**Vantagens**: Organizado por passagem, alta resolucao, variedade de estilos.
**Limitacoes**: Licencas variam por set, algumas imagens sao ilustracoes modernas (diferem do estilo classico).

---

### 3. BibleVSA Dataset

| Campo | Valor |
|-------|-------|
| Referencia | Dataset academico (verificar disponibilidade) |
| Imagens | 2.282 iluminuras |
| Licenca | Academico/pesquisa |
| Acesso | Download ZIP |
| Mapeamento | Pre-mapeado (pares texto-imagem) |
| Formatos | JPEG |

Dataset de ML com 2.282 iluminuras da Biblia de Borso d'Este, cada uma pareada com texto biblico. E o dataset existente mais proximo do nosso objetivo.

**Vantagens**: Ja formatado para ML, pares texto-imagem prontos, dataset academico citavel.
**Limitacoes**: Apenas iluminuras de uma unica fonte (Borso d'Este), escopo limitado.

---

### 4. Visual Commentary on Scripture (VCS)

| Campo | Valor |
|-------|-------|
| URL | https://thevcs.org |
| Imagens estimadas | ~1.200 |
| Licenca | Creative Commons |
| Acesso | Scrape paginas de artwork |
| Mapeamento | Pre-mapeado (cada artwork associado a passagem + 3 obras relacionadas) |
| Formatos | JPEG |

Projeto academico que associa obras de arte a passagens biblicas com comentarios teologicos. Cada entrada inclui uma passagem biblica e tres obras de arte relacionadas.

**Vantagens**: Curadoria academica de alta qualidade, contexto teologico rico.
**Limitacoes**: Volume menor, necessita scraping.

---

### 5. ArtBible.info

| Campo | Valor |
|-------|-------|
| URL | https://www.artbible.info |
| Imagens estimadas | ~500 |
| Licenca | Dominio publico |
| Acesso | Scrape paginas de pinturas |
| Mapeamento | Pre-mapeado (cada pintura linkada a passagem KJV) |
| Formatos | JPEG |

Colecao de pinturas classicas organizadas por passagem biblica (KJV). Foco em grandes mestres da pintura europeia.

**Vantagens**: Obras de alta qualidade artistica, mapeamento direto a KJV.
**Limitacoes**: Volume pequeno, viez para arte europeia renascentista/barroca.

---

### 6. Internet Archive — Ilustracoes Historicas

| Campo | Valor |
|-------|-------|
| URL | https://archive.org |
| Imagens estimadas | ~500 |
| Licenca | Dominio publico |
| Acesso | Download bulk de colecoes |
| Mapeamento | Semi-mapeado (legendas com referencia biblica) |
| Artistas | Gustave Dore (241 gravuras), Harold Copping, Julius Schnorr von Carolsfeld |
| Formatos | JPEG, TIFF |

Colecoes de ilustracoes biblicas historicas em dominio publico. As gravuras de Dore sao as mais conhecidas e amplamente reproduzidas.

**Vantagens**: Alta qualidade artistica, dominio publico garantido, iconicas.
**Limitacoes**: Volume limitado por artista, legendas precisam de NLP para extrair refs OSIS.

---

## Tier 2 — APIs de Museus + ICONCLASS

Grandes colecoes com licenca CC0, onde o mapeamento imagem-versiculo e feito via codigos ICONCLASS ou NLP sobre titulos.

### 7. Metropolitan Museum of Art API

| Campo | Valor |
|-------|-------|
| URL | https://metmuseum.github.io |
| Imagens biblicas estimadas | ~3.000 (filtradas de 406.000+ objetos) |
| Licenca | CC0 (dominio publico) |
| Acesso | REST API (`/public/collection/v1/search?q=bible&isPublicDomain=true`) |
| Mapeamento | ICONCLASS codes + NLP sobre titulos |
| Formatos | JPEG (alta resolucao) |

A maior colecao de arte de acesso aberto do mundo. Filtrar por tags "biblical", "Bible", "Old Testament", "New Testament" + `isPublicDomain=true`. Muitos objetos tem tags ICONCLASS nos metadados.

**Vantagens**: Volume massivo, CC0, API REST bem documentada, metadados ricos.
**Limitacoes**: Necessita filtragem (maioria nao e biblica), ICONCLASS mapping necessario.

---

### 8. Rijksmuseum API

| Campo | Valor |
|-------|-------|
| URL | https://data.rijksmuseum.nl |
| Imagens biblicas estimadas | ~2.000 |
| Licenca | CC0 |
| Acesso | REST API com chave gratuita, filtro ICONCLASS code "7" |
| Mapeamento | ICONCLASS codes (nativamente tagueados) |
| Formatos | JPEG (multiplas resolucoes) |

O Rijksmuseum e especialmente valioso porque muitas obras ja estao tagueadas com codigos ICONCLASS detalhados, facilitando o mapeamento automatico para versiculos.

**Vantagens**: ICONCLASS nativo, CC0, API bem estruturada, arte holandesa de alta qualidade.
**Limitacoes**: Viez para arte holandesa dos seculos XVI-XVII (Rembrandt, etc.).

---

### 9. James Tissot Collection

| Campo | Valor |
|-------|-------|
| Colecao | Brooklyn Museum / Jewish Museum / Met |
| Imagens | 733 aquarelas biblicas |
| Licenca | CC0 |
| Acesso | Met API (colecao Brooklyn Museum) + Wikimedia Commons |
| Mapeamento | Semi-mapeado (titulos descritivos referenciando cenas biblicas) |
| Formatos | JPEG |

James Tissot (1836-1902) pintou 733 aquarelas retratando a vida de Cristo e cenas do Antigo Testamento. E a maior serie continua de ilustracoes biblicas por um unico artista.

**Vantagens**: Cobertura extensa do NT, estilo unico e consistente, CC0.
**Limitacoes**: Unico artista (viez de estilo), mapeamento por titulo necessita NLP.

---

## Tier 3 — Fontes Complementares

### 10. Wikimedia Commons

| Campo | Valor |
|-------|-------|
| URL | https://commons.wikimedia.org |
| Imagens biblicas estimadas | ~2.000+ |
| Licenca | CC / Dominio publico (varia por imagem) |
| Acesso | API MediaWiki, scrape por categoria |
| Categorias relevantes | "Biblical art", "Paintings of the Old Testament", "Paintings of the New Testament", subcategorias por livro |
| Mapeamento | NLP sobre titulos/descricoes + categorias |
| Formatos | JPEG, PNG, SVG |

Wikimedia Commons tem milhares de imagens em categorias de arte biblica. O mapeamento e menos preciso (depende de categorias e titulos).

**Vantagens**: Grande volume, comunidade ativa, metadados de categoria uteis.
**Limitacoes**: Qualidade variavel, licencas heterogeneas, mapeamento impreciso.

---

### 11. Pitts Theology Library (Emory University)

| Campo | Valor |
|-------|-------|
| URL | https://dia.pitts.emory.edu |
| Imagens | 65.000+ ilustracoes biblicas |
| Licenca | Academico (verificar termos) |
| Acesso | A verificar |
| Mapeamento | A verificar |

Potencialmente a maior colecao digital de ilustracoes biblicas. Requer investigacao adicional sobre termos de uso e formato de acesso.

---

### 12. Cathopic Public Domain

| Campo | Valor |
|-------|-------|
| URL | https://cathopic.com/public-domain |
| Imagens | Grande colecao (quantidade exata a verificar) |
| Licenca | Dominio publico |
| Acesso | Download individual ou bulk |
| Mapeamento | NLP sobre titulos |

Arte crista classica digitalmente restaurada em dominio publico.

---

### 13. WikiArt — Religious Painting Genre

| Campo | Valor |
|-------|-------|
| URL | https://www.wikiart.org/en/paintings-by-genre/religious-painting |
| Imagens no genero "Religious painting" | 12.118 |
| Imagens no genero "Mythological painting" | 3.315 (sobreposicao parcial) |
| Licenca | Uso nao-comercial para pesquisa. Obras pre-1928 sao dominio publico |
| API oficial | `https://www.wikiart.org/en/Api/2/` (chaves em `/App/GetApi`) |
| Formatos | JPEG |

WikiArt e a maior enciclopedia visual de belas artes, com ~250.000 obras. O genero "Religious painting" contem 12.118 obras — o 5o maior genero da plataforma.

**Endpoints da API**:

| Endpoint | Descricao |
|----------|-----------|
| `/login?accessCode=X&secretCode=Y` | Autenticacao, retorna SessionKey |
| `/Artist/AlphabetJson?v=new&inPublicDomain=true` | Lista artistas em dominio publico |
| `/Painting/PaintingsByArtist?artistUrl=X&json=2` | Pinturas por artista |
| `/Painting/ImageJson/{contentId}` | Metadados detalhados + URL da imagem |

**Metadados disponiveis por obra**: title, artist, completion (ano), styles, genres, tags, media, width, height, img_url, caption.

**Formas de acesso (3 opcoes)**:

1. **Hugging Face (mais rapido)**: `load_dataset("huggan/wikiart")` — 81.444 imagens, filtrar `genre == "religious_painting"`. ~5.27 GB total.
2. **Internet Archive (mais completo)**: 195.394 imagens com metadata em parquet. Filtrar pelo genero antes de baixar imagens. 103 GB total.
3. **API direta + `dominikwelke/wikiart-collector`**: Filtrar por genero antes de baixar. Requer API keys.

**Bibliotecas Python**:
- `lucasdavid/wikiart` — Retriever completo via API oficial
- `dominikwelke/wikiart-collector` — Filtragem por genero/estilo antes do download
- `asahi417/wikiart-image-dataset` — Crawler via API, `pip install .`
- `sodascience/artscraper` — `pip install artscraper`, requer chaves em `.wiki_api`

**Datasets pre-processados**:

| Fonte | Imagens | Tamanho | URL |
|-------|---------|---------|-----|
| Hugging Face `huggan/wikiart` | 81.444 | 5.27 GB | huggingface.co/datasets/huggan/wikiart |
| Internet Archive (completo) | 195.394 | 103 GB | archive.org/details/WikiArt_dataset |
| Kaggle (steubk) | ~80.000+ | Variavel | kaggle.com/datasets/steubk/wikiart |

**Estrategia recomendada**: Usar o dataset do Hugging Face, filtrar por `genre == "religious_painting"`, extrair metadata e imagens. Depois aplicar NLP sobre titulos (ex: "The Baptism of Christ" → Mat 3:13-17) para mapear a versiculos.

**Papers academicos que usaram WikiArt**: Karayev et al. 2013 (style recognition, 100K images), Saleh & Elgammal 2015 (genre/style classification), ArtGAN 2017.

---

## Ferramenta-chave: ICONCLASS

[ICONCLASS](https://iconclass.org/) e um sistema de classificacao hierarquico para conteudo de obras de arte:

```
7       Biblia
├── 71  Antigo Testamento
│   ├── 71A  Genesis: criacao, Adao e Eva
│   ├── 71B  Genesis: depois da queda
│   ├── 71C  Genesis: Noe
│   ├── 71D  Genesis: Abraao
│   ├── 71E  Genesis: Isaque, Jaco, Esau
│   ├── 71F  Genesis: Jose
│   ├── 71H  historias de reis e profetas
│   └── ...
├── 73  Novo Testamento
│   ├── 73A  Infancia e juventude de Cristo
│   ├── 73B  Vida publica de Cristo
│   ├── 73C  Paixao de Cristo
│   ├── 73D  Ressurreicao e aparicoes
│   └── ...
└── 71/73 subcodigos drillam ate episodios especificos
```

**Por que e importante**: Museus como Met e Rijksmuseum tagueiam suas colecoes com ICONCLASS. Ao construir uma tabela `ICONCLASS code → passagem biblica OSIS`, podemos mapear automaticamente milhares de imagens de museus a versiculos.

---

## Dataset Academico Existente

### BibleVSA (mais proximo do nosso objetivo)

O BibleVSA e o dataset de ML mais proximo do que estamos construindo. Contem 2.282 iluminuras da Biblia de Borso d'Este (seculo XV) com pares texto-imagem. Pode servir como baseline para avaliacao do nosso pipeline.

### ArtDL

42.479 pinturas com 19 classes de santos (ICONCLASS). Foco em iconografia de santos, nao diretamente em passagens biblicas, mas util para pre-treino de features visuais religiosas.

### ICONCLASS AI Test Set

~87.500 imagens com codigos ICONCLASS hierarquicos. Filtrando codigo "7" (Biblia), fornece imagens ja classificadas por episodio biblico.

---

## Resumo de Estimativas

| Tier | Fontes | Imagens brutas | Apos dedup |
|------|--------|----------------|------------|
| 1 — Pre-mapeadas | 6 fontes | ~16.500 | ~14.000 |
| 2 — Museus + ICONCLASS | 3 fontes | ~5.700 | ~5.000 |
| 3 — Complementares (Wikimedia, Pitts, Cathopic, WikiArt) | 4+ fontes | ~14.000+ | ~10.000 |
| **Total** | **13+** | **~36.000** | **~25.000–30.000** |

---

## Proximos Passos

1. Validar acesso e termos de uso de cada fonte Tier 1
2. Construir tabela ICONCLASS → OSIS (curadoria semi-automatica)
3. Implementar scripts de scraping/fetch para cada fonte
4. Coletar amostra piloto (100 imagens) para validar pipeline
