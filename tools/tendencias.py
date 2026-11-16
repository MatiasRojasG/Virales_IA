"""Busca los Shorts de IA más vistos de los últimos días (YouTube Data API v3).

La clave NO está en el código: el entorno la agrega como encabezado X-Goog-Api-Key a las
solicitudes a www.googleapis.com. Uso:  python tools/tendencias.py [--dias 7] [--n 15]
Costo: cada búsqueda = 100 unidades (límite gratis diario 10.000) → este script usa ~800.
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, urllib.parse, urllib.request
from pathlib import Path

API = "https://www.googleapis.com/youtube/v3/"
QUERIES = ["inteligencia artificial explicado", "cómo funciona la IA", "red neuronal explicada",
           "ChatGPT cómo funciona", "machine learning explicado", "algoritmo explicado",
           "IA curiosidades ciencia", "cómo aprende una IA"]


def get(endpoint, **params):
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url), timeout=30) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dias", type=int, default=7); ap.add_argument("--n", type=int, default=15)
    a = ap.parse_args()
    desde = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.dias)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = {}
    for q in QUERIES:
        r = get("search", part="snippet", q=q, type="video", videoDuration="short", order="viewCount",
                publishedAfter=desde, relevanceLanguage="es", maxResults=15)
        for it in r.get("items", []):
            ids[it["id"]["videoId"]] = q
    vids = []
    idl = list(ids)
    for k in range(0, len(idl), 50):
        r = get("videos", part="snippet,statistics", id=",".join(idl[k:k + 50]))
        for v in r.get("items", []):
            s = v["statistics"]
            vids.append({"titulo": v["snippet"]["title"], "canal": v["snippet"]["channelTitle"],
                         "vistas": int(s.get("viewCount", 0)), "likes": int(s.get("likeCount", 0)),
                         "comentarios": int(s.get("commentCount", 0)), "fecha": v["snippet"]["publishedAt"][:10],
                         "url": f"https://youtube.com/shorts/{v['id']}", "busqueda": ids[v["id"]]})
    vids.sort(key=lambda v: -v["vistas"])
    out = Path(__file__).resolve().parent.parent / "tendencias"; out.mkdir(exist_ok=True)
    hoy = dt.date.today().isoformat()
    (out / f"{hoy}.json").write_text(json.dumps(vids, ensure_ascii=False, indent=1))
    for v in vids[:a.n]:
        print(f"{v['vistas']:>10,}  {v['titulo'][:70]}  · {v['canal']}  ({v['fecha']})".replace(",", "."))


if __name__ == "__main__":
    main()
