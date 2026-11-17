"""Narración con Edge TTS (voces neuronales gratuitas) y marcas de tiempo por palabra.

Requiere acceso de red a speech.platform.bing.com. Los audios se guardan en
caché por hash del texto, así que re-renderizar no vuelve a llamar al servicio.
"""
from __future__ import annotations
import asyncio, hashlib, json, os, subprocess
from pathlib import Path
import numpy as np

SR = 48000
VOICE = "es-MX-JorgeNeural"       # latinoamericano neutro; alternativas: es-CL-LorenzoNeural, es-PE-AlexNeural
RATE = "+18%"


def _trust_proxy_ca():
    """edge-tts valida TLS solo con certifi e ignora SSL_CERT_FILE. Detrás de un proxy con CA propia
    (sesiones cloud de Claude Code) se reemplaza su contexto SSL por uno que incluya esa CA."""
    ca = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
    if not Path(ca).exists():
        return
    import ssl, edge_tts.communicate as com
    if hasattr(com, "_SSL_CTX"):
        ctx = ssl.create_default_context(cafile=ca)
        try:
            import certifi; ctx.load_verify_locations(certifi.where())
        except Exception:
            pass
        com._SSL_CTX = ctx


async def _synth(text, voice, rate, pitch, mp3_path):
    import edge_tts
    _trust_proxy_ca()
    kw = dict(rate=rate, pitch=pitch, boundary="WordBoundary")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        kw["proxy"] = proxy
    com = edge_tts.Communicate(text, voice, **kw)
    words = []
    with open(mp3_path, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"text": ch["text"], "start": ch["offset"] / 1e7,
                              "end": (ch["offset"] + ch["duration"]) / 1e7})
    return words


def decode(path, sr=SR) -> np.ndarray:
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le",
                          "-ac", "1", "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).copy()


def synthesize(text, cache_dir, voice=VOICE, rate=RATE, pitch="+0Hz", retries=7):
    """Devuelve (audio float32 mono 48 kHz, lista de palabras con start/end en s)."""
    cache_dir = Path(cache_dir); cache_dir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha1(f"{voice}|{rate}|{pitch}|{text}".encode()).hexdigest()[:16]
    mp3, js = cache_dir / f"{h}.mp3", cache_dir / f"{h}.json"
    if not (mp3.exists() and js.exists()):
        os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt") if Path("/root/.ccr/ca-bundle.crt").exists() else None
        for k in range(retries):
            try:
                words = asyncio.run(_synth(text, voice, rate, pitch, mp3)); break
            except Exception as e:  # red inestable: reintento con espera
                if k == retries - 1: raise
                import time; time.sleep(min(20, 2 ** k))
        js.write_text(json.dumps({"text": text, "voice": voice, "words": words}, ensure_ascii=False, indent=1))
    audio = decode(mp3)
    # recorta silencio inicial/final del TTS dejando un margen
    words = json.loads(js.read_text())["words"]
    return audio, words
