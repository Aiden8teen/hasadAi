"""SQLite persistence and Algerian smallholder farm/knowledge seed data for Hassad AI."""
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .config import DB_PATH


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            phone TEXT UNIQUE,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'farmer',
            locale TEXT NOT NULL DEFAULT 'en',
            region_code TEXT NOT NULL DEFAULT 'DZ-09',
            home_lat REAL,
            home_lon REAL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS farms (
            id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL,
            name TEXT NOT NULL,
            region_code TEXT NOT NULL,
            wilaya_name TEXT NOT NULL,
            area_hectares REAL NOT NULL,
            soil_type TEXT NOT NULL DEFAULT 'loamy',
            irrigation_source TEXT NOT NULL DEFAULT 'drip',
            lat REAL,
            lon REAL,
            version INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS plots (
            id TEXT PRIMARY KEY,
            farm_id TEXT NOT NULL,
            name TEXT NOT NULL,
            crop_name TEXT NOT NULL,
            crop_id TEXT NOT NULL,
            area_hectares REAL NOT NULL,
            growth_stage TEXT NOT NULL DEFAULT 'vegetative',
            planting_date TEXT NOT NULL,
            expected_harvest_date TEXT NOT NULL,
            expected_yield_kg REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'growing',
            version INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS diagnoses (
            id TEXT PRIMARY KEY,
            farmer_id TEXT NOT NULL,
            plot_id TEXT,
            growth_stage TEXT NOT NULL DEFAULT 'vegetative',
            image_url TEXT NOT NULL,
            image_sha256 TEXT NOT NULL,
            crop_id TEXT NOT NULL,
            crop_name TEXT NOT NULL,
            crop_confidence REAL NOT NULL,
            crop_source TEXT NOT NULL DEFAULT 'model',
            top3_crops_json TEXT NOT NULL DEFAULT '[]',
            disease_class TEXT NOT NULL,
            disease_name TEXT NOT NULL,
            disease_confidence REAL NOT NULL,
            top3_diseases_json TEXT NOT NULL DEFAULT '[]',
            active_seg_model TEXT NOT NULL,
            yolo_status TEXT NOT NULL,
            unet_status TEXT NOT NULL,
            lesion_count INTEGER NOT NULL DEFAULT 0,
            infected_area_pct REAL NOT NULL DEFAULT 0.0,
            severity TEXT NOT NULL DEFAULT 'low',
            estimated_yield_loss_pct INTEGER NOT NULL DEFAULT 0,
            mask_overlay_url TEXT,
            yolo_mask_url TEXT,
            unet_mask_url TEXT,
            treatment_type TEXT NOT NULL DEFAULT 'curative',
            recommendation TEXT NOT NULL,
            organic_treatments_json TEXT NOT NULL DEFAULT '[]',
            chemical_treatments_json TEXT NOT NULL DEFAULT '[]',
            recommendation_source TEXT NOT NULL DEFAULT 'disease-kb',
            status TEXT NOT NULL DEFAULT 'completed',
            needs_review INTEGER NOT NULL DEFAULT 0,
            verified_by TEXT,
            agronomist_notes TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            diagnosis_id TEXT,
            context_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            citations_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS knowledge_articles (
            id TEXT PRIMARY KEY,
            author_name TEXT NOT NULL,
            title_en TEXT NOT NULL,
            title_ar TEXT NOT NULL,
            title_fr TEXT NOT NULL,
            crop_name TEXT NOT NULL,
            tags_json TEXT NOT NULL,
            body_en TEXT NOT NULL,
            body_ar TEXT NOT NULL,
            body_fr TEXT NOT NULL,
            published_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS idempotency_keys (
            key TEXT PRIMARY KEY,
            response_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )

    # Seed users if empty
    cur.execute("SELECT COUNT(*) AS cnt FROM users")
    if cur.fetchone()["cnt"] == 0:
        now = utcnow_iso()
        cur.executemany(
            """
            INSERT INTO users (id, phone, full_name, role, locale, region_code, home_lat, home_lon, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("usr_farmer_01", "+213550123456", "Karim Benali (Mitidja Farm)", "farmer", "en", "DZ-09", 36.4700, 2.8300, now),
                ("usr_agro_01", "+213661987654", "Dr. Leenah Mansouri (INRA Agronomist)", "agronomist", "en", "DZ-16", 36.7538, 3.0588, now),
                ("usr_admin_01", "+213770112233", "Aiden (Hassad AI Lead)", "admin", "en", "DZ-16", 36.7538, 3.0588, now),
            ],
        )

    # Seed farms & plots if empty
    cur.execute("SELECT COUNT(*) AS cnt FROM farms")
    if cur.fetchone()["cnt"] == 0:
        now = utcnow_iso()
        cur.executemany(
            """
            INSERT INTO farms (id, owner_id, name, region_code, wilaya_name, area_hectares, soil_type, irrigation_source, lat, lon, version, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("frm_mitidja_01", "usr_farmer_01", "Domaine El-Mitidja (Boufarik)", "DZ-09", "Blida (09)", 4.8, "loamy", "drip", 36.5742, 2.9125, 1, now),
                ("frm_tipaza_02", "usr_farmer_01", "Ferme Côtière Tipaza", "DZ-42", "Tipaza (42)", 2.5, "sandy-loam", "drip", 36.5897, 2.4475, 1, now),
            ],
        )

        cur.executemany(
            """
            INSERT INTO plots (id, farm_id, name, crop_name, crop_id, area_hectares, growth_stage, planting_date, expected_harvest_date, expected_yield_kg, status, version, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("plt_01", "frm_mitidja_01", "Greenhouse A — Early Tomatoes", "Tomato", "crp_tomato", 1.5, "fruiting", "2026-08-01", "2026-11-12", 14500.0, "growing", 1, now),
                ("plt_02", "frm_mitidja_01", "North Field — Spunta Potatoes", "Potato", "crp_potato", 1.8, "vegetative", "2026-08-20", "2026-12-05", 19000.0, "growing", 1, now),
                ("plt_03", "frm_mitidja_01", "Orchard Block — Thomson Oranges", "Orange", "crp_orange", 1.5, "fruiting", "2026-03-10", "2026-11-28", 12000.0, "growing", 1, now),
                ("plt_04", "frm_tipaza_02", "Tunnel B — Bell Peppers", "Pepper, bell", "crp_pepper", 1.2, "flowering", "2026-08-15", "2026-11-20", 7800.0, "growing", 1, now),
                ("plt_05", "frm_tipaza_02", "East Parcel — Sweet Corn", "Corn (maize)", "crp_corn", 1.3, "vegetative", "2026-08-10", "2026-11-30", 6500.0, "growing", 1, now),
            ],
        )

    # Seed agronomic knowledge base articles for RAG chatbot
    cur.execute("SELECT COUNT(*) AS cnt FROM knowledge_articles")
    if cur.fetchone()["cnt"] == 0:
        now = utcnow_iso()
        cur.executemany(
            """
            INSERT INTO knowledge_articles (id, author_name, title_en, title_ar, title_fr, crop_name, tags_json, body_en, body_ar, body_fr, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "art_01",
                    "Dr. Leenah Mansouri (INRA)",
                    "Managing Late Blight (Mildiou) on Tomato & Potato in Humid Coastal Plains",
                    "إدارة اللفحة المتأخرة (الميلديو) في الطماطم والبطاطا في السهول الساحلية الرطبة",
                    "Gestion du Mildiou de la Tomate et de la Pomme de terre dans la Mitidja",
                    "Tomato",
                    json.dumps(["late_blight", "mildiou", "copper", "tomato", "potato", "organic"]),
                    "When night temperatures drop below 16°C with morning fog (>88% RH), Phytophthora infestans sporangia germinate within 2 hours. Remove infected basal leaves immediately, ventilate plastic tunnels at sunrise, and apply preventive Bordeaux mixture (10g/L) or copper oxychloride before rain. For active high-severity infections (>25% leaf area), apply cymoxanil + mancozeb and hill soil over potato tubers.",
                    "عندما تنخفض درجات الحرارة ليلاً عن 16 درجة مئوية مع ضباب صباحي (رطوبة >88%)، تنبت أبواغ اللفحة المتأخرة خلال ساعتين. أزل الأوراق السفلية المصابة فوراً، وافتح البيوت البلاستيكية عند الشروق للتهوية، ورش خليط بوردو (10 غ/لتر) أو أوكسي كلوريد النحاس وقائياً قبل المطر.",
                    "Lorsque les températures nocturnes descendent sous 16°C avec du brouillard matinal (>88% HR), Phytophthora infestans se propage rapidement. Aérez les serres dès l'aube, éliminez les folioles touchées et appliquez la bouillie bordelaise (10g/L) ou du cymoxanil en cas d'attaque sévère.",
                    now,
                ),
                (
                    "art_02",
                    "Dr. Leenah Mansouri (INRA)",
                    "Controlling Tomato Yellow Leaf Curl Virus (TYLCV) & Mosaic Virus Without Synthetic Virucides",
                    "مكافحة فيروس تجعد واصفرار أوراق الطماطم وفيروس الموزاييك بطرق وقائية وعضوية",
                    "Lutte intégrée contre le TYLCV et le Virus de la Mosaïque de la Tomate",
                    "Tomato",
                    json.dumps(["tylcv", "mosaic", "virus", "whitefly", "tomato", "sanitation"]),
                    "Plant viruses cannot be cured chemically once inside vascular tissue. For ToMV (Mosaic Virus), disinfect pruning shears and hands in 20% non-fat milk or 10% bleach between rows. For TYLCV, install 50-mesh insect netting, hang 1 yellow sticky trap per 10 m², and spray leaf undersides with 1% cold-pressed neem oil to suppress Bemisia tabaci whitefly vectors.",
                    "لا يمكن علاج الفيروسات النباتية كيميائياً بعد دخولها للأنسجة. لفيروس الموزاييك، عقم مقصات التقليم والأيدي بمحلول حليب خالي الدسم (20%) أو ماء جافيل مخفف (10%). ولفيروس التجعد الأصفر، ركّب شباك الحشرات (50-mesh) والمصائد الصفراء اللاصقة مع رش زيت النيم (1%) لمكافحة الذبابة البيضاء.",
                    "Les virus végétaux n'ont pas de traitement chimique curatif. Désinfectez les sécateurs dans une solution de lait écrémé (20%) ou d'eau de Javel (10%) contre le ToMV, et utilisez des filets insect-proof 50 mesh + huile de neem contre les aleurodes vecteurs du TYLCV.",
                    now,
                ),
                (
                    "art_03",
                    "Dr. Leenah Mansouri (INRA)",
                    "Citrus Greening (HLB) & Psyllid Vector Surveillance in Mitidja Groves",
                    "مراقبة اخضرار الحمضيات وحشرة البسيلا الناقلة في بساتين متيجة",
                    "Surveillance du HLB (Citrus Greening) et du Psylle dans les vergers d'agrumes",
                    "Orange",
                    json.dumps(["orange", "citrus", "hlb", "greening", "psyllid"]),
                    "Distinguish HLB from zinc deficiency by checking leaf symmetry: HLB causes asymmetrical blotchy mottling across the midrib, whereas nutrient deficiency is symmetrical on both halves of the leaf. Hang yellow sticky traps on outer Southern/Eastern orchard rows and apply 1.5% horticultural mineral oil during spring and autumn flush to suffocate psyllid nymphs.",
                    "ميز بين اخضرار الحمضيات ونقص الزنك عبر تناظر الورقة: يسبب مرض HLB تبقعاً غير متناظر على جانبي العرق الوسطي، بينما يكون نقص العناصر متناظراً. علق المصائد الصفراء في الصفوف الخارجية للبستان ورش الزيت المعدني الزراعي (1.5%) خلال نمو النموات الحديثة.",
                    "Distinguez le HLB d'une carence en zinc par l'asymétrie de la marbrure foliaire. Posez des pièges chromatiques jaunes en bordure de verger et pulvérisez de l'huile minérale horticole (1,5%) sur les jeunes pousses.",
                    now,
                ),
            ],
        )

    conn.commit()
    conn.close()
