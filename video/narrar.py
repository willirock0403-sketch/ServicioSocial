"""Genera la narración (voz Kokoro ef_dora, español latino) y los tiempos de cada escena.

Uso: python3 narrar.py <modelo.onnx> <voices.npz>
Salida: audio/narracion.wav y tiempos.json (en esta carpeta).
"""
import json, os, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

AQUI = os.path.dirname(os.path.abspath(__file__))
INTRO = 2.6        # cortinilla de entrada (sin voz)
ENTRADA = 0.7      # silencio al empezar cada escena
ENTRE = 0.45       # pausa entre frases
SALIDA = 1.1       # silencio al terminar cada escena
VOZ, VEL = "ef_dora", 0.98

k = Kokoro(sys.argv[1], sys.argv[2])
escenas = json.load(open(os.path.join(AQUI, "narracion.json"), encoding="utf-8"))
sr = 24000
pistas, tiempos, t = [np.zeros(int(INTRO * sr))], {"intro": INTRO, "escenas": []}, INTRO
for e in escenas:
    ini, t, frases = t, t + ENTRADA, []
    pistas.append(np.zeros(int(ENTRADA * sr)))
    for n, f in enumerate(e["frases"]):
        f = f if isinstance(f, dict) else {"texto": f}
        a, sr = k.create(f["texto"], voice=VOZ, speed=VEL, lang="es-419")
        frases.append({"texto": f["texto"], "ini": round(t - ini, 3), "fin": round(t - ini + len(a) / sr, 3), "aviso": f.get("aviso", False)})
        pistas.append(a); t += len(a) / sr
        pausa = ENTRE if n < len(e["frases"]) - 1 else SALIDA
        pistas.append(np.zeros(int(pausa * sr))); t += pausa
    tiempos["escenas"].append({"id": e["id"], "ini": round(ini, 3), "dur": round(t - ini, 3), "frases": frases})
    print(e["id"], round(t - ini, 2))
os.makedirs(os.path.join(AQUI, "audio"), exist_ok=True)
sf.write(os.path.join(AQUI, "audio", "narracion.wav"), np.concatenate(pistas), sr)
json.dump(tiempos, open(os.path.join(AQUI, "tiempos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total", round(t, 2))
