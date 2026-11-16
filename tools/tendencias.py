"""Los 10 videos cortos de IA más vistos del DÍA en YouTube (YouTube Data API v3).
Si en las últimas 24 h hay menos de 10, amplía la ventana a 48 h y luego a 72 h.

La clave NO está en el código: el entorno la agrega como encabezado X-Goog-Api-Key a las
solicitudes a www.googleapis.com. Uso:  python tools/tendencias.py [--dias 7] [--n 15]
Costo: cada búsqueda = 100 unidades (límite gratis diario 10.000) → este script usa ~800.
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, urllib.parse, urllib.request
from pathlib import Path

API = "https://www.googleapis.com/youtube/v3/"
QUERIES = ["inteligencia artificial", "IA", "ChatGPT", "IA curiosidades", "robot inteligencia artificial",
           "le pregunté a la IA", "IA increíble", "Gemini IA", "IA explicado", "algoritmo"]
import re
SIGLA = re.compile(r"(?<![A-Za-z])(IA|AI|I\.A\.)(?![a-z])")            # sigla en mayúsculas («Ia» indonesio = él/ella)
TEMA = re.compile(r"(inteligencia artificial|artificial intelligence|chat ?gpt|gemini|robot|algoritmo|red(es)? neuronal|deepfake)", re.I)
SOLO_LATINO = re.compile(r"^[\x00-\u024F\u2000-\u2BFF\U0001F000-\U0001FAFF\s]*$")


def get(endpoint, **params):
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url), timeout=30) as r:
        return json.load(r)


def buscar(horas):
    desde = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=horas)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = {}
    for q in QUERIES:
        r = get("search", part="snippet", q=q, type="video", videoDuration="short", order="viewCount",
                publishedAfter=desde, maxResults=25)
        for it in r.get("items", []):
            ids.setdefault(it["id"]["videoId"], q)
    vids = []
    idl = list(ids)
    for k in range(0, len(idl), 50):
        r = get("videos", part="snippet,statistics", id=",".join(idl[k:k + 50]))
        for v in r.get("items", []):
            s_ = v["statistics"]; tit = v["snippet"]["title"]
            if not (SIGLA.search(tit) or TEMA.search(tit)) or not SOLO_LATINO.match(tit):
                continue                     # fuera: «ai» de otros idiomas, alfabetos no latinos
            vids.append({"titulo": v["snippet"]["title"], "canal": v["snippet"]["channelTitle"],
                         "vistas": int(s_.get("viewCount", 0)), "likes": int(s_.get("likeCount", 0)),
                         "comentarios": int(s_.get("commentCount", 0)), "fecha": v["snippet"]["publishedAt"][:16],
                         "url": f"https://youtube.com/shorts/{v['id']}", "busqueda": ids[v["id"]]})
    return sorted(vids, key=lambda v: -v["vistas"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()
    for horas in (24, 48, 72):
        vids = buscar(horas)
        if len(vids) >= a.n: break
    out = Path(__file__).resolve().parent.parent / "tendencias"; out.mkdir(exist_ok=True)
    hoy = dt.date.today().isoformat()
    (out / f"{hoy}.json").write_text(json.dumps(vids, ensure_ascii=False, indent=1))
    print(f"Top {a.n} videos de IA (últimas {horas} h):")
    for k, v in enumerate(vids[:a.n], 1):
        print(f"{k:>2}. {v['vistas']:>10,}  {v['titulo'][:70]}  · {v['canal']}".replace(",", "."))


if __name__ == "__main__":
    main()
