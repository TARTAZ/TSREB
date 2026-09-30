# Relatório — Revisão bibliométrica multivariada
**Projeto:** Orquestração de Ecossistemas de Inovação Dual-Use no Estado de São Paulo (Pós-Doc Profissional FGV EAESP)
**Fase do cronograma:** I — Revisão bibliométrica · **Base:** OpenAlex · **Data:** 30/09/2026 · **Buscas: 10 de 10 concluídas**

---

## 0. Leia primeiro: o que este relatório é e não é

| Item | Situação |
|---|---|
| Dados primários (survey de firmas, ARS, fsQCA) | **Não existem ainda.** Nada aqui testa P1, P2 ou P3 do projeto. |
| Base consultada | OpenAlex (aberta). **Não** Scopus/WoS (exigem login institucional). |
| Idioma das buscas | **Somente inglês.** A literatura em português (RAP, RAE, dissertações de EGN/ECEME) está subamostrada. |
| Recall | Cada busca traz no máximo as 1.200 obras mais relevantes; o corpus **não é a população**. |
| Artefatos de busca | Q9 exigia militar/defesa + PI, e Q10 exigia capacidades + defesa/aeroespacial. A co-ocorrência desses pares **é construída pela busca** e não é achado (ver seção 1.C). |

**Funil do corpus:** 7.288 obras recuperadas → 6.844 após deduplicar por título → **4.188 após filtro de relevância** (regras textuais; "defesa" com sentido biológico ou clínico excluído).

**Retificação em relação à versão preliminar (7 buscas):** o efeito positivo do tema "orquestração" nas citações (IRR 1,68) **não se sustentou** com o corpus completo (IRR 1,26; IC 95% 0,83–1,91) e foi retirado das conclusões.

---

## 1. Achados

### A. Lacunas que sustentam o projeto

Teste exato de Fisher com correção FDR (Benjamini-Hochberg), observado versus esperado sob independência:

| Interseção | Observado | Esperado | Odds ratio | q (FDR) |
|---|---:|---:|---:|---:|
| Orquestração × defesa | **9** | 253 | 0,015 | < 0,001 |
| Orquestração × dual-use | **3** | 32 | 0,090 | < 0,001 |
| Coerência/proximidade × dual-use | **2** | 14 | 0,159 | < 0,001 |
| Coerência/proximidade × defesa | 36 | 112 | 0,188 | < 0,001 |
| **fsQCA × defesa** | **4** | 181 | 0,011 | < 0,001 |
| fsQCA × dual-use | 3 | 23 | 0,133 | < 0,001 |

**A1. Interseção tripla do projeto** (orquestração ∩ dual-use/defesa ∩ cluster/ecossistema): **6 obras**. Leitura manual dos títulos: 2 claramente pertinentes (*Using patents to orchestrate ecosystem stability: a French aerospace company*, 2017; *Collaborative innovation ecosystems for defense space technology development*, 2026); 4 plausíveis ou ambíguas. A lacuna teórica declarada no projeto tem respaldo quantitativo.

**A2. fsQCA em defesa é quase inexistente.** Das 6 obras que casaram com fsQCA ∩ defesa/dual-use, apenas **1 é pertinente**: *Clusters and firm-level innovation: a configurational analysis of agglomeration, network and institutional advantages in European aerospace* (2020, **104 citações**). Esse é o precedente metodológico mais direto do seu desenho e deve ser lido e citado. As outras 5 são falsos positivos ou ambíguas (IA em regiões, e-governança, administração pública aeroespacial na Ucrânia).

**A3. Lente de instituições inclusivas/extrativistas aplicada à PI militar:** dentro do conjunto que a Q9 foi desenhada para achar (defesa × PI), **3 obras** usam a interseção PI ∩ defesa ∩ instituições, e **nenhuma aplica claramente a lente de Acemoglu**. *Military-Civil Collaboration in the USA in the Sphere of Advanced Technologies* (2025) é adjacente. Isso é informativo justamente porque a busca forçou defesa e PI.

**Limite comum:** o recall depende de termos em inglês e de cluster/ecossistema/hélice/inovação nas buscas Q1–Q2 e Q8. Trabalhos que discutam esses temas sem tais termos podem ter escapado.

### B. Estrutura e dinâmica da literatura

**B1. Silos temáticos.** Nove temas por LSA + k-means (silhueta 0,056; estabilidade por bootstrap ARI = 0,74; concordância com Ward ARI = 0,36). Separação **fraca**: tratar como temas difusos, não como categorias nítidas.

| Tema | n | Ano médio | % defesa | Observação |
|---|---:|---:|---:|---|
| C2 Ecossistemas/orquestração (negócios, digital) | 515 | 2022 | 4% | 86% orquestração; mediana 2 citações |
| C6 fsQCA/QCA em inovação | 306 | 2024 | 1% | 98% menciona QCA; **fora da defesa** |
| C1 / C4 Base industrial de defesa | 464 / 263 | 2017 | 95% | quase zero em orquestração |
| C5 Militar, segurança, China/EUA | 451 | 2018 | 89% | |
| C8 Complexo militar-industrial (Ucrânia) | 256 | 2023 | 70% | |
| C0 Propriedade intelectual | 239 | 2017 | 63% | |
| C3 Spin-offs universitários | 587 | 2015 | 2% | |
| C7 Clusters, aeroespacial, Brasil | 851 | 2017 | 50% | 25% mencionam Brasil |

**B2. Crescimento anual dentro do corpus** (Poisson com erro-padrão robusto HC1): ecossistema **+34%/ano**, orquestração +20%/ano, QCA +49%/ano, defesa/dual-use +12%/ano (todos p < 0,001). **Limite:** não normalizado pelo crescimento geral do OpenAlex, e Q3/Q5 foram truncadas em 1.200 obras. Vale como comparação **relativa** entre temas. O crescimento de QCA é parcialmente efeito da Q8 e deve ser lido com cautela.

**B3. Termos emergentes 2010–2025** (Poisson por termo, FDR 5%, mínimo 6 fontes distintas), crescimento % ao ano: *defense capabilities* (+65), *digital transformation* (+54), **necessary condition** (+52, ligado à NCA do seu plano), *resilience* (+48), *artificial intelligence* (+45), *geopolitical* (+44), *strategic autonomy* (+40), *cybersecurity* (+38). **Declinando:** *spin-off firms*, *tacit*, *spin offs*. **Descartar** como conteúdo: *actionable, foundational, adaptability, multidimensional* (provável estilo de resumos assistidos por IA).

### C. O que NÃO é achado (artefato de busca)
- "Capacidades tecnológicas × defesa" aparece 9× sobre-representada (328 observadas). Isso decorre da Q10, que exigia os dois termos. **O que se pode dizer:** existe um corpo estabelecido de literatura sobre capacidades tecnológicas em defesa/aeroespacial (base para o encaixe da MAVITECDI), e não uma lacuna.
- Idem para instituições × PI × defesa na Q9.

### D. Determinantes de citação (n = 2.794 obras até 2024)
Poisson robusto (HC1), exposição = idade da publicação; pseudo-R² = 0,29; VIF máx. ≈ 4. Comparado ainda com binomial negativa, exclusão do 1% mais citado e regressão à mediana.

| Fator | IRR (IC 95%) | Robusto nas 4 especificações? |
|---|---|:-:|
| Coautoria internacional | 1,47 (1,06–2,03) | **Sim** |
| Tema ecossistemas/orquestração (C2, vs. clusters/aeroespacial) | 1,77 (1,07–2,93) | **Sim** |
| Menção a Brasil | 0,44 (0,23–0,85) | **Sim** |
| 1º autor América Latina | 0,59 (0,38–0,91) | **Sim** |
| 1º autor Ásia | 0,67 (0,48–0,95) | **Sim** |
| Temas de base industrial de defesa e militar (C1, C4, C5, C8) | 0,17–0,24 | **Sim** |
| Tema orquestração (marcador textual) | 1,26 (0,83–1,91) | Não significativo |
| Menção a dual-use | 0,31 (0,16–0,59) | **Não** (frágil) |
| 1º autor América do Norte | 2,73 (1,43–5,24) | **Não** |

**Limite:** associação, não causalidade; sem normalização por área (FWCI não usado); citações de obras pós-2022 são quase nulas por exposição curta.

### E. Posição do Brasil
Brasil é o **4º país em volume** (208 obras), atrás de China (411), EUA (360) e Reino Unido (247). Tem baixa conexão internacional: grau ponderado 58, contra 213 (EUA) e 208 (Reino Unido); centralidade de intermediação 0,044.

---

## 2. Literatura mais próxima do seu projeto (leitura recomendada)
Selecionada por similaridade de texto (TF-IDF, cosseno) **e** conferida pelo título. Similaridade máxima = 0,189 (p99 = 0,106; mediana = 0,027): nenhuma obra espelha o projeto, mas a medida é grosseira (saco de palavras).

**Defesa e dual-use**
1. *Using patents to orchestrate ecosystem stability: a French aerospace company* (2017), IJTM
2. *Collaborative innovation ecosystems for defense space technology development* (2026)
3. *Application of Design Science Research in Brazilian Air Force Technology Transfer Processes* (2026)
4. *A typology of contemporary models for dual-use technology transfer* (2023)
5. *National Defence and Security Sector Policies Development: IP and Innovation Management at the Brazilian Armed Forces* (2015)
6. *The Open Innovation Journey in Emerging Economies: the Brazilian Aerospace Industry* (2014)

**Método (fsQCA + clusters)**
7. *Clusters and firm-level innovation: a configurational analysis… European aerospace* (2020, 104 citações), **precedente mais direto**
8. *How Do Clusters Drive Firm Performance in the Regional Innovation System? A Causal Complexity Analysis in Chinese Strategic Emerging Industries* (2023)
9. *Innovation ecosystems and national talent competitiveness: a country-based comparison using fsQCA* (2023, 81 citações)

**Teoria (já no seu referencial):** *Unpacking the Nature of Orchestrator Coherence in Entrepreneurial Ecosystems* (2025).

Lista completa: `out/vizinhos_do_projeto.csv` e `out/interseccoes_criticas.csv`.

---

## 3. O que fazer com isto (decisões)

| # | Ação | Por quê |
|---|---|---|
| 1 | Posicionar a contribuição como **transferência da teoria de orquestração/coerência para o contexto militar**, e não como "mais um estudo de defesa" | A1 e B1 |
| 2 | Apresentar a **fsQCA em ecossistemas de defesa** como contribuição metodológica, ancorada no precedente aeroespacial europeu (item 7) | A2: interseção praticamente vazia |
| 3 | Mirar periódicos do eixo ecossistemas/inovação além dos de defesa | D: tema C2 com IRR 1,77, robusto |
| 4 | Incluir **coautor internacional** no artigo principal | D (IRR 1,47, robusto) e E |
| 5 | Ler e citar os 10 trabalhos da seção 2 antes da banca; o item 3 (DSR na FAB) é o vizinho mais direto | Evita o risco de "já existe" |
| 6 | Enquadrar em **spin-in, autonomia estratégica, resiliência** e usar NCA junto com fsQCA | B3 |
| 7 | Sustentar a lente de instituições inclusivas com argumento próprio: não há aplicação direta na literatura de PI militar | A3 |
| 8 | Repetir a busca em **português** e em Scopus/WoS via biblioteca FGV | Reduz viés de idioma e de base |

---

## 4. Limitações e rigor
- **Flags por regex** sobre título+resumo (não leitura integral). A precisão foi conferida manualmente apenas nas interseções críticas (tripla, fsQCA ∩ defesa e PI ∩ defesa ∩ instituições).
- **Clusters de baixa separação** (silhueta 0,056).
- **Rede de coocorrência de termos descartada** por não discriminar (densidade 0,85; modularidade 0,07). Não é achado.
- **Viés de recuperação:** o corpus não é a população; pares construídos pela busca não são interpretáveis (seção 1.C).
- **Sem correção por área** no modelo de citações.
- Todos os testes usam semente fixa (42) e os scripts reproduzem os números.

## 5. Reprodução
```
cd analysis
export OPENALEX_API_KEY=...    # opcional (chave gratuita); nunca gravar em arquivo
python3 01_harvest.py          # retoma dos checkpoints; PARTIAL=1 usa só o que já foi coletado
python3 02_analyze.py          # gera out/ (figuras, tabelas, results.json)
```
Dados brutos (`data/raw.jsonl`, ~80 MB) e checkpoints não são versionados; são regenerados pela busca.
