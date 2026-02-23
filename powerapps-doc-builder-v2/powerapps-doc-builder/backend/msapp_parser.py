"""
MSAPP Parser
=============
Parses Power Apps .msapp files (Canvas App packages).

An .msapp file is a ZIP archive containing:
  /Properties.json        - App properties
  /Header.json            - App metadata
  /AppCheckerResult.sarif  - App checker results
  /Connections/            - Connection definitions (JSON)
  /DataSources/            - Data source definitions
  /Resources/              - Media, images
  /Src/                    - Screen/control source files (YAML or JSON)
  /Components/             - Component definitions
  /References/             - Connector references

Extracts all data and converts into a dict structure the existing
PowerAppsYamlParser can process.
"""
from __future__ import annotations
import json, re, zipfile, io
from pathlib import PurePosixPath
from typing import Any


def is_msapp(data: bytes) -> bool:
    """Check if bytes look like a .msapp (ZIP) file."""
    return data[:4] == b'PK\x03\x04'  # ZIP magic bytes


class MsappParser:
    """Extract and normalize content from .msapp ZIP archives."""

    def parse(self, msapp_bytes: bytes) -> dict:
        """
        High-level: extract .msapp and return a merged dict
        that PowerAppsYamlParser can consume directly.
        Also stores unparsed sections inside the dict under '_unparsed_msapp'.
        """
        merged, unparsed = self.extract(msapp_bytes)
        if unparsed:
            merged["_unparsed_msapp"] = unparsed
        # Extract images info
        images = self.extract_images(msapp_bytes)
        if images:
            merged["_msapp_images"] = [name for name, _ in images]
        merged["_msapp_meta"] = {
            "file_count": len(self.list_contents(msapp_bytes)),
            "screen_count": len(merged.get("Screens", {})),
            "connection_count": len(merged.get("Connections", {})),
            "datasource_count": len(merged.get("DataSources", {})),
        }
        return merged

    def extract(self, msapp_bytes: bytes) -> tuple[dict, list[dict]]:
        """
        Parse .msapp and return (merged_data, unparsed_sections).
        merged_data mimics the YAML parser's expected structure.
        """
        unparsed = []
        merged = {
            "App": {"Name": "", "Properties": {}},
            "Screens": {},
            "Connections": {},
            "DataSources": {},
            "Components": {},
        }

        try:
            zf = zipfile.ZipFile(io.BytesIO(msapp_bytes))
        except zipfile.BadZipFile as e:
            return merged, [{"section": "msapp", "reason": f"Ungültiges ZIP/MSAPP: {e}", "raw_excerpt": ""}]

        filelist = {i.filename: i for i in zf.infolist()}

        # 1. Properties.json
        merged["App"]["Properties"] = self._read_json(zf, "Properties.json", unparsed)

        # 2. Header.json
        header = self._read_json(zf, "Header.json", unparsed)
        if header:
            merged["App"]["Name"] = header.get("DocVersion", header.get("AppName", ""))
            merged["App"]["Properties"].update({
                k: v for k, v in header.items() if isinstance(v, (str, int, float, bool))
            })

        # 3. Connections
        merged["Connections"] = self._read_folder_jsons(zf, "Connections/", filelist, unparsed)

        # 4. DataSources
        merged["DataSources"] = self._read_folder_jsons(zf, "DataSources/", filelist, unparsed)

        # 5. References -> also connections
        refs = self._read_folder_jsons(zf, "References/", filelist, unparsed)
        for name, ref in refs.items():
            if name not in merged["Connections"]:
                merged["Connections"][name] = ref

        # 6. Screens from Src/ and/or Controls/
        screen_folders = ["Src/", "Controls/"]
        for folder in screen_folders:
            for fname in self._list_folder(filelist, folder):
                content = zf.read(fname)
                stem = PurePosixPath(fname).stem
                screen_data = self._try_parse_src(content, fname, unparsed)
                if screen_data:
                    norm = self._normalize_screen(stem, screen_data)
                    if norm["name"] not in merged["Screens"]:
                        merged["Screens"][norm["name"]] = norm["data"]

        # Also check root-level numbered JSONs (some msapp versions)
        for fname in filelist:
            if re.match(r'^\d+\.json$', fname):
                content = zf.read(fname)
                screen_data = self._try_parse_src(content, fname, unparsed)
                if screen_data:
                    norm = self._normalize_screen(PurePosixPath(fname).stem, screen_data)
                    if norm["name"] not in merged["Screens"]:
                        merged["Screens"][norm["name"]] = norm["data"]

        # 7. Components
        for fname in self._list_folder(filelist, "Components/"):
            content = zf.read(fname)
            stem = PurePosixPath(fname).stem
            comp_data = self._try_parse_src(content, fname, unparsed)
            if comp_data:
                merged["Components"][stem] = comp_data

        # 8. Resources list
        res_files = self._list_folder(filelist, "Resources/")
        if res_files:
            merged["App"]["Properties"]["_resources"] = [PurePosixPath(f).name for f in res_files]

        # 9. AppCheckerResult.sarif
        sarif = self._read_json(zf, "AppCheckerResult.sarif", [])
        if sarif and isinstance(sarif, dict):
            checker = []
            for run in sarif.get("runs", []):
                for r in run.get("results", []):
                    checker.append({
                        "ruleId": r.get("ruleId", ""),
                        "message": r.get("message", {}).get("text", ""),
                        "level": r.get("level", ""),
                    })
            if checker:
                merged["App"]["Properties"]["_checker_results"] = checker

        zf.close()

        # Derive name
        if not merged["App"]["Name"]:
            p = merged["App"]["Properties"]
            merged["App"]["Name"] = p.get("AppName") or p.get("Name") or p.get("DocumentAppName") or "MSAPP App"

        return merged, unparsed

    def extract_images(self, msapp_bytes: bytes) -> list[tuple[str, bytes]]:
        """Extract images from Resources/."""
        images = []
        try:
            zf = zipfile.ZipFile(io.BytesIO(msapp_bytes))
        except:
            return images
        for info in zf.infolist():
            if info.is_dir():
                continue
            low = info.filename.lower()
            if any(low.endswith(e) for e in ('.png','.jpg','.jpeg','.gif','.webp','.bmp','.svg')):
                safe = re.sub(r'[^\w.\-]', '_', PurePosixPath(info.filename).name)
                images.append((safe, zf.read(info)))
        zf.close()
        return images

    def list_contents(self, msapp_bytes: bytes) -> list[str]:
        """List all files inside the .msapp for debugging."""
        try:
            zf = zipfile.ZipFile(io.BytesIO(msapp_bytes))
            return [i.filename for i in zf.infolist()]
        except:
            return []

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _read_json(self, zf, path, unparsed):
        try:
            return json.loads(zf.read(path).decode("utf-8-sig", errors="replace"))
        except KeyError:
            return {}
        except (json.JSONDecodeError, Exception) as e:
            unparsed.append({"section": f"msapp/{path}", "reason": f"JSON-Fehler: {e}", "raw_excerpt": ""})
            return {}

    def _read_folder_jsons(self, zf, prefix, filelist, unparsed):
        result = {}
        for fname in self._list_folder(filelist, prefix):
            if not fname.lower().endswith('.json'):
                continue
            name = PurePosixPath(fname).stem
            data = self._read_json(zf, fname, unparsed)
            if data:
                result[name] = data
        return result

    def _list_folder(self, filelist, prefix):
        return [f for f in filelist if f.startswith(prefix) and not filelist[f].is_dir()]

    def _try_parse_src(self, content_bytes, fname, unparsed):
        text = content_bytes.decode("utf-8-sig", errors="replace")
        # Try JSON
        try:
            d = json.loads(text)
            if isinstance(d, dict):
                return d
        except json.JSONDecodeError:
            pass
        # Try YAML
        try:
            import yaml
            d = yaml.safe_load(text)
            if isinstance(d, dict):
                return d
        except Exception:
            pass
        unparsed.append({"section": f"msapp/{fname}", "reason": "Weder JSON noch YAML.", "raw_excerpt": text[:500]})
        return None

    def _normalize_screen(self, fallback_name, data):
        """Normalize msapp JSON screen structure into YAML-parser-compatible dict."""
        top = data.get("TopParent", data)
        name = top.get("Name") or top.get("name") or data.get("Name") or fallback_name

        # Properties from Rules OR Properties array (two different msapp formats)
        properties = {}
        for src_key in ("Rules", "rules", "Properties", "properties", "DynamicProperties"):
            src = top.get(src_key, [])
            if isinstance(src, list):
                for r in src:
                    if isinstance(r, dict):
                        pn = r.get("Property", r.get("property", r.get("Name", "")))
                        sc = r.get("InvariantScript", r.get("invariantScript",
                             r.get("Script", r.get("script",
                             r.get("Value", r.get("value", ""))))))
                        if pn and sc:
                            properties[pn] = str(sc)
            elif isinstance(src, dict) and src_key in ("Properties", "properties"):
                # Properties is already a dict {key: value}
                for k, v in src.items():
                    if isinstance(v, dict):
                        properties[k] = str(v.get("InvariantScript", v.get("Value", v)))
                    else:
                        properties[k] = str(v) if v is not None else ""

        # Direct properties on the top-level object
        skip = {"Name","Type","Children","Rules","Properties","ControlUniqueId","TopParent","Template",
                "IsLocked","PublishOrderIndex","StyleName","IsAutoGenerated",
                "HasDynamicProperties","ChildrenOrder","IsGroupControl","ControlPropertyState",
                "DynamicProperties"}
        for k, v in top.items():
            if k not in skip and isinstance(v, (str, int, float, bool)):
                properties[k] = str(v)

        # Children
        children = {}
        for child in top.get("Children", top.get("children", [])):
            if isinstance(child, dict):
                cn = child.get("Name", child.get("name", f"Ctrl_{len(children)}"))
                children[cn] = self._normalize_control(child)

        result = {"Control": "screen", "Properties": properties}
        if children:
            result["Children"] = children
        return {"name": name, "data": result}

    def _normalize_control(self, ctrl):
        """Normalize a single control from msapp JSON."""
        ct = str(ctrl.get("Type", ctrl.get("type", ctrl.get("Control", "Unknown"))))
        # Map msapp types
        for pat, mapped in {"typedDataCard":"datacard","groupControl":"group","fluidGrid":"container"}.items():
            if pat.lower() in ct.lower():
                ct = mapped; break

        properties = {}
        for src_key in ("Rules", "rules", "Properties", "properties", "DynamicProperties"):
            src = ctrl.get(src_key, [])
            if isinstance(src, list):
                for r in src:
                    if isinstance(r, dict):
                        pn = r.get("Property", r.get("property", r.get("Name", "")))
                        sc = r.get("InvariantScript", r.get("invariantScript",
                             r.get("Script", r.get("script",
                             r.get("Value", r.get("value", ""))))))
                        if pn:
                            properties[pn] = str(sc) if sc else ""
            elif isinstance(src, dict) and src_key in ("Properties", "properties"):
                for k, v in src.items():
                    if isinstance(v, dict):
                        properties[k] = str(v.get("InvariantScript", v.get("Value", v)))
                    else:
                        properties[k] = str(v) if v is not None else ""

        skip = {"Name","Type","Children","Rules","Properties","ControlUniqueId","Template",
                "IsLocked","PublishOrderIndex","StyleName","IsAutoGenerated",
                "HasDynamicProperties","ChildrenOrder","IsGroupControl","ControlPropertyState",
                "DynamicProperties"}
        for k, v in ctrl.items():
            if k not in skip and isinstance(v, (str, int, float, bool)):
                properties[k] = str(v)

        children = {}
        for child in ctrl.get("Children", ctrl.get("children", [])):
            if isinstance(child, dict):
                cn = child.get("Name", child.get("name", f"C_{len(children)}"))
                children[cn] = self._normalize_control(child)

        result = {"Control": ct, "Properties": properties}
        if children:
            result["Children"] = children
        return result
