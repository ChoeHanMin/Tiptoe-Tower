import sys, json, os
import numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
def runs(v, gap):
    idx = np.where(v)[0]
    if not len(idx): return []
    res=[]; s=idx[0]; p=idx[0]
    for i in idx[1:]:
        if i-p > gap: res.append((s,p)); s=i
        p=i
    res.append((s,p)); return res
meta={}
for name in sorted(os.listdir(src)):
    if not name.endswith('.png') or name.startswith('title'): continue
    im=Image.open(os.path.join(src,name)).convert('RGBA'); a=np.array(im)[...,3]>40
    pieces=[]
    for (r0,r1) in runs(a.any(1), 14):
        band=a[r0:r1+1]
        cols=runs(band.any(0), 14)
        cells=[]
        for (c0,c1) in cols:
            sub=band[:,c0:c1+1]; rr=np.where(sub.any(1))[0]
            cells.append([c0,c1,r0+rr[0],r0+rr[-1]])
        # 작은 조각(효과선 등)은 가까운 큰 조각에 합침
        big=[c for c in cells if c[1]-c[0] > 70 and c[3]-c[2] > 50]
        for c in cells:
            if c in big: continue
            if not big: big.append(c); continue
            cx=(c[0]+c[1])/2
            t=min(big,key=lambda b: abs((b[0]+b[1])/2-cx))
            t[0]=min(t[0],c[0]); t[1]=max(t[1],c[1]); t[2]=min(t[2],c[2]); t[3]=max(t[3],c[3])
        big=sorted(big, key=lambda b: b[0])
        # 주민 시트는 4칸이어야 함: 붙어 있으면 가장 얇은 세로줄에서 나눔
        while name.startswith('res_') and len(big) < 4:
            w=max(big,key=lambda b:b[1]-b[0]); i=big.index(w)
            sub=band[:,w[0]:w[1]+1].sum(0); n=len(sub); lo,hi=int(n*.3),int(n*.7)
            cut=w[0]+lo+int(np.argmin(sub[lo:hi]))
            left=[w[0],cut-1,w[2],w[3]]; right=[cut+1,w[1],w[2],w[3]]
            for c in (left,right):
                rr=np.where(band[:,c[0]:c[1]+1].any(1))[0]; c[2]=r0+rr[0]; c[3]=r0+rr[-1]
            big[i:i+1]=[left,right]
        pieces += big
    base=name[:-4]; meta[base]=[]
    for i,(c0,c1,r0,r1) in enumerate(pieces):
        crop=im.crop((c0,r0,c1+1,r1+1))
        crop.save(f'{out}/{base}_{i}.png'); meta[base].append([int(c1-c0+1), int(r1-r0+1)])
    print(base, len(pieces), meta[base])
json.dump(meta, open(f'{out}/meta.json','w'))
