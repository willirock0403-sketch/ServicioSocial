# Video del Servicio Social

Cómo se genera `Servicio_Social_FIT.mp4` (1920x1080, 30 fps, voz en español con subtítulos).

1. `narracion.json`: texto de la narración por escena, en trato de usted.
2. `python3 narrar.py <kokoro.onnx> <voices.npz>`: genera la voz (Kokoro-82M, voz `ef_dora`, español latino) en `audio/narracion.wav` y los tiempos en `tiempos.json`.
3. `python3 construir_render.py`: arma `render.html` a partir de `escenas.html` y le agrega la cortinilla de entrada.
4. `node grabar.mjs ../Servicio_Social_FIT.mp4`: graba `render.html` cuadro por cuadro con Playwright y une el video con la narración usando ffmpeg.

Para revisar algunos cuadros sueltos sin grabar todo: `node grabar.mjs --prueba 1.5,20,60`.
