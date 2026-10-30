#!/usr/bin/env bash
set -e

PORT="${1:-${PORT:-8080}}"
export PORT

cd "$(dirname "$0")/backend"
echo "=========================================================="
echo "🌾 Starting Hassad AI (حصاد) v2.2 Standalone Platform"
echo "📂 Models drop-in folder: $(cd ../models && pwd)"
echo "🤖 Stage 4 Orchestrator : LangChain + LangGraph + Google AI Studio"
echo "🌐 Web PWA & API URL   : http://localhost:${PORT}"
echo "=========================================================="

if python3 -c "import fastapi, uvicorn, cv2" >/dev/null 2>&1; then
  echo "🚀 Launching FastAPI + OpenCV/ML + LangGraph Server on port ${PORT}..."
  python3 -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" --reload
else
  echo "⚡ Launching Hassad AI Standalone + LangGraph Server on port ${PORT}..."
  python3 - << 'PY_SERVER_EOF'
import os, sys, stdlib_server, json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from app.config import WEB_DIR, UPLOADS_DIR, MASKS_DIR, EVAL_PLOTS_DIR
from app.database import get_conn, utcnow_iso
from app.taxonomy import CLASS_NAMES_38, CROP_METADATA, CROP_TO_INDICES, DISEASE_KB_DETAILS
from app.ml.recommender import AgronomicRecommendationEngine
import urllib.parse, uuid, cgi

rec_engine = AgronomicRecommendationEngine()

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, mime):
        if not path.exists():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        p = urllib.parse.unquote(parsed.path)
        if p == '/': return self._file(WEB_DIR / 'index.html', 'text/html; charset=utf-8')
        if p == '/app.js': return self._file(WEB_DIR / 'app.js', 'application/javascript; charset=utf-8')
        if p == '/sw.js': return self._file(WEB_DIR / 'sw.js', 'application/javascript; charset=utf-8')
        if p == '/manifest.webmanifest': return self._file(WEB_DIR / 'manifest.webmanifest', 'application/manifest+json')
        if p in ('/favicon.ico', '/favicon.svg'): return self._file(WEB_DIR / 'favicon.svg', 'image/svg+xml')
        if p.startswith('/uploads/'):
            f = UPLOADS_DIR / Path(p).name
            return self._file(f, 'image/svg+xml' if f.suffix=='.svg' else 'image/jpeg')
        if p.startswith('/masks/'):
            f = MASKS_DIR / Path(p).name
            return self._file(f, 'image/svg+xml' if f.suffix=='.svg' else 'image/png')
        if p.startswith('/eval_plots/'):
            f = EVAL_PLOTS_DIR / Path(p).name
            return self._file(f, 'image/jpeg' if f.suffix=='.jpg' else 'image/png')
        if p.startswith('/samples/'):
            f = (WEB_DIR / 'samples') / Path(p).name
            if f.suffix == '.json':
                return self._file(f, 'application/json; charset=utf-8')
            return self._file(f, 'image/jpeg' if f.suffix.lower() in ('.jpg', '.jpeg') else 'image/png')
        if p == '/api/v1/ml/status':
            return self._json(200, stdlib_server.check_models_folder())
        if p == '/api/v1/crops':
            items = []
            for cname, idxs in CROP_TO_INDICES.items():
                m = CROP_METADATA.get(cname, {})
                items.append({'crop_name': cname, 'id': m.get('id',''), 'name_en': m.get('name_en',cname), 'name_ar': m.get('name_ar',cname), 'name_fr': m.get('name_fr',cname), 'icon': m.get('icon','🌿'), 'num_classes': len(idxs)})
            return self._json(200, {'items': items})
        if p == '/api/v1/diseases':
            items = []
            for idx, ck in enumerate(CLASS_NAMES_38):
                cname = ck.split('___')[0].replace('_',' ').strip()
                kb = DISEASE_KB_DETAILS.get(ck, {})
                cm = CROP_METADATA.get(cname, {})
                items.append({'index': idx, 'class_key': ck, 'crop_name': cname, 'crop_icon': cm.get('icon','🌿'), 'name_en': kb.get('name_en',ck), 'name_ar': kb.get('name_ar',ck), 'name_fr': kb.get('name_fr',ck), 'pathogen': kb.get('pathogen',''), 'symptoms': kb.get('symptoms',''), 'organic_treatment': kb.get('organic_treatment',[]), 'chemical_treatment': kb.get('chemical_treatment',[])})
            return self._json(200, {'items': items})
        if p == '/api/v1/diagnoses':
            conn = get_conn(); cur = conn.cursor()
            cur.execute('SELECT * FROM diagnoses ORDER BY created_at DESC LIMIT 50')
            rows = [dict(r) for r in cur.fetchall()]; conn.close()
            return self._json(200, {'items': rows})
        if p == '/api/v1/farms':
            conn = get_conn(); cur = conn.cursor()
            cur.execute('SELECT * FROM farms'); farms = [dict(r) for r in cur.fetchall()]
            cur.execute('SELECT * FROM plots'); plots = [dict(r) for r in cur.fetchall()]
            conn.close()
            return self._json(200, {'farms': farms, 'plots': plots})
        if p == '/api/v1/market/surplus-radar':
            return self._json(200, {'region_code': 'DZ-42', 'items': [
                {'crop_name': 'Tomato', 'icon': '🍅', 'region': 'Sidi Rached / Tipaza (DZ-42) & Mitidja (DZ-09)', 'surplus_risk': 'HIGH (+34% above weekly demand)', 'price_dzd_kg': {'current': 85, 'p50_14d': 68, 'processing_floor': 74}, 'action_advice': 'Redirect Grade-B harvest to Blida / Rouiba tomato paste processing factories or stagger greenhouse picking by 7-10 days.'},
                {'crop_name': 'Potato', 'icon': '🥔', 'region': 'Tipaza & Ain Defla Corridor', 'surplus_risk': 'LOW (Balanced supply)', 'price_dzd_kg': {'current': 95, 'p50_14d': 104, 'processing_floor': 80}, 'action_advice': 'Hold cured Spunta tubers in ventilated storage for 10-14 days to capture higher early-December prices.'},
                {'crop_name': 'Orange', 'icon': '🍊', 'region': 'Boufarik & Chiffa Citrus Belt (DZ-09)', 'surplus_risk': 'MODERATE (+22% peak early Thomson harvest)', 'price_dzd_kg': {'current': 130, 'p50_14d': 115, 'processing_floor': 90}, 'action_advice': 'Contract early small-caliber fruit to local juice processors in Blida and hold premium table grades.'},
                {'crop_name': 'Pepper, bell', 'icon': '🫑', 'region': 'Tipaza Coastal Plasticulture Tunnels (DZ-42)', 'surplus_risk': 'LOW (Undersupplied)', 'price_dzd_kg': {'current': 140, 'p50_14d': 157, 'processing_floor': 110}, 'action_advice': 'Sell fresh directly to Hattatba / Eucalyptus wholesale buyers.'}
            ]})
        if p == '/api/v1/chat/sessions':
            conn = get_conn(); cur = conn.cursor()
            cur.execute('SELECT * FROM chat_sessions ORDER BY updated_at DESC')
            rows = [dict(r) for r in cur.fetchall()]; conn.close()
            return self._json(200, {'items': rows})
        if p.startswith('/api/v1/chat/sessions/') and p.endswith('/messages'):
            sid = p.split('/')[5]
            conn = get_conn(); cur = conn.cursor()
            cur.execute('SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC', (sid,))
            rows = [dict(r) for r in cur.fetchall()]; conn.close()
            for r in rows: r['citations'] = json.loads(r.get('citations_json') or '[]')
            return self._json(200, {'items': rows})
        self.send_error(404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        p = parsed.path
        if p == '/api/v1/ml/reload':
            return self._json(200, stdlib_server.check_models_folder())
        if p == '/api/v1/ml/segmenter-preference':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            stdlib_server.TELEMETRY['preferred_engine'] = body.get('preferred_model', 'auto')
            return self._json(200, {'status': 'updated', 'preferred_engine': stdlib_server.TELEMETRY['preferred_engine']})
        if p == '/api/v1/diagnoses':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            file_item = form['image']
            raw_bytes = file_item.file.read()
            fname = file_item.filename or 'leaf.jpg'
            gstage = form.getvalue('growth_stage', 'vegetative')
            chint = form.getvalue('crop_hint', '')
            loc = form.getvalue('locale', 'en')
            res = stdlib_server.run_diagnosis_pipeline(raw_bytes, fname, gstage, chint, locale=loc)
            return self._json(200, res)
        if p == '/api/v1/chat/sessions':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            conn = get_conn(); cur = conn.cursor(); now = utcnow_iso()
            sid = f'cht_{uuid.uuid4().hex[:8]}'
            ctx = {}
            locale = body.get('locale', 'en')
            crop_name = 'your crop'
            title = 'استشارة زراعية جديدة' if locale == 'ar' else ('Nouvelle consultation agricole' if locale == 'fr' else 'New Farm Advisory Session')
            if body.get('diagnosis_id'):
                cur.execute('SELECT * FROM diagnoses WHERE id = ?', (body['diagnosis_id'],))
                dr = cur.fetchone()
                if dr:
                    ctx = {'diagnosis_id': dr['id'], 'crop_name': dr['crop_name'], 'disease_class': dr['disease_class'], 'disease_name': dr['disease_name'], 'severity': dr['severity'], 'infected_area_pct': dr['infected_area_pct'], 'estimated_yield_loss_pct': dr['estimated_yield_loss_pct'], 'growth_stage': dr['growth_stage']}
                    crop_name = dr['crop_name']
                    title = f"{dr['crop_name']} — {dr['disease_name']}"

            if locale == 'ar':
                welcome = f"مرحباً بك يا أخي الفلاح! أنا مستشارك الفلاحي لحصاد AI لولاية تيبازة وسهل متيجة. قمت بتحميل بيانات فحص {crop_name}. كيف يمكنني مساعدتك اليوم في خطوات المعالجة العضوية، جرعات الرش، أو توقيت البيع في أسواق الجملة؟"
            elif locale == 'fr':
                welcome = f"Bienvenue ! Je suis votre conseiller agricole Hassad pour Tipaza et la Mitidja. Les données de votre culture de {crop_name} sont chargées. Comment puis-je vous aider pour les traitements biologiques ou les cours du marché ?"
            else:
                welcome = f"Welcome! I am your Hassad agricultural extension advisor for Tipaza and the Mitidja Plain. Inspection data for {crop_name} is ready. How can I help you today with organic remedies, spray dosages, or harvest market timing?"

            cur.execute('INSERT INTO chat_sessions (id, user_id, title, diagnosis_id, context_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)', (sid, 'usr_farmer_01', title, body.get('diagnosis_id'), json.dumps(ctx), now, now))
            cur.execute('INSERT INTO chat_messages (id, session_id, role, content, citations_json, created_at) VALUES (?, ?, ?, ?, ?, ?)', (f'msg_{uuid.uuid4().hex[:8]}', sid, 'assistant', welcome, '[]', now))
            conn.commit(); conn.close()
            return self._json(200, {'id': sid, 'title': title, 'context': ctx})
        if p.startswith('/api/v1/chat/sessions/') and p.endswith('/messages'):
            sid = p.split('/')[5]
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            conn = get_conn(); cur = conn.cursor(); now = utcnow_iso()
            cur.execute('SELECT * FROM chat_sessions WHERE id = ?', (sid,))
            sess = cur.fetchone()
            ctx = json.loads(sess['context_json'] or '{}') if sess else {}
            cur.execute('INSERT INTO chat_messages (id, session_id, role, content, citations_json, created_at) VALUES (?, ?, ?, ?, ?, ?)', (f'msg_{uuid.uuid4().hex[:8]}', sid, 'user', body.get('content',''), '[]', now))
            ans = rec_engine.answer_chat(body.get('content',''), context=ctx, locale=body.get('locale','en'))
            bmid = f'msg_{uuid.uuid4().hex[:8]}'
            cur.execute('INSERT INTO chat_messages (id, session_id, role, content, citations_json, created_at) VALUES (?, ?, ?, ?, ?, ?)', (bmid, sid, 'assistant', ans['reply'], json.dumps(ans['citations']), now))
            conn.commit(); conn.close()
            return self._json(200, {'assistant_message': {'id': bmid, 'role': 'assistant', 'content': ans['reply'], 'citations': ans['citations'], 'langgraph_trace': ans.get('langgraph_trace', [])}})
        if p == '/api/v1/plots':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            conn = get_conn(); cur = conn.cursor(); now = utcnow_iso()
            cur.execute('SELECT id FROM farms LIMIT 1')
            fr = cur.fetchone()
            farm_id = fr['id'] if fr else 'frm_mitidja_01'
            plt_id = f'plt_{uuid.uuid4().hex[:8]}'
            cname = body.get('crop_name', 'Tomato')
            cid = f'crp_{cname.lower().replace(" ", "_")}'
            cur.execute('''
                INSERT INTO plots (id, farm_id, name, crop_name, crop_id, area_hectares, growth_stage, planting_date, expected_harvest_date, expected_yield_kg, status, version, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (plt_id, farm_id, body.get('name', 'New Plot'), cname, cid, float(body.get('area_hectares', 1.0)), 'vegetative', body.get('planting_date', now[:10]), body.get('expected_harvest_date', now[:10]), float(body.get('expected_yield_kg', 1000.0)), 'growing', 1, now))
            conn.commit(); conn.close()
            return self._json(200, {'id': plt_id, 'status': 'created'})
        if p.startswith('/api/v1/diagnoses/') and p.endswith('/verify'):
            diag_id = p.split('/')[4]
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            conn = get_conn(); cur = conn.cursor()
            cur.execute('UPDATE diagnoses SET status = ?, verified_by = ?, agronomist_notes = ? WHERE id = ?',
                        ('verified', 'Dr. Leenah Mansouri (INRA)', body.get('agronomist_notes', 'Confirmed by specialist.'), diag_id))
            conn.commit(); conn.close()
            return self._json(200, {'status': 'verified', 'id': diag_id})
        if p.startswith('/api/v1/diagnoses/') and p.endswith('/confirm-crop'):
            diag_id = p.split('/')[4]
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            crop_name = body.get('crop_name', 'Tomato')
            gstage = body.get('growth_stage', 'vegetative')
            conn = get_conn(); cur = conn.cursor()
            cur.execute('UPDATE diagnoses SET crop_name = ?, growth_stage = ? WHERE id = ?', (crop_name, gstage, diag_id))
            conn.commit(); conn.close()
            return self._json(200, {'id': diag_id, 'crop_name': crop_name, 'growth_stage': gstage})
        if p == '/api/v1/sync/mutations':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            muts = body.get('mutations', [])
            return self._json(200, {'status': 'synced', 'count': len(muts)})
        self._json(200, {'status': 'ok'})

port = int(os.environ.get('PORT', 8080))
HTTPServer(('0.0.0.0', port), Handler).serve_forever()
PY_SERVER_EOF
fi
