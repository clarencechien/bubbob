import zlib, struct

SZ = 32
def blank(): return [['.' for _ in range(SZ)] for _ in range(SZ)]

def ellipse(g, cx, cy, rx, ry, ch, cond=None):
    for y in range(SZ):
        for x in range(SZ):
            if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1.0:
                if cond is None or cond(x, y):
                    g[y][x] = ch

def put(g, pts, ch):
    for x, y in pts:
        if 0 <= x < SZ and 0 <= y < SZ: g[y][x] = ch

def outline(g, ch='K'):
    # 在形狀外圍加 1px 描邊
    out = [row[:] for row in g]
    for y in range(SZ):
        for x in range(SZ):
            if g[y][x] != '.': continue
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x+dx, y+dy
                if 0 <= nx < SZ and 0 <= ny < SZ and g[ny][nx] not in ('.', ch):
                    out[y][x] = ch; break
    return out

def shade(g, body_chs, cx, cy, light_ch, dark_ch, t=4.2):
    # 左上受光、右下陰影
    for y in range(SZ):
        for x in range(SZ):
            if g[y][x] in body_chs:
                v = (x-cx)*0.55 + (y-cy)
                if v < -t: g[y][x] = light_ch
                elif v > t+1: g[y][x] = dark_ch

# ---------- 小龍（面向右，前視、瞳孔朝右） ----------
def dragon():
    g = blank()
    ellipse(g, 16, 17, 10.5, 11.2, 'G')          # 身體
    shade(g, ('G',), 16, 17, 'L', 'g')
    ellipse(g, 16, 23, 6.2, 5.0, 'B')            # 肚皮
    ellipse(g, 16, 21, 5.0, 2.4, 'B')
    # 手臂（小圓球）
    ellipse(g, 5.4, 19.5, 2.0, 2.3, 'g')
    ellipse(g, 26.6, 19.5, 2.0, 2.3, 'g')
    # 腳
    ellipse(g, 10.5, 28.6, 3.0, 2.2, 'G')
    ellipse(g, 21.5, 28.6, 3.0, 2.2, 'G')
    # 角（奶油色）
    put(g, [(10,3),(11,3),(10,4),(11,4),(12,4),(9,5),(10,5),(11,5),(12,5)], 'B')
    put(g, [(20,3),(21,3),(19,4),(20,4),(21,4),(19,5),(20,5),(21,5),(22,5)], 'B')
    # 短尾（左下圓潤小球＋橘尖）
    ellipse(g, 3.6, 23.5, 2.4, 2.0, 'G')
    put(g, [(1,24),(1,25),(2,25)], 'O')
    # 眼白
    ellipse(g, 12.3, 12, 2.4, 3.0, 'W')
    ellipse(g, 19.7, 12, 2.4, 3.0, 'W')
    # 瞳孔（朝右）＋眼神光
    put(g, [(13,11),(14,11),(13,12),(14,12),(13,13),(14,13)], 'P')
    put(g, [(20,11),(21,11),(20,12),(21,12),(20,13),(21,13)], 'P')
    put(g, [(14,11),(21,11)], 'W')
    # 鼻孔
    put(g, [(14,15),(17,15)], 'P')
    # 微笑嘴＋雙虎牙（乾淨的一條弧線）
    put(g, [(12,16),(13,17),(14,17),(15,17),(16,17),(17,17),(18,17),(19,16)], 'K')
    put(g, [(13,18),(18,18)], 'W')
    # 臉頰
    put(g, [(8,14),(9,14),(22,14),(23,14)], 'R')
    return outline(g)

# ---------- 敵人「氣噗噗」（紫色圓怪） ----------
def grump():
    g = blank()
    ellipse(g, 16, 17, 10.6, 10.2, 'M')
    # 底部壓平一點
    for x in range(SZ):
        for y in range(28, SZ): 
            if g[y][x] == 'M': g[y][x] = '.'
    shade(g, ('M',), 16, 16, 'N', 'm')
    # 角（深紫）
    put(g, [(8,4),(9,4),(8,5),(9,5),(10,5),(7,6),(8,6),(9,6),(10,6)], 'm')
    put(g, [(22,4),(23,4),(21,5),(22,5),(23,5),(21,6),(22,6),(23,6),(24,6)], 'm')
    # 腳
    ellipse(g, 11, 28.3, 2.8, 2.0, 'm')
    ellipse(g, 21, 28.3, 2.8, 2.0, 'm')
    # 眼白
    ellipse(g, 11.6, 13.5, 2.4, 2.5, 'W')
    ellipse(g, 20.4, 13.5, 2.4, 2.5, 'W')
    # 怒眉（內斜，短一點、離眼白遠一點）
    put(g, [(9,9),(10,9),(11,10),(12,10)], 'K')
    put(g, [(22,9),(21,9),(20,10),(19,10)], 'K')
    # 瞳孔
    put(g, [(12,14),(13,14),(12,15),(13,15)], 'P')
    put(g, [(19,14),(20,14),(19,15),(20,15)], 'P')
    # 大嘴（怒）＋牙
    for x in range(11, 21):
        for y in range(20, 24): g[y][x] = 'D'
    put(g, [(10,20),(10,21),(21,20),(21,21),(11,19),(20,19)], 'K')
    put(g, [(12,20),(13,20),(15,20),(16,20),(18,20),(19,20)], 'W')  # 上排牙
    put(g, [(14,23),(17,23)], 'W')                                   # 下排牙
    # 身上斑點
    put(g, [(7,20),(8,21),(24,19),(23,22),(16,7)], 'N')
    return outline(g)

PAL = {
  'K': (26,28,44,255),    # 描邊
  'G': (63,191,90,255),   # 綠
  'g': (46,143,67,255),   # 綠影
  'L': (116,224,138,255), # 綠亮
  'B': (247,237,192,255), # 奶油
  'W': (255,255,255,255),
  'P': (20,20,31,255),
  'R': (255,143,158,255), # 臉頰
  'O': (255,157,60,255),  # 橘
  'M': (138,92,245,255),  # 紫
  'm': (106,63,208,255),  # 紫影
  'N': (177,140,255,255), # 紫亮
  'D': (74,29,110,255),   # 嘴內
  '.': (0,0,0,0),
}

def write_png(path, g):
    raw = b''
    for row in g:
        raw += b'\x00' + b''.join(bytes(PAL[c]) for c in row)
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data))
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', SZ, SZ, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    open(path, 'wb').write(png)

d, e = dragon(), grump()
write_png('dragon.png', d)
write_png('grump.png', e)
for name, g in (('DRAGON', d), ('GRUMP', e)):
    print(name)
    print('\n'.join(''.join(r) for r in g))
