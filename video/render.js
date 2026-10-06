// Control del tiempo para grabar el video cuadro por cuadro.
// window.prep(tiempos) prepara las escenas; window.seek(T) deja el cuadro en el segundo T.
(function(){
  var stage = document.getElementById('stage'),
      scenes = Array.prototype.slice.call(document.querySelectorAll('.scene')),
      wipe = document.getElementById('wipe'),
      cc = document.getElementById('cc'),
      warn = document.getElementById('warn');
  var TM, cur = -1, starts = new Map();

  window.prep = function(tiempos){
    TM = tiempos;
    TM.escenas.forEach(function(e, k){
      e.frases.forEach(function(f){ if(f.aviso && warn) warn.style.setProperty('--d', Math.max(0, f.ini - .3) + 's'); });
    });
    TM.total = TM.escenas.reduce(function(a, e){ return Math.max(a, e.ini + e.dur); }, 0);
    return TM.total;
  };

  function go(i, T0){
    cur = i;
    scenes.forEach(function(s){ s.classList.remove('active'); });
    var sc = scenes[i];
    sc.style.setProperty('--dur', TM.escenas[i].dur + 's');
    void sc.offsetWidth;
    sc.classList.add('active');
    stage.classList.toggle('cover-mode', sc.classList.contains('cover'));
    if(i > 0){ wipe.classList.remove('go'); void wipe.offsetWidth; wipe.classList.add('go'); }
    document.getAnimations().forEach(function(a){ if(!starts.has(a)) starts.set(a, T0); });
  }

  window.seek = function(T){
    var i = -1;
    TM.escenas.forEach(function(e, k){ if(T >= e.ini) i = k; });
    if(i >= 0 && i !== cur) go(i, TM.escenas[i].ini);
    if(i < 0) stage.classList.add('cover-mode');
    var anims = document.getAnimations();
    anims.forEach(function(a){
      if(!starts.has(a)) starts.set(a, i < 0 ? 0 : TM.escenas[i].ini);
      a.pause();
      a.currentTime = Math.max(0, (T - starts.get(a)) * 1000);
    });
    // subtítulo: la frase que se está diciendo (o la próxima, si aún no empieza)
    var txt = '';
    if(i >= 0){
      var e = TM.escenas[i], t = T - e.ini;
      txt = e.frases[0].texto;
      e.frases.forEach(function(f){ if(t >= f.ini - .15) txt = f.texto; });
    }
    if(cc.textContent !== txt) cc.textContent = txt;
  };

  document.getAnimations().forEach(function(a){ a.pause(); starts.set(a, 0); });
})();
