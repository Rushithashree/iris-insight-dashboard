"""IRIS INSIGHT - dependency-light Windows dashboard server.
Uses Python stdlib + the project's already-installed PyMySQL driver.
No pandas, NumPy, Streamlit, SQLAlchemy, Flask, or WSL required.
"""
from __future__ import annotations
import csv, io, json, os, re, sqlite3, threading, time, webbrowser
from datetime import date, datetime
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
STATIC = APP_DIR / "static"
TEMPLATES = APP_DIR / "templates"
REPORTS = ROOT / "database" / "reports"
HISTORY_DB = ROOT / "data" / "app" / "query_history.sqlite3"
PORT = int(os.getenv("IRIS_PORT", "8765"))
HOST = os.getenv("IRIS_HOST", "127.0.0.1")

# Read .env without requiring python-dotenv. Existing project credentials stay local.
def load_env(path: Path) -> None:
    if not path.exists(): return
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ: os.environ[key] = value

load_env(ROOT / ".env")

REPORTS_REGISTRY = {
    "R01": ("Species Record Count", "Count of specimens in each species group", "R01_species_record_count.sql"),
    "R02": ("Species Distribution Percentage", "Relative representation of each species", "R02_species_share.sql"),
    "R03": ("Mean Sepal Length", "Species-wise average sepal length", "R03_mean_sepal_length.sql"),
    "R04": ("Mean Sepal Width", "Species-wise average sepal width", "R04_mean_sepal_width.sql"),
    "R05": ("Mean Petal Length", "Species-wise average petal length", "R05_mean_petal_length.sql"),
    "R06": ("Mean Petal Width", "Species-wise average petal width", "R06_mean_petal_width.sql"),
    "R07": ("Sepal Scatter Data", "Specimen-level sepal measurements", "R07_sepal_scatter_data.sql"),
    "R08": ("Petal Scatter Data", "Specimen-level petal measurements", "R08_petal_scatter_data.sql"),
    "R09": ("Measurement Spread", "Ranges and standard deviations by species", "R09_measurement_spread.sql"),
    "R10": ("Filtered Specimen Explorer", "Specimen records with optional filters", "R10_filtered_specimen_explorer_app.sql"),
}
MEASUREMENTS = {
    "sepal_length_cm": "Sepal length", "sepal_width_cm": "Sepal width",
    "petal_length_cm": "Petal length", "petal_width_cm": "Petal width"
}

class DashboardError(Exception): pass

def db_connection():
    try:
        import pymysql
        from pymysql.cursors import DictCursor
    except Exception as exc:
        raise DashboardError("PyMySQL is not available in the existing project environment. The dashboard does not require Pandas or NumPy.") from exc
    required = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [k for k in required if not os.getenv(k)]
    if missing: raise DashboardError("Missing database settings in the existing .env: " + ", ".join(missing))
    return pymysql.connect(host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"),
        charset="utf8mb4", cursorclass=DictCursor, connect_timeout=5, read_timeout=20, write_timeout=20,
        autocommit=True)

def rows(sql: str, params: dict | tuple | None = None):
    conn = db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or {})
            return list(cur.fetchall())
    finally: conn.close()

def scalar(sql: str, params=None):
    result = rows(sql, params)
    return next(iter(result[0].values())) if result else None

def json_safe(value):
    if isinstance(value, Decimal): return float(value)
    if isinstance(value, (datetime, date)): return value.isoformat()
    if isinstance(value, dict): return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [json_safe(v) for v in value]
    return value

def overview_data():
    # These are the six KPIs specified in the approved product brief.
    species = rows("""SELECT sm.species_name, COUNT(s.specimen_id) AS specimen_count,
        AVG(s.sepal_length_cm) AS avg_sepal_length_cm, AVG(s.sepal_width_cm) AS avg_sepal_width_cm,
        AVG(s.petal_length_cm) AS avg_petal_length_cm, AVG(s.petal_width_cm) AS avg_petal_width_cm,
        MIN(s.sepal_length_cm) AS min_sepal_length_cm, MAX(s.sepal_length_cm) AS max_sepal_length_cm,
        MIN(s.sepal_width_cm) AS min_sepal_width_cm, MAX(s.sepal_width_cm) AS max_sepal_width_cm,
        MIN(s.petal_length_cm) AS min_petal_length_cm, MAX(s.petal_length_cm) AS max_petal_length_cm,
        MIN(s.petal_width_cm) AS min_petal_width_cm, MAX(s.petal_width_cm) AS max_petal_width_cm,
        STDDEV_POP(s.sepal_length_cm) AS sd_sepal_length_cm,
        STDDEV_POP(s.sepal_width_cm) AS sd_sepal_width_cm,
        STDDEV_POP(s.petal_length_cm) AS sd_petal_length_cm,
        STDDEV_POP(s.petal_width_cm) AS sd_petal_width_cm
        FROM species_master sm LEFT JOIN specimen s ON s.species_id=sm.species_id
        GROUP BY sm.species_id, sm.species_name ORDER BY sm.species_id""")
    total = sum(int(x["specimen_count"] or 0) for x in species)
    counts = [int(x["specimen_count"] or 0) for x in species]
    quality = quality_data(quick=True)
    kpis = [
        {"label":"Total specimens", "value":total, "detail":"Records currently stored in MySQL", "icon":"◉"},
        {"label":"Species groups", "value":len(species), "detail":"Distinct registered species", "icon":"✿"},
        {"label":"Measurement variables", "value":4, "detail":"Continuous dimensions · centimetres", "icon":"⌁"},
        {"label":"Smallest species group", "value":min(counts) if counts else 0, "detail":min(species,key=lambda x:x["specimen_count"])["species_name"] if species else "No data", "icon":"↓"},
        {"label":"Largest species group", "value":max(counts) if counts else 0, "detail":max(species,key=lambda x:x["specimen_count"])["species_name"] if species else "No data", "icon":"↑"},
        {"label":"Verified SQL reports", "value":len(REPORTS_REGISTRY), "detail":"Registered R01–R10 report definitions", "icon":"▤"},
    ]
    # Derived scientific highlights use actual rows from the database.
    insights=[]
    if species:
        for key, title, unit in [("avg_petal_length_cm","Highest average petal length","cm"),("avg_sepal_length_cm","Highest average sepal length","cm")]:
            best=max(species,key=lambda x: float(x[key] or 0))
            insights.append({"title":title,"species":best["species_name"],"value":round(float(best[key] or 0),2),"unit":unit})
        variability=max(((float(x["sd_petal_length_cm"] or 0),x["species_name"]) for x in species),default=(0,"—"))
        insights.append({"title":"Greatest petal-length variability","species":variability[1],"value":round(variability[0],2),"unit":"SD · cm"})
    return {"kpis":kpis,"species":species,"total":total,"insights":insights,"quality":quality}

def quality_data(quick=False):
    result={"status":"available","imported":None,"accepted":None,"rejected":None,"logs":[],"duplicate_groups":None,"missing_values":0,"invalid_measurements":0}
    try:
        # Core integrity checks; these do not modify or delete records.
        result["missing_values"] = int(scalar("""SELECT COUNT(*) FROM specimen WHERE
            sepal_length_cm IS NULL OR sepal_width_cm IS NULL OR petal_length_cm IS NULL OR petal_width_cm IS NULL""") or 0)
        result["invalid_measurements"] = int(scalar("""SELECT COUNT(*) FROM specimen WHERE
            sepal_length_cm<=0 OR sepal_width_cm<=0 OR petal_length_cm<=0 OR petal_width_cm<=0""") or 0)
        result["duplicate_groups"] = int(scalar("""SELECT COUNT(*) FROM (SELECT sepal_length_cm,sepal_width_cm,petal_length_cm,petal_width_cm
            FROM specimen GROUP BY sepal_length_cm,sepal_width_cm,petal_length_cm,petal_width_cm HAVING COUNT(*)>1) d""") or 0)
    except Exception as exc:
        result["status"]="partial"; result["integrity_note"]=str(exc)
    if quick: return result
    try:
        cols=rows("SHOW COLUMNS FROM import_batch")
        names={c["Field"] for c in cols}
        # Dynamic field matching avoids assuming unverified import_batch column names.
        idcol=next((x for x in ("import_batch_id","batch_id") if x in names),None)
        if idcol:
            result["imported"]=int(scalar(f"SELECT COUNT(*) FROM import_batch") or 0)
            for field,key in [("accepted_records","accepted"),("accepted_count","accepted"),("rejected_records","rejected"),("rejected_count","rejected")]:
                if field in names and result[key] is None: result[key]=int(scalar(f"SELECT COALESCE(SUM({field}),0) FROM import_batch") or 0)
    except Exception: pass
    try:
        cols=rows("SHOW COLUMNS FROM data_quality_log")
        names={c["Field"] for c in cols}
        if "severity" in names:
            result["logs"]=rows("SELECT severity, COUNT(*) AS issue_count FROM data_quality_log GROUP BY severity ORDER BY severity")
        if "resolution_status" in names:
            result["resolution"]=rows("SELECT resolution_status, COUNT(*) AS issue_count FROM data_quality_log GROUP BY resolution_status ORDER BY resolution_status")
    except Exception: pass
    return result

def specimens_data(query):
    where=[]; params={}
    species=query.get("species","").strip()
    if species: where.append("sm.species_name=%(species)s"); params["species"]=species
    sid=query.get("specimen_id","").strip()
    if sid:
        if not sid.isdigit(): raise ValueError("Specimen ID must be a whole number.")
        where.append("s.specimen_id=%(specimen_id)s"); params["specimen_id"]=int(sid)
    for key,col in [("min_sepal_length","sepal_length_cm"),("max_sepal_length","sepal_length_cm"),("min_sepal_width","sepal_width_cm"),("max_sepal_width","sepal_width_cm"),("min_petal_length","petal_length_cm"),("max_petal_length","petal_length_cm"),("min_petal_width","petal_width_cm"),("max_petal_width","petal_width_cm")]:
        val=query.get(key,"").strip()
        if val:
            try: params[key]=float(val)
            except ValueError: raise ValueError(f"{key.replace('_',' ')} must be numeric.")
            op=">=" if key.startswith("min") else "<="
            where.append(f"s.{col}{op}%({key})s")
    for mn,mx in [("min_sepal_length","max_sepal_length"),("min_sepal_width","max_sepal_width"),("min_petal_length","max_petal_length"),("min_petal_width","max_petal_width")]:
        if mn in params and mx in params and params[mn]>params[mx]: raise ValueError(f"{mn} cannot exceed {mx}.")
    page=max(1,int(query.get("page",1) or 1)); limit=min(5000,max(10,int(query.get("limit",25) or 25))); offset=(page-1)*limit
    clause=(" WHERE "+" AND ".join(where)) if where else ""
    total=int(scalar("SELECT COUNT(*) AS n FROM specimen s JOIN species_master sm ON sm.species_id=s.species_id"+clause,params) or 0)
    data=rows("""SELECT s.specimen_id,s.source_row_number,sm.species_name,s.sepal_length_cm,s.sepal_width_cm,
        s.petal_length_cm,s.petal_width_cm,s.import_batch_id FROM specimen s JOIN species_master sm
        ON sm.species_id=s.species_id"""+clause+" ORDER BY s.specimen_id LIMIT %(lim)s OFFSET %(off)s",{**params,"lim":limit,"off":offset})
    return {"rows":data,"total":total,"page":page,"limit":limit,"pages":max(1,(total+limit-1)//limit)}

def report_data(report_id, filters=None):
    if report_id not in REPORTS_REGISTRY: raise ValueError("Unknown report ID.")
    path=REPORTS / REPORTS_REGISTRY[report_id][2]
    if not path.exists(): raise DashboardError(f"Existing report file not found: {path.name}")
    sql=path.read_text(encoding="utf-8-sig")
    params={}
    if report_id=="R10":
        allowed=["species_name","specimen_id","min_sepal_length","max_sepal_length","min_sepal_width","max_sepal_width","min_petal_length","max_petal_length","min_petal_width","max_petal_width"]
        filters=filters or {}
        for k in allowed:
            v=filters.get(k)
            params[k]=None if v in (None,"") else (int(v) if k=="specimen_id" else float(v) if k.startswith(("min_","max_")) else str(v))
        sql=re.sub(r":([a-zA-Z_][a-zA-Z0-9_]*)",r"%(\1)s",sql)
    # R10 app SQL is a single SELECT; the general report definitions are SELECT-only.
    clean=re.sub(r"--.*?$","",sql,flags=re.M).strip().rstrip(";")
    if not re.match(r"(?is)^SELECT\b",clean): raise DashboardError("Report blocked: only read-only SELECT reports are permitted.")
    started=time.perf_counter(); data=rows(clean,params); elapsed=round((time.perf_counter()-started)*1000,2)
    return {"report_id":report_id,"name":REPORTS_REGISTRY[report_id][0],"sql":clean,"rows":data,"row_count":len(data),"column_count":len(data[0]) if data else 0,"duration_ms":elapsed}

ASK_RULES=[
 (re.compile(r"(highest|largest|max).*(average|mean)?.*(petal length)"),"highest_petal_length"),
 (re.compile(r"(highest|largest|max).*(average|mean)?.*(sepal length)"),"highest_sepal_length"),
 (re.compile(r"(count|number).*(species|each species)"),"species_counts"),
 (re.compile(r"(compare|average|mean).*(sepal width)"),"mean_sepal_width"),
 (re.compile(r"(compare|average|mean).*(petal width)"),"mean_petal_width"),
 (re.compile(r"(variability|standard deviation|most variable|greatest.*variability).*(petal length)?|(petal length).*(variability|standard deviation)"),"petal_variability"),
 (re.compile(r"(show|list|find).*(specimen|record).*(petal length).*(above|greater|over)\s*(\d+(?:\.\d+)?)"),"petal_length_threshold"),
]
def ask_iris(question):
    q=question.strip(); low=q.lower()
    if not q: raise ValueError("Enter a question first.")
    for pattern,intent in ASK_RULES:
        match=pattern.search(low)
        if not match: continue
        if intent=="highest_petal_length": sql="SELECT species_name, AVG(petal_length_cm) AS mean_value FROM specimen s JOIN species_master sm ON sm.species_id=s.species_id GROUP BY sm.species_id,sm.species_name ORDER BY mean_value DESC LIMIT 1"; params={}
        elif intent=="highest_sepal_length": sql="SELECT species_name, AVG(sepal_length_cm) AS mean_value FROM specimen s JOIN species_master sm ON sm.species_id=s.species_id GROUP BY sm.species_id,sm.species_name ORDER BY mean_value DESC LIMIT 1"; params={}
        elif intent=="species_counts": sql="SELECT sm.species_name,COUNT(*) AS specimen_count FROM specimen s JOIN species_master sm ON sm.species_id=s.species_id GROUP BY sm.species_id,sm.species_name ORDER BY sm.species_id"; params={}
        elif intent=="mean_sepal_width": sql="SELECT sm.species_name,AVG(sepal_width_cm) AS mean_sepal_width_cm FROM specimen s JOIN species_master sm ON sm.species_id=s.species_id GROUP BY sm.species_id,sm.species_name ORDER BY sm.species_id"; params={}
        elif intent=="mean_petal_width": sql="SELECT sm.species_name,AVG(petal_width_cm) AS mean_petal_width_cm FROM specimen s JOIN species_master sm ON sm.species_id=s.species_id GROUP BY sm.species_id,sm.species_name ORDER BY sm.species_id"; params={}
        elif intent=="petal_variability": sql="SELECT sm.species_name,STDDEV_POP(petal_length_cm) AS sd_petal_length_cm FROM specimen s JOIN species_master sm ON sm.species_id=s.species_id GROUP BY sm.species_id,sm.species_name ORDER BY sd_petal_length_cm DESC LIMIT 1"; params={}
        else:
            threshold=float(match.group(5)); sql="SELECT s.specimen_id,sm.species_name,s.petal_length_cm FROM specimen s JOIN species_master sm ON sm.species_id=s.species_id WHERE s.petal_length_cm > %(threshold)s ORDER BY s.petal_length_cm DESC LIMIT 200"; params={"threshold":threshold}
        result=rows(sql,params)
        record_history(q,intent,sql,result,"SUCCESS",len(result))
        return {"question":q,"intent":intent,"validated":True,"status":"SUCCESS","sql":sql,"rows":result,"row_count":len(result),"interpretation":f"Executed a read-only, parameterized analysis against {os.getenv('DB_NAME','the configured database')}."}
    record_history(q,"unsupported","","","REJECTED",0)
    return {"question":q,"intent":"unsupported","validated":False,"status":"REJECTED","sql":"","rows":[],"row_count":0,"interpretation":"I could not safely map that wording to a supported analysis. Try one of the example questions shown below."}

def init_history():
    HISTORY_DB.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(HISTORY_DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS query_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL, intent TEXT NOT NULL,
            sql_text TEXT, status TEXT NOT NULL, row_count INTEGER NOT NULL,
            created_at TEXT NOT NULL, result_json TEXT)""")

def record_history(question,intent,sql,result,status,row_count):
    try:
        init_history()
        with sqlite3.connect(HISTORY_DB) as con:
            con.execute("INSERT INTO query_history(question,intent,sql_text,status,row_count,created_at,result_json) VALUES(?,?,?,?,?,?,?)",
                (question,intent,sql,status,row_count,datetime.now().astimezone().isoformat(),json.dumps(json_safe(result),ensure_ascii=False)))
    except Exception: pass

def history_data():
    init_history()
    with sqlite3.connect(HISTORY_DB) as con:
        con.row_factory=sqlite3.Row
        return [dict(x) for x in con.execute("SELECT id,question,intent,status,row_count,created_at,sql_text,result_json FROM query_history ORDER BY id DESC LIMIT 100")]

class Handler(BaseHTTPRequestHandler):
    server_version="IrisInsight/1.0"
    def log_message(self,*args): pass
    def send(self,status,body,ctype="application/json; charset=utf-8"):
        raw=body if isinstance(body,bytes) else body.encode("utf-8")
        self.send_response(status); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
    def body_json(self):
        length=int(self.headers.get("Content-Length","0")); return json.loads(self.rfile.read(length) or b"{}")
    def do_GET(self):
        u=urlparse(self.path); path=u.path; q={k:v[-1] for k,v in parse_qs(u.query).items()}
        try:
            if path=="/": return self.send(200,(TEMPLATES/"index.html").read_text(encoding="utf-8"),"text/html; charset=utf-8")
            if path.startswith("/static/"):
                f=(STATIC/path.removeprefix("/static/")).resolve()
                if STATIC.resolve() not in f.parents or not f.is_file(): return self.send(404,"Not found","text/plain")
                typ="text/css; charset=utf-8" if f.suffix==".css" else "application/javascript; charset=utf-8" if f.suffix==".js" else "application/octet-stream"
                return self.send(200,f.read_bytes(),typ)
            if path=="/api/health":
                try: db=scalar("SELECT DATABASE() AS database_name"); return self.send(200,json.dumps({"connected":True,"database":db,"mode":"live"}))
                except Exception as e: return self.send(200,json.dumps({"connected":False,"database":os.getenv("DB_NAME"),"error":str(e),"mode":"disconnected"}))
            if path=="/api/overview": return self.send(200,json.dumps(json_safe(overview_data())))
            if path=="/api/species": return self.send(200,json.dumps(json_safe(overview_data()["species"])))
            if path=="/api/specimens": return self.send(200,json.dumps(json_safe(specimens_data(q))))
            if path=="/api/quality": return self.send(200,json.dumps(json_safe(quality_data())))
            if path=="/api/reports": return self.send(200,json.dumps([{"id":k,"name":v[0],"description":v[1]} for k,v in REPORTS_REGISTRY.items()]))
            if path.startswith("/api/report/"):
                rid=path.rsplit("/",1)[-1]; result=report_data(rid,q); return self.send(200,json.dumps(json_safe(result)))
            if path=="/api/history": return self.send(200,json.dumps(json_safe(history_data())))
            return self.send(404,json.dumps({"error":"Not found"}))
        except ValueError as e: return self.send(400,json.dumps({"error":str(e)}))
        except Exception as e: return self.send(503,json.dumps({"error":str(e),"type":type(e).__name__}))
    def do_POST(self):
        try:
            data=self.body_json()
            if self.path=="/api/ask": return self.send(200,json.dumps(json_safe(ask_iris(str(data.get("question",""))))))
            if self.path=="/api/export/specimens":
                result=specimens_data({**data,"limit":5000,"page":1}); out=io.StringIO(); fields=list(result["rows"][0].keys()) if result["rows"] else ["specimen_id","species_name",*MEASUREMENTS.keys()]
                writer=csv.DictWriter(out,fieldnames=fields); writer.writeheader(); writer.writerows(result["rows"])
                return self.send(200,out.getvalue(),"text/csv; charset=utf-8")
            return self.send(404,json.dumps({"error":"Not found"}))
        except ValueError as e: return self.send(400,json.dumps({"error":str(e)}))
        except Exception as e: return self.send(503,json.dumps({"error":str(e),"type":type(e).__name__}))

def main():
    print("IRIS INSIGHT dashboard server")
    print(f"Project root: {ROOT}")
    print(f"Opening http://{HOST}:{PORT}")
    print("No Pandas, NumPy, Streamlit, SQLAlchemy, or Flask imports are used.")
    server = ThreadingHTTPServer((HOST,PORT),Handler)
    threading.Timer(1.0, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()
    server.serve_forever()

if __name__=="__main__": main()
