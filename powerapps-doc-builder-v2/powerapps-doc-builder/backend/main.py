#!/usr/bin/env python3
"""
Power Apps Doc Builder - Backend Server
Pure Python stdlib HTTP server. Only dependency: PyYAML (pre-installed).
Run: python3 main.py   ->  http://127.0.0.1:8000
"""
from __future__ import annotations
import os, sys, json, re, uuid, hashlib, zipfile, io, mimetypes, traceback
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, unquote_plus

sys.path.insert(0, str(Path(__file__).parent))
from parser import PowerAppsYamlParser
from msapp_parser import MsappParser, is_msapp
from doc_generator import DocGenerator
from diff_engine import DiffEngine

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
IMAGES_DIR = DATA_DIR / "images"
FRONTEND_DIR = BASE_DIR / "frontend"
PROJECT_FILE = DATA_DIR / "project.json"
MODEL_FILE = DATA_DIR / "app_model.json"
for d in [DATA_DIR, OUTPUT_DIR, IMAGES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def load_project():
    if PROJECT_FILE.exists():
        return json.loads(PROJECT_FILE.read_text("utf-8"))
    return {"id":str(uuid.uuid4()),"name":"Neues Projekt","created":datetime.now(timezone.utc).isoformat(),"updated":datetime.now(timezone.utc).isoformat(),"yaml_hash":None,"screenshot_map":{},"manual_notes":{"purpose":"","intended_users":"","environments":"","roles":"","limitations":"","alm_notes":"","security_notes":"","connector_classification":""},"change_log":[],"settings":{"redact_ids":True,"include_best_practice_checks":True,"language":"de"}}

def save_project(p):
    p["updated"] = datetime.now(timezone.utc).isoformat()
    PROJECT_FILE.write_text(json.dumps(p, indent=2, ensure_ascii=False), "utf-8")

def load_model():
    return json.loads(MODEL_FILE.read_text("utf-8")) if MODEL_FILE.exists() else None

def save_model(m):
    MODEL_FILE.write_text(json.dumps(m, indent=2, ensure_ascii=False), "utf-8")

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *a):
        msg = fmt % a
        if '/api/' in msg or 'POST' in msg: print(f"  {msg}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        self.wfile.write(body)

    def send_err(self, status, detail):
        self.send_json({"detail":detail}, status)

    def serve_file(self, fpath, fname=None):
        if not fpath.exists(): return self.send_err(404,"Datei nicht gefunden.")
        mime,_ = mimetypes.guess_type(str(fpath))
        data = fpath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        if fname: self.send_header("Content-Disposition",f'attachment; filename="{fname}"')
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        self.wfile.write(data)

    def read_body(self):
        n = int(self.headers.get("Content-Length",0))
        return self.rfile.read(n) if n else b""

    def read_json_body(self):
        return json.loads(self.read_body().decode("utf-8"))

    def parse_multipart(self):
        ct = self.headers.get("Content-Type","")
        if "multipart" not in ct: return {},{}
        boundary = None
        for p in ct.split(";"):
            p=p.strip()
            if p.startswith("boundary="): boundary=p[9:].strip('"'); break
        if not boundary: return {},{}
        body = self.read_body()
        fields,files = {},{}
        for part in body.split(f"--{boundary}".encode()):
            if not part or part.strip() in (b"--",b""): continue
            sep = b"\r\n\r\n" if b"\r\n\r\n" in part else (b"\n\n" if b"\n\n" in part else None)
            if not sep: continue
            hdr,fdata = part.split(sep,1)
            if fdata.endswith(b"\r\n"): fdata=fdata[:-2]
            elif fdata.endswith(b"\n"): fdata=fdata[:-1]
            hs = hdr.decode("utf-8",errors="replace")
            nm = re.search(r'name="([^"]+)"',hs)
            fn = re.search(r'filename="([^"]*)"',hs)
            if not nm: continue
            name = nm.group(1)
            if fn and fn.group(1):
                files.setdefault(name,[]).append({"filename":fn.group(1),"data":fdata})
            else:
                fields[name] = fdata.decode("utf-8",errors="replace")
        return fields,files

    def do_OPTIONS(self):
        self.send_response(204)
        for h,v in [("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Methods","GET,POST,OPTIONS"),("Access-Control-Allow-Headers","Content-Type")]:
            self.send_header(h,v)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path=="/api/project": return self._get_project()
        if path=="/api/screens": return self._get_screens()
        if path=="/api/images": return self._get_images()
        if path=="/api/screenshots/auto-match": return self._auto_match()
        if path.startswith("/api/preview/"): return self._preview(path.split("/")[-1])
        if path.startswith("/api/download/"): return self.serve_file(OUTPUT_DIR/path.split("/")[-1],path.split("/")[-1])
        if path=="/api/model":
            m=load_model()
            return self.send_json(m) if m else self.send_err(404,"Kein Modell.")
        if path.startswith("/images/"): return self.serve_file(IMAGES_DIR/path[8:])
        if path.startswith("/output/"): return self.serve_file(OUTPUT_DIR/path[8:])
        if path=="/" or path=="": path="/index.html"
        fp = FRONTEND_DIR/path.lstrip("/")
        if fp.exists() and fp.is_file(): return self.serve_file(fp)
        return self.serve_file(FRONTEND_DIR/"index.html")

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            routes = {"/api/parse":self._parse,"/api/project/notes":self._notes,"/api/project/settings":self._settings,"/api/screenshots/upload":self._upload,"/api/screenshots/upload-zip":self._upload_zip,"/api/screenshots/map":self._map,"/api/generate":self._generate,"/api/changelog/note":self._cl_note,"/api/reset":self._reset}
            fn = routes.get(path)
            if fn: return fn()
            self.send_err(404,"Nicht gefunden.")
        except Exception as e:
            traceback.print_exc()
            self.send_err(500,str(e))

    def _get_project(self):
        proj=load_project(); m=load_model(); s=None
        if m:
            s={"app_name":m.get("app_name","?"),"screen_count":len(m.get("screens",[])),"control_count":m.get("stats",{}).get("total_controls",0),"connector_count":len(m.get("connectors",[])),"variable_count":len(m.get("variables",{}).get("global_vars",[])),"collection_count":len(m.get("variables",{}).get("collections",[])),"component_count":len(m.get("components",[])),"formula_count":m.get("stats",{}).get("total_formulas",0)}
        self.send_json({"project":proj,"model_summary":s})

    def _get_screens(self):
        m=load_model()
        self.send_json({"screens":[s["name"] for s in m.get("screens",[])] if m else []})

    def _get_images(self):
        self.send_json({"images":sorted(f.name for f in IMAGES_DIR.iterdir() if f.is_file())})

    def _auto_match(self):
        m=load_model()
        if not m: return self.send_json({"matches":{}})
        names=[s["name"] for s in m.get("screens",[])]
        imgs=[f.name for f in IMAGES_DIR.iterdir() if f.is_file()]
        matches={}
        for sn in names:
            sl=sn.lower().replace(" ","").replace("_","")
            for img in imgs:
                st=Path(img).stem.lower().replace(" ","").replace("_","")
                if sl in st or st in sl: matches[sn]=img; break
        self.send_json({"matches":matches})

    def _preview(self, fmt):
        em={"md":"docs.md","html":"docs.html","json":"docs.json","latex":"docs.tex"}
        fn=em.get(fmt)
        if not fn: return self.send_err(400,"Ungültig.")
        fp=OUTPUT_DIR/fn
        if not fp.exists(): return self.send_err(404,"Nicht generiert.")
        self.send_json({"content":fp.read_text("utf-8"),"filename":fn})

    def _parse(self):
        ct=self.headers.get("Content-Type","")
        raw=""; msapp_data=None; parse_mode="auto"
        if "multipart" in ct:
            fields,files=self.parse_multipart()
            # Check for mode field
            parse_mode = fields.get("mode", "auto")
            # Check for .msapp file upload
            if "msapp_file" in files and files["msapp_file"]:
                msapp_data = files["msapp_file"][0]["data"]
            elif "yaml_file" in files and files["yaml_file"]:
                fdata = files["yaml_file"][0]["data"]
                fname = files["yaml_file"][0]["filename"].lower()
                if fname.endswith(".msapp") or is_msapp(fdata):
                    msapp_data = fdata
                else:
                    raw = fdata.decode("utf-8",errors="replace")
            if "yaml_text" in fields and not raw and not msapp_data:
                raw = fields["yaml_text"]
        elif "json" in ct:
            body = self.read_json_body()
            raw = body.get("yaml_text","")
            parse_mode = body.get("mode", "auto")
        else:
            body=self.read_body().decode("utf-8",errors="replace")
            if "yaml_text=" in body:
                for p in body.split("&"):
                    if p.startswith("yaml_text="): raw=unquote_plus(p[10:]); break
                    if p.startswith("mode="): parse_mode=unquote_plus(p[5:]); break
            else: raw=body

        if not raw.strip() and not msapp_data:
            return self.send_err(400,"Kein YAML oder .msapp-Inhalt.")

        # Handle .msapp file
        input_type = "yaml"
        if msapp_data:
            input_type = "msapp"
            msapp_parser = MsappParser()
            try:
                parsed_dict = msapp_parser.parse(msapp_data)
            except Exception as e:
                return self.send_err(422, f"MSAPP-Parsing fehlgeschlagen: {e}")
            # Hash the binary for diff detection
            nh = hashlib.sha256(msapp_data).hexdigest()
        else:
            nh = hashlib.sha256(raw.encode()).hexdigest()

        proj=load_project(); om=load_model(); dr=None
        parser=PowerAppsYamlParser()
        try:
            if msapp_data:
                model = parser.parse(parsed_dict, mode="full")
            else:
                model = parser.parse(raw, mode=parse_mode)
        except Exception as e:
            return self.send_err(422,f"Parse-Fehler: {e}")

        # Store input type and detected mode in model
        model["input_type"] = input_type
        detected_mode = model.get("parse_mode", parse_mode)

        if om and proj.get("yaml_hash") and proj["yaml_hash"]!=nh:
            dr=DiffEngine().compute(om,model)
            proj["change_log"].append({"timestamp":datetime.now(timezone.utc).isoformat(),"yaml_hash":nh,"diff_summary":dr.get("summary",""),"user_note":""})
        proj["yaml_hash"]=nh; save_model(model); save_project(proj)
        s={
            "app_name":model.get("app_name","?"),
            "screen_count":len(model.get("screens",[])),
            "control_count":model.get("stats",{}).get("total_controls",0),
            "connector_count":len(model.get("connectors",[])),
            "variable_count":len(model.get("variables",{}).get("global_vars",[])),
            "collection_count":len(model.get("variables",{}).get("collections",[])),
            "component_count":len(model.get("components",[])),
            "formula_count":model.get("stats",{}).get("total_formulas",0),
            "unparsed_sections":len(model.get("unparsed",[])),
            "input_type": input_type,
            "parse_mode": detected_mode,
        }
        self.send_json({"summary":s,"diff":dr})

    def _notes(self):
        proj=load_project(); proj["manual_notes"].update(self.read_json_body()); save_project(proj); self.send_json({"ok":True})

    def _settings(self):
        proj=load_project(); proj["settings"].update(self.read_json_body()); save_project(proj); self.send_json({"ok":True})

    def _upload(self):
        _,files=self.parse_multipart(); saved=[]
        for fl in files.values():
            for f in fl:
                ext=Path(f["filename"]).suffix.lower()
                if ext not in (".png",".jpg",".jpeg",".gif",".webp",".bmp"): continue
                sn=re.sub(r"[^\w.\-]","_",f["filename"])
                (IMAGES_DIR/sn).write_bytes(f["data"]); saved.append(sn)
        self.send_json({"uploaded":saved})

    def _upload_zip(self):
        _,files=self.parse_multipart(); saved=[]
        for fl in files.values():
            for f in fl:
                try:
                    with zipfile.ZipFile(io.BytesIO(f["data"])) as zf:
                        for i in zf.infolist():
                            if i.is_dir(): continue
                            ext=Path(i.filename).suffix.lower()
                            if ext not in (".png",".jpg",".jpeg",".gif",".webp",".bmp"): continue
                            sn=re.sub(r"[^\w.\-]","_",Path(i.filename).name)
                            (IMAGES_DIR/sn).write_bytes(zf.read(i)); saved.append(sn)
                except: pass
        self.send_json({"uploaded":saved})

    def _map(self):
        proj=load_project(); proj["screenshot_map"]=self.read_json_body(); save_project(proj); self.send_json({"ok":True})

    def _generate(self):
        model=load_model()
        if not model: return self.send_err(400,"Kein Modell.")
        ct=self.headers.get("Content-Type","")
        fmts=["md","html","json","latex"]
        if "json" in ct:
            try: fmts=self.read_json_body()
            except: pass
        if not isinstance(fmts,list): fmts=["md","html","json","latex"]
        proj=load_project()
        g=DocGenerator(model=model,project=proj,output_dir=OUTPUT_DIR,images_dir=IMAGES_DIR)
        gen=[]
        if "md" in fmts: g.generate_markdown(); gen.append("docs.md")
        if "html" in fmts: g.generate_html(); gen.append("docs.html")
        if "json" in fmts: g.generate_json(); gen.append("docs.json")
        if "latex" in fmts: g.generate_latex(); gen.append("docs.tex")
        self.send_json({"generated":gen})

    def _cl_note(self):
        b=self.read_json_body(); proj=load_project()
        idx=b.get("index",-1); note=b.get("note","")
        if proj["change_log"] and -len(proj["change_log"])<=idx<len(proj["change_log"]):
            proj["change_log"][idx]["user_note"]=note; save_project(proj)
        self.send_json({"ok":True})

    def _reset(self):
        for f in [PROJECT_FILE,MODEL_FILE]:
            if f.exists(): f.unlink()
        for f in OUTPUT_DIR.iterdir():
            if f.is_file(): f.unlink()
        for f in IMAGES_DIR.iterdir():
            if f.is_file(): f.unlink()
        self.send_json({"ok":True})

def main():
    port=int(os.environ.get("PORT",8000))
    srv=HTTPServer(("127.0.0.1",port),Handler)
    print(f"\n  ⚡ Power Apps Doc Builder\n  http://127.0.0.1:{port}\n  Ctrl+C to stop\n")
    try: srv.serve_forever()
    except KeyboardInterrupt: print("\nStopped."); srv.server_close()

if __name__=="__main__":
    main()
