# Cuerpo al Dato - equipo de producción (playbook)

Meta: máximas vistas para ingresos. Idioma: español latino neutro, tuteo (NUNCA voseo). Canal: @cuerpoaldato (Instagram, TikTok, YouTube).

## Roles
1. **Investigador**: busca en la web 14 temas nuevos (datos del cuerpo humano, "¿qué pasa si…?" y "cómo prevenir…"). Evita repetir temas ya publicados (lista abajo). Prioriza temas universales y con riesgo/curiosidad personal.
2. **Guionista**: 50-58 s por video. Gancho de 3 s con tensión o dato sorprendente, un dato por línea, cierre con pregunta o "guárdalo". Datos verificables, sin consejos médicos peligrosos. Formato en `ep08.txt` y `ep08.beats.json` (ejemplo).
3. **Voz**: `tts_b3z.py` (edge-tts es-CL-LorenzoNeural) corre en GitHub Actions del repo privado `diegoauguin-ux/bodyfacts-studio` (workflow `tts.yml`). Genera mp3 por línea.
4. **Editor**: `build_audio.py` y `render5.py` (ver comandos) producen el mp4 1080x1920. Comprimir para subir: `ffmpeg -i in.mp4 -vf scale=720:1280 -b:v 330k -maxrate 420k -bufsize 800k -c:a aac -b:a 64k -ac 1 out.mp4`.
5. **Publicador**: sube mp4 a este repo público (URL raw) y programa con Buffer (`create_post`, canales Instagram `6af1954b62b70b94b0cd748f` y TikTok `6af195e562b70b94b0cd783b`, `isAiGenerated: true`). YouTube se programa en studio.youtube.com (Shorts, "no es para niños", título con #Shorts).
6. **Analista**: revisa vistas y retención (Buffer insights, YouTube Studio) y ajusta ganchos y horarios.

## Horarios (Sydney)
10:00 y 13:00 todos los días (≈ tarde en Chile y México).

## Comandos
```
python3 build_audio.py b3 epXX        # une mp3 -> b3/epXX.wav + b3/epXX.json
python3 render5.py b3/epXX.json b3/epXX.wav out.mp4 epXX.beats.json
```
Tipos de beat: hook{prop,mood,label}, stat{big,label,prop,size}, bars{label,bars}, stamp{claim,verdict,vcol}, cards, cta. Props: stomach, glass, bulb, cell, drop, shield, virus, brain, phone, clock, moon.

## Temas ya publicados
ep05 estómago/ácido, ep06 agua en ayunas, ep07 luz del cuerpo, ep08 8 h sentado, ep09 celular en cama, ep10 café y adenosina.
