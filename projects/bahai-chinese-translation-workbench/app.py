import json
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from db import (
    init_db, create_document, get_document, get_stage_outputs,
    save_stage_output, update_document_stage, log_audit, get_audit_log,
)
from agents import load_glossary, translation_agent, editing_agent

app = FastAPI(title="Bahai Chinese Translation Workbench")

GLOSSARY = []


@app.on_event("startup")
def startup():
    init_db()
    _load_glossary()


def _load_glossary():
    global GLOSSARY
    glossary_path = Path(__file__).parent / "glossary.json"
    if glossary_path.exists():
        GLOSSARY = load_glossary(str(glossary_path))


_load_glossary()


class CreateDocumentRequest(BaseModel):
    title: str
    source_text: str
    source_lang: str = "en"


class ReviewRequest(BaseModel):
    decision: str
    edited_text: str | None = None
    notes: str | None = None


class StageOutput(BaseModel):
    stage: int
    input_text: str
    output_text: str
    operator: str
    model_used: str | None = None
    human_notes: str | None = None
    created_at: str


class DocumentDetailResponse(BaseModel):
    id: int
    title: str
    source_text: str
    source_lang: str
    current_stage: int
    status: str
    stages: list[StageOutput]
    audit: list[dict] = []


def _build_response(doc_id):
    doc = get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    stages = get_stage_outputs(doc_id)
    audit = get_audit_log(doc_id)
    return DocumentDetailResponse(
        id=doc["id"], title=doc["title"], source_text=doc["source_text"],
        source_lang=doc["source_lang"], current_stage=doc["current_stage"],
        status=doc["status"],
        stages=[StageOutput(stage=s["stage"], input_text=s["input_text"], output_text=s["output_text"],
                            operator=s["operator"], model_used=s.get("model_used"),
                            human_notes=s.get("human_notes"), created_at=s["created_at"]) for s in stages],
        audit=audit,
    )


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/glossary")
def get_glossary():
    return {"terms": GLOSSARY}


@app.post("/api/documents")
def create_doc(req: CreateDocumentRequest):
    doc_id = create_document(req.title, req.source_text, req.source_lang)
    log_audit(doc_id, "stage1_started")
    result = translation_agent(req.source_text, req.source_lang, GLOSSARY)
    save_stage_output(doc_id=doc_id, stage=1, input_text=req.source_text,
                      output_text=result["translation"], operator="ai",
                      model_used=result.get("model_used"), prompt_used=result.get("prompt_used"))
    log_audit(doc_id, "stage1_completed", {"term_usage": result.get("term_usage", []), "notes": result.get("notes", "")})
    update_document_stage(doc_id, 2)
    return _build_response(doc_id)


@app.get("/api/documents/{doc_id}")
def get_doc(doc_id: int):
    return _build_response(doc_id)


@app.post("/api/documents/{doc_id}/review")
def review_doc(doc_id: int, req: ReviewRequest):
    doc = get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc["current_stage"] != 2:
        raise HTTPException(status_code=400, detail="Document is not at Stage 2 (review)")
    stages = get_stage_outputs(doc_id)
    stage1_output = next((s for s in stages if s["stage"] == 1), None)
    if stage1_output is None:
        raise HTTPException(status_code=400, detail="Stage 1 output not found")

    if req.decision == "approve":
        save_stage_output(doc_id=doc_id, stage=2, input_text=stage1_output["output_text"],
                          output_text=stage1_output["output_text"], operator="human", human_notes=req.notes)
        log_audit(doc_id, "stage2_approved", {"notes": req.notes})
        update_document_stage(doc_id, 3)
    elif req.decision == "edit":
        if not req.edited_text:
            raise HTTPException(status_code=400, detail="edited_text required when decision is 'edit'")
        save_stage_output(doc_id=doc_id, stage=2, input_text=stage1_output["output_text"],
                          output_text=req.edited_text, operator="human", human_notes=req.notes)
        log_audit(doc_id, "stage2_edited", {"notes": req.notes})
        update_document_stage(doc_id, 3)
    elif req.decision == "reject":
        log_audit(doc_id, "stage2_rejected", {"notes": req.notes})
    else:
        raise HTTPException(status_code=400, detail="decision must be 'approve', 'edit', or 'reject'")
    return _build_response(doc_id)


@app.post("/api/documents/{doc_id}/edit")
def edit_doc(doc_id: int):
    doc = get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc["current_stage"] != 3:
        raise HTTPException(status_code=400, detail="Document is not at Stage 3 (editing)")
    stages = get_stage_outputs(doc_id)
    stage2_output = next((s for s in stages if s["stage"] == 2), None)
    if stage2_output is None:
        raise HTTPException(status_code=400, detail="Stage 2 output not found")

    log_audit(doc_id, "stage3_started")
    result = editing_agent(doc["source_text"], stage2_output["output_text"], GLOSSARY)
    output_data = json.dumps({"edited_text": result["edited_text"], "changes_made": result.get("changes_made", []),
                              "checklist": result.get("checklist", {})}, ensure_ascii=False)
    save_stage_output(doc_id=doc_id, stage=3, input_text=stage2_output["output_text"],
                      output_text=output_data, operator="ai",
                      model_used=result.get("model_used"), prompt_used=result.get("prompt_used"))
    log_audit(doc_id, "stage3_completed", {"changes_made": result.get("changes_made", []), "checklist": result.get("checklist", {})})
    update_document_stage(doc_id, 3, status="completed")
    return _build_response(doc_id)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
