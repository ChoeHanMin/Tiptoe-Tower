# 그림 다시 넣기

`assets/`의 원본 PNG를 바꾼 뒤 아래 순서로 실행하면 `index.html` 맨 아래 그림 데이터(SPRITES 블록)가 새로 만들어집니다. (Python 3 + Pillow 필요)

```bash
mkdir -p work/sprites
python3 tools/slice.py assets work/sprites          # 시트를 한 장씩 잘라냄
python3 tools/build_sprites.py work                   # work/sprites.html 생성 (assets 폴더를 work/assets_in 으로 복사해 두기)
```

만들어진 `work/sprites.html` 내용으로 `index.html`의 `<!-- SPRITES:BEGIN` ~ `<!-- SPRITES:END -->` 부분을 바꾸면 됩니다.
방 소품의 위치(바닥/벽)와 크기는 `build_sprites.py`의 `PROPS` 표에서 정합니다.
