from pptx import Presentation
from pptx.oxml.ns import qn
from copy import deepcopy
import zipfile, os

SRC = r'd:/claude mini max 2.7/storage_market_output/CCS_Global_Storage_2025_2030.pptx'

with zipfile.ZipFile(SRC) as z:
    files = sorted(z.namelist())
    media = [f for f in files if f.startswith('ppt/media/')]
    slides = [f for f in files if f.endswith('.xml') and '/slides/slide' in f and '_rels' not in f]
    print(f"Media: {len(media)}")
    print(f"Slides: {len(slides)}")
    print("Media samples:", media[:8])

    # Check slide rels for images
    for s in slides[:3]:
        r = s.replace('.xml', '.xml.rels')
        r = r.replace('slides/', 'slides/_rels/')
        if r in files:
            data = z.read(r).decode('utf-8')
            has_img = 'image' in data.lower()
            print(f"{s}: has_image_rel={has_img}")
