# 32x32 原創像素角色產生器（v2：參考使用者提供的概念圖重繪）
# 產出：
#   dragon_walk1/2.png  玩家小龍（側面朝右、行走兩幀）
#   grump_walk1/2.png   敵人氣噗噗（正面、行走兩幀）
#   rage_walk1/2.png    暴走型態（紅色調色盤置換，同兩幀）
# 用法：python3 tools/pixelart.py [輸出資料夾]
import zlib, struct, sys, os

SZ = 32
def blank(): return [['.' for _ in range(SZ)] for _ in range(SZ)]

def ellipse(g, cx, cy, rx, ry, ch, only=None):
    for y in range(SZ):
        for x in range(SZ):
            if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1.0:
                if only is None or g[y][x] in only:
                    g[y][x] = ch

def put(g, pts, ch):
    for x, y in pts:
        if 0 <= x < SZ and 0 <= y < SZ: g[y][x] = ch

def rect(g, x0, y0, x1, y1, ch):
    for y in range(y0, y1+1):
        for x in range(x0, x1+1):
            if 0 <= x < SZ and 0 <= y < SZ: g[y][x] = ch

def tri(g, apex, base_y, half, ch):
    # 尖端在上的三角形
    ax, ay = apex
    for y in range(ay, base_y+1):
        w = round(half * (y-ay) / max(1, base_y-ay))
        for x in range(ax-w, ax+w+1):
            if 0 <= x < SZ and 0 <= y < SZ: g[y][x] = ch

def outline(g, ch='K'):
    out = [row[:] for row in g]
    for y in range(SZ):
        for x in range(SZ):
            if g[y][x] != '.': continue
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x+dx, y+dy
                if 0 <= nx < SZ and 0 <= ny < SZ and g[ny][nx] not in ('.', ch):
                    out[y][x] = ch; break
    return out

def shade(g, body, cx, cy, light, dark, t=4.0):
    for y in range(SZ):
        for x in range(SZ):
            if g[y][x] in body:
                v = (x-cx)*0.5 + (y-cy)
                if v < -t: g[y][x] = light
                elif v > t+1: g[y][x] = dark

# ---------------- 玩家小龍（側面朝右，依概念圖：大頭小身、張嘴紅舌） ----------------
def dragon(frame):
    g = blank()
    bob = 1 if frame == 1 else 0
    hy = 11 + bob   # 頭中心 y
    by = 22 + bob   # 身體中心 y
    # 身體（小）先畫，頭（大）疊上去
    ellipse(g, 13.5, by, 7.0, 6.0, 'G')
    ellipse(g, 19, hy, 9.0, 8.3, 'G')
    shade(g, ('G',), 17, hy + 3, 'L', 'g', t=5.5)
    # 頭頂 + 背側 圓角黃刺（概念圖是圓方塊不是尖刺）
    rect(g, 15, 0 + bob, 17, 2 + bob, 'Y')
    rect(g, 10, 2 + bob, 12, 4 + bob, 'Y')
    rect(g, 7, 7 + bob, 9, 9 + bob, 'Y')
    # 背側小翅膀（深綠、一道亮摺）
    put(g, [(6,14+bob),(7,14+bob),(8,14+bob),(9,14+bob),
            (5,15+bob),(6,15+bob),(7,15+bob),(8,15+bob),(9,15+bob),
            (6,16+bob),(7,16+bob),(8,16+bob),(7,17+bob),(8,17+bob)], 'g')
    put(g, [(7,15+bob),(8,15+bob)], 'G')
    # 白肚（大、乾淨）＋底部淡藍影（概念圖特徵）
    ellipse(g, 16.5, by + 1.5, 5.6, 5.2, 'B', only=('G','L','g'))
    ellipse(g, 16.5, by + 4.5, 4.2, 1.8, 'w', only=('B',))
    # 超大眼（白）＋大黑瞳（右側）＋眼神光
    ellipse(g, 21.5, hy - 2, 3.4, 4.0, 'W')
    rect(g, 22, hy - 4, 24, hy + 1, 'P')
    put(g, [(22, hy - 4), (22, hy - 3)], 'W')
    # 鼻孔
    put(g, [(27, hy + 1)], 'P')
    # 張嘴大笑：黑口 + 紅舌（下半）
    rect(g, 20, hy + 4, 26, hy + 6, 'P')
    put(g, [(27, hy + 3), (19, hy + 4)], 'K')
    rect(g, 21, hy + 5, 25, hy + 7, 'R')
    put(g, [(20, hy + 4), (21, hy + 4)], 'W')  # 上排小牙
    # 黃色臉頰（嘴左邊）
    rect(g, 17, hy + 4, 18, hy + 5, 'Y')
    # 前爪（跨在肚子前、白色小爪尖）
    put(g, [(14,by-2),(15,by-2),(16,by-2),(15,by-1),(16,by-1),(17,by-1)], 'G')
    put(g, [(17,by-2),(18,by-2)], 'W')
    # 粗尾巴（左下勾、底緣淡藍）
    put(g, [(6,by+2),(5,by+3),(4,by+3),(5,by+4),(4,by+4),(3,by+4),(3,by+5),(4,by+5)], 'G')
    put(g, [(2,by+5),(3,by+6),(4,by+6)], 'g')
    put(g, [(2,by+6)], 'w')
    # 腳（兩幀交替）＋白爪尖
    if frame == 0:
        rect(g, 16, 27, 20, 29, 'G'); put(g, [(21,29)], 'W')
        rect(g, 9, 27, 13, 29, 'g')
    else:
        rect(g, 13, 28, 17, 30, 'G'); put(g, [(18,30)], 'W')
        rect(g, 9, 28, 12, 30, 'g')
    return outline(g)

# ---------------- 敵人氣噗噗（正面，參考概念圖：大蝙蝠耳） ----------------
def grump(frame):
    g = blank()
    bob = 1 if frame == 1 else 0
    cy = 17 + bob
    ellipse(g, 16, cy, 9.6, 8.8, 'M')
    shade(g, ('M',), 16, cy - 1, 'N', 'm')
    # 大蝙蝠耳（左右）+ 內耳
    tri(g, (6, 4 + bob), 11 + bob, 3, 'M')
    tri(g, (26, 4 + bob), 11 + bob, 3, 'M')
    put(g, [(6,7+bob),(6,8+bob),(7,8+bob),(26,7+bob),(26,8+bob),(25,8+bob)], 'm')
    # 頭頂小刺
    put(g, [(14,7+bob),(15,6+bob),(17,6+bob),(18,7+bob),(16,5+bob)], 'm')
    # 怒眉（粗黑內斜，高一點別壓住眼白）
    put(g, [(9,10+bob),(10,10+bob),(11,11+bob),(12,11+bob),(13,12+bob),
            (9,11+bob),(10,11+bob),(11,12+bob),(12,12+bob)], 'K')
    put(g, [(23,10+bob),(22,10+bob),(21,11+bob),(20,11+bob),(19,12+bob),
            (23,11+bob),(22,11+bob),(21,12+bob),(20,12+bob)], 'K')
    # 眼白 + 內下瞳孔
    rect(g, 9, 13+bob, 12, 16+bob, 'W')
    rect(g, 20, 13+bob, 23, 16+bob, 'W')
    rect(g, 11, 14+bob, 12, 16+bob, 'P')
    rect(g, 20, 14+bob, 21, 16+bob, 'P')
    put(g, [(11,14+bob),(21,14+bob)], 'W')
    # 上唇線 + 往下的白獠牙（參考圖特徵）
    put(g, [(10,19+bob),(11,19+bob),(12,19+bob),(13,19+bob),(14,19+bob),(15,19+bob),
            (16,19+bob),(17,19+bob),(18,19+bob),(19,19+bob),(20,19+bob),(21,19+bob)], 'K')
    rect(g, 12, 20+bob, 13, 21+bob, 'W')
    rect(g, 19, 20+bob, 20, 21+bob, 'W')
    # 小拳頭（兩側）
    ellipse(g, 5.2, cy + 3, 1.9, 2.1, 'm')
    ellipse(g, 26.8, cy + 3, 1.9, 2.1, 'm')
    # 腳（兩幀交替）
    if frame == 0:
        rect(g, 9, 27, 13, 29, 'm')
        rect(g, 19, 27, 23, 29, 'm')
    else:
        rect(g, 10, 28, 14, 30, 'm')
        rect(g, 18, 28, 22, 30, 'm')
    return outline(g)

PAL = {
  'K': (17,19,30,255),
  # 龍
  'G': (70,176,46,255), 'g': (44,122,28,255), 'L': (122,214,74,255),
  'B': (255,255,255,255), 'w': (199,221,242,255),
  'Y': (246,201,46,255), 'R': (224,49,49,255),
  # 怪
  'M': (138,92,245,255), 'm': (92,55,184,255), 'N': (183,149,255,255),
  'W': (255,255,255,255), 'P': (16,16,24,255),
  '.': (0,0,0,0),
}
# 暴走 = 強度色置換（紫 → 紅系；「強度的顏色」）
RAGE_MAP = { 'M': (239,83,68,255), 'm': (181,45,36,255), 'N': (255,159,138,255) }

def write_png(path, g, pal_over=None):
    pal = dict(PAL)
    if pal_over: pal.update(pal_over)
    raw = b''
    for row in g:
        raw += b'\x00' + b''.join(bytes(pal[c]) for c in row)
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data))
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', SZ, SZ, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    open(path, 'wb').write(png)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'assets'
    os.makedirs(out, exist_ok=True)
    for f in (0, 1):
        write_png(f'{out}/dragon_walk{f+1}.png', dragon(f))
        write_png(f'{out}/grump_walk{f+1}.png', grump(f))
        write_png(f'{out}/rage_walk{f+1}.png', grump(f), RAGE_MAP)
    print('written to', out)
