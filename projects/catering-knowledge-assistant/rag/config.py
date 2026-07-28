"""Shared configuration for the Tasty Kitchen RAG assistant."""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = ROOT / "corpus"
DB_PATH = ROOT / "tasty_kitchen.db"
QDRANT_PATH = ROOT / "qdrant_store"
CHUNKS_JSON = ROOT / "chunks.json"
EMBED_CACHE = ROOT / ".embed_cache.json"

COLLECTION = "tasty_kitchen_corpus"

# Qdrant runs either as a server (docker run -p 6333:6333 qdrant/qdrant) or in
# local embedded mode. Same engine and same filter semantics either way; the
# server additionally makes payload indexes real rather than a no-op.
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")


def qdrant_client():
    """Return a Qdrant client, preferring the server when it is reachable."""
    from qdrant_client import QdrantClient
    try:
        qc = QdrantClient(url=QDRANT_URL, timeout=2.0)
        qc.get_collections()
        return qc, "server"
    except Exception:
        return QdrantClient(path=str(QDRANT_PATH)), "local"

# gemini-embedding-001 is the current GA embedding model. text-embedding-004,
# named in the original outline, is no longer served on the Gemini API.
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768          # MRL truncation from 3072, normalised manually below
# Measured 2026-07-28: the free tier caps BOTH gemini-2.5-flash and
# gemini-2.5-flash-lite at 20 generate_content requests per DAY, per model
# (quotaId GenerateRequestsPerDayPerProjectPerModel-FreeTier, quotaValue 20).
# An earlier comment here claimed flash-lite sat in a separate, far larger
# bucket. That was wrong, and it is why the end to end evaluation had never
# completed: the run died partway and took its results with it.
#
# The 48 question end to end set costs two calls each (route + generate), so 96
# calls against 20/day per model. It CANNOT finish in one day on the free tier.
# Either use paid quota, or re-run `python -m rag.evaluate end2end` on later
# days: it resumes from the saved results and tops them up.
#
# Splitting the router onto a different model from the generator is a real
# lever, not cosmetic, because the cap is per model: pointing ROUTER_MODEL at
# gemini-2.5-flash doubles how many questions can be scored per day.
GEN_MODEL = os.environ.get("GEN_MODEL", "gemini-2.5-flash-lite")
ROUTER_MODEL = os.environ.get("ROUTER_MODEL", "gemini-2.5-flash-lite")

# Local cross-encoder. Runs on CPU, no API cost, genuine second-stage rerank.
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

TOP_K_VECTOR = 12        # candidates pulled from the vector store
TOP_K_RERANK = 4         # survivors passed to the generator
MIN_RERANK_SCORE = -6.0  # below this, treat as "nothing relevant retrieved"

# Authority precedence takes effect only above this cross-encoder score. It is
# the one tunable in the ranking rule: how relevant a binding document must be
# before it is allowed to outrank a better-matching secondary one. Set too low,
# an off-topic policy outranks the FAQ that actually answers; set too high, the
# rule stops firing and precedence collapses back toward the vector ordering.
# Swept on the labelled set, see the table in retriever.py.
RELEVANCE_FLOOR = 2.0

BUSINESS_NAME = "好吃厨房 Tasty Kitchen"


def load_api_key():
    """Read GEMINI_API_KEY from the environment, falling back to ~/.env."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    env_file = Path.home() / ".env"
    if env_file.exists():
        m = re.search(r"^GEMINI_API_KEY\s*=\s*(.*)$",
                      env_file.read_text(errors="ignore"), re.M)
        if m:
            key = m.group(1).strip().strip('"').strip("'")
            if key:
                os.environ["GEMINI_API_KEY"] = key
                return key
    raise RuntimeError(
        "GEMINI_API_KEY not found in the environment or in ~/.env")
