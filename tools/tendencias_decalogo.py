"""Temas en tendencia para los reels de stheq.ia (explicaciones y decálogos): compara las vistas de
Shorts en español por categoría (cuidado personal, estoicismo, tecnología, hábitos).

La clave NO está en el código: el entorno la agrega como encabezado a las solicitudes a
www.googleapis.com. Uso:  python tools/tendencias_decalogo.py [--dias 30] [--top 30]
Costo: cada búsqueda = 100 unidades (límite gratis diario 10.000) → ~3.000 por ejecución.
Imprime, por categoría, la mediana de vistas de sus 10 videos más vistos (la señal de tendencia)
y la lista de los videos más vistos (solo como inspiración de tema: nunca se copia nada).
"""
from __future__ import annotations
import argparse, collections, datetime as dt, json, urllib.parse, urllib.request

API = "https://www.googleapis.com/youtube/v3/"
CATEGORIAS = {
    "verse mejor": ["cómo verse mejor", "glow up tips", "looksmaxing"],
    "piel": ["rutina skincare", "cuidado de la piel tips"],
    "pelo y barba": ["cuidado del cabello tips", "barba tips"],
    "ejercicio": ["ejercicio en casa", "rutina de ejercicio principiantes", "ganar músculo tips"],
    "dormir": ["cómo dormir mejor", "hábitos de sueño"],
    "estudiar": ["cómo estudiar mejor", "tips para estudiar", "técnica de estudio"],
    "alimentación": ["comer saludable tips", "hábitos alimenticios"],
    "mente y hábitos": ["hábitos que cambiarán tu vida", "disciplina hábitos", "ansiedad tips"],
    "productividad": ["productividad tips", "cómo dejar de procrastinar"],
    "estoicismo": ["estoicismo", "marco aurelio", "filosofía estoica", "séneca frases"],
    "tecnología": ["cómo funciona la tecnología", "tecnología curiosidades", "datos curiosos tecnología"],
    "IA": ["inteligencia artificial explicada", "cómo funciona la IA"],
}


def get(ep, **p):
    with urllib.request.urlopen(API + ep + "?" + urllib.parse.urlencode(p), timeout=30) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=30)
    ap.add_argument("--top", type=int, default=30)
    a = ap.parse_args()
    desde = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.dias)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = {}
    for cat, qs in CATEGORIAS.items():
        for q in qs:
            r = get("search", part="snippet", q=q, type="video", videoDuration="short", order="viewCount",
                    publishedAfter=desde, maxResults=25, relevanceLanguage="es")
            for it in r.get("items", []):
                ids.setdefault(it["id"]["videoId"], cat)
    vids, idl = [], list(ids)
    for k in range(0, len(idl), 50):
        for v in get("videos", part="snippet,statistics", id=",".join(idl[k:k + 50])).get("items", []):
            vids.append((int(v["statistics"].get("viewCount", 0)), ids[v["id"]], v["snippet"]["title"][:90],
                         v["snippet"]["channelTitle"][:25], f"https://youtube.com/shorts/{v['id']}"))
    vids.sort(reverse=True)
    agg = collections.defaultdict(list)
    for vw, cat, *_ in vids: agg[cat].append(vw)
    print(f"Shorts en español, últimos {a.dias} días — mediana de vistas del top 10 por categoría:\n")
    filas = []
    for cat, l in agg.items():
        top = sorted(l, reverse=True)[:10]
        filas.append((top[len(top) // 2], cat, len(l), top[0]))
    for med, cat, n, mx in sorted(filas, reverse=True):
        print(f"  {cat:16s} mediana top10 = {med:>11,d}   máx = {mx:>12,d}   ({n} videos)")
    print(f"\nTop {a.top} videos:")
    for vw, cat, ti, ch, url in vids[:a.top]:
        print(f"{vw:>12,d}  [{cat}] {ti} — {ch}  {url}")


if __name__ == "__main__":
    main()
