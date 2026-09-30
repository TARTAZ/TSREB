"""Fase 1 - Busca avançada no OpenAlex (blocos derivados do projeto de pós-doc).
Cada consulta = interseção de blocos conceituais, título+resumo, 1990-2026.
Saída: data/raw.jsonl (uma obra por linha, com flags das consultas que a recuperaram)."""
import json, time, sys, urllib.parse, urllib.request, urllib.error, collections

BASE = "https://api.openalex.org/works"
FIELDS = ("id,doi,title,publication_year,type,cited_by_count,fwci,language,abstract_inverted_index,"
          "authorships,primary_location,open_access,keywords,primary_topic,topics,referenced_works,"
          "referenced_works_count,countries_distinct_count,institutions_distinct_count")

DU  = '("dual-use" OR "dual use" OR "civil-military" OR "military-civil" OR "spin-off" OR "spin-in" OR "spinoff")'
DEF = '(defense OR defence OR military OR aerospace OR "armed forces")'
ECO = '("innovation ecosystem" OR "innovation cluster" OR "innovation system" OR "triple helix" OR "quadruple helix" OR "industrial cluster")'
ORC = '(orchestrator OR orchestration OR "ecosystem orchestration" OR "hub firm" OR "keystone")'
COH = '(coherence OR "proximity dimensions" OR "cognitive proximity" OR "institutional proximity")'

QUERIES = {
 "Q1_dualuse_ecosystem": f'{DU} AND {ECO}',
 "Q2_defense_ecosystem": f'{DEF} AND {ECO}',
 "Q3_dualuse_techtransfer": f'{DU} AND ("technology transfer" OR "technology transfers" OR commercialization OR "intellectual property")',
 "Q4_orchestration_ecosystem": f'{ORC} AND ("innovation ecosystem" OR "business ecosystem" OR "entrepreneurial ecosystem" OR "innovation network")',
 "Q5_coherence_proximity": f'{COH} AND (ecosystem OR cluster OR "innovation network")',
 "Q6_brazil_defense_innov": f'(Brazil OR Brazilian) AND {DEF} AND (innovation OR "technology transfer" OR cluster OR "industrial base")',
 "Q7_defense_industrial_base": '("defense industrial base" OR "defence industrial base" OR "defense industry" OR "defence industry") AND (innovation OR "technology transfer" OR "small and medium" OR SME OR supplier)',
 "Q8_fsqca_ecosystem": '("fuzzy-set qualitative comparative" OR fsQCA OR "qualitative comparative analysis") AND (ecosystem OR cluster OR "innovation network" OR "technological capabilit*")',
 "Q9_inclusive_institutions_IP": '("inclusive institutions" OR "extractive institutions" OR "intellectual property") AND (military OR defense OR defence) AND (innovation OR "technology transfer")',
 "Q10_techcapab_defense": '("technological capabilit*" OR "technological accumulation" OR "technological learning") AND (defense OR defence OR aerospace OR military)',
}
MAXPER = 1200

def get(url, tries=40):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                time.sleep(1.0)  # cortesia entre requisições
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read()
            wait = 30
            if e.code == 429:
                try: wait = min(90.0, float(json.loads(body).get("retryAfter", 30)) + 3)
                except Exception: pass
            else:
                print("HTTP", e.code, body[:200], flush=True)
                wait = min(60, 5 * 2**i)
            print(f"  aguardando {wait:.0f}s (tentativa {i+1})", flush=True); time.sleep(wait)
        except Exception as e:
            time.sleep(min(60, 3 * 2**i))
    raise RuntimeError(url)

def harvest(name, q):
    out, page = [], 1
    while len(out) < MAXPER:
        params = {"filter": f"title_and_abstract.search:{q},publication_year:1990-2026,type:article|review|book-chapter|book",
                  "per-page": 200, "page": page, "select": FIELDS, "sort": "relevance_score:desc"}
        url = BASE + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        d = get(url)
        if name not in meta: meta[name] = d["meta"]["count"]
        out += d["results"]; page += 1
        if not d["results"]: break
    return out[:MAXPER]

import os
CK = "data/checkpoints"; os.makedirs(CK, exist_ok=True)
meta, works = {}, {}
for name, q in QUERIES.items():
    ck = f"{CK}/{name}.json"
    if os.path.exists(ck):                       # retomada: consulta já coletada
        d = json.load(open(ck)); res, meta[name] = d["res"], d["count"]
    else:
        res = harvest(name, q)
        json.dump({"res": res, "count": meta[name]}, open(ck, "w"))
    for w in res:
        e = works.setdefault(w["id"], w); e.setdefault("_q", [])
        if name not in e["_q"]: e["_q"].append(name)
    print(f"{name}: total_base={meta[name]:>6}  coletadas={len(res):>5}  acumulado_unicas={len(works)}", flush=True)

with open("data/raw.jsonl", "w") as f:
    for w in works.values(): f.write(json.dumps(w) + "\n")
json.dump({"queries": QUERIES, "hits_total": meta, "max_per_query": MAXPER}, open("data/search_log.json", "w"), indent=1, ensure_ascii=False)
print("ÚNICAS:", len(works))
