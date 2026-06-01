"""
tool_runner.py — the governed gate.

This is the ONLY component that touches the database, and it can execute
nothing but the tools declared in toolbox/tools.yaml:

  * It loads a single toolset (front_desk) — the agent's entire universe.
  * SQL tools run their FIXED statement with BOUND named parameters.
  * Vector tools run a FIXED candidate statement, then cosine in Python.
  * Unknown tool name  -> refused.   Unknown parameter -> refused.
  * The SQLite connection is opened READ-ONLY (mode=ro) as a backstop.

There is no code path here that runs caller-supplied SQL. That is the
no-free-SQL guarantee, in code.
"""
import os, sqlite3, json, yaml
from collections import Counter
from embeddings import embed, cosine

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_YAML = os.path.join(HERE, "..", "toolbox", "tools.yaml")


class GovernedToolset:
    def __init__(self, toolset_name="front_desk"):
        with open(TOOLS_YAML, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.cfg = cfg
        self.tools = cfg["tools"]
        names = cfg["toolsets"][toolset_name]
        self.loaded = {n: self.tools[n] for n in names}  # scoping = access control

        src = cfg["sources"][next(iter(cfg["sources"]))]
        db_path = os.path.normpath(os.path.join(HERE, "..", "toolbox", src["database"]))
        # READ-ONLY connection (governance layer 4). Any write is impossible.
        self.con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        self.con.row_factory = sqlite3.Row

    # -- introspection for the agent layer (names + descriptions + params only) --
    def specs(self):
        out = []
        for name, t in self.loaded.items():
            out.append({
                "name": name,
                "description": " ".join(t.get("description", "").split()),
                "parameters": t.get("parameters", []),
            })
        return out

    def _check_params(self, name, spec, params):
        declared = {p["name"] for p in spec.get("parameters", [])}
        unknown = set(params) - declared
        if unknown:
            raise ValueError(f"{name}: unknown parameter(s) {sorted(unknown)} — refused.")
        missing = declared - set(params)
        if missing:
            raise ValueError(f"{name}: missing required parameter(s) {sorted(missing)}.")

    def run(self, name, **params):
        if name not in self.loaded:
            raise ValueError(
                f"Tool '{name}' is not in this agent's toolset. "
                f"No such capability exists — refused.")
        spec = self.loaded[name]
        self._check_params(name, spec, params)
        kind = spec["kind"]
        if kind == "sqlite-sql":
            return self._run_sql(spec, params)
        if kind == "vector-cluster":
            return self._run_cluster(spec, params)
        if kind == "vector-knn":
            return self._run_knn(spec, params)
        raise ValueError(f"Unsupported tool kind: {kind}")

    # ---- fixed SQL, bound params ----
    def _run_sql(self, spec, params):
        rows = self.con.execute(spec["statement"], params).fetchall()
        return [dict(r) for r in rows]

    # ---- vector clustering over a fixed candidate set ----
    def _run_cluster(self, spec, params):
        thresh = float(spec.get("similarity_threshold", 0.55))
        rows = self.con.execute(spec["candidate_statement"], params).fetchall()
        items = [(r["id"], r["presenting_complaint"], json.loads(r["embedding"])) for r in rows]
        clusters, used = [], set()
        for i, (cid, complaint, vec) in enumerate(items):
            if cid in used:
                continue
            members = [(cid, complaint)]
            used.add(cid)
            for cid2, complaint2, vec2 in items[i + 1:]:
                if cid2 in used:
                    continue
                if cosine(vec, vec2) >= thresh:
                    members.append((cid2, complaint2))
                    used.add(cid2)
            label = Counter(m[1] for m in members).most_common(1)[0][0]
            clusters.append({
                "cluster": label,
                "size": len(members),
                "examples": sorted({m[1] for m in members})[:4],
            })
        clusters.sort(key=lambda c: c["size"], reverse=True)
        return clusters

    # ---- k-nearest cases over a fixed candidate set ----
    def _run_knn(self, spec, params):
        top_k = int(params["top_k"])
        tgt = self.con.execute(spec["target_statement"], params).fetchone()
        if not tgt:
            return []
        tvec = json.loads(tgt["embedding"])
        rows = self.con.execute(spec["candidate_statement"], params).fetchall()
        scored = []
        for r in rows:
            sim = cosine(tvec, json.loads(r["embedding"]))
            scored.append({
                "complaint": r["presenting_complaint"],
                "visit_date": r["visit_date"],
                "similarity": round(sim, 3),
            })
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]


if __name__ == "__main__":
    # Phase-3 style direct test: exercise every tool, bypassing the agent.
    ts = GovernedToolset()
    print("Loaded toolset 'front_desk':", [s["name"] for s in ts.specs()], "\n")
    demos = [
        ("cluster_recent_symptoms", dict(start_date="2026-05-18", end_date="2026-06-01")),
        ("condition_trend", dict(condition="Dengue (suspected)", since_date="2025-12-01")),
        ("attendance_trend", dict(start_date="2026-01-01", end_date="2026-06-01")),
        ("frequent_attenders", dict(min_visits=10, since_date="2025-01-01")),
        ("segment_patients", dict()),
        ("list_inactive_patients", dict(since_date="2025-06-01")),
        ("find_similar_cases", dict(case_id=1, top_k=5)),
    ]
    for name, params in demos:
        res = ts.run(name, **params)
        print(f"### {name}({params})")
        for row in (res[:6] if isinstance(res, list) else [res]):
            print("   ", row)
        if isinstance(res, list) and len(res) > 6:
            print(f"    ... (+{len(res)-6} more)")
        print()
