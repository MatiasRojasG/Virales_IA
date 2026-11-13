"""Guion -> línea de tiempo sincronizada con la voz.

Sintaxis de narración (un string por beat):
  *palabra*            palabra clave (se resalta en cyan en los subtítulos)
  *dos palabras*       grupo de palabras clave
  15%|quince_por_ciento   se MUESTRA "15%" y se PRONUNCIA "quince por ciento"
  α|alfa               idem para símbolos
"""
from __future__ import annotations
import re, unicodedata
from dataclasses import dataclass, field
import numpy as np
from . import tts as TTS

PUNCT = ".,;:!?…»)\"'"


@dataclass
class Token:
    display: str
    say: str
    kw: bool
    beat: str
    start: float = -1.0
    end: float = -1.0


@dataclass
class Ph:
    """Frase con prosodia propia: se sintetiza aparte, se recortan sus silencios
    y se separa de la siguiente por una pausa diseñada (`pause`, en s)."""
    text: str
    pause: float = 0.22
    rate: str | None = None      # p.ej. "-6%" para frases de énfasis
    pitch: str | None = None     # p.ej. "+6Hz" para preguntas/sorpresa


@dataclass
class Beat:
    id: str
    text: object                 # str o lista de Ph
    pause: float = 0.30          # silencio después del beat (s)
    rate: str | None = None      # velocidad específica (p.ej. "+0%")
    # se completan al construir
    start: float = 0.0
    dur: float = 0.0
    audio: np.ndarray | None = None
    tokens: list = field(default_factory=list)

    @property
    def end(self):
        return self.start + self.dur


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", s)


def parse(text, beat_id):
    toks, kw = [], False
    for raw in text.split():
        opens = raw.startswith("*")
        core = raw.lstrip("*")
        trail = ""
        while core and core[-1] in PUNCT + "*":
            trail = core[-1] + trail; core = core[:-1]
        closes = "*" in trail
        trail = trail.replace("*", "")
        if opens: kw = True
        disp, _, say = core.partition("|")
        say = say.replace("_", " ") if say else disp
        toks.append(Token(disp + trail, say + trail, kw, beat_id))
        if closes: kw = False
    return toks


def _align(tokens, words, offset):
    """Asigna tiempos a tokens a partir de las WordBoundary del TTS."""
    say_words = []
    for ti, t in enumerate(tokens):
        for w in t.say.split():
            if _norm(w): say_words.append((ti, _norm(w)))
    p = 0
    for w in words:
        nw = _norm(w["text"])
        if not nw: continue
        for j in range(p, min(p + 6, len(say_words))):
            ti, sw = say_words[j]
            if sw == nw or (len(nw) > 3 and (sw.startswith(nw) or nw.startswith(sw))):
                tk = tokens[ti]
                if tk.start < 0: tk.start = offset + w["start"]
                tk.end = offset + w["end"]
                p = j + 1
                break
    # interpola tokens sin tiempo
    known = [i for i, t in enumerate(tokens) if t.start >= 0]
    for i, t in enumerate(tokens):
        if t.start >= 0: continue
        prev = max([k for k in known if k < i], default=None)
        nxt = min([k for k in known if k > i], default=None)
        a = tokens[prev].end if prev is not None else offset
        b = tokens[nxt].start if nxt is not None else a + 0.3
        t.start, t.end = a, max(a + 0.05, b)


class Timeline:
    def __init__(self, beats, cache_dir, voice=TTS.VOICE, rate=TTS.RATE, lead_in=0.1, tail=0.6):
        self.beats = beats
        self.sr = sr = TTS.SR
        t = lead_in
        for b in beats:
            phrases = b.text if isinstance(b.text, (list, tuple)) else [Ph(b.text, pause=b.pause)]
            b.start, b.tokens, b.segments = t, [], []
            for ph in phrases:
                toks = parse(ph.text, b.id)
                say = " ".join(tk.say for tk in toks)
                audio, words = TTS.synthesize(say, cache_dir, voice=voice, rate=ph.rate or b.rate or rate,
                                              pitch=ph.pitch or "+0Hz")
                if words:   # recorta el silencio que agrega el TTS antes y después
                    s0 = max(0.0, words[0]["start"] - 0.05)
                    s1 = min(len(audio) / sr, words[-1]["end"] + 0.14)
                else:
                    s0, s1 = 0.0, len(audio) / sr
                seg = audio[int(s0 * sr):int(s1 * sr)].copy()
                fi, fo = int(0.008 * sr), int(0.05 * sr)
                seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.linspace(1, 0, fo)
                _align(toks, words, t - s0)
                b.segments.append((t, seg))
                b.tokens += toks
                t += len(seg) / sr + ph.pause
            b.audio = np.concatenate([sg for _, sg in b.segments])
            b.dur = t - b.start
        self.duration = t + tail
        self.tokens = [tk for b in beats for tk in b.tokens]
        self.by_id = {b.id: b for b in beats}

    # ------- cues -------
    def t(self, beat_id, word=None, which=0, end=False):
        """Tiempo de inicio del beat o de la palabra `word` (n-ésima aparición)."""
        b = self.by_id[beat_id]
        if word is None:
            return b.end if end else b.start
        nw = _norm(word); k = 0
        for tk in b.tokens:
            if nw in (_norm(tk.display), _norm(tk.say)) or _norm(tk.say).startswith(nw) \
                    or _norm(tk.display).startswith(nw):
                if k == which:
                    return tk.end if end else tk.start
                k += 1
        raise KeyError(f"palabra '{word}' no encontrada en beat '{beat_id}'")

    def voice_track(self):
        n = int(self.duration * self.sr) + 1
        out = np.zeros(n, np.float32)
        for b in self.beats:
            for st, sg in b.segments:
                i = int(st * self.sr)
                seg = sg[: max(0, n - i)]
                out[i:i + len(seg)] += seg
        return out

    # ------- subtítulos -------
    def chunks(self, measure, max_w=880, max_lines=2, max_words=5):
        """Agrupa tokens en bloques de ≤2 líneas. measure(str)->ancho px."""
        out = []
        for b in self.beats:
            cur = []
            def flush():
                if cur: out.append(cur.copy()); cur.clear()
            for k, tk in enumerate(b.tokens):
                if cur:
                    lines = wrap([x.display for x in cur + [tk]], measure, max_w)
                    # evita dejar una palabra huérfana que cierra la frase
                    orphan = tk.display[-1] in ".?!:;," and len(cur) < max_words + 2
                    if len(lines) > max_lines or (len(cur) >= max_words and not orphan):
                        flush()
                cur.append(tk)
                if tk.display[-1] in ".?!:;" or (tk.display[-1] == "," and len(cur) >= 3):
                    flush()
            flush()
        res = []
        for i, ch in enumerate(out):
            st = ch[0].start
            nxt = out[i + 1][0].start if i + 1 < len(out) else ch[-1].end + 0.6
            en = min(nxt, ch[-1].end + 0.7)
            res.append({"tokens": ch, "start": st, "end": en,
                        "lines": wrap([x.display for x in ch], measure, max_w)})
        return res

    def srt(self, chunks):
        def fmt(s):
            ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000)
            sec, ms = divmod(ms, 1000); return f"{h:02}:{m:02}:{sec:02},{ms:03}"
        lines = []
        for i, c in enumerate(chunks, 1):
            words = [t.display for t in c["tokens"]]
            txt = "\n".join(" ".join(words[a:b]) for a, b in c["lines"])
            lines += [str(i), f"{fmt(c['start'])} --> {fmt(c['end'])}", txt, ""]
        return "\n".join(lines)

    def script_text(self):
        return "\n\n".join(f"[{b.id}] ({b.start:5.1f}s – {b.end:5.1f}s)\n" +
                           " ".join(t.display for t in b.tokens) for b in self.beats)


def wrap(words, measure, max_w):
    """Devuelve lista de (i0, i1) índices por línea, equilibrando largo."""
    lines, i0, wcur = [], 0, 0.0
    sp = measure(" ")
    for i, w in enumerate(words):
        ww = measure(w)
        if i > i0 and wcur + sp + ww > max_w:
            lines.append((i0, i)); i0, wcur = i, ww
        else:
            wcur = ww if i == i0 else wcur + sp + ww
    lines.append((i0, len(words)))
    # equilibra 2 líneas: mueve palabras si la segunda es muy corta
    if len(lines) == 2:
        best = None
        for k in range(1, len(words)):
            a = measure(" ".join(words[:k])); b = measure(" ".join(words[k:]))
            if a <= max_w and b <= max_w:
                score = abs(a - b)
                if best is None or score < best[0]: best = (score, k)
        if best: lines = [(0, best[1]), (best[1], len(words))]
    return lines
