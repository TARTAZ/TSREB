# Relatório preliminar — Revisão bibliométrica multivariada
**Projeto:** Orquestração de Ecossistemas de Inovação Dual-Use no Estado de São Paulo (Pós-Doc Profissional FGV EAESP)
**Fase do cronograma:** I — Revisão bibliométrica · **Base:** OpenAlex · **Data:** 30/09/2026 · **Status: PRELIMINAR (7 de 10 buscas)**

---

## 0. Leia primeiro: o que este relatório é e não é

| Item | Situação |
|---|---|
| Dados primários (survey de firmas, ARS, fsQCA) | **Não existem ainda.** Nada aqui testa P1, P2 ou P3 do projeto. |
| Base consultada | OpenAlex (aberta). **Não** Scopus/WoS (exigem login institucional). |
| Buscas executadas | **Q1–Q7** (dual-use, defesa, transferência/PI, orquestração, coerência/proximidade, Brasil, base industrial de defesa). |
| Buscas pendentes | **Q8 (fsQCA), Q9 (instituições inclusivas/PI), Q10 (capacidades tecnológicas).** O orçamento diário gratuito da API esgotou (renova 00:00 UTC). Q8 e Q10 também tinham um erro de sintaxe (curinga entre aspas), já corrigido. |
| Consequência | Conclusões sobre **fsQCA, instituições inclusivas e capacidades tecnológicas não são válidas nesta rodada** (esses temas só aparecem por recall incidental). O mapa de lacunas os marca com `*`. |
| Idioma das buscas | **Somente inglês.** A literatura em português (RAP, RAE, dissertações de EGN/ECEME) está subamostrada. |

**Funil do corpus:** 5.658 obras recuperadas → 5.330 após deduplicar por título → **3.250 após filtro de relevância** (regras textuais; "defesa" com sentido biológico/clínico excluído) → 3.031 com resumo utilizável para modelagem de texto.

---

## 1. Achados (do mais para o menos sólido)

### A1. A interseção central do projeto está praticamente vazia — ACHADO PRINCIPAL
Teste exato de Fisher com correção FDR (Benjamini-Hochberg), observado vs. esperado sob independência:

| Interseção | Observado | Esperado | Odds ratio | q (FDR) |
|---|---:|---:|---:|---:|
| Orquestração × defesa | **5** | 238 | 0,009 | < 0,001 |
| Orquestração × dual-use | **3** | 35 | 0,079 | < 0,001 |
| Coerência/proximidade × dual-use | **2** | 14,6 | 0,151 | < 0,001 |
| Coerência/proximidade × defesa | 29 | 99 | 0,169 | < 0,001 |
| Ecossistema × dual-use | 21 | 60 | 0,270 | < 0,001 |
| Orquestração × Brasil | 20 | 58 | 0,287 | < 0,001 |

A interseção tripla do projeto (orquestração ∩ dual-use/defesa ∩ cluster/ecossistema) tem **5 obras**. Leitura manual dos 5 títulos: 2 claramente pertinentes (*Using patents to orchestrate ecosystem stability: a French aerospace company*, 2017; *Collaborative innovation ecosystems for defense space technology*, 2026), 3 plausíveis mas ambíguas. **Precisão estimada da interseção: 2 a 5 de 5.** Contagens brutas só podem *superestimar* a interseção verdadeira (falsos positivos entram, não saem), o que torna a conclusão de "lacuna" conservadora quanto a esse ponto.

**Implicação:** a lacuna que o projeto declara (transferir a teoria de coerência do orquestrador para uma Força Armada como orquestradora) tem respaldo quantitativo.
**Limite:** recall restrito às minhas buscas. Trabalhos sobre orquestração em defesa que não usem termos de cluster/ecossistema/hélice/inovação podem ter escapado.

### A2. A literatura está em silos, e o lado teórico cresce mais rápido que o lado defesa
Sete temas por LSA + k-means (k=7; silhueta 0,054; estabilidade por bootstrap ARI = 0,78; concordância com Ward ARI = 0,48). Separação **fraca**: tratar como temas difusos.

| Tema | n | Ano médio | % defesa | % orquestração |
|---|---:|---:|---:|---:|
| C5 Ecossistemas/orquestração (negócios, digital) | 509 | 2022 | 4% | **89%** |
| C2/C3 Base industrial de defesa (EUA/Ásia; Europa) | 752 | 2017 | **94%** | 0–0,4% |
| C4 Complexo militar-industrial (Ucrânia/Rússia) | 230 | 2023 | 70% | 1% |
| C0 Brasil, aeroespacial, geopolítica | 715 | 2017 | 65% | 3% |
| C1 Spin-offs universitários / transferência | 607 | 2015 | 2% | 1% |
| C6 Clusters industriais / proximidade | 218 | 2015 | 22% | 1% |

Crescimento anual dentro do corpus (Poisson com erro-padrão robusto HC1): **ecossistema +30%/ano**, **orquestração +19,8%/ano**, defesa/dual-use +12,3%/ano (todos p < 0,001).
**Limite:** não normalizado pelo crescimento geral do OpenAlex, e as buscas Q3/Q5 foram truncadas em 1.200 obras. Vale como comparação **relativa entre temas**, não como taxa absoluta.

### A3. Termos emergentes 2010–2025 (Poisson por termo, FDR 5%, mínimo 6 fontes distintas)
- **Crescendo:** *defense capabilities* (+76%/ano), *digital transformation* (+64%), *resilience* (+54%), *geopolitical* (+44%), *strategic autonomy* (+41%), *artificial intelligence* (+41%), *full-scale* (guerra da Ucrânia, +41%).
- **Declinando:** *tacit/explicit knowledge*, *spin-off firms*, *technology-based*, *inventors*: a agenda acadêmica clássica de spin-off perde espaço.
- **Descartar:** *actionable, foundational, adaptability, technological advancements* são provável artefato de estilo de resumos assistidos por IA, não conteúdo.

**Implicação:** o enquadramento de *statecraft* tecnoeconômico e autonomia estratégica do projeto está alinhado à fronteira; o de "spin-off acadêmico" está saindo dela.

### A4. Determinantes de citação (n = 2.253 obras até 2024)
Poisson robusto (HC1) com exposição = idade da publicação; pseudo-R² = 0,30; VIF máximo = 4,3; superdispersão forte (Pearson ≈ 180). Checado ainda por binomial negativa, exclusão do 1% mais citado e regressão à mediana.

| Fator | IRR (IC 95%) | Robusto nas 4 especificações? |
|---|---|:-:|
| Coautoria internacional | 1,55 (1,13–2,13) | **Sim** |
| Tema orquestração | 1,68 (1,11–2,54) | **Sim** |
| Menção a Brasil | 0,47 (0,26–0,84) | **Sim** |
| 1º autor Ásia | 0,58 (0,37–0,89) | **Sim** |
| Temas de base industrial de defesa (C2, C3, C4) | 0,14–0,21 | **Sim** |
| Menção a dual-use | 0,26 (0,15–0,45) | **Não** (frágil) |
| 1º autor América do Norte | 2,97 (1,54–5,74) | **Não** |

**Implicação prática:** publicações em orquestração e com coautoria internacional colecionam mais citações; a literatura de base industrial de defesa e a com foco Brasil colecionam menos.
**Limite:** associação, não causalidade; sem normalização por área (FWCI não usado); citações de obras pós-2022 são quase nulas por exposição curta.

### A5. Posição do Brasil
Brasil é o **3º país em volume** (193 obras), mas tem centralidade de intermediação baixa na rede de coautoria (0,056) e grau ponderado de 46, contra 158 (EUA) e 175 (Reino Unido).

---

## 2. Literatura mais próxima do seu projeto (leitura recomendada)
Selecionada por similaridade de texto (TF-IDF, cosseno) **e** conferida pelo título. Similaridade máxima = 0,168 (p99 do corpus = 0,106; mediana = 0,029): nenhuma obra espelha o projeto, mas a medida é grosseira (saco de palavras).

1. *Using patents to orchestrate ecosystem stability: a French aerospace company* (2017), IJTM
2. *Collaborative innovation ecosystems for defense space technology development* (2026)
3. *Application of Design Science Research in Brazilian Air Force Technology Transfer Processes* (2026)
4. *A typology of contemporary models for dual-use technology transfer* (2023)
5. *National Defence and Security Sector Policies Development: IP and Innovation Management at the Brazilian Armed Forces* (2015)
6. *Absorptive capacity and institutional environment as determinants of defence industry transformation* (2025)
7. *The Open Innovation Journey in Emerging Economies: the Brazilian Aerospace Industry* (2014)
8. *Unpacking the Nature of Orchestrator Coherence in Entrepreneurial Ecosystems* (2025) — já no seu referencial
9. *Assessing Systemic Strengths and Vulnerabilities of China's Defense Industrial Base* (2022)

Lista completa: `out/vizinhos_do_projeto.csv` e `out/interseccoes_criticas.csv`.

---

## 3. O que fazer com isto (decisões)

| # | Ação | Por quê |
|---|---|---|
| 1 | Posicionar a contribuição como **transferência da teoria de orquestração/coerência (corrente que cresce 20–30%/ano) para o contexto militar**, e não como "mais um estudo de defesa" | A1 e A2 |
| 2 | Mirar periódicos do eixo ecossistemas/inovação (*Research Policy*, *Journal of Technology Transfer*) além de revistas de defesa | A2 e A4 |
| 3 | Incluir **coautor internacional** no artigo principal | A4 (IRR 1,55, robusto) e A5 |
| 4 | Ler e citar os 8 trabalhos da seção 2 antes da banca; o item 3 (DSR na FAB) é o vizinho mais direto | Evita o risco de "já existe" |
| 5 | Migrar o enquadramento de "spin-off" para **spin-in / autonomia estratégica / resiliência** | A3 |
| 6 | **Completar Q8–Q10** (chave gratuita do OpenAlex ou após 00:00 UTC) e refazer o mapa de lacunas | Sem isso, nada se afirma sobre fsQCA, instituições inclusivas ou capacidades |
| 7 | Repetir a busca em **português** e em Scopus/WoS via biblioteca FGV | Reduz o viés de idioma e de base |

---

## 4. Limitações e rigor
- **Flags por regex** sobre título+resumo (não leitura integral); precisão conferida manualmente apenas na interseção tripla (n = 5).
- **Clusters de baixa separação** (silhueta 0,054); C6 traz ruído residual de "coherence" em outras áreas.
- **Rede de coocorrência de termos descartada** por não discriminar (densidade 0,85; modularidade 0,07). Não é achado.
- **Viés de recuperação:** cada busca limitada às 1.200 obras mais relevantes; o corpus não é a população.
- **Sem correção por área** no modelo de citações; efeito de idioma e de base não modelados.
- Todos os testes usam semente fixa (42), e os scripts reproduzem os números.

## 5. Reprodução
```
cd analysis
python3 01_harvest.py          # retoma dos checkpoints; PARTIAL=1 usa só o que já foi coletado
python3 02_analyze.py          # gera out/ (figuras, tabelas, results.json)
```
Dados brutos (`data/raw.jsonl`, 65 MB) e checkpoints não são versionados; são regenerados pela busca.
