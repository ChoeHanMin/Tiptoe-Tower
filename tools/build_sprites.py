# 잘라낸 그림을 게임용 크기로 줄여 WebP data URI 로 만든다.
import sys, json, base64, io
from PIL import Image, ImageEnhance
S = sys.argv[1]; SP = S + '/sprites'; meta = json.load(open(SP + '/meta.json'))
PX = 3.2   # 논리 1px 당 저장 픽셀 (폰 고해상도 대비)
out = {}
def enc(im, q=82):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6); return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
def add(key, im, logical_h, dim=False):
    h = max(4, round(logical_h * PX)); w = max(4, round(im.size[0] * h / im.size[1]))
    im = im.resize((w, h), Image.LANCZOS)
    if dim:   # 배경 소품: 채도·밝기 낮춤
        rgb = im.convert('RGB'); a = im.getchannel('A')
        rgb = ImageEnhance.Color(rgb).enhance(.55); rgb = ImageEnhance.Brightness(rgb).enhance(.62)
        im = rgb.convert('RGBA'); im.putalpha(a.point(lambda v: int(v * .92)))
    out[key] = [enc(im), round(logical_h / h, 5)]   # [이미지, 논리px/저장px]
def sheet(base, logical_h0, keys=None):
    # 시트 안 그림끼리 크기 비율을 유지 (0번 그림 높이 = logical_h0)
    h0 = meta[base][0][1]
    for i, (w, h) in enumerate(meta[base]):
        if keys is not None and i not in keys: continue
        add(f'{base}_{i}', Image.open(f'{SP}/{base}_{i}.png'), logical_h0 * h / h0)
for r in ['normal', 'sensitive', 'heavy', 'baby', 'grandpa', 'gamer']:
    sheet('res_' + r, 62 if r != 'baby' else 56)
sheet('dog_guard', 20)                  # 0번(엎드린 강아지) 기준 → 경비원 약 55
sheet('ball_faces', 26)
# 다른 공 5종: 몸통 폭이 지름(약 28)이 되게 그림마다 폭 기준으로 맞춤
def by_width(base, logical_w, keys=None, dim=False):
    for i, (w, h) in enumerate(meta[base]):
        if keys is not None and i not in keys: continue
        add(f'{base}_{i}', Image.open(f'{SP}/{base}_{i}.png'), logical_w * h / w, dim)
for b in ['bowling', 'feather', 'ghost', 'hamster', 'ice']:
    if 'ball_' + b in meta: by_width('ball_' + b, 27)
if 'items' in meta: by_width('items', 24)
if 'movers' in meta:
    for i, lw in {0: 34, 1: 34, 2: 36, 3: 46, 4: 34, 5: 36, 6: 38, 7: 26, 8: 16}.items():
        by_width('movers', lw, [i])
sheet('tv', 40)
PROPS = {   # 번호: (위치 f=바닥/w=벽/c=천장 근처, 논리 높이)
  'props_home':  {0: ('f', 40), 1: ('w', 28), 3: ('c', 16), 4: ('w', 22), 5: ('f', 18)},
  'props_pet':   {0: ('f', 60), 1: ('f', 10), 3: ('f', 18), 4: ('w', 34), 5: ('f', 13), 6: ('w', 36)},
  'props_kids':  {0: ('w', 38), 1: ('f', 28), 2: ('f', 24), 3: ('f', 38), 4: ('f', 34), 5: ('f', 10)},
  'props_old':   {0: ('w', 42), 1: ('w', 42), 2: ('c', 28), 3: ('c', 13), 5: ('f', 46)},   # 4번(낡은 선풍기)은 선풍기 장애물과 헷갈려서 제외
  'props_gamer': {0: ('f', 42), 3: ('f', 44), 4: ('f', 20), 5: ('f', 15), 6: ('f', 13)},
  'props_guard': {0: ('f', 46), 1: ('f', 40), 2: ('w', 36), 3: ('f', 28), 5: ('f', 16)},
}
plist = {}
for base, items in PROPS.items():
    plist[base] = []
    for i, (pos, lh) in items.items():
        add(f'{base}_{i}', Image.open(f'{SP}/{base}_{i}.png'), lh, dim=True); plist[base].append([f'{base}_{i}', pos])
# 타이틀 (불투명 그림)
for name, size in [('title_portrait', (720, 1080)), ('title_landscape', (1152, 768)), ('ending', (720, 1080)), ('ending_landscape', (1280, 720))]:
    im = Image.open(f'{S}/assets_in/{name}.png').convert('RGB').resize(size, Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=72, method=6); out[name] = ['data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode(), 1]
js = ('<!-- SPRITES:BEGIN (자동 생성된 그림 데이터. 직접 고치지 마세요) -->\n<script>\nwindow.TT_SPRITES = ' + json.dumps(out, separators=(',', ':')) +
      ';\nwindow.TT_PROPS = ' + json.dumps(plist, ensure_ascii=False, separators=(',', ':')) + ';\n</script>\n<!-- SPRITES:END -->')
open(S + '/sprites.html', 'w').write(js)
tot = sum(len(v[0]) for v in out.values())
print('sprites', len(out), 'total KB', tot // 1024)
for k in ['res_normal_0', 'res_baby_0', 'dog_guard_0', 'dog_guard_3', 'ball_faces_0', 'tv_2', 'props_home_0', 'title_portrait', 'title_landscape']:
    print(k, len(out[k][0]) // 1024, 'KB', out[k][1])
