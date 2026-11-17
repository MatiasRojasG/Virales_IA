"""Fotos con licencia libre de Wikimedia Commons para carruseles (con autor y licencia para el crédito).

    python tools/commons.py buscar "Jensen Huang" [--n 8]
    python tools/commons.py bajar "File:Jensen Huang 2023.jpg" destino.jpg [--ancho 1280]

Solo licencias que permiten uso comercial con atribución (CC0, dominio público, CC BY, CC BY-SA).
`bajar` guarda también destino.json con título, autor, licencia y página, para el crédito.
"""
from __future__ import annotations
import argparse, html, json, re, urllib.parse, urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "ReelForge-carruseles/1.0 (uso editorial)"}
OK = re.compile(r"^(cc0|public domain|pd|cc by(-sa)? [0-9.]+|cc by(-sa)?)", re.I)


def _get(url, timeout=30):
    """GET con reintentos (Commons limita la frecuencia: 429/503)."""
    import time
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception:
            if k == 5: raise
            time.sleep(5 * (k + 1))


def api(**p):
    p.update(format="json", formatversion=2)
    return json.loads(_get(API + "?" + urllib.parse.urlencode(p)))


def limpio(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def info(titles, ancho=1280):
    r = api(action="query", titles="|".join(titles), prop="imageinfo",
            iiprop="url|size|extmetadata|mime", iiurlwidth=ancho)
    out = []
    for pg in r["query"]["pages"]:
        if "imageinfo" not in pg: continue
        ii = pg["imageinfo"][0]; md = ii.get("extmetadata", {})
        lic = limpio(md.get("LicenseShortName", {}).get("value"))
        out.append({"titulo": pg["title"], "url": ii.get("thumburl") or ii["url"], "ancho": ii["width"],
                    "alto": ii["height"], "mime": ii.get("mime"), "licencia": lic,
                    "autor": limpio(md.get("Artist", {}).get("value"))[:80],
                    "pagina": ii.get("descriptionurl"), "libre": bool(OK.match(lic))})
    return out


def buscar(q, n=8):
    r = api(action="query", list="search", srsearch=q, srnamespace=6, srlimit=n * 2)
    tit = [s["title"] for s in r["query"]["search"] if re.search(r"\.(jpe?g|png|webp)$", s["title"], re.I)][:n]
    return [x for x in info(tit) if x["libre"]] if tit else []


def bajar(titulo, destino, ancho=1280):
    x = info([titulo], ancho)[0]
    if not x["libre"]:
        raise SystemExit(f"licencia no apta: {x['licencia']}")
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(_get(x["url"], timeout=120))).convert("RGB")
    im.thumbnail((ancho, ancho), Image.LANCZOS)          # miniatura estándar (los originales dan 429)
    im.save(destino, quality=92)
    Path(destino).with_suffix(".json").write_text(json.dumps(x, ensure_ascii=False, indent=1))
    return x


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("buscar"); b.add_argument("q"); b.add_argument("--n", type=int, default=8)
    d = sp.add_parser("bajar"); d.add_argument("titulo"); d.add_argument("destino"); d.add_argument("--ancho", type=int, default=1280, help="miniatura estándar de Wikimedia: 960, 1280 o 1920")
    a = ap.parse_args()
    if a.cmd == "buscar":
        for x in buscar(a.q, a.n):
            print(f"{x['ancho']}x{x['alto']}  {x['licencia']:14s} {x['autor'][:30]:30s} {x['titulo']}")
    else:
        x = bajar(a.titulo, a.destino, a.ancho)
        print("ok", x["licencia"], "|", x["autor"], "->", a.destino)


if __name__ == "__main__":
    main()
