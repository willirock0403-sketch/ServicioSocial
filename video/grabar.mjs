// Graba render.html cuadro por cuadro y arma el MP4 con la narración.
// Uso: node grabar.mjs [salida.mp4] [--prueba T1,T2,...]
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { spawn } from 'node:child_process';
import { readFileSync, mkdirSync, rmSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// playwright local o global
let chromium;
try { ({ chromium } = createRequire(import.meta.url)('playwright')); }
catch { ({ chromium } = createRequire(execSync('npm root -g').toString().trim() + '/')('playwright')); }

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30, PARTES = 4;
const args = process.argv.slice(2);
const prueba = args.includes('--prueba') ? args[args.indexOf('--prueba') + 1].split(',').map(Number) : null;
const salida = path.resolve(args.find(a => a.endsWith('.mp4')) || path.join(AQUI, '..', 'Servicio_Social_FIT.mp4'));
const tiempos = JSON.parse(readFileSync(path.join(AQUI, 'tiempos.json'), 'utf8'));

async function abrir(browser){
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(AQUI, 'render.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth));
  const total = await page.evaluate(t => window.prep(t), tiempos);
  return { page, total };
}

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
if (prueba) {
  const { page } = await abrir(browser);
  for (const T of prueba) {
    await page.evaluate(T => window.seek(T), T);
    await page.screenshot({ path: path.join(AQUI, 'prueba_' + T + '.jpg'), type: 'jpeg', quality: 85 });
  }
  await browser.close(); process.exit(0);
}

const { page: p0, total } = await abrir(browser);
await p0.close();
const N = Math.ceil(total * FPS), tmp = path.join(AQUI, '.partes');
rmSync(tmp, { recursive: true, force: true }); mkdirSync(tmp);
console.log(`total ${total.toFixed(2)} s, ${N} cuadros`);

async function parte(k){
  const a = Math.floor(N * k / PARTES), b = Math.floor(N * (k + 1) / PARTES);
  const { page } = await abrir(browser);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', String(FPS), path.join(tmp, `p${k}.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
  // recorre desde el inicio para que cada escena se active en orden
  for (let f = 0; f < b; f++) {
    await page.evaluate(T => window.seek(T), f / FPS);
    if (f < a) continue;
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 300 === 0) console.log(`parte ${k}: cuadro ${f}/${b}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await page.close();
}
await Promise.all([...Array(PARTES).keys()].map(parte));
await browser.close();

const lista = [...Array(PARTES).keys()].map(k => `file '${path.join(tmp, `p${k}.mp4`)}'`).join('\n');
const { writeFileSync } = await import('node:fs');
writeFileSync(path.join(tmp, 'lista.txt'), lista);
await new Promise((res, rej) => spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'lista.txt'),
  '-i', path.join(AQUI, 'audio', 'narracion.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
  '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-af', 'loudnorm=I=-16:TP=-1.5', '-shortest', '-movflags', '+faststart', salida],
  { stdio: 'inherit' }).on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()));
rmSync(tmp, { recursive: true, force: true });
console.log('listo:', salida);
