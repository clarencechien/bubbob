// 參考圖 → 32x32 像素精靈轉檔器（pixel-by-pixel：區塊眾數 + 調色盤合併）
// 用法：node tools/convert_ref.mjs <輸入圖> <輸出前綴>
// 產出 <前綴>1.png（原姿勢）與 <前綴>2.png（下沉 1px 的走路 bob 幀）
// 開發工具：需要 Playwright 的 Chromium 來解碼/編碼 PNG，遊戲本體仍零相依。
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync, writeFileSync } from 'fs';

const [,, input, prefix] = process.argv;
if (!input || !prefix) { console.error('usage: node convert_ref.mjs <in.png> <out-prefix>'); process.exit(1); }

const b64 = readFileSync(input).toString('base64');
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage();

const result = await page.evaluate(async (b64) => {
  const img = new Image();
  await new Promise(res => { img.onload = res; img.src = 'data:image/png;base64,' + b64; });
  const W = img.width, H = img.height;
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const g = cv.getContext('2d');
  g.drawImage(img, 0, 0);
  const d = g.getImageData(0, 0, W, H).data;
  const px = (x, y) => { const i = (y * W + x) * 4; return [d[i], d[i+1], d[i+2]]; };
  const alpha = (x, y) => d[(y * W + x) * 4 + 3];
  const dist = (a, b) => Math.hypot(a[0]-b[0], a[1]-b[1], a[2]-b[2]);

  // 1) 背景判定：AI 匯出的 PNG 常把背景（甚至白色區）做成透明。
  //    「可視為背景」= 透明，或角落是不透明色時的近似色。
  const corners = [[0,0],[W-1,0],[0,H-1],[W-1,H-1]];
  const cornerOpaque = corners.filter(([x,y]) => alpha(x,y) > 200).map(([x,y]) => px(x,y));
  const bgLike = (x, y) => alpha(x, y) < 200 || cornerOpaque.some(k => dist(px(x,y), k) < 120);
  // 從邊界 flood-fill：連得到外面的才算背景
  const bg = new Uint8Array(W * H);
  const stack = [];
  for (let x = 0; x < W; x++) { stack.push([x,0], [x,H-1]); }
  for (let y = 0; y < H; y++) { stack.push([0,y], [W-1,y]); }
  while (stack.length) {
    const [x, y] = stack.pop();
    const i = y * W + x;
    if (bg[i] || !bgLike(x, y)) continue;
    bg[i] = 1;
    if (x > 0) stack.push([x-1,y]);
    if (x < W-1) stack.push([x+1,y]);
    if (y > 0) stack.push([x,y-1]);
    if (y < H-1) stack.push([x,y+1]);
  }
  // 被輪廓包住的透明洞 = 被 key 掉的白色（眼白、肚皮），補回白色
  const holeWhite = (x, y) => !bg[y*W+x] && alpha(x, y) < 200;

  // 2) bounding box：用行/列直方圖，忽略零星噪點（門檻 6px）
  const colN = new Array(W).fill(0), rowN = new Array(H).fill(0);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    if (!bg[y*W+x]) { colN[x]++; rowN[y]++; }
  }
  const TH = 6;
  let x0 = colN.findIndex(n => n >= TH), x1 = W - 1 - [...colN].reverse().findIndex(n => n >= TH);
  let y0 = rowN.findIndex(n => n >= TH), y1 = H - 1 - [...rowN].reverse().findIndex(n => n >= TH);
  const side = Math.max(x1-x0+1, y1-y0+1);
  const cx = (x0+x1)/2, cy = (y0+y1)/2;
  x0 = Math.round(cx - side/2); y0 = Math.round(cy - side/2);

  // 3) 每個目標格 = 來源區塊的「非背景眾數色」（16 階分桶）
  const T = 32;
  const cell = side / T;
  const out = []; // [r,g,b,a] * T*T
  for (let ty = 0; ty < T; ty++) {
    for (let tx = 0; tx < T; tx++) {
      const sx0 = Math.max(0, Math.round(x0 + tx*cell)), sx1 = Math.min(W-1, Math.round(x0 + (tx+1)*cell) - 1);
      const sy0 = Math.max(0, Math.round(y0 + ty*cell)), sy1 = Math.min(H-1, Math.round(y0 + (ty+1)*cell) - 1);
      const buckets = new Map(); let n = 0, nbg = 0;
      for (let y = sy0; y <= sy1; y++) for (let x = sx0; x <= sx1; x++) {
        n++;
        if (bg[y*W+x]) continue;
        nbg++;
        const c = holeWhite(x, y) ? [255, 255, 255] : px(x, y);
        const key = (c[0]>>4)+','+(c[1]>>4)+','+(c[2]>>4);
        const b = buckets.get(key) || { c: [0,0,0], n: 0 };
        b.c[0]+=c[0]; b.c[1]+=c[1]; b.c[2]+=c[2]; b.n++;
        buckets.set(key, b);
      }
      if (!n || nbg / n < 0.45) { out.push([0,0,0,0]); continue; }
      let best = null;
      for (const b of buckets.values()) if (!best || b.n > best.n) best = b;
      out.push([Math.round(best.c[0]/best.n), Math.round(best.c[1]/best.n), Math.round(best.c[2]/best.n), 255]);
    }
  }

  // 4) 全域調色盤合併：把出現的顏色聚成少數代表色（貪婪、距離門檻）
  const colors = [];
  for (const c of out) {
    if (!c[3]) continue;
    const hit = colors.find(k => dist(k.c, c) < 52);
    if (hit) { hit.n++; hit.sum[0]+=c[0]; hit.sum[1]+=c[1]; hit.sum[2]+=c[2]; }
    else colors.push({ c: [...c], sum: [...c.slice(0,3)], n: 1 });
  }
  colors.forEach(k => { k.c = [Math.round(k.sum[0]/k.n), Math.round(k.sum[1]/k.n), Math.round(k.sum[2]/k.n)]; });
  for (const c of out) {
    if (!c[3]) continue;
    let best = null, bd = 1e9;
    for (const k of colors) { const dd = dist(k.c, c); if (dd < bd) { bd = dd; best = k; } }
    c[0] = best.c[0]; c[1] = best.c[1]; c[2] = best.c[2];
  }

  // 5) 輸出兩幀：原姿勢 + 下沉 1px（走路 bob）
  const render = (shift) => {
    const oc = document.createElement('canvas');
    oc.width = T; oc.height = T;
    const og = oc.getContext('2d');
    const id = og.createImageData(T, T);
    for (let y = 0; y < T; y++) for (let x = 0; x < T; x++) {
      const sy = y - shift;
      if (sy < 0 || sy >= T) continue;
      const c = out[sy*T+x];
      const i = (y*T+x)*4;
      id.data[i] = c[0]; id.data[i+1] = c[1]; id.data[i+2] = c[2]; id.data[i+3] = c[3];
    }
    og.putImageData(id, 0, 0);
    return oc.toDataURL('image/png');
  };
  return { f1: render(0), f2: render(1), palette: colors.length };
}, b64);

writeFileSync(prefix + '1.png', Buffer.from(result.f1.split(',')[1], 'base64'));
writeFileSync(prefix + '2.png', Buffer.from(result.f2.split(',')[1], 'base64'));
console.log('palette colors:', result.palette);
await browser.close();
