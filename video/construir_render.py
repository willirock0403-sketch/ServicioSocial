"""Arma render.html (solo el cuadro de 1920x1080) a partir de escenas.html.

escenas.html es la animación original de las escenas; aquí se le agrega la
cortinilla de entrada y el control de tiempo para grabarla en MP4.
"""
import os, re, json
AQUI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(AQUI, "escenas.html"), encoding="utf-8").read()

css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
stage = re.search(r'(<div id="stage".*?)\n</div>\n\n<div id="bar">', src, re.S).group(1)

stage = stage.replace('<div id="stage" class="paused">', '<div id="stage">')
stage = stage.replace(
    '<img class="l-uat" data-img="uat" alt="Universidad Autónoma de Tamaulipas">',
    '<img class="l-uat" data-img="uat" alt="">\n      <p class="mid">Registro · <b>Servicio Social</b></p>')
n = [0]
def paso(m):
    n[0] += 1
    return m.group(0) + f'<span class="of">{n[0]} / 6</span>'
stage = re.sub(r'<div class="step a-wipe"><span class="tag">PASO \d</span><h2>.*?</h2>', paso, stage)
stage = stage.replace('<div class="title-band a-wipe" style="--d:.55s">',
    '<p class="kicker a-rise" style="--d:.35s">Guía paso a paso · <b>Servicio Social</b></p>\n        <div class="title-band a-wipe" style="--d:.55s">', 1)
stage = stage.replace('<div class="warn a-rise" style="--d:11s">', '<div class="warn a-rise" id="warn">')

sting = '''
    <!-- cortinilla de entrada -->
    <div id="sting">
      <span class="s-lg"></span><span class="s-red"></span><span class="s-gray"></span><span class="s-rail"></span>
      <div class="s-box">
        <img class="s-logo" data-img="lockup" alt="">
        <span class="s-line"></span>
        <p class="s-dept">Coordinación de<br>Exámenes Estandarizados</p>
        <p class="s-name">Mtra. Paulina Fernández Izaguirre</p>
      </div>
    </div>
'''
stage = stage.replace('    <div id="cc"></div>', sting + '    <div id="cc"></div>')

extra = '''
html,body{background:#fff;overflow:hidden}
#stage{left:0;top:0}
#hdr .mid{font-size:17px;font-weight:700;letter-spacing:.14em;color:var(--gris-med);text-transform:uppercase}
#hdr .mid b{color:var(--rojo);font-weight:800}
.step .of{background:var(--gris);color:#fff;font-size:20px;font-weight:700;display:flex;align-items:center;padding:0 26px;letter-spacing:.08em;white-space:nowrap}
.kicker{font-size:22px;font-weight:700;letter-spacing:.22em;color:var(--gris-med);text-transform:uppercase;margin-bottom:22px}
.kicker b{color:var(--rojo);font-weight:800}
.lockup{margin-bottom:40px}
#cc:empty{opacity:0}
#stage:not(.nocc) #ftr{opacity:0}

#sting{position:absolute;inset:0;z-index:8;background:#fff;overflow:hidden;display:flex;align-items:center;justify-content:center;text-align:center;
  animation:curtain .85s cubic-bezier(.77,0,.18,1) 2.6s both}
#sting::after{content:"";position:absolute;left:0;right:0;bottom:0;height:14px;background:var(--rojo)}
#sting .s-rail{position:absolute;left:0;top:0;width:16px;height:100%;background:var(--rojo)}
#sting .s-lg{position:absolute;left:0;top:0;width:78%;height:240px;background:var(--gris-claro);clip-path:polygon(0 0,100% 0,100% 40%,0 100%)}
#sting .s-red{position:absolute;right:0;top:0;width:380px;height:300px;background:var(--rojo);clip-path:polygon(30% 0,100% 0,100% 100%)}
#sting .s-gray{position:absolute;left:0;bottom:14px;width:100%;height:110px;background:var(--gris-med);clip-path:polygon(0 100%,100% 18%,100% 100%)}
#sting .s-box{position:relative}
#sting .s-logo{display:block;width:820px;height:auto;margin:0 auto 44px;animation:iPop .8s cubic-bezier(.2,.9,.3,1) .05s both}
#sting .s-line{display:block;width:170px;height:7px;background:var(--rojo);margin:0 auto 38px;animation:iLine .6s cubic-bezier(.4,0,.2,1) .45s both}
#sting .s-dept{font-size:48px;font-weight:800;color:var(--gris);line-height:1.22;letter-spacing:.01em;animation:iRise .7s cubic-bezier(.2,.8,.25,1) .6s both}
#sting .s-name{margin-top:22px;font-size:34px;font-weight:700;color:var(--rojo);letter-spacing:.02em;animation:iRise .7s cubic-bezier(.2,.8,.25,1) .85s both}
@keyframes iPop{from{opacity:0;transform:scale(.92) translateY(14px)}to{opacity:1;transform:none}}
@keyframes iLine{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes iRise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes curtain{from{transform:none}to{transform:translateY(-100%)}}
'''

imgs = {k: f"img/{k}." + ("png" if k in ("uat", "fit", "lockup") else "jpg")
        for k in ["uat", "fit", "lockup", "hoja", "login", "panel", "cal", "d1", "d2", "d3", "d4"]}

html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Render — Servicio Social</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=block" rel="stylesheet">
<style>{css}{extra}</style>
</head>
<body>
{stage}
<script>
var IMG = {json.dumps(imgs)};
document.querySelectorAll('[data-img]').forEach(function(el){{ el.src = IMG[el.getAttribute('data-img')]; }});
</script>
<script src="render.js"></script>
</body>
</html>
'''
open(os.path.join(AQUI, "render.html"), "w", encoding="utf-8").write(html)
print("render.html listo,", n[0], "pasos")
