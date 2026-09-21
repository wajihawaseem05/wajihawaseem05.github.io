"""Make web-sized copies of photos in images/community/.

Drop the original photo into images/community/ (named by date, e.g. 26-Oct-2022.jpg),
then run:  python tools/make-community-images.py

For each photo it writes
  images/community/fulls/<name>.jpg   longest edge 1600px, for the lightbox
  images/community/thumbs/<name>.jpg  740x434 crop, for the grid
Photos that already have both outputs are skipped. Originals are never modified.
"""
from PIL import Image, ImageOps
import glob, os

ROOT = os.path.join(os.path.dirname(__file__), '..', 'images', 'community')
TW, TH = 740, 434       # thumbnail size (same shape as the grid slot)
FULL_MAX = 1600         # longest edge of the lightbox version
ANCHOR_Y = 0.40         # 0 = keep top of photo, 0.5 = centre, 1 = keep bottom

os.makedirs(os.path.join(ROOT, 'thumbs'), exist_ok=True)
os.makedirs(os.path.join(ROOT, 'fulls'), exist_ok=True)

for src in sorted(glob.glob(os.path.join(ROOT, '*.*'))):
    name = os.path.splitext(os.path.basename(src))[0]
    full_path = os.path.join(ROOT, 'fulls', name + '.jpg')
    thumb_path = os.path.join(ROOT, 'thumbs', name + '.jpg')
    if os.path.exists(full_path) and os.path.exists(thumb_path):
        continue

    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')

    if not os.path.exists(full_path):
        full = im.copy()
        full.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
        full.save(full_path, quality=82, optimize=True, progressive=True)

    if not os.path.exists(thumb_path):
        w, h = im.size
        scale = max(TW / w, TH / h)                       # scale so the photo covers the box
        big = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        left = (big.width - TW) // 2
        top = int((big.height - TH) * ANCHOR_Y)
        big.crop((left, top, left + TW, top + TH)).save(thumb_path, quality=82, optimize=True)

    print(f'{name}: full {os.path.getsize(full_path)//1024} KB, thumb {os.path.getsize(thumb_path)//1024} KB')

print('done')
