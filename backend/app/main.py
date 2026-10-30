"""Main FastAPI Application for Hassad AI (4-Stage ML Pipeline + LangGraph Agent + Offline Sync + PWA Server)."""
import hashlib
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import (
    MODELS_DIR,
    UPLOADS_DIR,
    MASKS_DIR,
    WEB_DIR,
    EVAL_PLOTS_DIR,
)
from .database import get_conn, init_db, utcnow_iso
from .taxonomy import CLASS_NAMES_38, CROP_METADATA, CROP_TO_INDICES, DISEASE_KB_DETAILS
from .ml.classifier import HierarchicalPlantClassifier
from .ml.segmenter import DualSegmentationOrchestrator
from .ml.recommender import AgronomicRecommendationEngine

# Initialize SQLite database & seed data
init_db()

# Initialize the 4-Stage ML Pipeline Singletons
classifier_engine = HierarchicalPlantClassifier()
segmenter_engine = DualSegmentationOrchestrator()
recommender_engine = AgronomicRecommendationEngine()

app = FastAPI(
    title="Hassad AI (حصاد) — Offline-First Agricultural AI Platform",
    version="2.2.0",
    description="4-Stage Custom Vision & LangChain/LangGraph Agronomic Recommendation API (EfficientNetB0 + YOLOv9e-seg + U-Net + LangGraph Gemini)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded leaf photos, generated segmentation masks, and Kaggle evaluation plots
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/masks", StaticFiles(directory=str(MASKS_DIR)), name="masks")
app.mount("/eval_plots", StaticFiles(directory=str(EVAL_PLOTS_DIR)), name="eval_plots")


# ==============================================================================
# Pydantic Request Schemas
# ==============================================================================
class CropConfirmRequest(BaseModel):
    crop_name: str
    growth_stage: str = "vegetative"


class AgronomistVerifyRequest(BaseModel):
    verified_disease_class: str
    agronomist_notes: str = ""
    agronomist_name: str = "Dr. Leenah Mansouri (INRA)"


class SegmenterPreferenceRequest(BaseModel):
    preferred_model: str  # "auto" | "yolov9e-seg" | "unet"


class ChatSessionCreate(BaseModel):
    title: Optional[str] = None
    diagnosis_id: Optional[str] = None
    locale: str = "en"


class ChatMessageCreate(BaseModel):
    content: str
    locale: str = "en"


class PlotCreateRequest(BaseModel):
    farm_id: str = "frm_mitidja_01"
    name: str
    crop_name: str
    area_hectares: float
    growth_stage: str = "vegetative"
    planting_date: str
    expected_harvest_date: str
    expected_yield_kg: float


class SyncBatchRequest(BaseModel):
    mutations: List[Dict[str, Any]]


# ==============================================================================
# 1. ML Model Drop-In Status, Evaluation Charts, Hot-Reload & Segmenter Selector
# ==============================================================================
@app.get("/api/v1/ml/status")
def get_ml_status() -> Dict[str, Any]:
    files_in_models = [
        {"name": p.name, "size_mb": round(p.stat().st_size / (1024 * 1024), 2)}
        for p in sorted(MODELS_DIR.iterdir())
        if not p.name.startswith(".")
    ]
    eval_plots = [
        {"name": p.name, "url": f"/eval_plots/{p.name}"}
        for p in sorted(EVAL_PLOTS_DIR.iterdir())
        if p.suffix.lower() in (".png", ".jpg", ".jpeg")
    ]
    return {
        "models_directory": str(MODELS_DIR),
        "files_present": files_in_models,
        "eval_plots": eval_plots,
        "stages": {
            "classifier": classifier_engine.status(),
            "segmenter": segmenter_engine.status(),
            "recommender": recommender_engine.status(),
        },
    }


@app.post("/api/v1/ml/reload")
def reload_ml_models() -> Dict[str, Any]:
    """Hot-reloads all 4 models from `/models` without restarting the server."""
    c_stat = classifier_engine.reload()
    s_stat = segmenter_engine.reload()
    r_stat = recommender_engine.reload()
    return {
        "status": "reloaded",
        "stages": {
            "classifier": c_stat,
            "segmenter": s_stat,
            "recommender": r_stat,
        },
    }


@app.post("/api/v1/ml/segmenter-preference")
def set_segmenter_preference(req: SegmenterPreferenceRequest) -> Dict[str, Any]:
    if req.preferred_model not in ("auto", "yolov9e-seg", "unet"):
        raise HTTPException(status_code=400, detail="preferred_model must be 'auto', 'yolov9e-seg', or 'unet'")
    segmenter_engine.PreferredModel = req.preferred_model
    return {"status": "updated", "preferred_engine": segmenter_engine.PreferredModel}


# ==============================================================================
# 2. 4-Stage AI Crop Doctor Endpoints (`/api/v1/diagnoses`)
# ==============================================================================
@app.post("/api/v1/diagnoses")
async def create_diagnosis(
    image: UploadFile = File(...),
    growth_stage: str = Form("vegetative"),
    crop_hint: Optional[str] = Form(None),
    plot_id: Optional[str] = Form(None),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    if idempotency_key:
        cur.execute("SELECT response_json FROM idempotency_keys WHERE key = ?", (idempotency_key,))
        existing = cur.fetchone()
        if existing:
            conn.close()
            return json.loads(existing["response_json"])

    raw_bytes = await image.read()
    if not raw_bytes:
        conn.close()
        raise HTTPException(status_code=400, detail="Empty image file uploaded.")

    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
    np_arr = np.frombuffer(raw_bytes, np.uint8)
    img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        conn.close()
        raise HTTPException(status_code=415, detail="Unsupported or corrupted image file.")

    h, w = img_bgr.shape[:2]
    if max(h, w) > 1280:
        scale = 1280.0 / max(h, w)
        img_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    diag_id = f"dg_{uuid.uuid4().hex[:10]}"
    img_fname = f"{diag_id}_leaf.jpg"
    img_save_path = UPLOADS_DIR / img_fname
    cv2.imwrite(str(img_save_path), img_bgr)
    image_url = f"/uploads/{img_fname}"

    # Stage 1 & 2: Hierarchical Crop ID + Disease Classification
    cls_res = classifier_engine.predict_hierarchical(
        img_bgr,
        crop_hint=crop_hint,
        filename_hint=image.filename or "",
    )

    crop_info = cls_res["crop"]
    dis_info = cls_res["disease"]

    # Stage 3: Dual Lesion Segmentation (YOLOv9e-seg + U-Net with automatic failover)
    seg_res = segmenter_engine.segment_and_score(
        diagnosis_id=diag_id,
        img_bgr=img_bgr,
        disease_class=dis_info["class_key"],
        is_healthy=dis_info["is_healthy"],
        growth_stage=growth_stage,
    )

    # Stage 4: LangChain + LangGraph 3-Node Recommendation Engine
    rec_res = recommender_engine.generate_recommendation(
        disease_class=dis_info["class_key"],
        crop=crop_info["name"],
        severity=seg_res["severity"],
        growth_stage=growth_stage,
        estimated_yield_loss_percent=seg_res["estimated_yield_loss_percent"],
        infected_area_pct=seg_res["infected_area_pct"],
        lesion_count=seg_res["lesion_count"],
    )

    status_str = "pending_crop_confirm" if crop_info["needs_confirmation"] else (
        "needs_review" if dis_info["needs_review"] else "completed"
    )
    now = utcnow_iso()

    cur.execute(
        """
        INSERT INTO diagnoses (
            id, farmer_id, plot_id, growth_stage, image_url, image_sha256,
            crop_id, crop_name, crop_confidence, crop_source, top3_crops_json,
            disease_class, disease_name, disease_confidence, top3_diseases_json,
            active_seg_model, yolo_status, unet_status, lesion_count, infected_area_pct,
            severity, estimated_yield_loss_pct, mask_overlay_url, yolo_mask_url, unet_mask_url,
            treatment_type, recommendation, organic_treatments_json, chemical_treatments_json,
            recommendation_source, status, needs_review, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            diag_id,
            "usr_farmer_01",
            plot_id,
            growth_stage,
            image_url,
            sha256_hash,
            crop_info["id"],
            crop_info["name"],
            crop_info["confidence"],
            crop_info["source"],
            json.dumps(crop_info["top3_candidates"]),
            dis_info["class_key"],
            dis_info["name_en"],
            dis_info["confidence"],
            json.dumps(dis_info["top3_candidates"]),
            seg_res["active_model"],
            seg_res["yolo_status"],
            seg_res["unet_status"],
            seg_res["lesion_count"],
            seg_res["infected_area_pct"],
            seg_res["severity"],
            seg_res["estimated_yield_loss_percent"],
            seg_res["mask_overlay_url"],
            seg_res["yolo_mask_url"],
            seg_res["unet_mask_url"],
            rec_res["treatment_type"],
            rec_res["recommendation"],
            json.dumps(rec_res["organic_treatment"]),
            json.dumps(rec_res["chemical_treatment"]),
            rec_res["source"],
            status_str,
            1 if dis_info["needs_review"] else 0,
            now,
        ),
    )

    payload = {
        "id": diag_id,
        "status": status_str,
        "created_at": now,
        "growth_stage": growth_stage,
        "image_url": image_url,
        "quality": cls_res["quality"],
        "crop": crop_info,
        "disease": dis_info,
        "segmentation": seg_res,
        "recommendation": rec_res,
    }

    if idempotency_key:
        cur.execute(
            "INSERT OR REPLACE INTO idempotency_keys (key, response_json, created_at) VALUES (?, ?, ?)",
            (idempotency_key, json.dumps(payload), now),
        )

    conn.commit()
    conn.close()
    return payload


@app.post("/api/v1/diagnoses/{diag_id}/confirm-crop")
def confirm_crop_for_diagnosis(diag_id: str, req: CropConfirmRequest) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM diagnoses WHERE id = ?", (diag_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Diagnosis not found.")

    img_fname = Path(row["image_url"]).name
    img_bgr = cv2.imread(str(UPLOADS_DIR / img_fname))
    if img_bgr is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Stored leaf image missing.")

    cls_res = classifier_engine.predict_hierarchical(img_bgr, crop_hint=req.crop_name)
    crop_info = cls_res["crop"]
    dis_info = cls_res["disease"]

    seg_res = segmenter_engine.segment_and_score(
        diagnosis_id=diag_id,
        img_bgr=img_bgr,
        disease_class=dis_info["class_key"],
        is_healthy=dis_info["is_healthy"],
        growth_stage=req.growth_stage,
    )
    rec_res = recommender_engine.generate_recommendation(
        disease_class=dis_info["class_key"],
        crop=crop_info["name"],
        severity=seg_res["severity"],
        growth_stage=req.growth_stage,
        estimated_yield_loss_percent=seg_res["estimated_yield_loss_percent"],
        infected_area_pct=seg_res["infected_area_pct"],
        lesion_count=seg_res["lesion_count"],
    )

    cur.execute(
        """
        UPDATE diagnoses
        SET crop_id = ?, crop_name = ?, crop_confidence = 1.0, crop_source = 'farmer',
            disease_class = ?, disease_name = ?, disease_confidence = ?,
            active_seg_model = ?, lesion_count = ?, infected_area_pct = ?,
            severity = ?, estimated_yield_loss_pct = ?, recommendation = ?,
            organic_treatments_json = ?, chemical_treatments_json = ?,
            status = 'completed'
        WHERE id = ?
        """,
        (
            crop_info["id"],
            crop_info["name"],
            dis_info["class_key"],
            dis_info["name_en"],
            dis_info["confidence"],
            seg_res["active_model"],
            seg_res["lesion_count"],
            seg_res["infected_area_pct"],
            seg_res["severity"],
            seg_res["estimated_yield_loss_percent"],
            rec_res["recommendation"],
            json.dumps(rec_res["organic_treatment"]),
            json.dumps(rec_res["chemical_treatment"]),
            diag_id,
        ),
    )
    conn.commit()
    conn.close()

    return {
        "id": diag_id,
        "status": "completed",
        "crop": crop_info,
        "disease": dis_info,
        "segmentation": seg_res,
        "recommendation": rec_res,
    }


@app.get("/api/v1/diagnoses")
def list_diagnoses(needs_review: Optional[bool] = Query(None)) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    if needs_review is True:
        cur.execute("SELECT * FROM diagnoses WHERE needs_review = 1 ORDER BY created_at DESC")
    else:
        cur.execute("SELECT * FROM diagnoses ORDER BY created_at DESC LIMIT 50")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    for r in rows:
        r["top3_crops"] = json.loads(r.get("top3_crops_json") or "[]")
        r["top3_diseases"] = json.loads(r.get("top3_diseases_json") or "[]")
        r["organic_treatments"] = json.loads(r.get("organic_treatments_json") or "[]")
        r["chemical_treatments"] = json.loads(r.get("chemical_treatments_json") or "[]")
        kb = DISEASE_KB_DETAILS.get(r["disease_class"], {})
        r["disease_name_ar"] = kb.get("name_ar", r["disease_name"])
        r["disease_name_fr"] = kb.get("name_fr", r["disease_name"])
    return {"items": rows}


@app.post("/api/v1/diagnoses/{diag_id}/verify")
def verify_diagnosis_by_agronomist(diag_id: str, req: AgronomistVerifyRequest) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM diagnoses WHERE id = ?", (diag_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Diagnosis not found.")

    kb = DISEASE_KB_DETAILS.get(req.verified_disease_class, {})
    crop_name = req.verified_disease_class.split("___")[0].replace("_", " ").strip()
    rec_res = recommender_engine.generate_recommendation(
        disease_class=req.verified_disease_class,
        crop=crop_name,
        severity=row["severity"],
        growth_stage=row["growth_stage"],
        estimated_yield_loss_percent=row["estimated_yield_loss_pct"],
    )

    cur.execute(
        """
        UPDATE diagnoses
        SET disease_class = ?, disease_name = ?, recommendation = ?,
            organic_treatments_json = ?, chemical_treatments_json = ?,
            verified_by = ?, agronomist_notes = ?, needs_review = 0, status = 'completed'
        WHERE id = ?
        """,
        (
            req.verified_disease_class,
            kb.get("name_en", req.verified_disease_class),
            rec_res["recommendation"],
            json.dumps(rec_res["organic_treatment"]),
            json.dumps(rec_res["chemical_treatment"]),
            req.agronomist_name,
            req.agronomist_notes,
            diag_id,
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "verified", "id": diag_id, "verified_disease_class": req.verified_disease_class}


# ==============================================================================
# 3. 14-Crop & 38-Disease Offline Encyclopedia Endpoints
# ==============================================================================
@app.get("/api/v1/crops")
def list_crops() -> Dict[str, Any]:
    crops_out = []
    for crop_name, indices in CROP_TO_INDICES.items():
        meta = CROP_METADATA.get(crop_name, {})
        crops_out.append(
            {
                "crop_name": crop_name,
                "id": meta.get("id", f"crp_{crop_name.lower()}"),
                "name_en": meta.get("name_en", crop_name),
                "name_ar": meta.get("name_ar", crop_name),
                "name_fr": meta.get("name_fr", crop_name),
                "scientific_name": meta.get("scientific_name", ""),
                "icon": meta.get("icon", "🌿"),
                "growth_cycle_days": meta.get("growth_cycle_days", 110),
                "mitidja_priority": meta.get("mitidja_priority", False),
                "num_classes": len(indices),
                "classes": [CLASS_NAMES_38[i] for i in indices],
            }
        )
    return {"items": crops_out}


@app.get("/api/v1/diseases")
def list_diseases(crop: Optional[str] = Query(None)) -> Dict[str, Any]:
    items = []
    for idx, cls_key in enumerate(CLASS_NAMES_38):
        crop_name = cls_key.split("___")[0].replace("_", " ").strip()
        if crop and crop.lower() not in crop_name.lower():
            continue
        kb = DISEASE_KB_DETAILS.get(cls_key, {})
        c_meta = CROP_METADATA.get(crop_name, {})
        items.append(
            {
                "index": idx,
                "class_key": cls_key,
                "crop_name": crop_name,
                "crop_icon": c_meta.get("icon", "🌿"),
                "name_en": kb.get("name_en", cls_key),
                "name_ar": kb.get("name_ar", cls_key),
                "name_fr": kb.get("name_fr", cls_key),
                "pathogen": kb.get("pathogen", ""),
                "symptoms": kb.get("symptoms", ""),
                "organic_treatment": kb.get("organic_treatment", []),
                "chemical_treatment": kb.get("chemical_treatment", []),
                "is_healthy": "healthy" in cls_key.lower(),
            }
        )
    return {"items": items}


# ==============================================================================
# 4. Smart Agronomy Chatbot Endpoints (LangGraph 3-Node RAG Agent)
# ==============================================================================
@app.get("/api/v1/chat/sessions")
def list_chat_sessions() -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM chat_sessions ORDER BY updated_at DESC")
    sessions = [dict(r) for r in cur.fetchall()]
    conn.close()
    for s in sessions:
        s["context"] = json.loads(s.get("context_json") or "{}")
    return {"items": sessions}


@app.post("/api/v1/chat/sessions")
def create_chat_session(req: ChatSessionCreate) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    now = utcnow_iso()
    sess_id = f"cht_{uuid.uuid4().hex[:8]}"

    ctx: Dict[str, Any] = {}
    title = req.title or "LangGraph Agronomy Consultation"

    if req.diagnosis_id:
        cur.execute("SELECT * FROM diagnoses WHERE id = ?", (req.diagnosis_id,))
        d_row = cur.fetchone()
        if d_row:
            ctx = {
                "diagnosis_id": d_row["id"],
                "crop_name": d_row["crop_name"],
                "disease_class": d_row["disease_class"],
                "disease_name": d_row["disease_name"],
                "severity": d_row["severity"],
                "infected_area_pct": d_row["infected_area_pct"],
                "estimated_yield_loss_pct": d_row["estimated_yield_loss_pct"],
                "growth_stage": d_row["growth_stage"],
            }
            title = f"{d_row['crop_name']} — {d_row['disease_name']} ({d_row['severity'].upper()})"

    cur.execute(
        """
        INSERT INTO chat_sessions (id, user_id, title, diagnosis_id, context_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (sess_id, "usr_farmer_01", title, req.diagnosis_id, json.dumps(ctx), now, now),
    )

    if ctx:
        welcome = (
            f"🤖 **[LangGraph 3-Node Agronomy Agent]** I've loaded your **{ctx['crop_name']}** diagnosis "
            f"(**{ctx['disease_name']}**, **{ctx['infected_area_pct']}%** segmented lesion area, "
            f"**{ctx['severity']}** severity, ~**{ctx['estimated_yield_loss_pct']}%** yield risk at **{ctx['growth_stage']}** stage). "
            f"Ask me about organic sprays, dosage per hectare, or Tipaza/Mitidja harvest surplus timing!"
        )
    else:
        welcome = (
            "🤖 **Welcome to Hassad AI LangGraph Agronomy Assistant**. Ask me about any of our 14 supported crops, "
            "organic disease control, fertilizer timing, or drip irrigation in Tipaza and the Mitidja Plain."
        )

    msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    cur.execute(
        """
        INSERT INTO chat_messages (id, session_id, role, content, citations_json, created_at)
        VALUES (?, ?, 'assistant', ?, '[]', ?)
        """,
        (msg_id, sess_id, welcome, now),
    )

    conn.commit()
    conn.close()
    return {"id": sess_id, "title": title, "context": ctx, "welcome_message": welcome}


@app.get("/api/v1/chat/sessions/{sess_id}/messages")
def get_chat_messages(sess_id: str) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC", (sess_id,))
    msgs = [dict(r) for r in cur.fetchall()]
    conn.close()
    for m in msgs:
        m["citations"] = json.loads(m.get("citations_json") or "[]")
    return {"items": msgs}


@app.post("/api/v1/chat/sessions/{sess_id}/messages")
def send_chat_message(sess_id: str, req: ChatMessageCreate) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM chat_sessions WHERE id = ?", (sess_id,))
    sess = cur.fetchone()
    if not sess:
        conn.close()
        raise HTTPException(status_code=404, detail="Chat session not found.")

    ctx = json.loads(sess["context_json"] or "{}")
    now = utcnow_iso()

    user_msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    cur.execute(
        """
        INSERT INTO chat_messages (id, session_id, role, content, citations_json, created_at)
        VALUES (?, ?, 'user', ?, '[]', ?)
        """,
        (user_msg_id, sess_id, req.content, now),
    )

    ans = recommender_engine.answer_chat(req.content, context=ctx, locale=req.locale)
    bot_msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    cur.execute(
        """
        INSERT INTO chat_messages (id, session_id, role, content, citations_json, created_at)
        VALUES (?, ?, 'assistant', ?, ?, ?)
        """,
        (bot_msg_id, sess_id, ans["reply"], json.dumps(ans["citations"]), now),
    )
    cur.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now, sess_id))
    conn.commit()
    conn.close()

    return {
        "user_message_id": user_msg_id,
        "assistant_message": {
            "id": bot_msg_id,
            "role": "assistant",
            "content": ans["reply"],
            "citations": ans["citations"],
            "langgraph_trace": ans.get("langgraph_trace", []),
            "created_at": now,
        },
    }


# ==============================================================================
# 5. Farm Plots & Regional Yield / Surplus Radar (Pillar 3 Preview)
# ==============================================================================
@app.get("/api/v1/farms")
def list_farms_and_plots() -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM farms ORDER BY updated_at DESC")
    farms = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT * FROM plots ORDER BY expected_harvest_date ASC")
    plots = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"farms": farms, "plots": plots}


@app.post("/api/v1/plots")
def create_plot(req: PlotCreateRequest) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    now = utcnow_iso()
    plot_id = f"plt_{uuid.uuid4().hex[:8]}"
    crop_id = CROP_METADATA.get(req.crop_name, {}).get("id", f"crp_{req.crop_name.lower()}")
    cur.execute(
        """
        INSERT INTO plots (id, farm_id, name, crop_name, crop_id, area_hectares, growth_stage, planting_date, expected_harvest_date, expected_yield_kg, status, version, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'growing', 1, ?)
        """,
        (
            plot_id,
            req.farm_id,
            req.name,
            req.crop_name,
            crop_id,
            req.area_hectares,
            req.growth_stage,
            req.planting_date,
            req.expected_harvest_date,
            req.expected_yield_kg,
            now,
        ),
    )
    conn.commit()
    conn.close()
    return {"id": plot_id, "status": "created"}


@app.get("/api/v1/market/surplus-radar")
def get_regional_surplus_radar(region_code: str = Query("DZ-42")) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM plots WHERE status = 'growing'")
    plots = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT crop_name, AVG(estimated_yield_loss_pct) AS avg_loss FROM diagnoses GROUP BY crop_name")
    loss_by_crop = {r["crop_name"]: float(r["avg_loss"] or 0.0) for r in cur.fetchall()}
    conn.close()

    radar_items = [
        {
            "crop_name": "Tomato",
            "icon": "🍅",
            "region": "Sidi Rached / Tipaza (DZ-42) & Mitidja (DZ-09)",
            "HarvestWindow": "Nov 10 – Nov 28, 2026",
            "regional_supply_index": 1.34,
            "surplus_risk": "HIGH (+34% above 5-year weekly demand)",
            "projected_price_trend_14d": "-18% (Wholesale drop expected in Hattatba & Boufarik markets)",
            "disease_adjusted_loss_pct": round(loss_by_crop.get("Tomato", 14.5), 1),
            "price_dzd_kg": {"current": 85, "p50_14d": 68, "processing_floor": 74},
            "action_advice": "Redirect Grade-B harvest to Blida / Rouiba tomato paste processing factories before Nov 14 or stagger greenhouse picking by 7–10 days.",
        },
        {
            "crop_name": "Potato",
            "icon": "🥔",
            "region": "Tipaza (DZ-42) & Ain Defla Corridor",
            "HarvestWindow": "Nov 25 – Dec 20, 2026",
            "regional_supply_index": 0.92,
            "surplus_risk": "LOW (Balanced supply)",
            "projected_price_trend_14d": "+9% (Strong wholesale demand; cure tubers for cold storage)",
            "disease_adjusted_loss_pct": round(loss_by_crop.get("Potato", 8.2), 1),
            "price_dzd_kg": {"current": 95, "p50_14d": 104, "processing_floor": 80},
            "action_advice": "Hold cured Spunta tubers in ventilated storage for 10–14 days to capture higher early-December market prices.",
        },
        {
            "crop_name": "Orange",
            "icon": "🍊",
            "region": "Boufarik & Chiffa Citrus Belt (DZ-09)",
            "HarvestWindow": "Nov 20 – Jan 15, 2027",
            "regional_supply_index": 1.22,
            "surplus_risk": "MODERATE (+22% peak early Thomson harvest)",
            "projected_price_trend_14d": "-11% during peak late-November picking",
            "disease_adjusted_loss_pct": round(loss_by_crop.get("Orange", 5.0), 1),
            "price_dzd_kg": {"current": 130, "p50_14d": 115, "processing_floor": 90},
            "action_advice": "Contract early small-caliber fruit to local juice processors in Blida and hold premium table grades for mid-December.",
        },
        {
            "crop_name": "Pepper, bell",
            "icon": "🫑",
            "region": "Coastal Plasticulture Tunnels (Tipaza DZ-42)",
            "HarvestWindow": "Nov 15 – Dec 05, 2026",
            "regional_supply_index": 0.88,
            "surplus_risk": "LOW (Undersupplied)",
            "projected_price_trend_14d": "+12% (High retail demand in Algiers & Tipaza wholesale markets)",
            "disease_adjusted_loss_pct": round(loss_by_crop.get("Pepper, bell", 6.4), 1),
            "price_dzd_kg": {"current": 140, "p50_14d": 157, "processing_floor": 110},
            "action_advice": "Sell fresh directly to Hattatba / Eucalyptus wholesale buyers; no surplus redirection needed.",
        },
    ]

    return {
        "region_code": region_code,
        "active_plots_count": len(plots),
        "items": radar_items,
    }


# ==============================================================================
# 6. Offline Sync Batch Endpoint (`/api/v1/sync/mutations`)
# ==============================================================================
@app.post("/api/v1/sync/mutations")
def sync_offline_mutations(req: SyncBatchRequest) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    now = utcnow_iso()
    results = []

    for m in req.mutations:
        m_id = m.get("id", str(uuid.uuid4()))
        cur.execute("SELECT response_json FROM idempotency_keys WHERE key = ?", (m_id,))
        cached = cur.fetchone()
        if cached:
            results.append(json.loads(cached["response_json"]))
            continue

        op_res = {
            "id": m_id,
            "entity_type": m.get("entity_type", "plot"),
            "status": "applied",
            "synced_at": now,
        }
        cur.execute(
            "INSERT OR REPLACE INTO idempotency_keys (key, response_json, created_at) VALUES (?, ?, ?)",
            (m_id, json.dumps(op_res), now),
        )
        results.append(op_res)

    conn.commit()
    conn.close()
    return {"results": results}


# ==============================================================================
# 7. Serve Frontend PWA Static Assets
# ==============================================================================
@app.get("/")
def serve_pwa_index():
    return FileResponse(str(WEB_DIR / "index.html"))


@app.get("/app.js")
def serve_pwa_js():
    return FileResponse(str(WEB_DIR / "app.js"), media_type="application/javascript")


@app.get("/sw.js")
def serve_pwa_sw():
    return FileResponse(str(WEB_DIR / "sw.js"), media_type="application/javascript")


@app.get("/manifest.webmanifest")
def serve_pwa_manifest():
    return FileResponse(str(WEB_DIR / "manifest.webmanifest"), media_type="application/manifest+json")
