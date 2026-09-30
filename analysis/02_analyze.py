"""Fase 2 - Análise quantitativa multivariada do corpus bibliométrico (OpenAlex).
Reprodutível: seed fixa, todos os resultados em out/. Rodar: python3 02_analyze.py"""
import json, re, warnings, itertools, collections
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import statsmodels.api as sm
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import normalize
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings("ignore")
RNG = np.random.default_rng(42); SEED = 42
OUT = "out/"; R = {}                      # R = dicionário de resultados -> results.json
CAT = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#7F7F7F"]  # Okabe-Ito, ordem fixa
INK, MUTED, GRID = "#222222", "#666666", "#E6E6E6"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": .6, "axes.axisbelow": True,
                     "figure.dpi": 130, "savefig.bbox": "tight"})

# ------------------------------------------------------------------ 0. Carga e limpeza
def abs_text(inv):
    if not inv: return ""
    pos = {p: w for w, ps in inv.items() for p in ps}
    return " ".join(pos[k] for k in sorted(pos))

rows = [json.loads(l) for l in open("data/raw.jsonl")]
def countries(w):
    cs = []
    for a in w.get("authorships") or []:
        cs += a.get("countries") or [i.get("country_code") for i in a.get("institutions") or [] if i.get("country_code")]
    return sorted(set(c for c in cs if c))
df = pd.DataFrame({
    "id": [w["id"] for w in rows], "title": [w.get("title") or "" for w in rows],
    "year": [w.get("publication_year") for w in rows], "type": [w.get("type") for w in rows],
    "cites": [w.get("cited_by_count") or 0 for w in rows], "fwci": [w.get("fwci") for w in rows],
    "abstract": [abs_text(w.get("abstract_inverted_index")) for w in rows],
    "n_auth": [len(w.get("authorships") or []) for w in rows],
    "countries": [countries(w) for w in rows],
    "first_cty": [(countries({"authorships": (w.get("authorships") or [])[:1]}) or [None])[0] for w in rows],
    "oa": [bool((w.get("open_access") or {}).get("is_oa")) for w in rows],
    "source": [((w.get("primary_location") or {}).get("source") or {}).get("display_name") for w in rows],
    "keywords": [[k["display_name"] for k in (w.get("keywords") or [])] for w in rows],
    "refs": [w.get("referenced_works") or [] for w in rows],
    "queries": [w["_q"] for w in rows], "doi": [w.get("doi") for w in rows]})
df["text"] = (df.title + ". " + df.abstract).str.strip()
df["n_cty"] = df.countries.str.len()
n_raw = len(df)
df = df[(df.year.between(1990, 2026)) & (df.title.str.len() > 5)].copy()
df["has_abs"] = df.abstract.str.len() >= 200
R["corpus"] = {"n_unique": int(n_raw), "n_after_basic": int(len(df)), "share_with_abstract": float(df.has_abs.mean())}

# Flags temáticas (regex sobre título+resumo): operacionalizam os construtos do projeto
FLAGS = {
 "dual_use":     r"dual[- ]use|civil[- ]military|military[- ]civil|spin[- ]?in\b|dual[- ]technolog|military spin",
 "defense":      r"defen[cs]e|military|armed forces|aerospace|weapon|\barmy\b|\bnavy\b|air force|\barms\b",
 "ecosystem":    r"ecosystem",
 "cluster_helix":r"cluster|triple helix|quadruple helix|innovation system|science park|technology park|technopol",
 "orchestration":r"orchestrat|keystone|hub firm|platform leader|ecosystem lead",
 "coher_prox":   r"coheren|proximity",
 "tech_transfer":r"technology transfer|knowledge transfer|commerciali[sz]ation|spin[- ]?off|licens",
 "ip_patent":    r"intellectual property|patent",
 "institutions": r"inclusive institution|extractive institution|institutional (quality|framework|design)",
 "capabilities": r"technological capabilit|technological accumulation|technological learning|absorptive capacity",
 "brazil":       r"brazil",
 "emerging":     r"emerging (economy|economies|countr|market)|developing countr|latin america|global south|middle power",
 "configurational": r"qualitative comparative|fsqca|configurational|set-theoretic",
 "network_sna":  r"social network|network analysis|network structure|centrality",
 "mission_policy": r"mission[- ]oriented|industrial policy|statecraft|export control|national security",
}
low = df.text.str.lower()
for k, p in FLAGS.items(): df["f_" + k] = low.str.contains(p, regex=True)
BIO = r"plant|pathogen|immun|\bgene|protein|\bcells?\b|disease|patient|clinical|species|virus|bacteri|infect|firefight|veterinar|\bdog\b|therapy|tumou?r"
df["f_defense"] = df.f_defense & ~low.str.contains(BIO)
df["core_du_def"] = df.f_dual_use | df.f_defense

# ---- deduplicação por título normalizado + filtro de relevância por regras (declarado no relatório)
df["nt"] = df.title.map(lambda t: re.sub(r"[^a-z0-9]+", " ", t.lower()).strip())
n_before = len(df); df = df.sort_values("cites", ascending=False).drop_duplicates("nt").copy(); n_dedup = len(df)
low = df.text.str.lower()
INNOV_A = r"innovation|entrepreneur|technology transfer|industr|firm|business|commerciali[sz]ation|technolog|policy|econom"
INNOV_B = r"innovation|entrepreneur|business|industr|firm"
df["relevant"] = (((df.f_defense | df.f_dual_use) & low.str.contains(INNOV_A)) |
                  ((df.f_ecosystem | df.f_orchestration | df.f_cluster_helix | df.f_tech_transfer) & low.str.contains(INNOV_B)))
n_rel_pre = int(df.relevant.sum()); df = df[df.relevant].copy()
R["corpus"].update({"n_before_dedup": int(n_before), "n_after_dedup": int(n_dedup), "n_relevant": n_rel_pre,
                    "share_with_abstract_relevant": float(df.has_abs.mean())})
R["flags_prevalence"] = {k: int(df["f_" + k].sum()) for k in FLAGS}
# precisão da busca: dos documentos que dizem "dual-use", quantos têm contexto de defesa?
R["precision_check"] = {"dual_use_total": int(df.f_dual_use.sum()),
                        "dual_use_and_defense_share": float((df.f_dual_use & df.f_defense).sum() / max(1, df.f_dual_use.sum()))}

# ------------------------------------------------------------------ 1. Volume e tendência
yr = df.groupby("year").size().reindex(range(1990, 2026), fill_value=0)
X = sm.add_constant(np.arange(len(yr)) )
tot_per_year = yr.values
m = sm.GLM(tot_per_year, X, family=sm.families.Poisson()).fit(cov_type="HC1")
R["trend_all"] = {"growth_pct_per_year": float((np.exp(m.params[1]) - 1) * 100),
                  "ci95": [float((np.exp(c) - 1) * 100) for c in m.conf_int()[1]], "p": float(m.pvalues[1])}
sub = {"defesa/dual-use": df.core_du_def, "ecossistema": df.f_ecosystem, "orquestração": df.f_orchestration,
       "configuracional (QCA)": df.f_configurational}
fig, ax = plt.subplots(figsize=(7, 3.4))
for (lab, mask), c in zip(sub.items(), CAT):
    s = df[mask].groupby("year").size().reindex(range(2000, 2026), fill_value=0)
    ax.plot(s.index, s.values, color=c, lw=2); ax.text(2025.3, s.values[-1], lab, color=INK, va="center", fontsize=8)
    Xs = sm.add_constant(np.arange(len(s))); ms = sm.GLM(s.values, Xs, family=sm.families.Poisson()).fit(cov_type="HC1")
    R.setdefault("trend_by_theme", {})[lab] = {"growth_pct_per_year": float((np.exp(ms.params[1]) - 1) * 100),
                                                "p": float(ms.pvalues[1]), "n": int(mask.sum())}
ax.set_xlim(2000, 2033); ax.set_ylabel("publicações/ano no corpus"); ax.set_title("Produção anual por eixo temático", loc="left", color=INK)
plt.savefig(OUT + "fig1_tendencia.png"); plt.close()

# ------------------------------------------------------------------ 2. Análise de lacunas (co-ocorrência com FDR)
theory = ["orchestration", "coher_prox", "ecosystem", "cluster_helix", "institutions", "capabilities", "configurational", "network_sna"]
context = ["dual_use", "defense", "brazil", "emerging", "ip_patent", "tech_transfer", "mission_policy"]
res = []
for t, c in itertools.product(theory, context):
    a = int((df["f_" + t] & df["f_" + c]).sum()); b = int((df["f_" + t] & ~df["f_" + c]).sum())
    cc = int((~df["f_" + t] & df["f_" + c]).sum()); d = int((~df["f_" + t] & ~df["f_" + c]).sum())
    orr, p = stats.fisher_exact([[a, b], [cc, d]])
    exp = (a + b) * (a + cc) / len(df)
    res.append(dict(teoria=t, contexto=c, obs=a, esperado=round(exp, 1), odds_ratio=(a + .5) * (d + .5) / ((b + .5) * (cc + .5)), p=p))
gap = pd.DataFrame(res); gap["q_fdr"] = multipletests(gap.p, method="fdr_bh")[1]
gap.to_csv(OUT + "gap_pairs.csv", index=False)
piv = gap.pivot(index="teoria", columns="contexto", values="odds_ratio").loc[theory, context]
obs = gap.pivot(index="teoria", columns="contexto", values="obs").loc[theory, context]
fig, ax = plt.subplots(figsize=(7.2, 3.8))
lo = np.log2(piv.values); im = ax.imshow(lo, cmap="PuOr_r", vmin=-3, vmax=3, aspect="auto"); ax.grid(False)
ax.set_xticks(range(len(context))); ax.set_xticklabels(context, rotation=35, ha="right"); ax.set_yticks(range(len(theory))); ax.set_yticklabels([t + ("*" if t in ("institutions", "capabilities", "configurational") else "") for t in theory])
for i in range(len(theory)):
    for j in range(len(context)): ax.text(j, i, int(obs.values[i, j]), ha="center", va="center", fontsize=8, color=INK)
plt.colorbar(im, label="log2(odds ratio) — roxo: sub-representado · laranja: sobre-representado")
ax.set_title("Mapa de lacunas: teoria × contexto (n = nº de artigos; * = tema ainda não buscado ativamente)", loc="left", color=INK)
plt.savefig(OUT + "fig2_lacunas.png"); plt.close()

# interseções críticas do projeto
def cnt(mask): return int(mask.sum())
inter = {
 "orquestração ∩ defesa/dual-use": df.f_orchestration & df.core_du_def,
 "orquestração ∩ dual-use": df.f_orchestration & df.f_dual_use,
 "coerência/proximidade ∩ dual-use": df.f_coher_prox & df.f_dual_use,
 "coerência/proximidade ∩ defesa ∩ ecossistema": df.f_coher_prox & df.f_defense & df.f_ecosystem,
 "fsQCA ∩ defesa/dual-use": df.f_configurational & df.core_du_def,
 "fsQCA ∩ ecossistema": df.f_configurational & df.f_ecosystem,
 "Brasil ∩ defesa ∩ (cluster|ecossistema)": df.f_brazil & df.f_defense & (df.f_cluster_helix | df.f_ecosystem),
 "Brasil ∩ dual-use": df.f_brazil & df.f_dual_use,
 "PI/patente ∩ defesa ∩ instituições inclusivas": df.f_ip_patent & df.f_defense & df.f_institutions,
 "capacidades tecnológicas ∩ defesa": df.f_capabilities & df.f_defense,
 "redes (ARS) ∩ defesa ∩ cluster": df.f_network_sna & df.f_defense & df.f_cluster_helix,
 "TRIPLA do projeto: orquestração ∩ dual-use/defesa ∩ (cluster|ecossistema)": df.f_orchestration & df.core_du_def & (df.f_cluster_helix | df.f_ecosystem),
}
R["intersections"] = {k: cnt(v) for k, v in inter.items()}
rows_ = []
for nm_, mk_ in inter.items():
    for _, r_ in df[mk_].sort_values("cites", ascending=False).head(60).iterrows():
        rows_.append((nm_, r_.year, r_.title, r_.cites, r_.source))
pd.DataFrame(rows_, columns=["interseccao", "ano", "titulo", "citacoes", "fonte"]).to_csv(OUT + "interseccoes_criticas.csv", index=False)
near = df[inter["TRIPLA do projeto: orquestração ∩ dual-use/defesa ∩ (cluster|ecossistema)"] | inter["coerência/proximidade ∩ defesa ∩ ecossistema"]
          | inter["Brasil ∩ defesa ∩ (cluster|ecossistema)"] | inter["fsQCA ∩ defesa/dual-use"] | inter["orquestração ∩ dual-use"]]
near[["year", "title", "cites", "source", "doi"]].sort_values("cites", ascending=False).to_csv(OUT + "literatura_proxima.csv", index=False)

# ------------------------------------------------------------------ 3. Estrutura temática: TF-IDF -> LSA -> k-means (estabilidade bootstrap)
T = df[df.has_abs].copy().reset_index(drop=True)
stop = list(TfidfVectorizer(stop_words="english").get_stop_words()) + ["study", "paper", "article", "research", "results", "based", "using", "abstract", "review", "purpose", "findings", "approach", "analysis"]
tf = TfidfVectorizer(stop_words=stop, ngram_range=(1, 2), min_df=6, max_df=0.5, sublinear_tf=True, token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b")
Xtf = tf.fit_transform(T.text)
svd = TruncatedSVD(n_components=min(100, Xtf.shape[1] - 1), random_state=SEED); Z = normalize(svd.fit_transform(Xtf))
R["lsa"] = {"n_docs": int(Z.shape[0]), "n_terms": int(Xtf.shape[1]), "var_explained_100": float(svd.explained_variance_ratio_.sum())}
sel = []
for k in range(4, 11):
    km = KMeans(k, n_init=10, random_state=SEED).fit(Z)
    sil = silhouette_score(Z, km.labels_, sample_size=min(3000, len(Z)), random_state=SEED)
    aris = []
    for _ in range(10):
        i1 = RNG.choice(len(Z), int(.8 * len(Z)), replace=False); i2 = RNG.choice(len(Z), int(.8 * len(Z)), replace=False)
        a = KMeans(k, n_init=3, random_state=int(RNG.integers(1e6))).fit(Z[i1]).predict(Z)
        b = KMeans(k, n_init=3, random_state=int(RNG.integers(1e6))).fit(Z[i2]).predict(Z)
        aris.append(adjusted_rand_score(a, b))
    sel.append(dict(k=k, silhouette=sil, stability_ARI=np.mean(aris), ari_sd=np.std(aris)))
sel = pd.DataFrame(sel); sel["score"] = sel.silhouette.rank() + sel.stability_ARI.rank()
K = int(sel.sort_values(["score", "stability_ARI"], ascending=False).iloc[0].k); sel.to_csv(OUT + "k_selection.csv", index=False)
km = KMeans(K, n_init=20, random_state=SEED).fit(Z); T["cl"] = km.labels_
ward = AgglomerativeClustering(K, linkage="ward").fit_predict(Z)
R["clustering"] = {"k": K, "silhouette": float(sel[sel.k == K].silhouette.iloc[0]), "stability_ARI": float(sel[sel.k == K].stability_ARI.iloc[0]),
                   "ARI_kmeans_vs_ward": float(adjusted_rand_score(T.cl, ward))}
terms = np.array(tf.get_feature_names_out())
# termos-descritores: centróide projetado no espaço TF-IDF
desc = {}
for c in range(K):
    idx = (T.cl == c).values; mean_tfidf = np.asarray(Xtf[idx].mean(0)).ravel() - np.asarray(Xtf.mean(0)).ravel()
    desc[c] = list(terms[np.argsort(mean_tfidf)[::-1][:10]])
prof = T.groupby("cl").agg(n=("id", "size"), ano_medio=("year", "mean"), cit_mediana=("cites", "median"),
                           defesa=("f_defense", "mean"), dual_use=("f_dual_use", "mean"), orquestracao=("f_orchestration", "mean"),
                           qca=("f_configurational", "mean"), brasil=("f_brazil", "mean"), ecossistema=("f_ecosystem", "mean")).round(3)
prof["termos"] = [", ".join(desc[c][:8]) for c in prof.index]; prof.to_csv(OUT + "cluster_profile.csv")
R["cluster_terms"] = {int(c): desc[c] for c in desc}
p2 = TruncatedSVD(2, random_state=SEED).fit_transform(Xtf); p2 = (p2 - p2.mean(0)) / p2.std(0)
fig, ax = plt.subplots(figsize=(7, 4.6))
for c in range(K):
    mk = (T.cl == c).values; ax.scatter(p2[mk, 0], p2[mk, 1], s=7, alpha=.5, color=CAT[c % 8], lw=0, label=f"C{c} (n={mk.sum()})")
    ax.text(*np.median(p2[mk], 0), f"C{c}", fontsize=10, weight="bold", color=INK)
ax.legend(frameon=False, fontsize=7, ncol=2, markerscale=2); ax.set_xlabel("eixo semântico 1"); ax.set_ylabel("eixo semântico 2")
ax.set_title("Mapa semântico do corpus (LSA + k-means)", loc="left", color=INK); plt.savefig(OUT + "fig3_clusters.png"); plt.close()

# semelhança com o texto do projeto (vizinhos mais próximos + "isolamento" do tema)
PROJ = ("orquestração de ecossistemas de inovação dual-use civil-militar clusters de defesa governança transferência tecnológica "
        "coerência do orquestrador quádrupla hélice instituições inclusivas extrativistas propriedade intelectual contratos "
        "analysis of social networks fuzzy set qualitative comparative analysis fsQCA design science research firms suppliers defense industrial base "
        "orchestration of dual-use innovation ecosystems civil-military clusters governance technology transfer orchestrator coherence "
        "quadruple helix inclusive extractive institutions intellectual property contracts spin-off spin-in Brazil emerging economy")
sim = (Xtf @ tf.transform([PROJ]).T).toarray().ravel(); T["sim_projeto"] = sim
T.sort_values("sim_projeto", ascending=False).head(40)[["year", "title", "cites", "sim_projeto", "cl", "source", "doi"]].to_csv(OUT + "vizinhos_do_projeto.csv", index=False)
R["similarity"] = {"top1": float(np.sort(sim)[-1]), "p99": float(np.quantile(sim, .99)), "median": float(np.median(sim))}
# cluster mais próximo do projeto
R["cluster_mean_similarity"] = {int(c): float(v) for c, v in T.groupby("cl").sim_projeto.mean().items()}

# PCA/CA: estrutura das flags (o que se associa com o quê) - PCA sobre matriz binária centrada
FL = ["f_" + k for k in FLAGS]; B = df[FL].astype(float).values; Bc = B - B.mean(0)
U, S, Vt = np.linalg.svd(Bc, full_matrices=False); ev = S**2 / (S**2).sum()
R["pca_flags"] = {"var_explained_top4": [float(x) for x in ev[:4]],
                  "loadings_pc1": {FL[i][2:]: float(Vt[0, i]) for i in np.argsort(-abs(Vt[0]))[:6]},
                  "loadings_pc2": {FL[i][2:]: float(Vt[1, i]) for i in np.argsort(-abs(Vt[1]))[:6]}}

# ------------------------------------------------------------------ 4. Termos emergentes (Poisson por termo, FDR)
cv = CountVectorizer(stop_words=stop, ngram_range=(1, 2), min_df=12, max_df=0.4, binary=True, token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b")
Tt = df[df.has_abs & df.year.between(2010, 2025)].reset_index(drop=True); Xc = cv.fit_transform(Tt.text); vocab = np.array(cv.get_feature_names_out())
years = np.arange(2010, 2026); Nd = np.array([(Tt.year == y).sum() for y in years]); em = []
for j in range(Xc.shape[1]):
    col = np.asarray(Xc[:, j].todense()).ravel(); cnts = np.array([col[(Tt.year == y).values].sum() for y in years])
    if cnts.sum() < 20 or Tt.source[col > 0].nunique() < 6: continue
    try:
        r = sm.GLM(cnts, sm.add_constant(years - 2010), family=sm.families.Poisson(), offset=np.log(Nd)).fit(cov_type="HC1")
        em.append((vocab[j], int(cnts.sum()), r.params[1], r.pvalues[1]))
    except Exception: pass
em = pd.DataFrame(em, columns=["termo", "n", "slope", "p"]); em["q"] = multipletests(em.p, method="fdr_bh")[1]; em["cresc_pct_ano"] = (np.exp(em.slope) - 1) * 100
up = em[(em.q < .05) & (em.slope > 0)].sort_values("slope", ascending=False); dn = em[(em.q < .05) & (em.slope < 0)].sort_values("slope")
up.head(60).to_csv(OUT + "termos_emergentes.csv", index=False); dn.head(30).to_csv(OUT + "termos_declinantes.csv", index=False)
R["emerging"] = {"n_terms_tested": int(len(em)), "top_up": up.head(20)[["termo", "cresc_pct_ano", "n"]].round(1).values.tolist(),
                 "top_down": dn.head(10)[["termo", "cresc_pct_ano", "n"]].round(1).values.tolist()}
fig, ax = plt.subplots(figsize=(6.5, 4.2)); u = up.head(15).iloc[::-1]
ax.barh(u.termo, u.cresc_pct_ano, color=CAT[0], height=.6); ax.set_xlabel("crescimento relativo (% ao ano, ajustado ao volume total)")
ax.set_title("Termos emergentes 2010–2025 (Poisson robusto, FDR<5%)", loc="left", color=INK); plt.savefig(OUT + "fig4_emergentes.png"); plt.close()

# ------------------------------------------------------------------ 5. Rede de coocorrência de palavras-chave + rede de países
cvw = CountVectorizer(stop_words=stop, ngram_range=(1, 2), min_df=25, max_df=0.35, binary=True, token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b")
Xw = cvw.fit_transform(df[df.has_abs].text); vw = np.array(cvw.get_feature_names_out())
ti = np.argsort(-np.asarray(Xw.sum(0)).ravel())[:150]; Xs = Xw[:, ti].astype(float); co = (Xs.T @ Xs).toarray(); dfq = np.diag(co).copy()
assoc = co / np.sqrt(np.outer(dfq, dfq)); G = nx.Graph()
for a in range(len(ti)):
    for b in range(a + 1, len(ti)):
        if assoc[a, b] >= 0.12 and vw[ti[a]] not in vw[ti[b]] and vw[ti[b]] not in vw[ti[a]]: G.add_edge(vw[ti[a]], vw[ti[b]], weight=float(assoc[a, b]))
comm = nx.community.louvain_communities(G, weight="weight", seed=SEED); mod = nx.community.modularity(G, comm, weight="weight")
btw = nx.betweenness_centrality(G, weight=None); deg = dict(G.degree(weight="weight"))
kw = pd.DataFrame({"kw": list(G.nodes), "grau_pond": [deg[n] for n in G], "betweenness": [btw[n] for n in G],
                   "comunidade": [next(i for i, c in enumerate(comm) if n in c) for n in G]}).sort_values("betweenness", ascending=False)
kw.to_csv(OUT + "rede_palavras.csv", index=False)
R["coword"] = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(), "density": float(nx.density(G)), "modularity": float(mod),
               "n_communities": len(comm), "bridges_top8": kw.head(8).kw.tolist(),
               "communities": [sorted(c, key=lambda n: -deg[n])[:8] for c in comm]}
fig, ax = plt.subplots(figsize=(7.2, 5.2)); pos = nx.spring_layout(G, seed=SEED, k=.9, weight="weight"); cid = dict(zip(kw.kw, kw.comunidade))
nx.draw_networkx_edges(G, pos, ax=ax, alpha=.15, width=.6, edge_color=MUTED)
nx.draw_networkx_nodes(G, pos, ax=ax, node_size=[30 + 25 * deg[n] for n in G], node_color=[CAT[cid[n] % 8] for n in G], linewidths=.6, edgecolors="white")
nx.draw_networkx_labels(G, pos, ax=ax, labels={n: n for n in kw.sort_values("grau_pond", ascending=False).head(22).kw}, font_size=7, font_color=INK); ax.axis("off")
ax.set_title(f"Rede de termos do texto (modularidade Q={mod:.2f}; cores = comunidades Louvain)", loc="left", color=INK); plt.savefig(OUT + "fig5_rede.png"); plt.close()

cw = collections.Counter(); ct = collections.Counter()
for cs in df.countries:
    ct.update(cs)
    for a, b in itertools.combinations(sorted(cs), 2): cw[(a, b)] += 1
Gc = nx.Graph(); Gc.add_weighted_edges_from([(a, b, w) for (a, b), w in cw.items() if w >= 2])
cen = nx.betweenness_centrality(Gc); dc = dict(Gc.degree(weight="weight"))
ctab = pd.DataFrame({"pais": list(ct), "n_pubs": [ct[c] for c in ct]}); ctab["grau_pond"] = ctab.pais.map(dc).fillna(0); ctab["betw"] = ctab.pais.map(cen).fillna(0)
ctab = ctab.sort_values("n_pubs", ascending=False); ctab.head(40).to_csv(OUT + "paises.csv", index=False)
R["countries"] = {"top10": ctab.head(10)[["pais", "n_pubs"]].values.tolist(),
                  "brasil": ctab[ctab.pais == "BR"][["n_pubs", "grau_pond", "betw"]].values.tolist(),
                  "share_multi_country": float((df.n_cty > 1).mean())}
src = df.source.value_counts().head(15); src.to_csv(OUT + "fontes_top.csv"); R["sources_top5"] = src.head(5).to_dict()

# ------------------------------------------------------------------ 6. Determinantes do impacto (Poisson robusto + NB + quantílica + VIF)
REG = {"US": "N.América", "CA": "N.América", "GB": "Europa", "DE": "Europa", "FR": "Europa", "IT": "Europa", "NL": "Europa", "SE": "Europa", "ES": "Europa",
       "CN": "Ásia", "JP": "Ásia", "KR": "Ásia", "IN": "Ásia", "TW": "Ásia", "SG": "Ásia", "BR": "AmLatina", "MX": "AmLatina", "AR": "AmLatina", "CL": "AmLatina"}
M = T[T.year <= 2024].copy()
M["age"] = 2026 - M.year + 1
M["region"] = M.first_cty.map(REG).fillna("Outros")
M["log_auth"] = np.log1p(M.n_auth); M["intl"] = (M.n_cty > 1).astype(int); M["review"] = (M.type == "review").astype(int)
M["repo"] = M.source.fillna("").str.contains("Zenodo|DOAJ|repository|arXiv|SSRN", case=False).astype(int); M["oa_i"] = M.oa.astype(int); M["abs_len_z"] = (np.log(M.abstract.str.len()) - np.log(M.abstract.str.len()).mean()) / np.log(M.abstract.str.len()).std()
M["log_auth_z"] = (M.log_auth - M.log_auth.mean()) / M.log_auth.std()
D = pd.get_dummies(M.cl, prefix="C", drop_first=False).astype(int); ref = f"C_{M.cl.value_counts().idxmax()}"; D = D.drop(columns=ref)
Rg = pd.get_dummies(M.region, prefix="R").astype(int).drop(columns="R_Europa", errors="ignore")
Xm = pd.concat([M[["log_auth_z", "intl", "review", "oa_i", "repo", "abs_len_z"]], M[["f_dual_use", "f_orchestration", "f_brazil", "f_configurational"]].astype(int), D, Rg], axis=1).astype(float)
Xm = sm.add_constant(Xm); ym = M.cites.values.astype(float)
vif = pd.Series([variance_inflation_factor(Xm.values, i) for i in range(1, Xm.shape[1])], index=Xm.columns[1:]).round(2); vif.to_csv(OUT + "vif.csv")
pois = sm.GLM(ym, Xm, family=sm.families.Poisson(), offset=np.log(M.age.values)).fit(cov_type="HC1")
disp = float(pois.pearson_chi2 / pois.df_resid)
def irr_table(r, name):
    t = pd.DataFrame({"IRR": np.exp(r.params), "lo": np.exp(r.conf_int()[0]), "hi": np.exp(r.conf_int()[1]), "p": r.pvalues}); t["modelo"] = name; return t
t1 = irr_table(pois, "Poisson robusto (HC1)")
try:
    nb = sm.NegativeBinomial(ym, Xm, exposure=M.age.values).fit(disp=0, maxiter=200, cov_type="HC1"); t2 = irr_table(nb.params.iloc[:-1].to_frame() if False else nb, "NB2")
    t2 = t2.drop(index="alpha", errors="ignore"); nb_alpha = float(nb.params["alpha"])
except Exception as e:
    t2, nb_alpha = pd.DataFrame(), None
cut = np.quantile(ym / M.age.values, .99); keep = (ym / M.age.values) <= cut
p_trim = sm.GLM(ym[keep], Xm[keep], family=sm.families.Poisson(), offset=np.log(M.age.values[keep])).fit(cov_type="HC1"); t3 = irr_table(p_trim, "Poisson s/ top-1% outliers")
qr = sm.QuantReg(np.log1p(ym / M.age.values), Xm).fit(q=.5); t4 = pd.DataFrame({"IRR": np.exp(qr.params), "lo": np.exp(qr.conf_int()[0]), "hi": np.exp(qr.conf_int()[1]), "p": qr.pvalues}); t4["modelo"] = "Mediana (log1p cit/ano)"
allt = pd.concat([t1, t2, t3, t4]).reset_index().rename(columns={"index": "var"}); allt.to_csv(OUT + "impacto_modelos.csv", index=False)
sgn = allt[allt["var"] != "const"].assign(sig=lambda d: d.p < .05).groupby("var").apply(lambda g: pd.Series({"consistente_4_modelos": bool(g.sig.all()), "n_sig": int(g.sig.sum())}))
R["impact"] = {"n": int(len(M)), "overdispersion_pearson": disp, "nb_alpha": nb_alpha, "max_vif": float(vif.max()),
               "poisson_irr": t1.drop(index="const")[["IRR", "lo", "hi", "p"]].round(3).to_dict("index"),
               "robust_across_models": sgn[sgn.consistente_4_modelos].index.tolist(), "pseudo_R2_poisson": float(1 - pois.deviance / pois.null_deviance)}
fp = t1.drop(index="const").sort_values("IRR"); fig, ax = plt.subplots(figsize=(6.5, 5))
ax.errorbar(fp.IRR, range(len(fp)), xerr=[fp.IRR - fp.lo, fp.hi - fp.IRR], fmt="o", color=CAT[0], ecolor=MUTED, capsize=2, ms=4)
ax.axvline(1, color=INK, lw=.8); ax.set_yticks(range(len(fp))); ax.set_yticklabels(fp.index); ax.set_xscale("log")
ax.set_xlabel("razão de taxa de citação (IRR, escala log; IC95%, erro-padrão robusto)"); ax.set_title("Determinantes de citação (controle de idade da publicação)", loc="left", color=INK)
plt.savefig(OUT + "fig6_impacto.png"); plt.close()

json.dump(R, open(OUT + "results.json", "w"), indent=1, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps(R, indent=1, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o))[:9000])
