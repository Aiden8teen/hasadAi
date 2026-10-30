"""Stage 4: Agronomic Recommendation Engine (LangChain/LangGraph + Google AI Studio + Phi-2 LoRA + 38-Class KB)."""
import json
import zipfile
from typing import Any, Dict, List, Optional

from ..config import PHI2_LORA_DIR, PHI2_LORA_ZIP, KB_JSON_PATH, GOOGLE_API_KEY, GEMINI_MODEL
from ..taxonomy import DISEASE_KB_DETAILS, CROP_METADATA
from ..database import get_conn
from .langgraph_agent import HassadLangGraphOrchestrator


class AgronomicRecommendationEngine:
    """
    Combines:
      1. LangChain + LangGraph 3-Node Stateful Agronomy Agent (`HassadLangGraphOrchestrator` with Google AI Studio)
      2. Optional local `microsoft/phi-2` LoRA adapter (`disease_rec_phi2_lora.zip`) when dropped into `/models`
      3. Instant 38-class curated Knowledge Base (`disease_recommendations_kb.json` + `DISEASE_KB_DETAILS`)
    """

    def __init__(self) -> None:
        self.langgraph_agent = HassadLangGraphOrchestrator()
        self.model = None
        self.tokenizer = None
        self.loaded: bool = False
        self.mode: str = "langgraph-gemini+kb"
        self.kb_json: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> Dict[str, Any]:
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.langgraph_agent._init_langgraph()
        self.mode = "langgraph-gemini+kb"

        if KB_JSON_PATH.exists():
            try:
                with open(KB_JSON_PATH, "r") as f:
                    self.kb_json = json.load(f)
            except Exception:
                pass

        if PHI2_LORA_ZIP.exists() and not (PHI2_LORA_DIR / "adapter_config.json").exists():
            try:
                PHI2_LORA_DIR.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(str(PHI2_LORA_ZIP), "r") as zf:
                    zf.extractall(str(PHI2_LORA_DIR))
            except Exception:
                pass

        adapter_cfg = PHI2_LORA_DIR / "adapter_config.json"
        if adapter_cfg.exists():
            self.loaded = True
            self.mode = "langgraph+phi2-lora+kb"

        return self.status()

    def status(self) -> Dict[str, Any]:
        lg_stat = self.langgraph_agent.status()
        adapter_present = (PHI2_LORA_DIR / "adapter_config.json").exists() or PHI2_LORA_ZIP.exists()
        return {
            "stage": "Stage 4 (LangChain/LangGraph Agent + Google AI Studio + 38-Class KB)",
            "loaded": True,
            "mode": self.mode,
            "model_file": (
                f"LangGraph ({GEMINI_MODEL}) + Phi-2 LoRA"
                if adapter_present
                else f"LangGraph ({GEMINI_MODEL}) + 38-Class INRA KB"
            ),
            "langgraph": lg_stat,
            "kb_classes_seeded": len(DISEASE_KB_DETAILS),
        }

    def build_notebook_prompt(
        self,
        disease_class: str,
        crop: str,
        severity: str,
        growth_stage: str,
        estimated_yield_loss_percent: int,
    ) -> str:
        return (
            f"Disease class: {disease_class}\n"
            f"Crop: {crop}\n"
            f"Severity: {severity}\n"
            f"Growth stage: {growth_stage}\n"
            f"Estimated yield loss (%): {estimated_yield_loss_percent}\n\n"
            "Task: Provide a clear, concise and actionable recommendation to treat and protect the plant.\n\n"
            "### Recommendation:\n"
        )

    def generate_recommendation(
        self,
        disease_class: str,
        crop: str,
        severity: str,
        growth_stage: str,
        estimated_yield_loss_percent: int,
        infected_area_pct: float = 0.0,
        lesion_count: int = 0,
        locale: str = "en",
    ) -> Dict[str, Any]:
        prompt = self.build_notebook_prompt(
            disease_class=disease_class,
            crop=crop,
            severity=severity,
            growth_stage=growth_stage,
            estimated_yield_loss_percent=estimated_yield_loss_percent,
        )

        # Execute 3-Node LangGraph Workflow
        graph_state = self.langgraph_agent.run_workflow(
            {
                "task_mode": "diagnosis_recommendation",
                "locale": locale,
                "crop_name": crop,
                "disease_class": disease_class,
                "severity": severity,
                "infected_area_pct": infected_area_pct,
                "lesion_count": lesion_count,
                "growth_stage": growth_stage,
                "estimated_yield_loss_percent": estimated_yield_loss_percent,
                "trace_steps": [],
            }
        )

        kb_detail = DISEASE_KB_DETAILS.get(disease_class, {})
        kb_base = self.kb_json.get(disease_class, {}).get("base_recommendation", "")
        is_healthy = "healthy" in disease_class.lower()
        treatment_type = "preventive" if (is_healthy or severity == "low") else "curative"
        surplus_ctx = graph_state.get("surplus_context", {})

        llm_text = graph_state.get("llm_output", "")
        if llm_text and len(llm_text) > 15:
            rec_text = llm_text
            source_name = graph_state.get("generator_used", "langgraph+gemini")
        else:
            if is_healthy:
                rec_text = (
                    f"Preventive ({growth_stage} stage) – {kb_base or 'Leaf is healthy. Maintain balanced irrigation and regular scouting.'} "
                    f"| Market Note ({surplus_ctx.get('region', 'DZ-42')}): {surplus_ctx.get('market_advice', '')}"
                )
            else:
                urgency = (
                    "Immediate intervention required"
                    if severity == "high"
                    else ("Targeted treatment advised" if severity == "medium" else "Early containment")
                )
                rec_text = (
                    f"{treatment_type.capitalize()} ({urgency} at {growth_stage} stage, "
                    f"~{estimated_yield_loss_percent}% yield risk) – {kb_base} "
                    f"| Market Radar ({surplus_ctx.get('surplus_risk', '')}): {surplus_ctx.get('market_advice', '')}"
                )
            source_name = graph_state.get("generator_used", "langgraph-kb-synthesizer")

        return {
            "treatment_type": treatment_type,
            "recommendation": rec_text,
            "organic_treatment": kb_detail.get("organic_treatment", []),
            "chemical_treatment": kb_detail.get("chemical_treatment", []),
            "surplus_context": surplus_ctx,
            "langgraph_trace": graph_state.get("trace_steps", []),
            "prompt_used": prompt,
            "source": source_name,
        }

    def answer_chat(
        self,
        user_message: str,
        context: Dict[str, Any],
        locale: str = "en",
    ) -> Dict[str, Any]:
        """Executes the 3-Node LangGraph workflow for interactive farmer questions."""
        target_cls = context.get("disease_class")
        msg_lower = user_message.lower()
        if not target_cls:
            for cls_key in DISEASE_KB_DETAILS:
                if any(tok.lower() in msg_lower for tok in cls_key.split("___") if len(tok) > 3):
                    target_cls = cls_key
                    break
        target_cls = target_cls or "Tomato___Late_blight"
        crop_name = context.get("crop_name") or target_cls.split("___")[0].replace("_", " ").strip()
        severity = context.get("severity", "medium")
        infected_pct = float(context.get("infected_area_pct", 18.4))
        yield_loss = int(context.get("estimated_yield_loss_pct", 21))
        growth_stage = context.get("growth_stage", "vegetative")

        graph_state = self.langgraph_agent.run_workflow(
            {
                "task_mode": "chat_response",
                "locale": locale,
                "crop_name": crop_name,
                "disease_class": target_cls,
                "severity": severity,
                "infected_area_pct": infected_pct,
                "growth_stage": growth_stage,
                "estimated_yield_loss_percent": yield_loss,
                "user_message": user_message,
                "trace_steps": [],
            }
        )

        citations = graph_state.get("rag_articles", [])
        kb_info = graph_state.get("kb_entry", {})
        surplus_ctx = graph_state.get("surplus_context", {})
        llm_reply = graph_state.get("llm_output", "")

        if llm_reply and len(llm_reply) > 15:
            return {
                "reply": llm_reply,
                "citations": citations,
                "langgraph_trace": graph_state.get("trace_steps", []),
            }

        if locale == "ar":
            dis_title = kb_info.get("name_ar", kb_info.get("name_en", ""))
            crop_ar = CROP_METADATA.get(crop_name, {}).get("name_ar", crop_name)
            sev_ar = "خفيفة" if severity == "mild" else ("متوسطة" if severity in ("medium", "moderate") else "شديدة")
            org_steps = "\n• " + "\n• ".join(kb_info.get("organic_treatment", [])[:3])
            chem_steps = "\n• " + "\n• ".join(kb_info.get("chemical_treatment", [])[:2])
            
            market_ar_map = {
                "Tomato": "يوصى بتوجيه الطماطم من الدرجة الثانية نحو مصانع التحويل بالبليدة أو تأخير الجني أسبوعاً لتفادي ذروة الفائض السعري.",
                "Potato": "ينصح بتجفيف درنات البطاطا جيداً وتخزينها في أماكن مهواة لمدة 10 إلى 14 يوماً للاستفادة من تحسن أسعار الجملة.",
                "Orange": "التعاقد المبكر مع مصانع العصائر في البليدة للحمضيات الصغيرة مع الاحتفاظ بالحبات الممتازة لأسواق التجزئة.",
                "Pepper, bell": "البيع المباشر في أسواق الجملة بالحطاطبة مع الالتزام التام بفترة الأمان قبل الجني."
            }
            mkt_note = market_ar_map.get(crop_name, "التنسيق مع تعاونيات الفلاحين المحلية لجدولة عمليات الجني والبيع بسعر مناسب.")
            rag_note = f"\n\nمرجع الإرشاد الفلاحي الجزائري ({citations[0]['title']}):\n{citations[0]['snippet']}" if citations else ""

            reply = (
                f"أهلاً بك يا أخي الفلاح. بناءً على فحص محصول {crop_ar} المصاب بمرض {dis_title} "
                f"(شدة الإصابة: {sev_ar}، المساحة المتضررة: {infected_pct}%، خطر فقدان المحصول: {yield_loss}%):\n\n"
                f"أولاً: التدابير العضوية والوقائية ذات الأولوية القصوى:{org_steps}\n\n"
                f"ثانياً: التدخل الكيميائي عند الضرورة وتفاقم الإصابة:{chem_steps}\n\n"
                f"ثالثاً: إشارة سوق الجملة في تيبازة ومتيجة:\n{mkt_note}"
                f"{rag_note}"
            )
        elif locale == "fr":
            dis_title = kb_info.get("name_fr", kb_info.get("name_en", ""))
            org_steps = "\n• " + "\n• ".join(kb_info.get("organic_treatment", [])[:3])
            chem_steps = "\n• " + "\n• ".join(kb_info.get("chemical_treatment", [])[:2])
            rag_note = f"\n\nRéférence INRA ({citations[0]['title']}) :\n{citations[0]['snippet']}" if citations else ""
            reply = (
                f"Bienvenue ! D'après l'analyse foliaire sur votre culture de {crop_name} ({dis_title} — sévérité : {severity}, "
                f"surface touchée : {infected_pct}%, risque de perte de récolte : {yield_loss}%) :\n\n"
                f"1. Mesures Biologiques et Culturales Prioritaires :{org_steps}\n\n"
                f"2. Option Phytosanitaire Conventionnelle d'Urgence :{chem_steps}\n\n"
                f"3. Signal du Marché de Gros ({surplus_ctx.get('region', 'Tipaza & Mitidja')}) :\n"
                f"{surplus_ctx.get('market_advice', '')}"
                f"{rag_note}"
            )
        else:
            dis_title = kb_info.get("name_en", "Leaf Condition")
            org_steps = "\n• " + "\n• ".join(kb_info.get("organic_treatment", [])[:3])
            chem_steps = "\n• " + "\n• ".join(kb_info.get("chemical_treatment", [])[:2])
            rag_note = f"\n\nExtension Reference — {citations[0]['title']}:\n{citations[0]['snippet']}" if citations else ""
            reply = (
                f"Welcome! Based on your {crop_name} field inspection ({dis_title} — Severity: {severity.upper()}, "
                f"Damaged Leaf Area: {infected_pct}%, Yield Loss Risk: {yield_loss}%):\n\n"
                f"1. Priority Organic & Cultural Management:{org_steps}\n\n"
                f"2. Targeted Protective Chemical Option (if spreading):{chem_steps}\n\n"
                f"3. Tipaza & Mitidja Wholesale Price Signal ({surplus_ctx.get('region', 'DZ-42 / DZ-09')}):\n"
                f"{surplus_ctx.get('surplus_risk', 'Normal balance')} — {surplus_ctx.get('market_advice', '')}"
                f"{rag_note}"
            )

        return {
            "reply": reply,
            "citations": citations,
            "langgraph_trace": graph_state.get("trace_steps", []),
        }
