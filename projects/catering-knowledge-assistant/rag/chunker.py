"""
Stage 1 of the pipeline: ingest and chunk.

Chunking strategy is per document type, because one size does not fit this
corpus:

  menu    one chunk per meal, so a retrieved chunk always carries its own
          date, day, service and both prices. A naive fixed-window splitter
          would orphan a dish from its date and make the answer unciteable.
  faq     one chunk per question and answer pair.
  policy  one chunk per section heading, which is the natural unit of a rule.
  notice  same as policy, but the override authority is carried in metadata.

Every chunk keeps its frontmatter metadata so the retriever can filter on
doc_type, category and authority at the vector store level.
"""

import json
import re
from dataclasses import dataclass, asdict, field

import frontmatter

from .config import CORPUS_DIR, CHUNKS_JSON


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    doc_type: str
    category: str
    authority: str
    doc_title: str
    heading: str
    text: str
    restates: str = ""      # doc_id of the binding document this chunk restates
    meta: dict = field(default_factory=dict)


def _split_on(pattern, body):
    """Split a markdown body into (heading, block) pairs on a heading regex."""
    parts = re.split(pattern, body, flags=re.M)
    preamble = parts[0].strip()
    pairs = []
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        block = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if block:
            pairs.append((heading, block))
    return preamble, pairs


def chunk_menu(post, meta):
    """One chunk per meal. The week context is prepended to every chunk."""
    body = post.content
    preamble, pairs = _split_on(r"^###\s+(.*)$", body)
    # Keep the week summary line, it answers "show all fish this week".
    summary = "\n".join(
        ln for ln in preamble.splitlines()
        if ln.strip().startswith(("Service dates", "Rotation position", "Week summary"))
    )
    chunks = []
    for i, (heading, block) in enumerate(pairs):
        text = (f"{meta['title']}, rotation week {meta.get('rotation_week')}.\n"
                f"{summary}\n\n### {heading}\n{block}")
        chunks.append((f"{meta['doc_id']}#meal{i:02d}", heading, text))
    # A whole-week overview chunk, for questions asked at week level.
    chunks.insert(0, (f"{meta['doc_id']}#overview", "Week overview",
                      f"{meta['title']}\n{preamble}"))
    return chunks


# The FAQ states its own authority inline. Nearly every answer closes with
# "See delivery_policy." or "See payment_and_refund_policy.", which names the
# binding document that entry restates. That relationship is what makes the FAQ
# secondary, so it is lifted out of the prose into a `restates` field rather
# than left in the text where only the generator can see it. Entries with no
# pointer are FAQ-only facts with no binding parent, and keep restates="".
SEE_REF = re.compile(r"\bSee\s+([a-z][a-z0-9_]*)\s*\.")


def chunk_faq(post, meta):
    """One chunk per Q&A pair, tagged with its FAQ section and binding parent."""
    body = post.content
    _, sections = _split_on(r"^##\s+(.*)$", body)
    chunks, n = [], 0
    for section, block in sections:
        parts = re.split(r"^\*\*Q:\s*(.*?)\*\*$", block, flags=re.M)
        for i in range(1, len(parts), 2):
            q = parts[i].strip()
            a = parts[i + 1].strip() if i + 1 < len(parts) else ""
            if not a:
                continue
            text = f"FAQ, {section}.\n\nQuestion: {q}\nAnswer: {a}"
            m = SEE_REF.search(a)
            chunks.append((f"{meta['doc_id']}#q{n:02d}", q, text,
                           m.group(1) if m else ""))
            n += 1
    return chunks


def chunk_sections(post, meta):
    """One chunk per '##' section, splitting long sections on '###'."""
    body = post.content
    preamble, sections = _split_on(r"^##\s+(.*)$", body)
    chunks, n = [], 0
    for section, block in sections:
        subs = re.split(r"^###\s+(.*)$", block, flags=re.M)
        head_block = subs[0].strip()
        if head_block:
            chunks.append((f"{meta['doc_id']}#s{n:02d}", section,
                           f"{meta['title']}, {section}.\n\n{head_block}"))
            n += 1
        for i in range(1, len(subs), 2):
            sub_head = subs[i].strip()
            sub_block = subs[i + 1].strip() if i + 1 < len(subs) else ""
            if sub_block:
                chunks.append((
                    f"{meta['doc_id']}#s{n:02d}", f"{section}: {sub_head}",
                    f"{meta['title']}, {section}, {sub_head}.\n\n{sub_block}"))
                n += 1
    if preamble and len(preamble) > 80:
        chunks.insert(0, (f"{meta['doc_id']}#intro", "Introduction",
                          f"{meta['title']}\n\n{preamble}"))
    return chunks


STRATEGY = {
    "menu": chunk_menu,
    "faq": chunk_faq,
    "policy": chunk_sections,
    "notice": chunk_sections,
    "reference": chunk_sections,
}


def build_chunks():
    chunks = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        post = frontmatter.load(path)
        meta = dict(post.metadata)
        doc_type = meta.get("doc_type", "reference")
        fn = STRATEGY.get(doc_type, chunk_sections)
        carried = {k: str(v) for k, v in meta.items()
                   if k in ("rotation_week", "date_start", "date_end",
                            "effective_from", "effective_to", "priority",
                            "applies_to", "language")}
        for row in fn(post, meta):
            # Strategies yield (chunk_id, heading, text), and optionally a
            # fourth element naming the binding document the chunk restates.
            cid, heading, text = row[0], row[1], row[2]
            restates = row[3] if len(row) > 3 else ""
            chunks.append(Chunk(
                chunk_id=cid,
                doc_id=meta["doc_id"],
                doc_type=doc_type,
                category=meta.get("category", "general"),
                authority=meta.get("authority", "primary"),
                doc_title=meta.get("title", meta["doc_id"]),
                heading=heading,
                text=text.strip(),
                restates=restates,
                meta=carried,
            ))
    return chunks


def main():
    chunks = build_chunks()
    CHUNKS_JSON.write_text(
        json.dumps([asdict(c) for c in chunks], ensure_ascii=False, indent=2),
        encoding="utf-8")

    from collections import Counter
    by_doc = Counter(c.doc_id for c in chunks)
    by_type = Counter(c.doc_type for c in chunks)
    lens = [len(c.text) for c in chunks]

    print(f"{len(chunks)} chunks written to {CHUNKS_JSON.name}\n")
    print("By document type:")
    for k, v in by_type.most_common():
        print(f"  {k:<12} {v}")
    print("\nBy document:")
    for k, v in sorted(by_doc.items()):
        print(f"  {k:<28} {v}")
    print(f"\nChunk size, characters: min {min(lens)}, "
          f"median {sorted(lens)[len(lens)//2]}, max {max(lens)}")


if __name__ == "__main__":
    main()
